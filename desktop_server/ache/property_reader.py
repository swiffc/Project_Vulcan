"""
ACHE Property Reader
Phase 24.2 & 24.3 - Property extraction from SolidWorks models

Extracts comprehensive properties from ACHE models including:
- Custom properties
- Mass properties
- Bounding box
- Configuration data
- Component hierarchy
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

logger = logging.getLogger("vulcan.ache.property_reader")


@dataclass
class MassProperties:
    """Mass properties of a model."""
    mass_kg: float = 0.0
    volume_m3: float = 0.0
    surface_area_m2: float = 0.0
    center_of_mass: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    moments_of_inertia: Tuple[float, float, float] = (0.0, 0.0, 0.0)


@dataclass
class BoundingBox:
    """Bounding box dimensions."""
    length_mm: float = 0.0
    width_mm: float = 0.0
    height_mm: float = 0.0
    min_point: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    max_point: Tuple[float, float, float] = (0.0, 0.0, 0.0)


@dataclass
class ComponentInfo:
    """Information about an assembly component."""
    name: str
    part_number: str = ""
    quantity: int = 1
    is_suppressed: bool = False
    configuration: str = ""
    filepath: str = ""


@dataclass
class ModelProperties:
    """Complete model properties."""
    filepath: str
    filename: str
    model_type: str  # part, assembly, drawing
    custom_properties: Dict[str, Any] = field(default_factory=dict)
    mass_properties: Optional[MassProperties] = None
    bounding_box: Optional[BoundingBox] = None
    configurations: List[str] = field(default_factory=list)
    active_configuration: str = ""
    components: List[ComponentInfo] = field(default_factory=list)
    extracted_at: datetime = field(default_factory=datetime.now)


class ACHEPropertyReader:
    """
    Reads comprehensive properties from SolidWorks ACHE models.

    Implements Phase 24.2 & 24.3: Property extraction

    Capabilities:
    - Custom property extraction
    - Mass properties (weight, CG, moments)
    - Bounding box dimensions
    - Configuration management
    - Assembly component hierarchy
    """

    def __init__(self):
        """Initialize the property reader."""
        self._sw_app = None

    def connect(self) -> bool:
        """Connect to SolidWorks."""
        try:
            import win32com.client
            self._sw_app = win32com.client.GetActiveObject("SldWorks.Application")
            logger.info("Property reader connected to SolidWorks")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to SolidWorks: {e}")
            return False

    def read_properties(self, doc=None) -> Optional[ModelProperties]:
        """
        Read all properties from active or specified document.

        Args:
            doc: SolidWorks document (optional, uses active if None)

        Returns:
            ModelProperties or None if failed
        """
        try:
            if doc is None:
                if not self._sw_app:
                    if not self.connect():
                        return None
                doc = self._sw_app.ActiveDoc

            if doc is None:
                logger.warning("No active document")
                return None

            filepath = doc.GetPathName()
            import os
            filename = os.path.basename(filepath)

            # Get model type
            doc_type = doc.GetType()
            type_map = {1: "part", 2: "assembly", 3: "drawing"}
            model_type = type_map.get(doc_type, "unknown")

            # Build properties
            props = ModelProperties(
                filepath=filepath,
                filename=filename,
                model_type=model_type,
            )

            # Extract all property types
            props.custom_properties = self._get_custom_properties(doc)
            props.mass_properties = self._get_mass_properties(doc)
            props.bounding_box = self._get_bounding_box(doc)
            props.configurations, props.active_configuration = self._get_configurations(doc)

            if model_type == "assembly":
                props.components = self._get_components(doc)

            logger.info(f"Read properties from: {filename}")
            return props

        except Exception as e:
            logger.error(f"Failed to read properties: {e}")
            return None

    def _get_custom_properties(self, doc) -> Dict[str, Any]:
        """Extract custom properties from document."""
        props = {}
        try:
            ext = doc.Extension
            prop_mgr = ext.CustomPropertyManager("")

            names = prop_mgr.GetNames()
            if names:
                for name in names:
                    try:
                        # Get6 returns: (retval, ValOut, ResolvedValOut, WasResolved, LinkToProperty)
                        result = prop_mgr.Get6(name, False, "", "", False, False)
                        if result and len(result) > 2:
                            # Use resolved value if available
                            props[name] = result[2] if result[2] else result[1]
                        elif result:
                            props[name] = result[1] if len(result) > 1 else str(result)
                    except Exception as e:
                        logger.debug(f"Could not get property '{name}': {e}")

        except Exception as e:
            logger.debug(f"Custom property extraction error: {e}")

        return props

    def _get_mass_properties(self, doc) -> Optional[MassProperties]:
        """Get mass properties from document."""
        try:
            ext = doc.Extension
            mass_prop = ext.CreateMassProperty2()

            if mass_prop is None:
                return None

            # Get mass
            mass = mass_prop.Mass

            # Get center of mass
            com = mass_prop.CenterOfMass
            if com:
                center = (com[0], com[1], com[2])
            else:
                center = (0.0, 0.0, 0.0)

            # Get moments of inertia
            moi = mass_prop.GetMomentOfInertia(0)  # At origin
            if moi:
                moments = (moi[0], moi[4], moi[8])  # Ixx, Iyy, Izz
            else:
                moments = (0.0, 0.0, 0.0)

            return MassProperties(
                mass_kg=mass,
                volume_m3=mass_prop.Volume if hasattr(mass_prop, 'Volume') else 0.0,
                surface_area_m2=mass_prop.SurfaceArea if hasattr(mass_prop, 'SurfaceArea') else 0.0,
                center_of_mass=center,
                moments_of_inertia=moments,
            )

        except Exception as e:
            logger.debug(f"Mass properties error: {e}")
            return None

    def _get_bounding_box(self, doc) -> Optional[BoundingBox]:
        """Get bounding box dimensions."""
        try:
            # Get bounding box from model
            box = doc.GetBoundingBox()
            if box is None:
                # Try visible component box
                box = doc.Extension.GetVisibleBox() if hasattr(doc.Extension, 'GetVisibleBox') else None

            if box is None:
                return None

            # Box format: [Xmin, Ymin, Zmin, Xmax, Ymax, Zmax] in meters
            min_pt = (box[0] * 1000, box[1] * 1000, box[2] * 1000)  # Convert to mm
            max_pt = (box[3] * 1000, box[4] * 1000, box[5] * 1000)

            return BoundingBox(
                length_mm=abs(max_pt[0] - min_pt[0]),
                width_mm=abs(max_pt[1] - min_pt[1]),
                height_mm=abs(max_pt[2] - min_pt[2]),
                min_point=min_pt,
                max_point=max_pt,
            )

        except Exception as e:
            logger.debug(f"Bounding box error: {e}")
            return None

    def _get_configurations(self, doc) -> Tuple[List[str], str]:
        """Get configuration names and active configuration."""
        configs = []
        active = ""

        try:
            config_mgr = doc.ConfigurationManager
            if config_mgr:
                active = config_mgr.ActiveConfiguration.Name

                # Get all configuration names
                config_names = doc.GetConfigurationNames()
                if config_names:
                    configs = list(config_names)

        except Exception as e:
            logger.debug(f"Configuration error: {e}")

        return configs, active

    def _get_components(self, doc) -> List[ComponentInfo]:
        """Get assembly component information."""
        components = []

        try:
            if doc.GetType() != 2:  # Not an assembly
                return components

            # Get root component
            config = doc.ConfigurationManager.ActiveConfiguration
            root_comp = config.GetRootComponent3(True)

            if root_comp:
                self._traverse_components(root_comp, components)

        except Exception as e:
            logger.debug(f"Component extraction error: {e}")

        return components

    def _traverse_components(
        self,
        component,
        result: List[ComponentInfo],
        depth: int = 0
    ) -> None:
        """Recursively traverse component tree."""
        try:
            children = component.GetChildren()
            if not children:
                return

            for child in children:
                try:
                    name = child.Name2
                    is_suppressed = child.IsSuppressed()

                    # Get referenced document
                    ref_doc = child.GetModelDoc2()
                    part_number = ""
                    filepath = ""

                    if ref_doc:
                        filepath = ref_doc.GetPathName()
                        # Try to get part number from custom properties
                        try:
                            ext = ref_doc.Extension
                            prop_mgr = ext.CustomPropertyManager("")
                            result = prop_mgr.Get6("Part Number", False, "", "", False, False)
                            if result and len(result) > 1:
                                part_number = result[1] or result[2] if len(result) > 2 else ""
                        except:
                            pass

                    info = ComponentInfo(
                        name=name,
                        part_number=part_number,
                        quantity=1,  # Will aggregate later
                        is_suppressed=is_suppressed,
                        configuration=child.ReferencedConfiguration if hasattr(child, 'ReferencedConfiguration') else "",
                        filepath=filepath,
                    )
                    result.append(info)

                    # Recurse
                    if depth < 5:  # Limit depth
                        self._traverse_components(child, result, depth + 1)

                except Exception as e:
                    logger.debug(f"Error processing component: {e}")

        except Exception as e:
            logger.debug(f"Traverse error: {e}")

    def to_dict(self, props: ModelProperties) -> Dict[str, Any]:
        """Convert ModelProperties to dictionary for API response."""
        return {
            "filepath": props.filepath,
            "filename": props.filename,
            "model_type": props.model_type,
            "custom_properties": props.custom_properties,
            "mass_properties": {
                "mass_kg": props.mass_properties.mass_kg,
                "volume_m3": props.mass_properties.volume_m3,
                "surface_area_m2": props.mass_properties.surface_area_m2,
                "center_of_mass": props.mass_properties.center_of_mass,
                "moments_of_inertia": props.mass_properties.moments_of_inertia,
            } if props.mass_properties else None,
            "bounding_box": {
                "length_mm": props.bounding_box.length_mm,
                "width_mm": props.bounding_box.width_mm,
                "height_mm": props.bounding_box.height_mm,
                "min_point": props.bounding_box.min_point,
                "max_point": props.bounding_box.max_point,
            } if props.bounding_box else None,
            "configurations": props.configurations,
            "active_configuration": props.active_configuration,
            "components": [
                {
                    "name": c.name,
                    "part_number": c.part_number,
                    "quantity": c.quantity,
                    "is_suppressed": c.is_suppressed,
                    "configuration": c.configuration,
                }
                for c in props.components
            ],
            "extracted_at": props.extracted_at.isoformat(),
        }
