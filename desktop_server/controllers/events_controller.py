from fastapi import APIRouter, HTTPException
import win32com.client
import pythoncom
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel

try:
    from com.events import EventManager
except ImportError:
    # Handle case where com package isn't fully set up in path
    import sys
    from pathlib import Path

    sys.path.append(str(Path(__file__).parent.parent))
    from com.events import EventManager

router = APIRouter(prefix="/api/solidworks/events", tags=["events"])
logger = logging.getLogger(__name__)

# Global Event Manager State
_event_manager: Optional[EventManager] = None
_latest_selection: Dict[str, Any] = {}


def _get_sw_app():
    """Get active SolidWorks application instance."""
    try:
        pythoncom.CoInitialize()
        return win32com.client.GetActiveObject("SldWorks.Application")
    except Exception as e:
        logger.error(f"Failed to get SolidWorks app: {e}")
        return None


def on_selection_callback():
    """Callback when a selection event occurs."""
    global _latest_selection
    logger.info("Selection callback triggered")

    app = _get_sw_app()
    if not app:
        return

    try:
        model = app.ActiveDoc
        if not model:
            return

        sel_mgr = model.SelectionManager
        count = sel_mgr.GetSelectedObjectCount2(-1)

        selection_data = {
            "timestamp": datetime.now().isoformat(),
            "event_type": "selection",
            "count": count,
            "features": [],
        }

        if count > 0:
            # Get up to 5 items
            for i in range(1, min(count + 1, 6)):
                try:
                    # GetSelectedObject6(Index, Mark)
                    # Index is 1-based
                    obj = sel_mgr.GetSelectedObject6(i, -1)

                    item_info = {"index": i, "type": "Unknown"}

                    # Try to identify object type
                    # 79 = swSelFACES, 22 = swSelEDGES, etc.
                    # Ideally we check the object interface

                    # If it's a Feature (IFeature)
                    if hasattr(obj, "Name"):
                        item_info["name"] = obj.Name
                        if hasattr(obj, "GetTypeName2"):
                            item_info["type"] = obj.GetTypeName2()
                        elif hasattr(obj, "GetTypeName"):
                            item_info["type"] = obj.GetTypeName()

                    # If we can get a feature from the selection (e.g. face -> feature)
                    # This requires more complex casting often

                    selection_data["features"].append(item_info)

                except Exception as ex:
                    logger.warning(f"Failed to parse selection item {i}: {ex}")

        _latest_selection = selection_data
        logger.info(f"Updated selection: {len(selection_data['features'])} items")

    except Exception as e:
        logger.error(f"Error fetching selection details: {e}")


@router.post("/subscribe")
async def subscribe_events():
    """Start listening for SolidWorks events."""
    global _event_manager

    if _event_manager:
        return {"status": "already_subscribed"}

    app = _get_sw_app()
    if not app:
        raise HTTPException(status_code=503, detail="SolidWorks not active")

    try:
        _event_manager = EventManager(app)
        _event_manager.start_listening(on_selection_callback)
        logger.info("Subscribed to SolidWorks events")
        return {"status": "subscribed"}
    except Exception as e:
        logger.error(f"Failed to subscribe: {e}")
        _event_manager = None
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/unsubscribe")
async def unsubscribe_events():
    """Stop listening for events."""
    global _event_manager
    if _event_manager:
        _event_manager.stop_listening()
        _event_manager = None
        logger.info("Unsubscribed from SolidWorks events")
    return {"status": "unsubscribed"}


@router.get("/latest")
async def get_latest_event():
    """Get the most recent detected event."""
    return _latest_selection or {"status": "no_events_yet"}
