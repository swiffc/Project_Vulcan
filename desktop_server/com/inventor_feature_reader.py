"""
Inventor Feature Reader - Extract geometry and dimensions from Inventor parts

Enables the bot to:
- Read Inventor feature trees
- Analyze sketches
- Extract dimensions
- Build strategies from existing Inventor parts
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import win32com.client
import pythoncom
import logging

router = APIRouter(prefix="/com/inventor-feature-reader", tags=["inventor-feature-reader"])
logger = logging.getLogger(__name__)


# Use same models as SolidWorks reader for consistency
from .feature_reader import (
    FeatureInfo,
    SketchEntity,
    DimensionInfo,
    FeatureAnalysis,
    PartAnalysis,
    StrategyFromPart
)


@router.get("/features", response_model=PartAnalysis)
async def get_inventor_feature_tree():
    """
    Enumerate all features in the active Inventor part.
    Returns feature tree with names, types, and hierarchy.
    """
    try:
        pythoncom.CoInitialize()
        
        # Get active Inventor instance
        try:
            inv_app = win32com.client.Dispatch("Inventor.Application")
        except:
            raise HTTPException(status_code=500, detail="Inventor not running")
        
        # Get active document
        doc = inv_app.ActiveDocument
        if not doc:
            raise HTTPException(status_code=400, detail="No active document")
        
        # Must be a part document
        if doc.DocumentType != 12290:  # kPartDocumentObject
            raise HTTPException(status_code=400, detail="Active document is not a part")
        
        part_doc = doc
        comp_def = part_doc.ComponentDefinition
        
        features = []
        feature_count = 0
        
        # Enumerate features
        for feature in comp_def.Features:
            try:
                feature_name = feature.Name
                feature_type = feature.Type
                is_suppressed = feature.Suppressed
                
                # Get type name
                type_name = _get_inventor_feature_type_name(feature_type)
                
                features.append(FeatureInfo(
                    name=feature_name,
                    type=type_name,
                    index=feature_count,
                    suppressed=is_suppressed
                ))
                
                feature_count += 1
                
            except Exception as e:
                logger.warning(f"Error reading feature: {e}")
                continue
        
        # Get material
        material_name = None
        try:
            if hasattr(comp_def, 'Material'):
                material_name = comp_def.Material.Name
        except:
            pass
        
        # Get mass properties
        mass = None
        volume = None
        try:
            mass_props = comp_def.MassProperties
            mass = mass_props.Mass  # kg
            volume = mass_props.Volume  # cm^3
        except:
            pass
        
        return PartAnalysis(
            filename=doc.FullFileName,
            total_features=feature_count,
            features=features,
            material=material_name,
            mass=mass,
            volume=volume
        )
        
    except Exception as e:
        logger.error(f"Error reading Inventor features: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.get("/feature/{feature_name}", response_model=FeatureAnalysis)
async def analyze_inventor_feature(feature_name: str):
    """
    Analyze a specific Inventor feature in detail.
    Returns dimensions, sketch entities, and properties.
    """
    try:
        pythoncom.CoInitialize()
        
        inv_app = win32com.client.Dispatch("Inventor.Application")
        doc = inv_app.ActiveDocument
        if not doc:
            raise HTTPException(status_code=400, detail="No active document")
        
        part_doc = doc
        comp_def = part_doc.ComponentDefinition
        
        # Find the feature
        feature = None
        for f in comp_def.Features:
            if f.Name == feature_name:
                feature = f
                break
        
        if not feature:
            raise HTTPException(status_code=404, detail=f"Feature '{feature_name}' not found")
        
        feature_type = _get_inventor_feature_type_name(feature.Type)
        dimensions = []
        sketch_entities = []
        properties = {}
        
        # Get feature-specific data
        if "Sketch" in feature_type:
            # Analyze sketch
            sketch = feature
            if hasattr(sketch, 'SketchLines'):
                sketch_entities = _analyze_inventor_sketch(sketch)
        
        elif "Extrude" in feature_type:
            try:
                extrude = feature
                if hasattr(extrude, 'ExtentOne'):
                    # Distance in cm (Inventor default)
                    properties["depth"] = extrude.ExtentOne.Distance.Value / 100  # Convert to meters
            except:
                pass
        
        elif "Revolve" in feature_type:
            try:
                revolve = feature
                if hasattr(revolve, 'Angle'):
                    properties["angle"] = revolve.Angle.Value  # In radians
            except:
                pass
        
        # Get dimensions
        try:
            if hasattr(feature, 'Parameters'):
                for param in feature.Parameters:
                    try:
                        if hasattr(param, 'Value'):
                            dimensions.append(DimensionInfo(
                                name=param.Name,
                                value=param.Value / 100,  # Convert cm to m
                                unit="meters",
                                type="Linear"
                            ))
                    except:
                        continue
        except:
            pass
        
        return FeatureAnalysis(
            feature_name=feature_name,
            feature_type=feature_type,
            dimensions=dimensions,
            sketch_entities=sketch_entities,
            properties=properties
        )
        
    except Exception as e:
        logger.error(f"Error analyzing Inventor feature: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/build-strategy", response_model=StrategyFromPart)
async def build_strategy_from_inventor_part():
    """
    Build a complete CAD strategy from the active Inventor part.
    Analyzes all features and generates strategy JSON.
    """
    try:
        pythoncom.CoInitialize()
        
        inv_app = win32com.client.Dispatch("Inventor.Application")
        doc = inv_app.ActiveDocument
        if not doc:
            raise HTTPException(status_code=400, detail="No active document")
        
        # Get part analysis
        part_analysis = await get_inventor_feature_tree()
        
        # Build strategy
        strategy_features = []
        all_dimensions = {}
        
        for feature_info in part_analysis.features:
            if feature_info.suppressed:
                continue
            
            try:
                feature_analysis = await analyze_inventor_feature(feature_info.name)
                
                strategy_feature = {
                    "type": feature_info.type,
                    "name": feature_info.name,
                    "dimensions": {dim.name: dim.value for dim in feature_analysis.dimensions},
                    "properties": feature_analysis.properties
                }
                
                strategy_features.append(strategy_feature)
                
                for dim in feature_analysis.dimensions:
                    all_dimensions[dim.name] = dim.value
                    
            except Exception as e:
                logger.warning(f"Could not analyze feature {feature_info.name}: {e}")
                continue
        
        description = f"Strategy extracted from {part_analysis.filename} with {len(strategy_features)} features"
        
        return StrategyFromPart(
            name=doc.DisplayName,
            description=description,
            material=part_analysis.material or "Not specified",
            features=strategy_features,
            dimensions=all_dimensions
        )
        
    except Exception as e:
        logger.error(f"Error building strategy from Inventor: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


def _get_inventor_feature_type_name(feature_type: int) -> str:
    """Convert Inventor feature type enum to readable name."""
    type_map = {
        83969: "ExtrudeFeature",
        84225: "RevolveFeature",
        84481: "HoleFeature",
        84737: "FilletFeature",
        84993: "ChamferFeature",
        85249: "RectangularPatternFeature",
        85505: "CircularPatternFeature",
        86017: "MirrorFeature",
        86273: "ShellFeature",
        86529: "ThickenFeature",
        87041: "SweepFeature",
        87297: "LoftFeature",
        87553: "RibFeature",
        88065: "EmbossFeature",
        88321: "DecalFeature",
    }
    
    return type_map.get(feature_type, f"Feature_{feature_type}")


def _analyze_inventor_sketch(sketch) -> List[SketchEntity]:
    """Extract entities from an Inventor sketch."""
    entities = []
    
    try:
        # Get sketch lines
        if hasattr(sketch, 'SketchLines'):
            for line in sketch.SketchLines:
                try:
                    start = line.StartSketchPoint
                    end = line.EndSketchPoint
                    entities.append(SketchEntity(
                        type="Line",
                        data={
                            "start_x": start.Geometry.X / 100,  # Convert cm to m
                            "start_y": start.Geometry.Y / 100,
                            "end_x": end.Geometry.X / 100,
                            "end_y": end.Geometry.Y / 100
                        }
                    ))
                except:
                    continue
        
        # Get sketch circles
        if hasattr(sketch, 'SketchCircles'):
            for circle in sketch.SketchCircles:
                try:
                    center = circle.CenterSketchPoint
                    radius = circle.Radius
                    entities.append(SketchEntity(
                        type="Circle",
                        data={
                            "center_x": center.Geometry.X / 100,
                            "center_y": center.Geometry.Y / 100,
                            "radius": radius / 100
                        }
                    ))
                except:
                    continue
        
        # Get sketch arcs
        if hasattr(sketch, 'SketchArcs'):
            for arc in sketch.SketchArcs:
                try:
                    center = arc.CenterSketchPoint
                    radius = arc.Radius
                    start_angle = arc.StartAngle
                    end_angle = arc.EndAngle
                    entities.append(SketchEntity(
                        type="Arc",
                        data={
                            "center_x": center.Geometry.X / 100,
                            "center_y": center.Geometry.Y / 100,
                            "radius": radius / 100,
                            "start_angle": start_angle,
                            "end_angle": end_angle
                        }
                    ))
                except:
                    continue
                    
    except Exception as e:
        logger.warning(f"Error reading Inventor sketch: {e}")
    
    return entities
