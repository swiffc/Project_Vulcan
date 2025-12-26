"""
SolidWorks Multi-Body & Cut List API
====================================
Body and cut list management including:
- Multi-body part operations
- Body folder management
- Weldment cut list
- Body properties and operations
"""

import logging
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

try:
    import win32com.client
    import pythoncom
    COM_AVAILABLE = True
except ImportError:
    COM_AVAILABLE = False


# Pydantic models
class MoveBodyRequest(BaseModel):
    body_name: str
    translation: List[float]  # [X, Y, Z] in mm
    rotation: Optional[List[float]] = None  # [angleX, angleY, angleZ] in degrees


class CopyBodyRequest(BaseModel):
    body_name: str
    new_name: Optional[str] = None


class CombineBodiesRequest(BaseModel):
    main_body: str
    tool_bodies: List[str]
    operation: str = "add"  # add, subtract, common


class SplitBodyRequest(BaseModel):
    body_name: str
    split_tool: str  # Face or plane name to split with


class RenameBodyRequest(BaseModel):
    old_name: str
    new_name: str


router = APIRouter(prefix="/solidworks-bodies", tags=["solidworks-bodies"])


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
# Body Management
# =============================================================================

@router.get("/list")
async def list_bodies():
    """
    List all bodies in the active part.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        solid_bodies = []
        surface_bodies = []

        # Get solid bodies (type 0)
        bodies = doc.GetBodies2(0, False)
        if bodies:
            for body in bodies:
                try:
                    solid_bodies.append({
                        "name": body.Name,
                        "visible": body.Visible,
                        "volume_m3": body.GetMassProperties(0)[3] if body.GetMassProperties(0) else 0,
                        "face_count": body.GetFaceCount(),
                        "edge_count": body.GetEdgeCount()
                    })
                except Exception:
                    solid_bodies.append({"name": "Unknown", "error": True})

        # Get surface bodies (type 1)
        surfaces = doc.GetBodies2(1, False)
        if surfaces:
            for surf in surfaces:
                try:
                    surface_bodies.append({
                        "name": surf.Name,
                        "visible": surf.Visible,
                        "face_count": surf.GetFaceCount()
                    })
                except Exception:
                    surface_bodies.append({"name": "Unknown", "error": True})

        return {
            "solid_body_count": len(solid_bodies),
            "surface_body_count": len(surface_bodies),
            "solid_bodies": solid_bodies,
            "surface_bodies": surface_bodies
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"List bodies failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.get("/body/{body_name}")
async def get_body_info(body_name: str):
    """
    Get detailed information about a specific body.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        bodies = doc.GetBodies2(0, False)
        if bodies:
            for body in bodies:
                if body.Name == body_name:
                    mass_props = body.GetMassProperties(0)

                    return {
                        "name": body_name,
                        "visible": body.Visible,
                        "face_count": body.GetFaceCount(),
                        "edge_count": body.GetEdgeCount(),
                        "vertex_count": body.GetVertexCount(),
                        "mass_properties": {
                            "volume_m3": mass_props[3] if mass_props else 0,
                            "surface_area_m2": mass_props[4] if mass_props else 0,
                            "center_of_mass": list(mass_props[0:3]) if mass_props else None
                        } if mass_props else None
                    }

        raise HTTPException(status_code=404, detail=f"Body '{body_name}' not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get body info failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/rename")
async def rename_body(request: RenameBodyRequest):
    """
    Rename a body.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        bodies = doc.GetBodies2(0, False)
        if bodies:
            for body in bodies:
                if body.Name == request.old_name:
                    body.Name = request.new_name
                    return {
                        "success": True,
                        "old_name": request.old_name,
                        "new_name": request.new_name
                    }

        raise HTTPException(status_code=404, detail=f"Body '{request.old_name}' not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Rename body failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/hide/{body_name}")
async def hide_body(body_name: str):
    """
    Hide a body.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        doc.Extension.SelectByID2(body_name, "SOLIDBODY", 0, 0, 0, False, 0, None, 0)
        doc.HideBody()

        return {"success": True, "body": body_name, "visible": False}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Hide body failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/show/{body_name}")
