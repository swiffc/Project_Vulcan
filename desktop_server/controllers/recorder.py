"""
Visual Replay Recorder
Captures screen recordings using mss and cv2 (OpenCV).
Designed to be lightweight and triggerable via API/MCP.
"""

import threading
import time
import os
import logging
from datetime import datetime
from pathlib import Path
import mss
import numpy as np
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

# lazy import cv2 to avoid startup cost if not recording
try:
    import cv2

    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

logger = logging.getLogger(__name__)


class ScreenRecorder:
    def __init__(self, output_dir="storage/recordings"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.is_recording = False
        self.thread = None
        self.stop_event = threading.Event()
        self.current_file = None

    def start(self, duration: int = 0, fps: int = 10):
        """Start recording.
        If duration > 0, stops automatically after seconds.
        If duration == 0, runs until stop() is called.
        """
        if not CV2_AVAILABLE:
            logger.error("OpenCV (cv2) not installed. Cannot record.")
            return "Error: OpenCV not installed"

        if self.is_recording:
            return "Already recording"

        self.is_recording = True
        self.stop_event.clear()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"replay_{timestamp}.avi"
        self.current_file = str(self.output_dir / filename)

        self.thread = threading.Thread(
            target=self._record_loop, args=(self.current_file, fps, duration)
        )
        self.thread.start()
        logger.info(f"Started recording to {self.current_file}")
        return f"Recording started: {filename}"

    def stop(self):
        """Stop current recording."""
        if not self.is_recording:
            return "Not recording"

        self.stop_event.set()
        if self.thread:
            self.thread.join()

        self.is_recording = False
        last_file = self.current_file
        self.current_file = None
        logger.info("Recording stopped")
        return f"Recording saved to {last_file}"

    def _record_loop(self, filename, fps, duration):
        with mss.mss() as sct:
            # Get primary monitor
            monitor = sct.monitors[1]
            width = monitor["width"]
            height = monitor["height"]

            # Define codec and create VideoWriter object
            fourcc = cv2.VideoWriter_fourcc(*"XVID")
            out = cv2.VideoWriter(filename, fourcc, fps, (width, height))

            start_time = time.time()
            frame_interval = 1.0 / fps

            while not self.stop_event.is_set():
                loop_start = time.time()

                # Check duration
                if duration > 0 and (loop_start - start_time) > duration:
                    break

                # Capture screen
                img = np.array(sct.grab(monitor))
                # Convert RGBA to RGB (OpenCV uses BGR)
                frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

                # Write frame
                out.write(frame)

                # Maintain FPS
                elapsed = time.time() - loop_start
                sleep_time = max(0, frame_interval - elapsed)
                time.sleep(sleep_time)

            out.release()


router = APIRouter(prefix="/recorder", tags=["recorder"])


class StartRecordingRequest(BaseModel):
    duration: Optional[int] = 0
    fps: Optional[int] = 10


@router.post("/start")
async def start_recording(req: StartRecordingRequest):
    """Start screen recording."""
    result = recorder.start(duration=req.duration, fps=req.fps)
    if "Error" in result:
        raise HTTPException(status_code=500, detail=result)
    return {"status": "ok", "message": result}


@router.post("/stop")
async def stop_recording():
    """Stop screen recording."""
    result = recorder.stop()
    if "Not recording" in result:
        return {"status": "warning", "message": result}
    return {"status": "ok", "message": result}


@router.get("/status")
async def recording_status():
    """Get current recording status."""
    return {
        "is_recording": recorder.is_recording,
        "current_file": recorder.current_file,
    }


# Global instance
recorder = ScreenRecorder()
