"""
SolidWorks Display States & Appearance API
==========================================
Display state and appearance management including:
- Display state creation and switching
- Component visibility states
- Appearance/color application
- Transparency settings
"""

import logging
from typing import Optional, Dict, Any, List
from enum import IntEnum
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

try:
    import win32com.client
    import pythoncom
    COM_AVAILABLE = True
except ImportError:
    COM_AVAILABLE = False


class DisplayMode(IntEnum):
    """Display modes."""
    WIREFRAME = 1
    HIDDEN_LINES_VISIBLE = 2
    HIDDEN_LINES_REMOVED = 3
    SHADED = 4
    SHADED_WITH_EDGES = 5


# Pydantic models
class CreateDisplayStateRequest(BaseModel):
    name: str
    copy_from: Optional[str] = None  # Copy settings from existing state


class SetColorRequest(BaseModel):
    color_rgb: List[int]  # [R, G, B] 0-255
    entity_type: str = "body"  # body, face, feature, component
    entity_name: Optional[str] = None


class SetTransparencyRequest(BaseModel):
    transparency: float  # 0.0 (opaque) to 1.0 (fully transparent)
    entity_name: Optional[str] = None


class ComponentVisibilityRequest(BaseModel):
    component_name: str
    visible: bool


class DisplayModeRequest(BaseModel):
    mode: str  # wireframe, hidden_visible, hidden_removed, shaded, shaded_edges


router = APIRouter(prefix="/solidworks-display", tags=["solidworks-display"])


def get_solidworks():
    """Get active SolidWorks application."""
    if not COM_AVAILABLE:
        raise HTTPException(status_code=501, detail="COM not available")
    pythoncom.CoInitialize()
    try:
        return win32com.client.GetActiveObject("SldWorks.Application")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SolidWorks not running: {e}")


# =============================================================================
# Display States
# =============================================================================

