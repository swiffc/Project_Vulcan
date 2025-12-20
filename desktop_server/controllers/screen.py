"""
Screen Controller - Screenshots and OCR via mss, pillow, pytesseract
~80 lines as per RULES.md
"""

from fastapi import APIRouter
from pydantic import BaseModel
import mss
import mss.tools
from PIL import Image
import pytesseract
import base64
import io
import logging

router = APIRouter(prefix="/screen", tags=["screen"])
logger = logging.getLogger(__name__)


class RegionRequest(BaseModel):
    x: int
    y: int
    width: int
    height: int

class FindImageRequest(BaseModel):
    template_base64: str  # Base64 encoded template image
    confidence: float = 0.9


def image_to_base64(img: Image.Image, format: str = "PNG") -> str:
    """Convert PIL Image to base64 string."""
    buffer = io.BytesIO()
    img.save(buffer, format=format)
    return base64.b64encode(buffer.getvalue()).decode()


def base64_to_image(b64: str) -> Image.Image:
    """Convert base64 string to PIL Image."""
    data = base64.b64decode(b64)
    return Image.open(io.BytesIO(data))


@router.post("/screenshot")
async def screenshot():
    """Take a full screen screenshot."""
    logger.info("Taking full screenshot")
    with mss.mss() as sct:
        # Capture all monitors
        monitor = sct.monitors[0]  # All monitors combined
        sct_img = sct.grab(monitor)
        img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")

    return {
        "status": "ok",
        "image": image_to_base64(img),
        "width": img.width,
        "height": img.height
    }


@router.post("/region")
async def screenshot_region(req: RegionRequest):
    """Take a screenshot of a specific region."""
    logger.info(f"Taking region screenshot: ({req.x}, {req.y}, {req.width}, {req.height})")
    with mss.mss() as sct:
        monitor = {"left": req.x, "top": req.y, "width": req.width, "height": req.height}
        sct_img = sct.grab(monitor)
        img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")

    return {
        "status": "ok",
        "image": image_to_base64(img),
        "width": img.width,
        "height": img.height
    }


@router.post("/ocr")
async def ocr_region(req: RegionRequest):
    """Extract text from a screen region using OCR."""
    logger.info(f"OCR on region: ({req.x}, {req.y}, {req.width}, {req.height})")
    with mss.mss() as sct:
        monitor = {"left": req.x, "top": req.y, "width": req.width, "height": req.height}
        sct_img = sct.grab(monitor)
        img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")

    text = pytesseract.image_to_string(img)
    return {
        "status": "ok",
        "text": text.strip(),
        "region": {"x": req.x, "y": req.y, "width": req.width, "height": req.height}
    }


@router.get("/size")
async def get_screen_size():
    """Get screen dimensions."""
    with mss.mss() as sct:
        monitor = sct.monitors[1]  # Primary monitor
        return {
            "width": monitor["width"],
            "height": monitor["height"],
            "monitors": len(sct.monitors) - 1  # Exclude combined monitor
        }


@router.post("/find")
async def find_image(req: FindImageRequest):
    """Find a template image on screen (returns center coordinates if found)."""
    import pyautogui

    logger.info("Searching for image on screen")
    template = base64_to_image(req.template_base64)

    # Save template temporarily for pyautogui
    template_path = "temp_template.png"
    template.save(template_path)

    try:
        location = pyautogui.locateOnScreen(template_path, confidence=req.confidence)
        if location:
            center = pyautogui.center(location)
            return {
                "status": "ok",
                "found": True,
                "x": center.x,
                "y": center.y,
                "region": {"left": location.left, "top": location.top,
                          "width": location.width, "height": location.height}
            }
        return {"status": "ok", "found": False}
    finally:
        import os
        if os.path.exists(template_path):
            os.remove(template_path)