async def show_body(body_name: str):
    """
    Show a hidden body.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        doc.Extension.SelectByID2(body_name, "SOLIDBODY", 0, 0, 0, False, 0, None, 0)
        doc.ShowBody()

        return {"success": True, "body": body_name, "visible": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Show body failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


# =============================================================================
# Body Operations
# =============================================================================

@router.post("/combine")
async def combine_bodies(request: CombineBodiesRequest):
    """
    Combine multiple bodies using boolean operations.
    operation: add (union), subtract, common (intersection)
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        fm = doc.FeatureManager

        # Select main body
        doc.Extension.SelectByID2(request.main_body, "SOLIDBODY", 0, 0, 0, False, 1, None, 0)

        # Select tool bodies
        for i, tool in enumerate(request.tool_bodies):
            doc.Extension.SelectByID2(tool, "SOLIDBODY", 0, 0, 0, True, 2 + i, None, 0)

        # Operation type mapping
        op_map = {"add": 0, "subtract": 1, "common": 2}
        op_type = op_map.get(request.operation.lower(), 0)

        # Create combine feature
        combine = fm.InsertCombineFeature(op_type, None, None)

        doc.ClearSelection2(True)
        doc.EditRebuild3()

        return {
            "success": combine is not None,
            "main_body": request.main_body,
            "tool_bodies": request.tool_bodies,
            "operation": request.operation
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Combine bodies failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/move")
async def move_body(request: MoveBodyRequest):
    """
    Move/copy a body by translation and/or rotation.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        fm = doc.FeatureManager

        # Select body
        doc.Extension.SelectByID2(request.body_name, "SOLIDBODY", 0, 0, 0, False, 0, None, 0)

        # Convert mm to meters
        tx, ty, tz = [v / 1000.0 for v in request.translation]

        # Create move/copy feature
        move = fm.InsertMoveCopyBody2(
            tx, ty, tz,  # Translation
            0, 0, 0, 0,  # Rotation axis origin
            0, 0, 0,     # Rotation axis direction
            0,           # Rotation angle
            False,       # Copy (False = move)
            1            # Number of copies
        )

        doc.ClearSelection2(True)
        doc.EditRebuild3()

        return {
            "success": move is not None,
            "body": request.body_name,
            "translation_mm": request.translation
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Move body failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.delete("/delete/{body_name}")
async def delete_body(body_name: str):
    """
    Delete a body from the part.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        fm = doc.FeatureManager

        doc.Extension.SelectByID2(body_name, "SOLIDBODY", 0, 0, 0, False, 1, None, 0)
        result = fm.InsertDeleteBody2(True)

        doc.ClearSelection2(True)
        doc.EditRebuild3()

        return {
            "success": result is not None,
            "deleted": body_name
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete body failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


# =============================================================================
# Cut List (Weldments)
# =============================================================================

@router.get("/cut-list")
async def get_cut_list():
    """
    Get weldment cut list items.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        cut_list_items = []

        # Find cut list folder in feature tree
        feature = doc.FirstFeature()
        while feature:
            if feature.GetTypeName2() == "CutListFolder":
                # Get cut list items
                sub_feature = feature.GetFirstSubFeature()
                while sub_feature:
                    try:
                        # Get custom properties for cut list item
                        props = {}
                        cpm = sub_feature.CustomPropertyManager
                        if cpm:
                            names = cpm.GetNames()
                            if names:
                                for name in names:
                                    val = ""
                                    resolved = ""
                                    cpm.Get5(name, False, val, resolved, False)
                                    props[name] = resolved or val

                        cut_list_items.append({
                            "name": sub_feature.Name,
                            "type": sub_feature.GetTypeName2(),
                            "properties": props
                        })
                    except Exception:
                        cut_list_items.append({"name": sub_feature.Name})

                    sub_feature = sub_feature.GetNextSubFeature()

            feature = feature.GetNextFeature()

        return {
            "count": len(cut_list_items),
            "items": cut_list_items
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get cut list failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/cut-list/update")
async def update_cut_list():
    """
    Force update of the cut list.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        # Find and update cut list folder
        feature = doc.FirstFeature()
        while feature:
            if feature.GetTypeName2() == "CutListFolder":
                feature.UpdateCutList()
                return {"success": True, "message": "Cut list updated"}
            feature = feature.GetNextFeature()

        raise HTTPException(status_code=404, detail="No cut list folder found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update cut list failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/cut-list/export")
async def export_cut_list(output_path: str):
    """
    Export cut list to Excel file.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        # Create weldment cut list export
        result = doc.ExportToDWG2(
            output_path,
            doc.GetPathName(),
            1,  # Export type
            True, False, False, False,
            0, None, 0
        )

        return {
            "success": result,
            "output_path": output_path
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Export cut list failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


# =============================================================================
# Body Folders
# =============================================================================

@router.get("/folders")
async def list_body_folders():
    """
    List all body folders in the feature tree.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        folders = []
        feature = doc.FirstFeature()

        while feature:
            feat_type = feature.GetTypeName2()
            if "Folder" in feat_type:
                folders.append({
                    "name": feature.Name,
                    "type": feat_type,
                    "suppressed": feature.IsSuppressed2(1)[0] if hasattr(feature, 'IsSuppressed2') else False
                })
            feature = feature.GetNextFeature()

        return {
            "count": len(folders),
            "folders": folders
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"List folders failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


__all__ = ["router"]