@router.post("/state/create")
async def create_display_state(request: CreateDisplayStateRequest):
    """
    Create a new display state.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        cfg_mgr = doc.ConfigurationManager
        if not cfg_mgr:
            raise HTTPException(status_code=501, detail="Configuration manager not available")

        # Create display state
        result = cfg_mgr.AddDisplayState(request.name)

        return {
            "success": result,
            "name": request.name,
            "message": f"Display state '{request.name}' created"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create display state failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.get("/states")
async def list_display_states():
    """
    List all display states in the document.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        cfg_mgr = doc.ConfigurationManager
        if not cfg_mgr:
            return {"count": 0, "states": []}

        states = cfg_mgr.GetDisplayStates()
        active = cfg_mgr.GetActiveDisplayState() if hasattr(cfg_mgr, 'GetActiveDisplayState') else None

        state_list = []
        if states:
            for state in states:
                state_list.append({
                    "name": state,
                    "active": state == active
                })

        return {
            "count": len(state_list),
            "active_state": active,
            "states": state_list
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"List display states failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/state/{name}/activate")
async def activate_display_state(name: str):
    """
    Activate a display state.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        cfg_mgr = doc.ConfigurationManager
        result = cfg_mgr.SetActiveDisplayState(name) if hasattr(cfg_mgr, 'SetActiveDisplayState') else False

        return {
            "success": result,
            "activated": name
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Activate display state failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.delete("/state/{name}")
async def delete_display_state(name: str):
    """
    Delete a display state.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        cfg_mgr = doc.ConfigurationManager
        result = cfg_mgr.DeleteDisplayState(name) if hasattr(cfg_mgr, 'DeleteDisplayState') else False

        return {
            "success": result,
            "deleted": name
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete display state failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


# =============================================================================
# Color & Appearance
# =============================================================================

@router.post("/color/set")
async def set_color(request: SetColorRequest):
    """
    Set color on body, face, or feature.
    color_rgb: [R, G, B] values 0-255
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        r, g, b = request.color_rgb
        # Convert RGB to SolidWorks color format (BGR integer)
        color_ref = r | (g << 8) | (b << 16)

        if request.entity_name:
            # Select specific entity
            type_map = {
                "body": "SOLIDBODY",
                "face": "FACE",
                "feature": "BODYFEATURE",
                "component": "COMPONENT"
            }
            entity_type = type_map.get(request.entity_type, "SOLIDBODY")
            doc.Extension.SelectByID2(request.entity_name, entity_type, 0, 0, 0, False, 0, None, 0)

        # Apply color to selection
        mat_props = doc.MaterialPropertyValues
        if mat_props:
            # Format: [R, G, B, Ambient, Diffuse, Specular, Shininess, Transparency, Emission]
            props = [r/255.0, g/255.0, b/255.0, 0.5, 0.5, 0.5, 0.5, 0.0, 0.0]
            doc.MaterialPropertyValues = props

        return {
            "success": True,
            "color_rgb": request.color_rgb,
            "entity_type": request.entity_type,
            "message": f"Color set to RGB({r}, {g}, {b})"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Set color failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.get("/color")
async def get_color():
    """
    Get color of selected entity or document default.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        mat_props = doc.MaterialPropertyValues
        if mat_props and len(mat_props) >= 3:
            r = int(mat_props[0] * 255)
            g = int(mat_props[1] * 255)
            b = int(mat_props[2] * 255)

            return {
                "color_rgb": [r, g, b],
                "hex": f"#{r:02x}{g:02x}{b:02x}"
            }

        return {"color_rgb": [128, 128, 128], "hex": "#808080"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get color failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/transparency/set")
async def set_transparency(request: SetTransparencyRequest):
    """
    Set transparency on body or component.
    transparency: 0.0 (opaque) to 1.0 (fully transparent)
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        if request.entity_name:
            doc.Extension.SelectByID2(request.entity_name, "SOLIDBODY", 0, 0, 0, False, 0, None, 0)

        mat_props = list(doc.MaterialPropertyValues) if doc.MaterialPropertyValues else [0.5]*9
        mat_props[7] = request.transparency  # Index 7 is transparency
        doc.MaterialPropertyValues = mat_props

        return {
            "success": True,
            "transparency": request.transparency,
            "message": f"Transparency set to {request.transparency * 100:.0f}%"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Set transparency failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


# =============================================================================
# Display Mode
# =============================================================================

@router.post("/mode/set")
async def set_display_mode(request: DisplayModeRequest):
    """
    Set the display mode for the view.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        mode_map = {
            "wireframe": 1,
            "hidden_visible": 2,
            "hidden_removed": 3,
            "shaded": 4,
            "shaded_edges": 5
        }
        mode = mode_map.get(request.mode.lower(), 4)

        # Get active view and set display mode
        view = doc.ActiveView
        if view:
            view.DisplayMode = mode

        return {
            "success": True,
            "mode": request.mode,
            "message": f"Display mode set to {request.mode}"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Set display mode failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.get("/mode")
async def get_display_mode():
    """
    Get current display mode.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        mode_names = {
            1: "wireframe",
            2: "hidden_visible",
            3: "hidden_removed",
            4: "shaded",
            5: "shaded_edges"
        }

        view = doc.ActiveView
        mode = view.DisplayMode if view else 4

        return {
            "mode_code": mode,
            "mode_name": mode_names.get(mode, "unknown")
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get display mode failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


# =============================================================================
# Component Visibility (Assemblies)
# =============================================================================

@router.post("/component/visibility")
async def set_component_visibility(request: ComponentVisibilityRequest):
    """
    Show or hide a component in an assembly.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        if doc.GetType() != 2:  # Assembly
            raise HTTPException(status_code=400, detail="Not an assembly")

        # Select component
        doc.Extension.SelectByID2(request.component_name, "COMPONENT", 0, 0, 0, False, 0, None, 0)

        if request.visible:
            doc.ShowComponent2()
        else:
            doc.HideComponent2()

        doc.ClearSelection2(True)

        return {
            "success": True,
            "component": request.component_name,
            "visible": request.visible
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Set component visibility failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/show-all")
async def show_all_components():
    """
    Show all hidden components in assembly.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        if doc.GetType() != 2:
            raise HTTPException(status_code=400, detail="Not an assembly")

        doc.Extension.SelectAll()
        doc.ShowComponent2()
        doc.ClearSelection2(True)

        return {"success": True, "message": "All components shown"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Show all failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


# =============================================================================
# View Orientation
# =============================================================================

@router.post("/view/{orientation}")
async def set_view_orientation(orientation: str):
    """
    Set view to standard orientation.
    orientation: front, back, left, right, top, bottom, isometric, trimetric, dimetric
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        orientation_map = {
            "front": 1, "back": 2, "left": 3, "right": 4,
            "top": 5, "bottom": 6, "isometric": 7,
            "trimetric": 8, "dimetric": 9
        }

        view_code = orientation_map.get(orientation.lower())
        if not view_code:
            raise HTTPException(status_code=400, detail=f"Unknown orientation: {orientation}")

        doc.ShowNamedView2("", view_code)
        doc.ViewZoomtofit2()

        return {
            "success": True,
            "orientation": orientation
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Set view orientation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/zoom-fit")
async def zoom_to_fit():
    """
    Zoom to fit entire model in view.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        doc.ViewZoomtofit2()

        return {"success": True, "message": "Zoomed to fit"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/zoom/{factor}")
async def zoom(factor: float):
    """
    Zoom by factor (>1 = zoom in, <1 = zoom out).
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        doc.ViewZoomBy2(factor)

        return {"success": True, "factor": factor}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


__all__ = ["router"]
