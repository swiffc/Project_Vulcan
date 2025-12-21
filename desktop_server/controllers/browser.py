"""
Browser Controller - Playwright-based browser automation for J2 Tracker and other web apps.

This module provides:
- Persistent browser session management
- Cookie-based authentication
- SSO login support (visible browser for user login)
- Page scraping and interaction
"""

import os
import logging
import json
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# Playwright is optional - gracefully handle missing
try:
    from playwright.async_api import async_playwright, Browser, BrowserContext, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logger.warning("Playwright not installed. Run: pip install playwright && playwright install chromium")

router = APIRouter(prefix="/browser", tags=["browser"])

# Session storage path
SESSION_DIR = Path(os.environ.get("SESSION_DIR", "./data/browser_sessions"))
SESSION_DIR.mkdir(parents=True, exist_ok=True)

# Global browser instance
_browser: Optional["Browser"] = None
_context: Optional["BrowserContext"] = None
_pages: Dict[str, "Page"] = {}


# ============= Request/Response Models =============

class NavigateRequest(BaseModel):
    url: str
    session_id: str = "default"
    wait_for: str = "load"  # load, domcontentloaded, networkidle


class ClickRequest(BaseModel):
    session_id: str = "default"
    selector: str


class TypeRequest(BaseModel):
    session_id: str = "default"
    selector: str
    text: str
    clear_first: bool = True


class WaitRequest(BaseModel):
    session_id: str = "default"
    selector: str
    timeout: int = 30000  # ms


class ExtractRequest(BaseModel):
    session_id: str = "default"
    selector: str
    attribute: Optional[str] = None  # None = inner text, 'href', 'src', etc.


class ExtractTableRequest(BaseModel):
    session_id: str = "default"
    table_selector: str
    header_row: int = 0


class SSOLoginRequest(BaseModel):
    session_id: str
    login_url: str
    success_url_pattern: str  # regex pattern to detect successful login
    timeout: int = 120  # seconds to wait for user to complete SSO


class SessionInfo(BaseModel):
    session_id: str
    url: Optional[str] = None
    title: Optional[str] = None
    cookies_stored: bool = False


# ============= Browser Lifecycle =============

async def get_browser() -> "Browser":
    """Get or create the browser instance."""
    global _browser

    if not PLAYWRIGHT_AVAILABLE:
        raise HTTPException(status_code=503, detail="Playwright not installed")

    if _browser is None or not _browser.is_connected():
        pw = await async_playwright().start()
        _browser = await pw.chromium.launch(
            headless=False,  # Visible browser for SSO
            args=[
                "--start-maximized",
                "--disable-blink-features=AutomationControlled",
            ]
        )
        logger.info("Browser launched (visible mode for SSO)")

    return _browser


