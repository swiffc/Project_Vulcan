"""
TradingView Browser Controller - Playwright-based browser automation
Allows logged-in TradingView with user's indicators to be displayed in Vulcan.

Features:
- Persistent session (login once, stays logged in)
- Navigate to any symbol/timeframe
- Screenshot streaming for web UI display
- Click/keyboard forwarding for interaction
"""

import os
import json
import base64
import asyncio
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# Playwright imported lazily
_browser = None
_context = None
_page = None
_streaming = False

# Session storage path
SESSION_DIR = Path(__file__).parent.parent / "data" / "tradingview_session"
SESSION_DIR.mkdir(parents=True, exist_ok=True)

router = APIRouter(prefix="/tradingview", tags=["tradingview"])


class NavigateRequest(BaseModel):
    symbol: str = "GBPUSD"
    interval: str = "60"  # 1, 5, 15, 60, 240, D, W


class ClickRequest(BaseModel):
    x: int
    y: int
    button: str = "left"


class KeyRequest(BaseModel):
    key: str
    modifiers: list[str] = []


_playwright = None

async def get_playwright():
    """Lazy import and initialize Playwright."""
    global _browser, _context, _page, _playwright

    # Check if existing page is still valid
    if _page is not None:
        try:
            # Test if page is still alive
            await _page.title()
            return _page
        except Exception:
            # Page is dead, reset everything
            logger.info("Browser was closed, resetting...")
            _page = None
            _context = None
            _browser = None

    try:
        from playwright.async_api import async_playwright
    except ImportError:
        raise HTTPException(
            status_code=503,
            detail="Playwright not installed. Run: pip install playwright && playwright install chromium"
        )

    logger.info("Initializing Playwright browser for TradingView...")

    # Start new playwright instance
    _playwright = await async_playwright().start()

    # Launch browser with persistent context for session storage
    _context = await _playwright.chromium.launch_persistent_context(
        user_data_dir=str(SESSION_DIR),
        headless=False,  # Show browser so user can login
        viewport=None,  # Let it use full window
        no_viewport=True,  # Don't constrain viewport
        args=[
            "--disable-blink-features=AutomationControlled",
            "--start-maximized",
            "--window-position=100,100",
            "--window-size=1600,900",
        ]
    )

    # Get or create page
    if _context.pages:
        _page = _context.pages[0]
    else:
        _page = await _context.new_page()

    logger.info("Playwright browser initialized with persistent session")
    return _page


async def close_browser():
    """Close the browser and cleanup."""
    global _browser, _context, _page

    if _context:
        await _context.close()
    _browser = None
    _context = None
    _page = None
    logger.info("TradingView browser closed")


@router.get("/status")
async def get_status():
    """Get TradingView browser status."""
    return {
        "browser_active": _page is not None,
        "session_dir": str(SESSION_DIR),
        "streaming": _streaming,
        "timestamp": datetime.now().isoformat()
    }


@router.post("/launch")
async def launch_tradingview(request: NavigateRequest = None):
    """
    Launch TradingView in browser.
    First time: Browser opens, user logs in manually.
    Subsequent times: Already logged in from saved session.
    """
    page = await get_playwright()

    symbol = request.symbol if request else "GBPUSD"
    interval = request.interval if request else "60"

    # Build TradingView URL
    url = f"https://www.tradingview.com/chart/?symbol={symbol}&interval={interval}"

    logger.info(f"Navigating to TradingView: {url}")
    await page.goto(url, wait_until="networkidle", timeout=30000)

    # Wait for chart to load
    await asyncio.sleep(2)

    # Check if login modal appeared
    try:
        login_button = await page.query_selector('button[data-name="header-user-menu-button"]')
        logged_in = login_button is not None
    except:
        logged_in = False

    return {
        "status": "launched",
        "url": url,
        "logged_in": logged_in,
        "message": "Browser opened. If not logged in, please log in manually - your session will be saved."
    }


@router.post("/navigate")
async def navigate_to_symbol(request: NavigateRequest):
    """Navigate to a different symbol/timeframe."""
    if _page is None:
        raise HTTPException(status_code=400, detail="Browser not launched. Call /launch first.")

    url = f"https://www.tradingview.com/chart/?symbol={request.symbol}&interval={request.interval}"

    logger.info(f"Navigating to: {url}")
    await _page.goto(url, wait_until="networkidle", timeout=30000)
    await asyncio.sleep(1)

    return {"status": "navigated", "symbol": request.symbol, "interval": request.interval}


