import win32com.client
import logging
from typing import Optional, Dict, Any
import pythoncom

logger = logging.getLogger("com.events")

# Global event listener reference to prevent garbage collection
_event_listener = None


class SolidWorksAppEvents:
    """Events for the main SolidWorks Application."""

    def __init__(self):
        self._doc_events = None

    def OnActiveModelDocChangeNotify(self) -> int:
        """Fired when the active document changes."""
        logger.info("Active document changed - re-hooking document events")
        # In a real implementation, we would re-attach document-level listeners here
        return 0

    def OnFileOpenNotify(self, filename: str) -> int:
        logger.info(f"File opened: {filename}")
        return 0

    def OnUserSelectionPreNotify(self, sel_type, item) -> int:
        # Note: This often fires *before* the item is fully selected in the tree
        # logger.info(f"Pre-selection: Type={sel_type}")
        return 0


class PartDocEvents:
    """Events for a Part Document."""

    def __init__(self, callback):
        self.callback = callback

    def OnNewSelectionNotify(self) -> int:
        """Fired when a selection is made in the part."""
        logger.info("New selection detected in Part")
        if self.callback:
            self.callback()
        return 0


class AssemblyDocEvents:
    """Events for an Assembly Document."""

    def __init__(self, callback):
        self.callback = callback

    def OnNewSelectionNotify(self) -> int:
        """Fired when a selection is made in the assembly."""
        logger.info("New selection detected in Assembly")
        if self.callback:
            self.callback()
        return 0


class EventManager:
    """Manages COM event listeners."""

    def __init__(self, sw_app):
        self.sw_app = sw_app
        self.app_events = None
        self.doc_events = None
        self.current_callback = None

    def start_listening(self, selection_callback):
        """Start listening for events."""
        self.current_callback = selection_callback

        # Hook Application Events
        try:
            self.app_events = win32com.client.WithEvents(
                self.sw_app, SolidWorksAppEvents
            )
            logger.info("Hooked SolidWorks Application Events")
        except Exception as e:
            logger.error(f"Failed to hook App events: {e}")

        # Hook Active Document Events (Initial attempt)
        self._hook_active_doc()

    def _hook_active_doc(self):
        """Hook events for the currently active document."""
        try:
            model = self.sw_app.ActiveDoc
            if not model:
                return

            # Determine document type (1=Part, 2=Assembly)
            doc_type = model.GetType()

            if doc_type == 1:  # Part
                self.doc_events = win32com.client.WithEvents(
                    model, lambda: PartDocEvents(self.current_callback)
                )
                logger.info("Hooked Part Events")
            elif doc_type == 2:  # Assembly
                self.doc_events = win32com.client.WithEvents(
                    model, lambda: AssemblyDocEvents(self.current_callback)
                )
                logger.info("Hooked Assembly Events")

        except Exception as e:
            logger.error(f"Failed to hook Doc events: {e}")

    def stop_listening(self):
        """Stop all listeners."""
        if self.app_events:
            self.app_events.close()
        if self.doc_events:
            self.doc_events.close()
        self.app_events = None
        self.doc_events = None