async def get_context(session_id: str = "default") -> "BrowserContext":
    """Get or create a browser context with session persistence."""
    global _context

    browser = await get_browser()

    if _context is None:
        # Load stored session if available
        session_file = SESSION_DIR / f"{session_id}_cookies.json"
        storage_state = None

        if session_file.exists():
            try:
                storage_state = str(session_file)
                logger.info(f"Restoring session from {session_file}")
            except Exception as e:
                logger.warning(f"Failed to load session: {e}")

        _context = await browser.new_context(
            storage_state=storage_state,
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        logger.info(f"Browser context created for session: {session_id}")

    return _context


async def get_page(session_id: str = "default") -> "Page":
    """Get or create a page for the session."""
    global _pages

    if session_id not in _pages or _pages[session_id].is_closed():
        context = await get_context(session_id)
        page = await context.new_page()
        _pages[session_id] = page
        logger.info(f"New page created for session: {session_id}")

    return _pages[session_id]


async def save_session(session_id: str):
    """Save the current session cookies."""
    global _context

    if _context:
        session_file = SESSION_DIR / f"{session_id}_cookies.json"
        await _context.storage_state(path=str(session_file))
        logger.info(f"Session saved: {session_file}")


# ============= Endpoints =============

@router.get("/status")
async def browser_status():
    """Get browser status."""
    global _browser, _context, _pages

    return {
        "playwright_available": PLAYWRIGHT_AVAILABLE,
        "browser_running": _browser is not None and _browser.is_connected() if _browser else False,
        "context_active": _context is not None,
        "active_pages": list(_pages.keys()),
        "session_dir": str(SESSION_DIR),
    }


@router.post("/launch")
async def launch_browser():
    """Launch the browser (visible for SSO)."""
    if not PLAYWRIGHT_AVAILABLE:
        raise HTTPException(status_code=503, detail="Playwright not installed. Run: pip install playwright && playwright install chromium")

    browser = await get_browser()
    return {
        "status": "ok",
        "browser_connected": browser.is_connected(),
        "message": "Browser launched in visible mode for SSO authentication"
    }


@router.post("/navigate")
async def navigate(request: NavigateRequest):
    """Navigate to a URL."""
    page = await get_page(request.session_id)

    try:
        response = await page.goto(request.url, wait_until=request.wait_for, timeout=30000)

        return {
            "status": "ok",
            "url": page.url,
            "title": await page.title(),
            "response_status": response.status if response else None,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/click")
async def click_element(request: ClickRequest):
    """Click an element."""
    page = await get_page(request.session_id)

    try:
        await page.click(request.selector, timeout=10000)
        return {"status": "ok", "clicked": request.selector}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Click failed: {e}")


@router.post("/type")
async def type_text(request: TypeRequest):
    """Type text into an input field."""
    page = await get_page(request.session_id)

    try:
        if request.clear_first:
            await page.fill(request.selector, request.text, timeout=10000)
        else:
            await page.type(request.selector, request.text, timeout=10000)
        return {"status": "ok", "typed": len(request.text), "selector": request.selector}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Type failed: {e}")


@router.post("/wait")
async def wait_for_element(request: WaitRequest):
    """Wait for an element to appear."""
    page = await get_page(request.session_id)

    try:
        await page.wait_for_selector(request.selector, timeout=request.timeout)
        return {"status": "ok", "found": request.selector}
    except Exception as e:
        raise HTTPException(status_code=408, detail=f"Wait timeout: {e}")


@router.post("/extract")
async def extract_text(request: ExtractRequest):
    """Extract text or attribute from elements."""
    page = await get_page(request.session_id)

    try:
        elements = await page.query_selector_all(request.selector)
        results = []

        for el in elements:
            if request.attribute:
                value = await el.get_attribute(request.attribute)
            else:
                value = await el.inner_text()
            results.append(value)

        return {
            "status": "ok",
            "count": len(results),
            "values": results,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extract failed: {e}")


@router.post("/extract-table")
async def extract_table(request: ExtractTableRequest):
    """Extract data from an HTML table."""
    page = await get_page(request.session_id)

    try:
        # Get all rows
        rows = await page.query_selector_all(f"{request.table_selector} tr")

        if not rows:
            return {"status": "ok", "headers": [], "data": []}

        # Extract headers from the specified row
        header_row = rows[request.header_row]
        header_cells = await header_row.query_selector_all("th, td")
        headers = [await cell.inner_text() for cell in header_cells]
        headers = [h.strip() for h in headers]

        # Extract data from remaining rows
        data = []
        for i, row in enumerate(rows):
            if i <= request.header_row:
                continue

            cells = await row.query_selector_all("td")
            row_data = {}

            for j, cell in enumerate(cells):
                if j < len(headers):
                    row_data[headers[j]] = (await cell.inner_text()).strip()

            if row_data:
                data.append(row_data)

        return {
            "status": "ok",
            "headers": headers,
            "row_count": len(data),
            "data": data,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Table extract failed: {e}")


@router.post("/sso-login")
async def sso_login(request: SSOLoginRequest):
    """
    Start SSO login flow - opens browser for user to complete authentication.
    Returns when user completes login or timeout.
    """
    import re

    page = await get_page(request.session_id)

    try:
        # Navigate to login URL
        await page.goto(request.login_url, wait_until="load")

        logger.info(f"SSO login started - waiting for user to complete authentication at {request.login_url}")

        # Wait for URL to match success pattern
        success_pattern = re.compile(request.success_url_pattern)
        start_time = datetime.now()

        while (datetime.now() - start_time).total_seconds() < request.timeout:
            current_url = page.url
            if success_pattern.search(current_url):
                # Save session cookies
                await save_session(request.session_id)

                return {
                    "status": "authenticated",
                    "session_id": request.session_id,
                    "url": current_url,
                    "cookies_saved": True,
                }

            await asyncio.sleep(1)

        return {
            "status": "timeout",
            "message": f"SSO login not completed within {request.timeout} seconds",
            "current_url": page.url,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SSO login failed: {e}")


@router.get("/session/{session_id}")
async def get_session_info(session_id: str):
    """Get information about a session."""
    global _pages

    session_file = SESSION_DIR / f"{session_id}_cookies.json"

    info = SessionInfo(
        session_id=session_id,
        cookies_stored=session_file.exists(),
    )

    if session_id in _pages and not _pages[session_id].is_closed():
        page = _pages[session_id]
        info.url = page.url
        info.title = await page.title()

    return info


@router.post("/session/{session_id}/save")
async def save_session_endpoint(session_id: str):
    """Manually save session cookies."""
    await save_session(session_id)
    return {"status": "ok", "session_id": session_id, "saved": True}


@router.delete("/session/{session_id}")
async def close_session(session_id: str):
    """Close a browser session."""
    global _pages, _context

    if session_id in _pages:
        page = _pages[session_id]
        if not page.is_closed():
            await page.close()
        del _pages[session_id]

    # Delete stored cookies
    session_file = SESSION_DIR / f"{session_id}_cookies.json"
    if session_file.exists():
        session_file.unlink()

    return {"status": "ok", "session_id": session_id, "closed": True}


@router.post("/close")
async def close_browser():
    """Close the browser completely."""
    global _browser, _context, _pages

    for page in _pages.values():
        if not page.is_closed():
            await page.close()
    _pages.clear()

    if _context:
        await _context.close()
        _context = None

    if _browser and _browser.is_connected():
        await _browser.close()
        _browser = None

    return {"status": "ok", "message": "Browser closed"}


@router.get("/screenshot/{session_id}")
async def take_screenshot(session_id: str):
    """Take a screenshot of the current page."""
    page = await get_page(session_id)

    try:
        screenshot_path = SESSION_DIR / f"{session_id}_screenshot.png"
        await page.screenshot(path=str(screenshot_path), full_page=False)

        return {
            "status": "ok",
            "path": str(screenshot_path),
            "url": page.url,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Screenshot failed: {e}")
