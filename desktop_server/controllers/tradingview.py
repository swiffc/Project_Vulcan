"""
TradingView Browser Controller - Playwright-based browser automation
Based on: https://github.com/ali-rajabpour/tradingview-mcp

Uses session cookies for authentication (more reliable than login flow).
User extracts cookies from browser DevTools once, then headless Playwright uses them.

Features:
- Session cookie authentication (no visible browser needed after setup)
- Headless mode for better performance
- Navigate to any symbol/timeframe
- Screenshot streaming for web UI display
"""

import os
import json
import base64
import asyncio
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# Playwright state
_playwright = None
_browser = None
_context = None
_page = None
_is_initialized = False

# Config paths
CONFIG_DIR = Path(__file__).parent.parent / "data"
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
COOKIES_FILE = CONFIG_DIR / "tradingview_cookies.json"
STORAGE_STATE_FILE = CONFIG_DIR / "tradingview_state.json"

router = APIRouter(prefix="/tradingview", tags=["tradingview"])


class NavigateRequest(BaseModel):
    symbol: str = "FX:GBPUSD"
    interval: str = "60"


class CookiesRequest(BaseModel):
    session_id: str
    session_id_sign: str


class ClickRequest(BaseModel):
    x: int
    y: int


async def init_playwright(headless: bool = True):
    """Initialize Playwright with stored cookies/state."""
    global _playwright, _browser, _context, _page, _is_initialized

    if _is_initialized and _page:
        try:
            await _page.title()
            return _page
        except Exception:
            logger.info("Browser closed, reinitializing...")
            _is_initialized = False

    try:
        from playwright.async_api import async_playwright
    except ImportError:
        raise HTTPException(
            status_code=503,
            detail="Playwright not installed. Run: pip install playwright && playwright install chromium"
        )

    logger.info(f"Initializing Playwright (headless={headless})...")

    _playwright = await async_playwright().start()

    # Check if we have storage state
    storage_state = None
    if STORAGE_STATE_FILE.exists():
        storage_state = str(STORAGE_STATE_FILE)
        logger.info("Loading saved browser state...")

    # Launch browser
    _browser = await _playwright.chromium.launch(
        headless=headless,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-setuid-sandbox",
        ]
    )

    # Create context with storage state if available
    context_options = {
        "viewport": {"width": 1920, "height": 1080},
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }

    if storage_state:
        context_options["storage_state"] = storage_state

    _context = await _browser.new_context(**context_options)
    _page = await _context.new_page()

    # If we have cookies file but no storage state, inject cookies
    if not storage_state and COOKIES_FILE.exists():
        logger.info("Injecting session cookies...")
        await inject_cookies_from_file()

    _is_initialized = True
    logger.info("Playwright initialized successfully")
    return _page


async def inject_cookies_from_file():
    """Inject TradingView cookies from saved file."""
    if not COOKIES_FILE.exists() or not _context:
        return False

    try:
        with open(COOKIES_FILE) as f:
            cookie_data = json.load(f)

        cookies = [
            {
                "name": "sessionid",
                "value": cookie_data.get("session_id", ""),
                "domain": ".tradingview.com",
                "path": "/",
                "httpOnly": True,
                "secure": True,
            },
            {
                "name": "sessionid_sign",
                "value": cookie_data.get("session_id_sign", ""),
                "domain": ".tradingview.com",
                "path": "/",
                "httpOnly": True,
                "secure": True,
            },
        ]

        await _context.add_cookies(cookies)
        logger.info("Cookies injected successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to inject cookies: {e}")
        return False


async def save_storage_state():
    """Save current browser state for future sessions."""
    if _context:
        await _context.storage_state(path=str(STORAGE_STATE_FILE))
        logger.info("Browser state saved")


@router.get("/status")
async def get_status():
    """Get TradingView browser status."""
    has_cookies = COOKIES_FILE.exists()
    has_state = STORAGE_STATE_FILE.exists()

    return {
        "browser_active": _is_initialized,
        "has_cookies": has_cookies,
        "has_storage_state": has_state,
        "cookies_file": str(COOKIES_FILE),
        "ready": has_cookies or has_state,
        "timestamp": datetime.now().isoformat()
    }


@router.post("/setup-cookies")
async def setup_cookies(request: CookiesRequest):
    """
    Save TradingView session cookies.
    User extracts these from browser DevTools after logging in.
    """
    if not request.session_id or not request.session_id_sign:
        raise HTTPException(status_code=400, detail="Both session_id and session_id_sign are required")

    # Save cookies to file
    cookie_data = {
        "session_id": request.session_id,
        "session_id_sign": request.session_id_sign,
        "saved_at": datetime.now().isoformat()
    }

    with open(COOKIES_FILE, "w") as f:
        json.dump(cookie_data, f, indent=2)

    logger.info("TradingView cookies saved")

    # Clear old storage state so new cookies are used
    if STORAGE_STATE_FILE.exists():
        STORAGE_STATE_FILE.unlink()

    return {"status": "saved", "message": "Cookies saved. Click 'Launch' to test."}


