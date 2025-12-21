"""
SolidWorks Assembly COM Adapter
Endpoints for assembly operations: new assembly, insert component, add mate.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import win32com.client
import pythoncom
import logging
import os
from typing import Optional

router = APIRouter(prefix="/com/solidworks", tags=["solidworks-assembly"])
logger = logging.getLogger(__name__)

# Share app reference with main solidworks_com module
_sw_app = None


class InsertComponentRequest(BaseModel):
    filepath: str
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0


class MateRequest(BaseModel):
    mate_type: str  # coincident, concentric, parallel, perpendicular, distance, angle
    value: Optional[float] = None  # For distance or angle mates


def get_app():
    """Get or create SolidWorks application instance."""
    global _sw_app
    if _sw_app is None:
        pythoncom.CoInitialize()
        try:
            _sw_app = win32com.client.Dispatch("SldWorks.Application")
            _sw_app.Visible = True
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Could not connect to SolidWorks: {e}")
    return _sw_app


@router.post("/new_assembly")
async def new_assembly():
    """Create a new assembly document."""
    logger.info("Creating new SolidWorks assembly")
    app = get_app()

    # Find assembly template
    template_path = app.GetUserPreferenceStringValue(23)  # swDefaultTemplateAssembly
    if not template_path or not os.path.exists(template_path):
        # Fallback to common paths
        common_paths = [
            r"C:\ProgramData\SolidWorks\SOLIDWORKS 2024\templates\Assembly.asmdot",
            r"C:\ProgramData\SolidWorks\SOLIDWORKS 2023\templates\Assembly.asmdot",
            r"C:\ProgramData\SolidWorks\SOLIDWORKS 2022\templates\Assembly.asmdot",
        ]
        for path in common_paths:
            if os.path.exists(path):
                template_path = path
                break

    if not template_path:
        raise HTTPException(status_code=500, detail="Could not find assembly template")

    model = app.NewDocument(template_path, 0, 0, 0)
    return {"status": "ok", "document_type": "assembly"}


@router.post("/insert_component")
async def insert_component(req: InsertComponentRequest):
    """Insert a component into the current assembly."""
    logger.info(f"Inserting component: {req.filepath}")
    app = get_app()
    model = app.ActiveDoc

    if not model:
        raise HTTPException(status_code=400, detail="No active document")

    # Check if it's an assembly
    doc_type = model.GetType()
    if doc_type != 2:  # 2 = swDocASSEMBLY
        raise HTTPException(status_code=400, detail="Active document is not an assembly")

    if not os.path.exists(req.filepath):
        raise HTTPException(status_code=400, detail=f"File not found: {req.filepath}")

    # Insert the component
    # AddComponent5(filepath, config, x, y, z)
    component = model.AddComponent5(
        req.filepath,
        0,  # swAddComponentConfigOptions_CurrentSelectedConfig
        "",  # Configuration name (empty = default)
        False,  # UseConfigForPartSize
        "",  # ConfigName for size
        req.x, req.y, req.z
    )

    if component:
        return {
            "status": "ok",
            "filepath": req.filepath,
            "position": {"x": req.x, "y": req.y, "z": req.z}
        }
    else:
        return {"status": "warning", "message": "Component may not have been inserted correctly"}


@router.post("/add_mate")
async def add_mate(req: MateRequest):
    """Add a mate constraint between two selected entities."""
    logger.info(f"Adding mate: {req.mate_type}")
    app = get_app()
    model = app.ActiveDoc

    if not model:
        raise HTTPException(status_code=400, detail="No active document")

    # Check if it's an assembly
    doc_type = model.GetType()
    if doc_type != 2:
        raise HTTPException(status_code=400, detail="Active document is not an assembly")

    # Mate type constants
    mate_types = {
        "coincident": 0,     # swMateCOINCIDENT
        "concentric": 1,     # swMateCONCENTRIC
        "perpendicular": 2,  # swMatePERPENDICULAR
        "parallel": 3,       # swMatePARALLEL
        "tangent": 4,        # swMateTANGENT
        "distance": 5,       # swMateDISTANCE
        "angle": 6,          # swMateANGLE
    }

    mate_type_const = mate_types.get(req.mate_type.lower(), 0)

    # Alignment: 0 = Aligned, 1 = Anti-aligned
    alignment = 0

    # Value for distance/angle mates
    value = req.value if req.value is not None else 0

    # Get assembly object
    assy = model  # model is already the assembly

    # Add the mate
    # AddMate5(MateTypeFromEnum, AlignFromEnum, Flip, Distance, DistanceAbsUpperLimit,
    #          DistanceAbsLowerLimit, GearRatioNumerator, GearRatioDenominator, Angle,
    #          AngleAbsUpperLimit, AngleAbsLowerLimit, ForPositioningOnly, LockRotation, ErrorStatus)
    errors = 0

    if req.mate_type.lower() == "distance":
        mate = assy.AddMate5(
            mate_type_const, alignment, False,
            value, 0, 0,  # Distance params
            0, 0,  # Gear ratio
            0, 0, 0,  # Angle params
            False, False, errors
        )
    elif req.mate_type.lower() == "angle":
        import math
        angle_rad = math.radians(value) if value else 0
        mate = assy.AddMate5(
            mate_type_const, alignment, False,
            0, 0, 0,  # Distance params
            0, 0,  # Gear ratio
            angle_rad, 0, 0,  # Angle params
            False, False, errors
        )
    else:
        mate = assy.AddMate5(
            mate_type_const, alignment, False,
            0, 0, 0,  # Distance params
            0, 0,  # Gear ratio
            0, 0, 0,  # Angle params
            False, False, errors
        )

    return {
        "status": "ok",
        "mate_type": req.mate_type,
        "value": req.value
    }


@router.get("/assembly_info")
async def assembly_info():
    """Get information about the current assembly."""
    app = get_app()
    model = app.ActiveDoc

    if not model:
        return {"status": "error", "message": "No active document"}

    doc_type = model.GetType()
    if doc_type != 2:
        return {"status": "error", "message": "Active document is not an assembly"}

    # Get component count
    components = model.GetComponents(True)  # Top-level only
    component_count = len(components) if components else 0

    # Get mate count
    feature = model.FirstFeature()
    mate_count = 0
    while feature:
        if feature.GetTypeName2() == "MateGroup":
            sub_feature = feature.GetFirstSubFeature()
            while sub_feature:
                mate_count += 1
                sub_feature = sub_feature.GetNextSubFeature()
        feature = feature.GetNextFeature()

    return {
        "status": "ok",
        "is_assembly": True,
        "component_count": component_count,
        "mate_count": mate_count,
        "title": model.GetTitle()
    }
