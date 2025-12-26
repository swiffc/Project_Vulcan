"""
SolidWorks Event Listener for ACHE Model Detection
Phase 24.1.1 - Event listener for model open

Listens for SolidWorks model open/close/activate events
and triggers ACHE detection when relevant.
"""

import logging
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, Dict, List, Optional, Any
from enum import Enum

logger = logging.getLogger("vulcan.ache.event_listener")


class ModelEventType(str, Enum):
    """Types of SolidWorks model events."""
    OPENED = "opened"
    CLOSED = "closed"
    ACTIVATED = "activated"
    SAVED = "saved"
    REBUILT = "rebuilt"


@dataclass
class ModelOpenEvent:
    """Event data for model open."""
    filepath: str
    filename: str
    model_type: str  # "part", "assembly", "drawing"
    timestamp: datetime = field(default_factory=datetime.now)
    is_ache: bool = False
    custom_properties: Dict[str, Any] = field(default_factory=dict)


class ACHEEventListener:
    """
    Listens for SolidWorks model events and triggers callbacks.

    Implements Phase 24.1.1: SolidWorks event listener for model open

    Usage:
        listener = ACHEEventListener()
        listener.on_model_open(callback_function)
        listener.start()
    """

    def __init__(self, poll_interval: float = 1.0):
        """
        Initialize the event listener.

        Args:
            poll_interval: Seconds between polls (default 1.0)
        """
        self._poll_interval = poll_interval
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._callbacks: Dict[ModelEventType, List[Callable]] = {
            event_type: [] for event_type in ModelEventType
        }
        self._last_model_path: Optional[str] = None
        self._sw_app = None

    def on_model_open(self, callback: Callable[[ModelOpenEvent], None]) -> None:
        """Register callback for model open events."""
        self._callbacks[ModelEventType.OPENED].append(callback)
        logger.debug(f"Registered model open callback: {callback.__name__}")

    def on_model_close(self, callback: Callable[[str], None]) -> None:
        """Register callback for model close events."""
        self._callbacks[ModelEventType.CLOSED].append(callback)

    def on_model_activate(self, callback: Callable[[ModelOpenEvent], None]) -> None:
        """Register callback for model activation (switching between docs)."""
        self._callbacks[ModelEventType.ACTIVATED].append(callback)

    def start(self) -> bool:
        """
        Start the event listener.

        Returns:
            True if started successfully, False otherwise
        """
        if self._running:
            logger.warning("Event listener already running")
            return True

        try:
            # Connect to SolidWorks
            if not self._connect_solidworks():
                logger.error("Cannot start listener - SolidWorks not connected")
                return False

            self._running = True
            self._thread = threading.Thread(target=self._poll_loop, daemon=True)
            self._thread.start()
            logger.info("ACHE Event Listener started")
            return True

        except Exception as e:
            logger.error(f"Failed to start event listener: {e}")
            return False

    def stop(self) -> None:
        """Stop the event listener."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)
        logger.info("ACHE Event Listener stopped")

    def _connect_solidworks(self) -> bool:
        """Connect to running SolidWorks instance."""
        try:
            import win32com.client
            self._sw_app = win32com.client.GetActiveObject("SldWorks.Application")
            logger.info("Connected to SolidWorks")
            return True
        except Exception as e:
            logger.warning(f"SolidWorks not running or not accessible: {e}")
            return False

    def _poll_loop(self) -> None:
        """Main polling loop to detect model changes."""
        while self._running:
            try:
                self._check_active_model()
            except Exception as e:
                logger.error(f"Error in poll loop: {e}")
            time.sleep(self._poll_interval)

    def _check_active_model(self) -> None:
        """Check if active model has changed."""
        if not self._sw_app:
            return

        try:
            active_doc = self._sw_app.ActiveDoc
            if active_doc is None:
                if self._last_model_path:
                    # Model was closed
                    self._trigger_close(self._last_model_path)
                    self._last_model_path = None
                return

            current_path = active_doc.GetPathName()

            if current_path != self._last_model_path:
                if self._last_model_path:
                    # Different model activated
                    event = self._create_model_event(active_doc, current_path)
                    self._trigger_event(ModelEventType.ACTIVATED, event)
                else:
                    # New model opened
                    event = self._create_model_event(active_doc, current_path)
                    self._trigger_event(ModelEventType.OPENED, event)

                self._last_model_path = current_path

        except Exception as e:
            logger.error(f"Error checking active model: {e}")

    def _create_model_event(self, doc, filepath: str) -> ModelOpenEvent:
        """Create a ModelOpenEvent from SolidWorks document."""
        import os

        # Determine model type
        doc_type = doc.GetType()
        type_map = {1: "part", 2: "assembly", 3: "drawing"}
        model_type = type_map.get(doc_type, "unknown")

        # Get custom properties for ACHE detection
        custom_props = self._get_custom_properties(doc)

        return ModelOpenEvent(
            filepath=filepath,
            filename=os.path.basename(filepath),
            model_type=model_type,
            custom_properties=custom_props,
        )

    def _get_custom_properties(self, doc) -> Dict[str, Any]:
        """Extract custom properties from document."""
        props = {}
        try:
            ext = doc.Extension
            prop_mgr = ext.CustomPropertyManager("")

            # Get all property names
            names = prop_mgr.GetNames()
            if names:
                for name in names:
                    try:
                        val_out = ""
                        resolved_out = ""
                        was_resolved = False
                        link_to_property = False
                        result = prop_mgr.Get6(
                            name, False, val_out, resolved_out,
                            was_resolved, link_to_property
                        )
                        props[name] = resolved_out if resolved_out else val_out
                    except:
                        pass
        except Exception as e:
            logger.debug(f"Could not get custom properties: {e}")

        return props

    def _trigger_event(self, event_type: ModelEventType, data: Any) -> None:
        """Trigger all callbacks for an event type."""
        for callback in self._callbacks[event_type]:
            try:
                callback(data)
            except Exception as e:
                logger.error(f"Callback error: {e}")

    def _trigger_close(self, filepath: str) -> None:
        """Trigger model close callbacks."""
        for callback in self._callbacks[ModelEventType.CLOSED]:
            try:
                callback(filepath)
            except Exception as e:
                logger.error(f"Close callback error: {e}")

    @property
    def is_running(self) -> bool:
        """Check if listener is running."""
        return self._running

    def get_status(self) -> Dict[str, Any]:
        """Get listener status."""
        return {
            "running": self._running,
            "solidworks_connected": self._sw_app is not None,
            "last_model": self._last_model_path,
            "poll_interval": self._poll_interval,
            "callbacks_registered": {
                event_type.value: len(callbacks)
                for event_type, callbacks in self._callbacks.items()
            }
        }