@router.get("/screenshot")
async def get_screenshot():
    """Get current screenshot of TradingView chart."""
    if _page is None:
        raise HTTPException(status_code=400, detail="Browser not launched. Call /launch first.")

    # Take screenshot
    screenshot_bytes = await _page.screenshot(type="jpeg", quality=85)
    screenshot_b64 = base64.b64encode(screenshot_bytes).decode("utf-8")

    return {
        "screenshot": f"data:image/jpeg;base64,{screenshot_b64}",
        "timestamp": datetime.now().isoformat()
    }


@router.post("/click")
async def click_on_chart(request: ClickRequest):
    """Send a click to the TradingView page."""
    if _page is None:
        raise HTTPException(status_code=400, detail="Browser not launched.")

    await _page.mouse.click(request.x, request.y, button=request.button)
    return {"status": "clicked", "x": request.x, "y": request.y}


@router.post("/key")
async def send_key(request: KeyRequest):
    """Send a keyboard input to TradingView."""
    if _page is None:
        raise HTTPException(status_code=400, detail="Browser not launched.")

    # Build key combination
    if request.modifiers:
        key_combo = "+".join(request.modifiers + [request.key])
        await _page.keyboard.press(key_combo)
    else:
        await _page.keyboard.press(request.key)

    return {"status": "key_sent", "key": request.key, "modifiers": request.modifiers}


@router.post("/type")
async def type_text(text: str):
    """Type text (for symbol search etc)."""
    if _page is None:
        raise HTTPException(status_code=400, detail="Browser not launched.")

    await _page.keyboard.type(text, delay=50)
    return {"status": "typed", "text": text}


@router.post("/close")
async def close_tradingview():
    """Close the TradingView browser."""
    await close_browser()
    return {"status": "closed"}


@router.websocket("/stream")
async def screenshot_stream(websocket: WebSocket):
    """
    WebSocket endpoint for streaming screenshots.
    Enables real-time chart display in web UI.
    """
    global _streaming

    await websocket.accept()
    _streaming = True

    logger.info("TradingView screenshot stream started")

    try:
        while True:
            if _page is None:
                await websocket.send_json({"error": "Browser not launched"})
                await asyncio.sleep(1)
                continue

            # Capture screenshot
            screenshot_bytes = await _page.screenshot(type="jpeg", quality=70)
            screenshot_b64 = base64.b64encode(screenshot_bytes).decode("utf-8")

            # Send to client
            await websocket.send_json({
                "screenshot": f"data:image/jpeg;base64,{screenshot_b64}",
                "timestamp": datetime.now().isoformat()
            })

            # ~10 FPS
            await asyncio.sleep(0.1)

    except WebSocketDisconnect:
        logger.info("TradingView stream client disconnected")
    except Exception as e:
        logger.error(f"Stream error: {e}")
    finally:
        _streaming = False


# Convenience endpoints for common actions
@router.post("/search")
async def search_symbol(symbol: str):
    """Open symbol search and type symbol."""
    if _page is None:
        raise HTTPException(status_code=400, detail="Browser not launched.")

    # Press / to open search (TradingView shortcut)
    await _page.keyboard.press("/")
    await asyncio.sleep(0.3)
    await _page.keyboard.type(symbol, delay=30)
    await asyncio.sleep(0.5)
    await _page.keyboard.press("Enter")
    await asyncio.sleep(1)

    return {"status": "searched", "symbol": symbol}


@router.post("/timeframe")
async def change_timeframe(interval: str):
    """
    Change timeframe using keyboard shortcut.
    Supported: 1, 5, 15, 60 (1H), 240 (4H), D, W, M
    """
    if _page is None:
        raise HTTPException(status_code=400, detail="Browser not launched.")

    # TradingView keyboard shortcuts for timeframes
    shortcuts = {
        "1": "1",
        "5": "5",
        "15": "1",  # Then 5
        "60": "shift+1",  # 1H
        "240": "shift+4",  # 4H
        "D": "d",
        "W": "w",
        "M": "m"
    }

    if interval in shortcuts:
        await _page.keyboard.press(shortcuts[interval])
        if interval == "15":
            await _page.keyboard.press("5")

    return {"status": "timeframe_changed", "interval": interval}
