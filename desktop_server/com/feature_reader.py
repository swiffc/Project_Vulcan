"""
SolidWorks Feature Reader - Extract geometry and dimensions from existing parts

Enables the bot to:
- Read feature trees
- Analyze sketches
- Extract dimensions
- Build strategies from existing parts
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import win32com.client
import pythoncom
import logging

router = APIRouter(prefix="/com/feature-reader", tags=["feature-reader"])
logger = logging.getLogger(__name__)


class FeatureInfo(BaseModel):
    name: str
    type: str
    index: int
    suppressed: bool = False
    parent: Optional[str] = None


class SketchEntity(BaseModel):
    type: str  # "Circle", "Line", "Arc", "Spline"
    data: Dict[str, Any]  # Geometry-specific data


class DimensionInfo(BaseModel):
    name: str
    value: float
    unit: str
    type: str  # "Linear", "Diameter", "Radius", "Angle"


class FeatureAnalysis(BaseModel):
    feature_name: str
    feature_type: str
    dimensions: List[DimensionInfo]
    sketch_entities: List[SketchEntity]
    properties: Dict[str, Any]


class PartAnalysis(BaseModel):
    filename: str
    total_features: int
    features: List[FeatureInfo]
    material: Optional[str] = None
    mass: Optional[float] = None
    volume: Optional[float] = None


class StrategyFromPart(BaseModel):
    name: str
    description: str
    material: str
    features: List[Dict[str, Any]]
    dimensions: Dict[str, float]


@router.get("/features", response_model=PartAnalysis)
async def get_feature_tree():
    """
    Enumerate all features in the active part.
    Returns feature tree with names, types, and hierarchy.
    """
    try:
        pythoncom.CoInitialize()
        
        # Get active SolidWorks instance
        try:
            sw_app = win32com.client.Dispatch("SldWorks.Application")
        except:
            raise HTTPException(status_code=500, detail="SolidWorks not running")
        
        # Get active document
        model = sw_app.ActiveDoc
        if not model:
            raise HTTPException(status_code=400, detail="No active document")
        
        # Get feature count
        feature_mgr = model.FeatureManager
        feature = model.FirstFeature()
        
        features = []
        feature_count = 0
        
        # Enumerate all features
        while feature is not None:
            try:
                feature_name = feature.Name
                feature_type = feature.GetTypeName2()
                is_suppressed = feature.IsSuppressed()
                
                features.append(FeatureInfo(
                    name=feature_name,
                    type=feature_type,
                    index=feature_count,
                    suppressed=is_suppressed
                ))
                
                feature_count += 1
                feature = feature.GetNextFeature()
                
            except Exception as e:
                logger.warning(f"Error reading feature: {e}")
                feature = feature.GetNextFeature()
                continue
        
        # Get material properties
        material_name = None
        try:
            material_name = model.GetMaterialPropertyName("", "")
        except:
            pass
        
        # Get mass properties
        mass = None
        volume = None
        try:
            mass_props = model.GetMassProperties(0)
            if mass_props:
                mass = mass_props[5]  # Mass in kg
                volume = mass_props[3]  # Volume in m^3
        except:
            pass
        
        return PartAnalysis(
            filename=model.GetPathName(),
            total_features=feature_count,
            features=features,
            material=material_name,
            mass=mass,
            volume=volume
        )
        
    except Exception as e:
        logger.error(f"Error reading features: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.get("/feature/{feature_name}", response_model=FeatureAnalysis)
async def analyze_feature(feature_name: str):
    """
    Analyze a specific feature in detail.
    Returns dimensions, sketch entities, and properties.
    """
    try:
        pythoncom.CoInitialize()
        
        sw_app = win32com.client.Dispatch("SldWorks.Application")
        model = sw_app.ActiveDoc
        if not model:
            raise HTTPException(status_code=400, detail="No active document")
        
        # Get the feature
        feature = model.FeatureByName(feature_name)
        if not feature:
            raise HTTPException(status_code=404, detail=f"Feature '{feature_name}' not found")
        
        feature_type = feature.GetTypeName2()
        dimensions = []
        sketch_entities = []
        properties = {}
        
        # Get feature-specific data based on type
        if "Sketch" in feature_type:
            # Analyze sketch
            sketch = feature.GetSpecificFeature2()
            if sketch:
                sketch_entities = _analyze_sketch(sketch)
        
        elif "Extrude" in feature_type or "Boss" in feature_type or "Cut" in feature_type:
            # Get extrude properties
            extrude_feature = feature.GetSpecificFeature2()
            if extrude_feature:
                try:
                    properties["depth"] = extrude_feature.GetDepth(True)  # In meters
                    properties["direction"] = extrude_feature.GetEndCondition(True)
                except:
                    pass
        
        elif "Revolve" in feature_type:
            # Get revolve properties
            revolve_feature = feature.GetSpecificFeature2()
            if revolve_feature:
                try:
                    properties["angle"] = revolve_feature.GetAngle()  # In radians
                except:
                    pass
        
        # Get dimensions for this feature
        dimensions = _get_feature_dimensions(feature)
        
        return FeatureAnalysis(
            feature_name=feature_name,
            feature_type=feature_type,
            dimensions=dimensions,
            sketch_entities=sketch_entities,
            properties=properties
        )
        
    except Exception as e:
        logger.error(f"Error analyzing feature: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/build-strategy", response_model=StrategyFromPart)
async def build_strategy_from_active_part():
    """
    Build a complete CAD strategy from the active part.
    Analyzes all features and generates strategy JSON.
    """
    try:
        pythoncom.CoInitialize()
        
        sw_app = win32com.client.Dispatch("SldWorks.Application")
        model = sw_app.ActiveDoc
        if not model:
            raise HTTPException(status_code=400, detail="No active document")
        
        # Get part analysis
        part_analysis = await get_feature_tree()
        
        # Build strategy
        strategy_features = []
        all_dimensions = {}
        
        for feature_info in part_analysis.features:
            if feature_info.suppressed:
                continue
            
            # Analyze each feature
            try:
                feature_analysis = await analyze_feature(feature_info.name)
                
                # Add to strategy
                strategy_feature = {
                    "type": feature_info.type,
                    "name": feature_info.name,
                    "dimensions": {dim.name: dim.value for dim in feature_analysis.dimensions},
                    "properties": feature_analysis.properties
                }
                
                strategy_features.append(strategy_feature)
                
                # Collect all dimensions
                for dim in feature_analysis.dimensions:
                    all_dimensions[dim.name] = dim.value
                    
            except Exception as e:
                logger.warning(f"Could not analyze feature {feature_info.name}: {e}")
                continue
        
        # Generate description
        description = f"Strategy extracted from {part_analysis.filename} with {len(strategy_features)} features"
        
        return StrategyFromPart(
            name=model.GetTitle(),
            description=description,
            material=part_analysis.material or "Not specified",
            features=strategy_features,
            dimensions=all_dimensions
        )
        
    except Exception as e:
        logger.error(f"Error building strategy: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


def _analyze_sketch(sketch) -> List[SketchEntity]:
    """Extract entities from a sketch."""
    entities = []
    
    try:
        # Get sketch segments
        segments = sketch.GetSketchSegments()
        if segments:
            for segment in segments:
                try:
                    seg_type = segment.GetType()
                    
                    if seg_type == 2:  # Circle
                        center = segment.GetCenterPoint2()
                        radius = segment.GetRadius()
                        entities.append(SketchEntity(
                            type="Circle",
                            data={
                                "center_x": center[0] if center else 0,
                                "center_y": center[1] if center else 0,
                                "radius": radius
                            }
                        ))
                    
                    elif seg_type == 1:  # Line
                        start = segment.GetStartPoint2()
                        end = segment.GetEndPoint2()
                        entities.append(SketchEntity(
                            type="Line",
                            data={
                                "start_x": start[0] if start else 0,
                                "start_y": start[1] if start else 0,
                                "end_x": end[0] if end else 0,
                                "end_y": end[1] if end else 0
                            }
                        ))
                    
                    elif seg_type == 3:  # Arc
                        center = segment.GetCenterPoint2()
                        radius = segment.GetRadius()
                        start_angle = segment.GetStartAngle()
                        end_angle = segment.GetEndAngle()
                        entities.append(SketchEntity(
                            type="Arc",
                            data={
                                "center_x": center[0] if center else 0,
                                "center_y": center[1] if center else 0,
                                "radius": radius,
                                "start_angle": start_angle,
                                "end_angle": end_angle
                            }
                        ))
                        
                except Exception as e:
                    logger.warning(f"Error reading sketch segment: {e}")
                    continue
    
    except Exception as e:
        logger.warning(f"Error reading sketch segments: {e}")
    
    return entities


def _get_feature_dimensions(feature) -> List[DimensionInfo]:
    """Extract dimensions from a feature."""
    dimensions = []
    
    try:
        # Get display dimensions
        display_dims = feature.GetDisplayDimensions()
        if display_dims:
            for dim in display_dims:
                try:
                    dim_name = dim.Name
                    dim_value = dim.GetSystemValue3(0, "")[0]  # Get value in meters
                    dim_type = dim.GetType()
                    
                    dim_type_name = "Linear"
                    if dim_type == 3:
                        dim_type_name = "Diameter"
                    elif dim_type == 4:
                        dim_type_name = "Radius"
                    elif dim_type == 2:
                        dim_type_name = "Angle"
                    
                    dimensions.append(DimensionInfo(
                        name=dim_name,
                        value=dim_value,
                        unit="meters",
                        type=dim_type_name
                    ))
                    
                except Exception as e:
                    logger.warning(f"Error reading dimension: {e}")
                    continue
    
    except Exception as e:
        logger.warning(f"Error getting dimensions: {e}")
    
    return dimensions
