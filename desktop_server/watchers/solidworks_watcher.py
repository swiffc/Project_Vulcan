"""
SolidWorks Process Watcher
==========================
Monitors for SolidWorks process startup and document changes.
Auto-opens chatbot URL when SolidWorks is detected.

Phase 24.1 Implementation
"""

import os
import time
import asyncio
import logging
import webbrowser
from typing import Optional, Callable, Dict, Any
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger("vulcan.watcher.solidworks")


class DocumentType(Enum):
    """SolidWorks document types."""
    PART = "part"
    ASSEMBLY = "assembly"
    DRAWING = "drawing"
    UNKNOWN = "unknown"


@dataclass
class SolidWorksState:
    """Current state of SolidWorks application."""
    is_running: bool = False
    process_id: Optional[int] = None
    document_path: Optional[str] = None
    document_type: DocumentType = DocumentType.UNKNOWN
    document_name: Optional[str] = None
    last_change: float = field(default_factory=time.time)


class SolidWorksWatcher:
    """
    Watches for SolidWorks process and document changes.
    Triggers callbacks on state changes for real-time UI updates.
    """

    PROCESS_NAMES = ["SLDWORKS.exe", "sldworks.exe"]
    CHATBOT_URL = os.getenv("CHATBOT_URL", "http://localhost:3000/cad")
    POLL_INTERVAL = 2.0  # seconds

    def __init__(self):
        self._state = SolidWorksState()
        self._running = False
        self._callbacks: list[Callable[[SolidWorksState], None]] = []
        self._ws_clients: list[Any] = []

    @property
    def state(self) -> SolidWorksState:
        """Current SolidWorks state."""
        return self._state

    def register_callback(self, callback: Callable[[SolidWorksState], None]):
        """Register a callback for state changes."""
        self._callbacks.append(callback)

    def register_websocket(self, ws_client: Any):
        """Register a WebSocket client for real-time updates."""
        self._ws_clients.append(ws_client)

    def unregister_websocket(self, ws_client: Any):
        """Remove a WebSocket client."""
        if ws_client in self._ws_clients:
            self._ws_clients.remove(ws_client)

    def _check_process_running(self) -> Optional[int]:
        """Check if SolidWorks process is running. Returns PID if found."""
        try:
            import psutil
        except ImportError:
            logger.warning("psutil not installed - process monitoring disabled")
            return None

        for proc in psutil.process_iter(["name", "pid"]):
            try:
                if proc.info["name"] in self.PROCESS_NAMES:
                    return proc.info["pid"]
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return None

    def _get_active_document(self) -> Dict[str, Any]:
        """Get info about the currently active SolidWorks document."""
        try:
            import win32com.client
        except ImportError:
            logger.warning("pywin32 not installed - document detection disabled")
            return {}

        try:
            sw_app = win32com.client.GetActiveObject("SldWorks.Application")
            doc = sw_app.ActiveDoc
            if not doc:
                return {}

            doc_type = doc.GetType()
            type_map = {1: DocumentType.PART, 2: DocumentType.ASSEMBLY, 3: DocumentType.DRAWING}

            return {
                "path": doc.GetPathName(),
                "name": doc.GetTitle(),
                "type": type_map.get(doc_type, DocumentType.UNKNOWN),
            }
        except Exception as e:
            logger.debug(f"Could not get active document: {e}")
            return {}

    def _notify_state_change(self, old_state: SolidWorksState):
        """Notify all registered callbacks of state change."""
        for callback in self._callbacks:
            try:
                callback(self._state)
            except Exception as e:
                logger.error(f"Callback error: {e}")

        # Notify WebSocket clients
        self._broadcast_ws_update()

    def _broadcast_ws_update(self):
        """Send state update to all WebSocket clients."""
        if not self._ws_clients:
            return

        message = {
            "type": "solidworks_state",
            "data": {
                "is_running": self._state.is_running,
                "document_path": self._state.document_path,
                "document_name": self._state.document_name,
                "document_type": self._state.document_type.value,
                "timestamp": self._state.last_change,
            }
        }

        for ws in self._ws_clients[:]:
            try:
                asyncio.create_task(ws.send_json(message))
            except Exception as e:
                logger.debug(f"WebSocket send failed: {e}")
                self._ws_clients.remove(ws)

    def _on_solidworks_started(self):
        """Called when SolidWorks process is first detected."""
        logger.info("SolidWorks detected - opening chatbot")
        try:
            webbrowser.open(self.CHATBOT_URL)
        except Exception as e:
            logger.error(f"Failed to open chatbot URL: {e}")

    def _poll_once(self) -> bool:
        """Poll for SolidWorks state. Returns True if state changed."""
        old_state = SolidWorksState(
            is_running=self._state.is_running,
            process_id=self._state.process_id,
            document_path=self._state.document_path,
            document_type=self._state.document_type,
            document_name=self._state.document_name,
            last_change=self._state.last_change,
        )

        # Check process
        pid = self._check_process_running()
        was_running = self._state.is_running
        self._state.is_running = pid is not None
        self._state.process_id = pid

        # Handle startup
        if self._state.is_running and not was_running:
            self._on_solidworks_started()

        # Get document info if running
        if self._state.is_running:
            doc_info = self._get_active_document()
            self._state.document_path = doc_info.get("path")
            self._state.document_name = doc_info.get("name")
            self._state.document_type = doc_info.get("type", DocumentType.UNKNOWN)
        else:
            self._state.document_path = None
            self._state.document_name = None
            self._state.document_type = DocumentType.UNKNOWN

        # Check for changes
        changed = (
            old_state.is_running != self._state.is_running
            or old_state.document_path != self._state.document_path
            or old_state.document_type != self._state.document_type
        )

        if changed:
            self._state.last_change = time.time()
            self._notify_state_change(old_state)

        return changed

    async def start(self):
        """Start the watcher loop."""
        if self._running:
            return

        self._running = True
        logger.info("SolidWorks watcher started")

        while self._running:
            try:
                self._poll_once()
            except Exception as e:
                logger.error(f"Watcher poll error: {e}")

            await asyncio.sleep(self.POLL_INTERVAL)

    def stop(self):
        """Stop the watcher loop."""
        self._running = False
        logger.info("SolidWorks watcher stopped")


# Singleton instance
_watcher: Optional[SolidWorksWatcher] = None


def get_watcher() -> SolidWorksWatcher:
    """Get the singleton watcher instance."""
    global _watcher
    if _watcher is None:
        _watcher = SolidWorksWatcher()
    return _watcher
