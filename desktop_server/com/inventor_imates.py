"""
Inventor iMate Automation - COM API wrapper for creating iMates
Automates creation of Insert, Mate, and Composite iMates for
hole-to-hole alignment in ACHE assemblies.

Requires: Autodesk Inventor installed and licensed on the machine
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging
import os
import math

# Import shared app reference from inventor_com
from .inventor_com import get_app

router = APIRouter(prefix="/com/inventor/imates", tags=["inventor-imates"])
logger = logging.getLogger(__name__)


class CreateIMatesRequest(BaseModel):
    filepath: str  # Path to part or assembly file
    part_ids: Optional[List[str]] = None  # Specific part IDs to process (None = all parts)


class CreateCompositeIMatesRequest(BaseModel):
    filepath: str  # Path to part file
    pattern_type: str = "auto"  # "auto", "circular", "rectangular"


class VerifyAlignmentRequest(BaseModel):
    filepath: str  # Path to assembly file
    tolerance: float = 0.0015875  # Default: 1/16" in meters


def detect_holes_in_part(doc) -> List[Dict[str, Any]]:
    """
    Detect holes in an Inventor part document.
    Returns list of hole information: {edge, center_point, axis_vector, radius}
    """
    holes = []
    comp_def = doc.ComponentDefinition
    
    try:
        # Get all edges in the part
        edges = comp_def.SurfaceBodies.Item(1).Faces
        hole_count = 0
        
        # Iterate through faces to find cylindrical holes
        for i in range(1, edges.Count + 1):
            try:
                face = edges.Item(i)
                surface_type = face.SurfaceType
                
                # Check if it's a cylindrical surface (hole)
                # SurfaceType 3 = kCylinderSurface
                if surface_type == 3:
                    # Get the edge of the cylinder
                    edge_collection = face.Edges
                    if edge_collection.Count > 0:
                        edge = edge_collection.Item(1)
                        
                        # Get geometry
                        geometry = edge.Geometry
                        if geometry:
                            # Get center point and axis
                            center = geometry.CenterPoint
                            axis = geometry.AxisVector
                            radius = geometry.Radius
                            
                            holes.append({
                                "edge": edge,
                                "center_point": {
                                    "x": center.X,
                                    "y": center.Y,
                                    "z": center.Z
                                },
                                "axis_vector": {
                                    "x": axis.X,
                                    "y": axis.Y,
                                    "z": axis.Z
                                },
                                "radius": radius,
                                "name": f"Hole_{hole_count + 1}"
                            })
                            hole_count += 1
            except Exception as e:
                logger.debug(f"Error processing face {i}: {e}")
                continue
                
    except Exception as e:
        logger.warning(f"Error detecting holes: {e}")
        # Fallback: try to find hole features
        try:
            features = comp_def.Features
            for i in range(1, features.Count + 1):
                feature = features.Item(i)
                # Check for hole feature types
                if hasattr(feature, 'HoleType'):
                    # This is a hole feature
                    holes.append({
                        "feature": feature,
                        "name": f"Hole_{len(holes) + 1}"
                    })
        except Exception as e2:
            logger.warning(f"Fallback hole detection also failed: {e2}")
    
    return holes


def create_insert_imate(comp_def, edge, name: str):
    """Create an Insert iMate for a cylindrical hole edge."""
    try:
        imate_defs = comp_def.iMateDefinitions
        
        # Create Insert iMate (Type = 1)
        # Insert iMate requires: edge geometry
        imate_def = imate_defs.Add(1, name)  # Type 1 = Insert
        
        # Set geometry to the edge
        if hasattr(imate_def, 'SetGeometry'):
            imate_def.SetGeometry(edge)
        elif hasattr(imate_def, 'Geometry'):
            imate_def.Geometry = edge
            
        return imate_def
    except Exception as e:
        logger.error(f"Error creating Insert iMate {name}: {e}")
        raise


def create_mate_imate(comp_def, face, name: str):
    """Create a Mate iMate for a planar face."""
    try:
        imate_defs = comp_def.iMateDefinitions
        
        # Create Mate iMate (Type = 0)
        # Mate iMate requires: face geometry
        imate_def = imate_defs.Add(0, name)  # Type 0 = Mate
        
        # Set geometry to the face
        if hasattr(imate_def, 'SetGeometry'):
            imate_def.SetGeometry(face)
        elif hasattr(imate_def, 'Geometry'):
            imate_def.Geometry = face
            
        return imate_def
    except Exception as e:
        logger.error(f"Error creating Mate iMate {name}: {e}")
        raise


def detect_bolt_patterns(holes: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
    """
    Detect bolt patterns from hole list.
    Groups holes into circular or rectangular patterns.
    """
    if len(holes) < 2:
        return []
    
    patterns = []
    processed = set()
    
    for i, hole1 in enumerate(holes):
        if i in processed:
            continue
            
        pattern = [hole1]
        processed.add(i)
        
        # Try to find circular pattern
        center1 = hole1.get("center_point")
        if center1:
            for j, hole2 in enumerate(holes[i+1:], start=i+1):
                if j in processed:
                    continue
                    
                center2 = hole2.get("center_point")
                if center2:
                    # Check if holes are at same radius from a common center
                    # This is a simplified check - could be improved
                    dist = math.sqrt(
                        (center2["x"] - center1["x"])**2 +
                        (center2["y"] - center1["y"])**2 +
                        (center2["z"] - center1["z"])**2
                    )
                    
                    # If holes are roughly equidistant, might be a pattern
                    if dist < 1.0:  # Within 1 meter (adjust threshold as needed)
                        pattern.append(hole2)
                        processed.add(j)
        
        if len(pattern) > 1:
            patterns.append(pattern)
    
    return patterns


@router.post("/create_imates")
async def create_imates(req: CreateIMatesRequest):
    """
    Create Insert and Mate iMates for holes in a part or assembly.
    Automatically detects holes and creates appropriate iMates.
    """
    logger.info(f"Creating iMates for {req.filepath}")
    app = get_app()
    
    if not os.path.exists(req.filepath):
        raise HTTPException(status_code=400, detail=f"File not found: {req.filepath}")
    
    try:
        # Open the document
        doc = app.Documents.Open(req.filepath, True)  # True = visible
        
        created_imates = []
        
        # Check if it's an assembly or part
        doc_type = doc.DocumentType
        if doc_type == 12291:  # kAssemblyDocumentObject
            # Process assembly - iterate through components
            comp_def = doc.ComponentDefinition
            occurrences = comp_def.Occurrences
            
            for i in range(1, occurrences.Count + 1):
                occ = occurrences.Item(i)
                comp = occ.Definition
                
                # Get part document
                part_doc = comp.Document
                if part_doc.DocumentType == 12290:  # kPartDocumentObject
                    part_comp_def = part_doc.ComponentDefinition
                    holes = detect_holes_in_part(part_doc)
                    
                    for hole in holes:
                        if "edge" in hole:
                            create_insert_imate(
                                part_comp_def, hole["edge"], hole["name"]
                            )
                            created_imates.append({
                                "name": hole["name"],
                                "type": "Insert",
                                "part": occ.Name
                            })
        else:
            # Process part
            comp_def = doc.ComponentDefinition
            holes = detect_holes_in_part(doc)
            
            for hole in holes:
                if "edge" in hole:
                    create_insert_imate(comp_def, hole["edge"], hole["name"])
                    created_imates.append({
                        "name": hole["name"],
                        "type": "Insert"
                    })
        
        # Save the document
        doc.Save()
        
        return {
            "status": "ok",
            "filepath": req.filepath,
            "created_count": len(created_imates),
            "imates": created_imates
        }
        
    except Exception as e:
        logger.error(f"Error creating iMates: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create iMates: {str(e)}")


@router.post("/create_composite_imates")
async def create_composite_imates(req: CreateCompositeIMatesRequest):
    """
    Create Composite iMates for bolt patterns.
    Groups multiple hole iMates into a single Composite iMate.
    """
    logger.info(f"Creating composite iMates for {req.filepath}")
    app = get_app()
    
    if not os.path.exists(req.filepath):
        raise HTTPException(status_code=400, detail=f"File not found: {req.filepath}")
    
    try:
        doc = app.Documents.Open(req.filepath, True)
        comp_def = doc.ComponentDefinition
        
        # Detect holes
        holes = detect_holes_in_part(doc)
        
        if len(holes) < 2:
            raise HTTPException(status_code=400, detail="Need at least 2 holes for composite iMate")
        
        # Detect patterns
        patterns = detect_bolt_patterns(holes)
        
        if not patterns:
            raise HTTPException(status_code=400, detail="No bolt patterns detected")
        
        created_composites = []
        imate_defs = comp_def.iMateDefinitions
        
        for pattern_idx, pattern in enumerate(patterns):
            # Create individual iMates first
            individual_imates = []
                    for hole in pattern:
                        if "edge" in hole:
                            imate = create_insert_imate(
                                comp_def, hole["edge"], hole["name"]
                            )
                            individual_imates.append(imate)
            
            # Create Composite iMate (Type = 2)
            composite_name = f"Composite_iMate_Pattern_{pattern_idx + 1}"
            composite_imate = imate_defs.Add(2, composite_name)  # Type 2 = Composite
            
            # Add individual iMates to composite
            if hasattr(composite_imate, 'AddChild'):
                for imate in individual_imates:
                    composite_imate.AddChild(imate)
            elif hasattr(composite_imate, 'Children'):
                # Alternative method
                for imate in individual_imates:
                    composite_imate.Children.Add(imate)
            
            created_composites.append({
                "name": composite_name,
                "hole_count": len(pattern),
                "pattern_type": req.pattern_type
            })
        
        doc.Save()
        
        return {
            "status": "ok",
            "filepath": req.filepath,
            "composite_count": len(created_composites),
            "composites": created_composites
        }
        
    except Exception as e:
        logger.error(f"Error creating composite iMates: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create composite iMates: {str(e)}")


@router.post("/verify_alignment")
async def verify_alignment(req: VerifyAlignmentRequest):
    """
    Verify hole alignment in an assembly by reading iMates and checking alignment.
    Returns report of aligned and mis-aligned holes.
    """
    logger.info(f"Verifying hole alignment for {req.filepath}")
    
    # Import verifier function
    from .hole_alignment_verifier import verify_inventor_alignment
    
    try:
        result = verify_inventor_alignment(req.filepath, req.tolerance)
        return result
    except Exception as e:
        logger.error(f"Error verifying alignment: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to verify alignment: {str(e)}")

