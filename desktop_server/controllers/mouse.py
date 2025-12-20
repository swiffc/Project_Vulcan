"""
Mouse Controller - Physical mouse control via pyautogui
~50 lines as per RULES.md
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import pyautogui
import logging

router = APIRouter(prefix="/mouse", tags=["mouse"])
logger = logging.getLogger(__name__)

# Safety: Disable pyautogui failsafe only if needed
# pyautogui.FAILSAFE = True  # Move mouse to corner to abort

class MoveRequest(BaseModel):
    x: int
    y: int
    duration: float = 0.2

class ClickRequest(BaseModel):
    x: int | None = None
    y: int | None = None
    button: str = "left"  # left, right, middle
    clicks: int = 1

class DragRequest(BaseModel):
    x1: int
    y1: int
    x2: int
    y2: int
    duration: float = 0.5
    button: str = "left"

class ScrollRequest(BaseModel):
    amount: int  # positive = up, negative = down
    x: int | None = None
    y: int | None = None


@router.post("/move")
async def move(req: MoveRequest):
    """Move mouse cursor to position."""
    logger.info(f"Moving mouse to ({req.x}, {req.y})")
    pyautogui.moveTo(req.x, req.y, duration=req.duration)
    return {"status": "ok", "position": {"x": req.x, "y": req.y}}


@router.post("/click")
async def click(req: ClickRequest):
    """Click at position (or current position if x,y not specified)."""
    logger.info(f"Clicking {req.button} at ({req.x}, {req.y})")
    if req.x is not None and req.y is not None:
        pyautogui.click(req.x, req.y, button=req.button, clicks=req.clicks)
    else:
        pyautogui.click(button=req.button, clicks=req.clicks)
    return {"status": "ok", "button": req.button, "clicks": req.clicks}


@router.post("/drag")
async def drag(req: DragRequest):
    """Drag from one position to another."""
    logger.info(f"Dragging from ({req.x1}, {req.y1}) to ({req.x2}, {req.y2})")
    pyautogui.moveTo(req.x1, req.y1)
    pyautogui.drag(req.x2 - req.x1, req.y2 - req.y1, duration=req.duration, button=req.button)
    return {"status": "ok", "from": {"x": req.x1, "y": req.y1}, "to": {"x": req.x2, "y": req.y2}}


@router.post("/scroll")
async def scroll(req: ScrollRequest):
    """Scroll mouse wheel."""
    logger.info(f"Scrolling {req.amount} at ({req.x}, {req.y})")
    if req.x is not None and req.y is not None:
        pyautogui.moveTo(req.x, req.y)
    pyautogui.scroll(req.amount)
    return {"status": "ok", "amount": req.amount}


@router.get("/position")
async def get_position():
    """Get current mouse position."""
    pos = pyautogui.position()
    return {"x": pos.x, "y": pos.y}
