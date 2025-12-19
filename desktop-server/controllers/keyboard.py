"""
Keyboard Controller - Physical keyboard control via pyautogui
~50 lines as per RULES.md
"""

from fastapi import APIRouter
from pydantic import BaseModel
import pyautogui
import logging

router = APIRouter(prefix="/keyboard", tags=["keyboard"])
logger = logging.getLogger(__name__)


class TypeRequest(BaseModel):
    text: str
    interval: float = 0.02  # seconds between keystrokes

class PressRequest(BaseModel):
    key: str  # e.g., "enter", "tab", "escape", "a", "1"

class HotkeyRequest(BaseModel):
    keys: list[str]  # e.g., ["ctrl", "c"] or ["alt", "f4"]

class HoldRequest(BaseModel):
    key: str
    duration: float = 0.5


@router.post("/type")
async def type_text(req: TypeRequest):
    """Type a string of text."""
    logger.info(f"Typing text: {req.text[:50]}...")
    pyautogui.typewrite(req.text, interval=req.interval)
    return {"status": "ok", "length": len(req.text)}


@router.post("/write")
async def write_text(req: TypeRequest):
    """Write text (supports unicode characters)."""
    logger.info(f"Writing text: {req.text[:50]}...")
    pyautogui.write(req.text)
    return {"status": "ok", "length": len(req.text)}


@router.post("/press")
async def press_key(req: PressRequest):
    """Press a single key."""
    logger.info(f"Pressing key: {req.key}")
    pyautogui.press(req.key)
    return {"status": "ok", "key": req.key}


@router.post("/hotkey")
async def hotkey(req: HotkeyRequest):
    """Press a key combination (e.g., Ctrl+C)."""
    logger.info(f"Pressing hotkey: {'+'.join(req.keys)}")
    pyautogui.hotkey(*req.keys)
    return {"status": "ok", "keys": req.keys}


@router.post("/hold")
async def hold_key(req: HoldRequest):
    """Hold a key for a duration."""
    logger.info(f"Holding key {req.key} for {req.duration}s")
    with pyautogui.hold(req.key):
        pyautogui.sleep(req.duration)
    return {"status": "ok", "key": req.key, "duration": req.duration}


@router.post("/keydown")
async def key_down(req: PressRequest):
    """Press and hold a key down."""
    logger.info(f"Key down: {req.key}")
    pyautogui.keyDown(req.key)
    return {"status": "ok", "key": req.key, "state": "down"}


@router.post("/keyup")
async def key_up(req: PressRequest):
    """Release a held key."""
    logger.info(f"Key up: {req.key}")
    pyautogui.keyUp(req.key)
    return {"status": "ok", "key": req.key, "state": "up"}