@router.post("/launch")
async def launch_tradingview(request: NavigateRequest = None):
    """Launch TradingView chart with saved credentials."""
    symbol = request.symbol if request else "FX:GBPUSD"
    interval = request.interval if request else "60"

    # Check if we have credentials
    if not COOKIES_FILE.exists() and not STORAGE_STATE_FILE.exists():
        raise HTTPException(
            status_code=400,
            detail="No credentials found. Please set up cookies first via /setup-cookies"
        )

    # Initialize browser (headless)
    page = await init_playwright(headless=True)

    # Navigate to TradingView chart
    url = f"https://www.tradingview.com/chart/?symbol={symbol}&interval={interval}"
    logger.info(f"Navigating to: {url}")

    try:
        await page.goto(url, wait_until="networkidle", timeout=30000)
        await asyncio.sleep(2)  # Wait for chart to render

        # Save state for future sessions
        await save_storage_state()

        # Check if logged in by looking for user menu
        is_logged_in = False
        try:
            user_menu = await page.query_selector('[data-name="header-user-menu-button"]')
            is_logged_in = user_menu is not None
        except:
            pass

        return {
            "status": "launched",
            "url": url,
            "logged_in": is_logged_in,
            "message": "TradingView loaded" + (" (logged in)" if is_logged_in else " (not logged in - check cookies)")
        }

    except Exception as e:
        logger.error(f"Failed to launch TradingView: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/navigate")
async def navigate_to_symbol(request: NavigateRequest):
    """Navigate to a different symbol/timeframe."""
    if not _is_initialized or not _page:
        raise HTTPException(status_code=400, detail="Browser not launched. Call /launch first.")

    url = f"https://www.tradingview.com/chart/?symbol={request.symbol}&interval={request.interval}"
    logger.info(f"Navigating to: {url}")

    try:
        await _page.goto(url, wait_until="networkidle", timeout=30000)
        await asyncio.sleep(1)
        return {"status": "navigated", "symbol": request.symbol, "interval": request.interval}
    except Exception as e:
        logger.error(f"Navigation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/screenshot")
async def get_screenshot():
    """Get current screenshot of TradingView chart."""
    if not _is_initialized or not _page:
        raise HTTPException(status_code=400, detail="Browser not launched. Call /launch first.")

    try:
        screenshot_bytes = await _page.screenshot(type="jpeg", quality=85)
        screenshot_b64 = base64.b64encode(screenshot_bytes).decode("utf-8")

        return {
            "screenshot": f"data:image/jpeg;base64,{screenshot_b64}",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Screenshot failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/click")
async def click_on_chart(request: ClickRequest):
    """Send a click to the TradingView page."""
    if not _is_initialized or not _page:
        raise HTTPException(status_code=400, detail="Browser not launched.")

    try:
        await _page.mouse.click(request.x, request.y)
        return {"status": "clicked", "x": request.x, "y": request.y}
    except Exception as e:
        logger.error(f"Click failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/close")
async def close_tradingview():
    """Close the TradingView browser."""
    global _playwright, _browser, _context, _page, _is_initialized

    try:
        if _context:
            await save_storage_state()
            await _context.close()
        if _browser:
            await _browser.close()
        if _playwright:
            await _playwright.stop()
    except Exception as e:
        logger.error(f"Close error: {e}")

    _playwright = None
    _browser = None
    _context = None
    _page = None
    _is_initialized = False

    return {"status": "closed"}


@router.delete("/cookies")
async def delete_cookies():
    """Delete saved cookies and storage state."""
    if COOKIES_FILE.exists():
        COOKIES_FILE.unlink()
    if STORAGE_STATE_FILE.exists():
        STORAGE_STATE_FILE.unlink()

    return {"status": "deleted", "message": "Cookies and storage state cleared"}


# WebSocket for streaming (alternative to polling)
@router.websocket("/stream")
async def screenshot_stream(websocket: WebSocket):
    """WebSocket endpoint for streaming screenshots."""
    await websocket.accept()
    logger.info("Screenshot stream started")

    try:
        while True:
            if not _is_initialized or not _page:
                await websocket.send_json({"error": "Browser not launched"})
                await asyncio.sleep(1)
                continue

            try:
                screenshot_bytes = await _page.screenshot(type="jpeg", quality=70)
                screenshot_b64 = base64.b64encode(screenshot_bytes).decode("utf-8")

                await websocket.send_json({
                    "screenshot": f"data:image/jpeg;base64,{screenshot_b64}",
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                await websocket.send_json({"error": str(e)})

            await asyncio.sleep(0.15)  # ~7 FPS

    except WebSocketDisconnect:
        logger.info("Stream client disconnected")
    except Exception as e:
        logger.error(f"Stream error: {e}")
