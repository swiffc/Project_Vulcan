"""
Window Controller - Window management via pywin32
~60 lines as per RULES.md
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import win32gui
import win32con
import win32process
import logging

router = APIRouter(prefix="/window", tags=["window"])
logger = logging.getLogger(__name__)


class FocusRequest(BaseModel):
    title: str  # Window title (partial match)

class ResizeRequest(BaseModel):
    title: str
    x: int
    y: int
    width: int
    height: int


def find_window_by_title(title: str) -> int | None:
    """Find window handle by partial title match."""
    result = None

    def callback(hwnd, _):
        nonlocal result
        if win32gui.IsWindowVisible(hwnd):
            window_title = win32gui.GetWindowText(hwnd)
            if title.lower() in window_title.lower():
                result = hwnd
                return False  # Stop enumeration
        return True

    win32gui.EnumWindows(callback, None)
    return result


@router.get("/list")
async def list_windows():
    """List all visible windows."""
    windows = []

    def callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title:  # Skip windows without titles
                rect = win32gui.GetWindowRect(hwnd)
                windows.append({
                    "handle": hwnd,
                    "title": title,
                    "rect": {
                        "left": rect[0],
                        "top": rect[1],
                        "right": rect[2],
                        "bottom": rect[3],
                        "width": rect[2] - rect[0],
                        "height": rect[3] - rect[1]
                    }
                })
        return True

    win32gui.EnumWindows(callback, None)
    logger.info(f"Found {len(windows)} windows")
    return {"status": "ok", "windows": windows}


@router.post("/focus")
async def focus_window(req: FocusRequest):
    """Bring a window to the foreground."""
    logger.info(f"Focusing window: {req.title}")
    hwnd = find_window_by_title(req.title)

    if not hwnd:
        raise HTTPException(status_code=404, detail=f"Window not found: {req.title}")

    # Restore if minimized
    if win32gui.IsIconic(hwnd):
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)

    # Bring to foreground
    win32gui.SetForegroundWindow(hwnd)

    return {"status": "ok", "title": win32gui.GetWindowText(hwnd), "handle": hwnd}


@router.post("/minimize")
async def minimize_window(req: FocusRequest):
    """Minimize a window."""
    logger.info(f"Minimizing window: {req.title}")
    hwnd = find_window_by_title(req.title)

    if not hwnd:
        raise HTTPException(status_code=404, detail=f"Window not found: {req.title}")

    win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
    return {"status": "ok", "title": win32gui.GetWindowText(hwnd)}


@router.post("/maximize")
async def maximize_window(req: FocusRequest):
    """Maximize a window."""
    logger.info(f"Maximizing window: {req.title}")
    hwnd = find_window_by_title(req.title)

    if not hwnd:
        raise HTTPException(status_code=404, detail=f"Window not found: {req.title}")

    win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
    return {"status": "ok", "title": win32gui.GetWindowText(hwnd)}


@router.post("/resize")
async def resize_window(req: ResizeRequest):
    """Move and resize a window."""
    logger.info(f"Resizing window: {req.title}")
    hwnd = find_window_by_title(req.title)

    if not hwnd:
        raise HTTPException(status_code=404, detail=f"Window not found: {req.title}")

    win32gui.MoveWindow(hwnd, req.x, req.y, req.width, req.height, True)
    return {"status": "ok", "title": win32gui.GetWindowText(hwnd)}


@router.post("/close")
async def close_window(req: FocusRequest):
    """Close a window."""
    logger.info(f"Closing window: {req.title}")
    hwnd = find_window_by_title(req.title)

    if not hwnd:
        raise HTTPException(status_code=404, detail=f"Window not found: {req.title}")

    win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
    return {"status": "ok", "title": req.title}
