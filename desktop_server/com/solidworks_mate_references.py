"""
SolidWorks Mate Reference Automation - COM API wrapper for creating Mate References
Automates creation of Concentric + Coincident Mate References (SmartMates) for hole alignment.

Requires: SolidWorks installed and licensed on the machine
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import win32com.client
import pythoncom
import logging
import os
import math

router = APIRouter(prefix="/com/solidworks/mate_references", tags=["solidworks-mate-refs"])
logger = logging.getLogger(__name__)

# Import shared app reference from solidworks_com
from .solidworks_com import get_app, _sw_model


class CreateMateRefsRequest(BaseModel):
    filepath: str  # Path to part or assembly file
    part_ids: Optional[List[str]] = None  # Specific part IDs to process (None = all parts)


class VerifyAlignmentRequest(BaseModel):
    filepath: str  # Path to assembly file
    tolerance: float = 0.0015875  # Default: 1/16" in meters


def detect_holes_in_part(model) -> List[Dict[str, Any]]:
    """
    Detect holes in a SolidWorks part document.
    Returns list of hole information: {edge, center_point, axis_vector, radius, feature}
    """
    holes = []
    
    try:
        # Get all features
        feature = model.FirstFeature()
        hole_count = 0
        
        while feature:
            feature_type = feature.GetTypeName2()
            
            # Check for hole features
            if feature_type == "HoleWizard" or feature_type == "Hole":
                # This is a hole feature
                try:
                    # Get the feature's edges (circular edges)
                    edges = []
                    
                    # Get feature faces
                    faces = feature.GetFaces()
                    if faces:
                        for face in faces:
                            face_edges = face.GetEdges()
                            if face_edges:
                                for edge in face_edges:
                                    edge_type = edge.GetType()
                                    # Check if it's a circular edge (type 5 = swEdgeTypeCircle)
                                    if edge_type == 5:
                                        # Get edge geometry
                                        edge_curve = edge.GetCurve()
                                        if edge_curve:
                                            # Get center and radius
                                            center = edge_curve.CenterPoint
                                            radius = edge_curve.Radius
                                            
                                            # Get axis (normal to circle plane)
                                            axis = edge_curve.AxisVector
                                            
                                            holes.append({
                                                "edge": edge,
                                                "feature": feature,
                                                "center_point": {
                                                    "x": center[0],
                                                    "y": center[1],
                                                    "z": center[2]
                                                },
                                                "axis_vector": {
                                                    "x": axis[0] if len(axis) > 0 else 0,
                                                    "y": axis[1] if len(axis) > 1 else 0,
                                                    "z": axis[2] if len(axis) > 2 else 1
                                                },
                                                "radius": radius,
                                                "name": f"Hole_{hole_count + 1}"
                                            })
                                            hole_count += 1
                except Exception as e:
                    logger.debug(f"Error processing hole feature {feature.Name}: {e}")
            
            feature = feature.GetNextFeature()
        
        # If no holes found via features, try to find circular edges directly
        if len(holes) == 0:
            try:
                # Get all edges from the model
                body = model.GetBody2()
                if body:
                    edges = body.GetEdges()
                    if edges:
                        for edge in edges:
                            try:
                                edge_type = edge.GetType()
                                if edge_type == 5:  # Circular edge
                                    edge_curve = edge.GetCurve()
                                    if edge_curve:
                                        center = edge_curve.CenterPoint
                                        radius = edge_curve.Radius
                                        
                                        holes.append({
                                            "edge": edge,
                                            "center_point": {
                                                "x": center[0],
                                                "y": center[1],
                                                "z": center[2]
                                            },
                                            "radius": radius,
                                            "name": f"Hole_{len(holes) + 1}"
                                        })
                            except Exception as e:
                                logger.debug(f"Error processing edge: {e}")
                                continue
            except Exception as e:
                logger.debug(f"Error detecting holes via edges: {e}")
                
    except Exception as e:
        logger.warning(f"Error detecting holes: {e}")
    
    return holes


def create_concentric_mate_ref(model, edge, name: str):
    """Create a Concentric Mate Reference for a circular edge (hole)."""
    try:
        # Clear selection first
        model.ClearSelection2(True)
        
        # Select the edge
        success = model.Extension.SelectByID2("", "EDGE", 0, 0, 0, False, 0, None, 0)
        if not success:
            # Try selecting by edge object
            edge.Select(False)
        
        # Create Mate Reference
        # InsertMateReference2(ReferenceType, PrimaryEntityType, SecondaryEntityType, 
        #                      PrimaryEntity, SecondaryEntity, Distance, Angle)
        # ReferenceType: 0=Concentric, 1=Coincident, 2=Parallel, etc.
        mate_ref = model.FeatureManager.InsertMateReference2(
            0,  # Concentric
            1,  # Primary entity type: Edge
            1,  # Secondary entity type: Edge
            edge,  # Primary entity
            None,  # Secondary entity (not needed for single selection)
            0,  # Distance
            0   # Angle
        )
        
        if mate_ref:
            # Rename the mate reference
            try:
                mate_ref.Name = name
            except:
                pass  # Name might be read-only
        
        return mate_ref
    except Exception as e:
        logger.error(f"Error creating Concentric Mate Reference {name}: {e}")
        raise


def create_coincident_mate_ref(model, face, name: str):
    """Create a Coincident Mate Reference for a planar face."""
    try:
        # Clear selection first
        model.ClearSelection2(True)
        
        # Select the face
        face.Select(False)
        
        # Create Mate Reference
        # ReferenceType: 1=Coincident
        mate_ref = model.FeatureManager.InsertMateReference2(
            1,  # Coincident
            2,  # Primary entity type: Face
            2,  # Secondary entity type: Face
            face,  # Primary entity
            None,  # Secondary entity
            0,  # Distance
            0   # Angle
        )
        
        if mate_ref:
            try:
                mate_ref.Name = name
            except:
                pass
        
        return mate_ref
    except Exception as e:
        logger.error(f"Error creating Coincident Mate Reference {name}: {e}")
        raise


@router.post("/create_mate_refs")
async def create_mate_refs(req: CreateMateRefsRequest):
    """
    Create Concentric and Coincident Mate References for holes in a part or assembly.
    Automatically detects holes and creates appropriate Mate References.
    """
    logger.info(f"Creating Mate References for {req.filepath}")
    app = get_app()
    
    if not os.path.exists(req.filepath):
        raise HTTPException(status_code=400, detail=f"File not found: {req.filepath}")
    
    try:
        # Open the document
        errors = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
        warnings = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
        
        model = app.OpenDoc6(
            req.filepath,
            1 if req.filepath.endswith('.sldprt') else 2,  # 1=Part, 2=Assembly
            0,  # swOpenDocOptions_Silent
            "",
            errors,
            warnings
        )
        
        if not model:
            raise HTTPException(status_code=400, detail="Failed to open document")
        
        created_mate_refs = []
        
        # Check if it's an assembly or part
        doc_type = model.GetType()
        if doc_type == 2:  # swDocASSEMBLY
            # Process assembly - iterate through components
            components = model.GetComponents(False)  # False = include sub-assemblies
            
            for comp in components:
                comp_name = comp.Name2
                comp_model = comp.GetModelDoc()
                
                if comp_model and comp_model.GetType() == 1:  # swDocPART
                    holes = detect_holes_in_part(comp_model)
                    
                    for hole in holes:
                        if "edge" in hole:
                            mate_ref = create_concentric_mate_ref(comp_model, hole["edge"], hole["name"])
                            created_mate_refs.append({
                                "name": hole["name"],
                                "type": "Concentric",
                                "component": comp_name
                            })
        else:
            # Process part
            holes = detect_holes_in_part(model)
            
            for hole in holes:
                if "edge" in hole:
                    mate_ref = create_concentric_mate_ref(model, hole["edge"], hole["name"])
                    created_mate_refs.append({
                        "name": hole["name"],
                        "type": "Concentric"
                    })
        
        # Save the document
        model.Save3(1, False, errors, warnings)  # 1 = swSaveAsOptions_Silent
        
        return {
            "status": "ok",
            "filepath": req.filepath,
            "created_count": len(created_mate_refs),
            "mate_refs": created_mate_refs
        }
        
    except Exception as e:
        logger.error(f"Error creating Mate References: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create Mate References: {str(e)}")


@router.post("/verify_alignment")
async def verify_alignment(req: VerifyAlignmentRequest):
    """
    Verify hole alignment in a SolidWorks assembly by reading Mate References.
    Returns report of aligned and mis-aligned holes.
    """
    logger.info(f"Verifying hole alignment for {req.filepath}")
    
    # Import verifier function
    from .hole_alignment_verifier import verify_solidworks_alignment
    
    try:
        result = verify_solidworks_alignment(req.filepath, req.tolerance)
        return result
    except Exception as e:
        logger.error(f"Error verifying alignment: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to verify alignment: {str(e)}")

