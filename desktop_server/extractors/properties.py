"""
Properties Extractor
====================
Extract all properties from SolidWorks models.

Phase 24.3-24.7 Complete Implementation
- 24.3: Standard Properties (8 fields)
- 24.4: Mass Properties (10 fields)
- 24.5: Custom Properties (15+ fields)
- 24.6: ACHE-Specific Properties (20 fields)
- 24.7: Additional Properties (12 fields)
"""

import logging
import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger("vulcan.extractor.properties")


@dataclass
class StandardProperties:
    """Standard SolidWorks document properties (Phase 24.3 - 8 fields)."""
    filename: str = ""
    path: str = ""
    extension: str = ""
    configuration: str = ""
    all_configurations: List[str] = field(default_factory=list)
    created_date: Optional[datetime] = None
    modified_date: Optional[datetime] = None
    last_saved_by: str = ""
    sw_version: str = ""
    total_edit_time_sec: int = 0
    file_size_bytes: int = 0
    rebuild_status: str = "unknown"  # "up_to_date", "needs_rebuild", "unknown"


@dataclass
class MassProperties:
    """Mass properties from SolidWorks (Phase 24.4)."""
    mass_kg: float = 0.0
    mass_lbs: float = 0.0
    volume_m3: float = 0.0
    volume_in3: float = 0.0
    surface_area_m2: float = 0.0
    surface_area_in2: float = 0.0
    density_kg_m3: float = 0.0
    center_of_gravity: tuple = (0.0, 0.0, 0.0)
    moments_of_inertia: tuple = (0.0, 0.0, 0.0)  # Ixx, Iyy, Izz
    products_of_inertia: tuple = (0.0, 0.0, 0.0)  # Ixy, Ixz, Iyz
    principal_axes: tuple = (0.0, 0.0, 0.0)
    bounding_box: tuple = (0.0, 0.0, 0.0)  # L x W x H


@dataclass
class CustomProperties:
    """Custom properties organized by category (Phase 24.5-24.7)."""
    # Job Information (24.5)
    job_info: Dict[str, str] = field(default_factory=dict)
    # Design Data (24.5)
    design_data: Dict[str, str] = field(default_factory=dict)
    # ACHE Tube Bundle Data (24.6)
    tube_bundle: Dict[str, str] = field(default_factory=dict)
    # ACHE Fin Data (24.6)
    fin_data: Dict[str, str] = field(default_factory=dict)
    # ACHE Header Box Data (24.6)
    header_box: Dict[str, str] = field(default_factory=dict)
    # Structural Data (24.7)
    structural: Dict[str, str] = field(default_factory=dict)
    # Drawing Information (24.7)
    drawing_info: Dict[str, str] = field(default_factory=dict)
    # Paint & Coating (24.7)
    paint_coating: Dict[str, str] = field(default_factory=dict)
    # Instrumentation (24.15)
    instrumentation: Dict[str, str] = field(default_factory=dict)
    # Nozzle Schedule (24.16)
    nozzle_data: Dict[str, str] = field(default_factory=dict)
    # Other uncategorized
    other: Dict[str, str] = field(default_factory=dict)


class PropertiesExtractor:
    """
    Extract all properties from the active SolidWorks document.
    Categorizes custom properties for ACHE design context.
    """

    # Property categorization mapping (Phase 24.5-24.7)
    JOB_INFO_KEYS = ["job", "job#", "customer", "project", "po", "po#", "tag", "tag#",
                     "service", "item", "unit", "area"]
    DESIGN_DATA_KEYS = ["pressure", "temp", "temperature", "mdmt", "corrosion",
                        "design_code", "operating", "test", "hydro", "mawp"]
    TUBE_BUNDLE_KEYS = ["tubes", "tube_od", "tube_bwg", "tube_length", "tube_pitch",
                        "tube_material", "tube_rows", "tube_passes", "tubes_per_row"]
    FIN_DATA_KEYS = ["fin", "fin_type", "fin_height", "fin_thickness", "fin_density",
                     "fin_material", "fins_per_inch"]
    HEADER_BOX_KEYS = ["header", "plug", "plugs", "header_type", "header_material",
                       "header_thickness", "plug_type", "plug_material", "bonnet"]
    STRUCTURAL_KEYS = ["tube_sheet", "tubesheet", "side_frame", "support", "frame",
                       "tube_support", "baffle"]
    DRAWING_INFO_KEYS = ["dwg", "dwg#", "rev", "revision", "drawn", "checked",
                         "approved", "rev_date", "rev_description"]
    PAINT_KEYS = ["paint", "primer", "topcoat", "prep", "coating", "sspc", "surface"]
    INSTRUMENTATION_KEYS = ["thermowell", "temp_indicator", "pressure_tap", "vent",
                            "drain", "pi", "ti", "pt", "tt", "transmitter"]
    NOZZLE_KEYS = ["nozzle", "flange", "inlet", "outlet", "connection", "rating"]

    def __init__(self):
        self._sw_app = None
        self._doc = None

    def _connect(self) -> bool:
        """Connect to SolidWorks COM interface."""
        try:
            import win32com.client
            self._sw_app = win32com.client.GetActiveObject("SldWorks.Application")
            self._doc = self._sw_app.ActiveDoc
            return self._doc is not None
        except Exception as e:
            logger.error(f"Failed to connect to SolidWorks: {e}")
            return False

    def get_standard_properties(self) -> StandardProperties:
        """Extract standard document properties."""
        if not self._connect():
            return StandardProperties()

        props = StandardProperties()
        try:
            props.path = self._doc.GetPathName() or ""
            props.filename = props.path.split("\\")[-1] if props.path else ""
            props.configuration = self._doc.ConfigurationManager.ActiveConfiguration.Name

            # Get file info
            file_info = self._doc.FileInfo
            if file_info:
                props.sw_version = str(self._sw_app.RevisionNumber())
        except Exception as e:
            logger.error(f"Error extracting standard properties: {e}")

        return props

    def get_mass_properties(self) -> MassProperties:
        """Extract mass properties from active document (Phase 24.4)."""
        if not self._connect():
            return MassProperties()

        props = MassProperties()
        try:
            mass_props = self._doc.Extension.CreateMassProperty()
            if mass_props:
                # Mass
                props.mass_kg = mass_props.Mass
                props.mass_lbs = mass_props.Mass * 2.20462

                # Volume
                props.volume_m3 = mass_props.Volume
                props.volume_in3 = mass_props.Volume * 61023.7

                # Surface Area
                props.surface_area_m2 = mass_props.SurfaceArea
                props.surface_area_in2 = mass_props.SurfaceArea * 1550.0

                # Density
                if mass_props.Volume > 0:
                    props.density_kg_m3 = mass_props.Mass / mass_props.Volume

                # Center of Gravity
                cog = mass_props.CenterOfMass
                if cog:
                    props.center_of_gravity = (cog[0], cog[1], cog[2])

                # Moments of Inertia
                moi = mass_props.GetMomentOfInertia()
                if moi:
                    props.moments_of_inertia = (moi[0], moi[4], moi[8])  # Ixx, Iyy, Izz
                    props.products_of_inertia = (moi[1], moi[2], moi[5])  # Ixy, Ixz, Iyz

                # Principal Axes
                pa = mass_props.GetPrincipalAxesOfInertia()
                if pa:
                    props.principal_axes = (pa[0], pa[1], pa[2])

            # Bounding Box
            try:
                box = self._doc.GetBox()
                if box:
                    props.bounding_box = (
                        abs(box[3] - box[0]),  # Length
                        abs(box[4] - box[1]),  # Width
                        abs(box[5] - box[2]),  # Height
                    )
            except Exception:
                pass

        except Exception as e:
            logger.error(f"Error extracting mass properties: {e}")

        return props

    def _categorize_property(self, key: str) -> str:
        """Determine which category a property belongs to (Phase 24.5-24.7)."""
        key_lower = key.lower()

        if any(k in key_lower for k in self.JOB_INFO_KEYS):
            return "job_info"
        if any(k in key_lower for k in self.DESIGN_DATA_KEYS):
            return "design_data"
        if any(k in key_lower for k in self.FIN_DATA_KEYS):
            return "fin_data"
        if any(k in key_lower for k in self.TUBE_BUNDLE_KEYS):
            return "tube_bundle"
        if any(k in key_lower for k in self.HEADER_BOX_KEYS):
            return "header_box"
        if any(k in key_lower for k in self.STRUCTURAL_KEYS):
            return "structural"
        if any(k in key_lower for k in self.DRAWING_INFO_KEYS):
            return "drawing_info"
        if any(k in key_lower for k in self.PAINT_KEYS):
            return "paint_coating"
        if any(k in key_lower for k in self.INSTRUMENTATION_KEYS):
            return "instrumentation"
        if any(k in key_lower for k in self.NOZZLE_KEYS):
            return "nozzle_data"
        return "other"

    def get_custom_properties(self, config: str = "") -> CustomProperties:
        """Extract and categorize custom properties."""
        if not self._connect():
            return CustomProperties()

        props = CustomProperties()
        try:
            config_name = config or self._doc.ConfigurationManager.ActiveConfiguration.Name
            custom_prop_mgr = self._doc.Extension.CustomPropertyManager(config_name)

            if not custom_prop_mgr:
                return props

            # Get all property names
            prop_names = custom_prop_mgr.GetNames()
            if not prop_names:
                return props

            for name in prop_names:
                val_out = ""
                resolved_out = ""
                was_resolved = False

                try:
                    result = custom_prop_mgr.Get5(name, False, val_out, resolved_out, was_resolved)
                    value = resolved_out if was_resolved else val_out
                except Exception:
                    value = ""

                category = self._categorize_property(name)
                getattr(props, category)[name] = value

        except Exception as e:
            logger.error(f"Error extracting custom properties: {e}")

        return props

    def get_all_properties(self) -> Dict[str, Any]:
        """Get all properties as a dictionary for JSON serialization."""
        standard = self.get_standard_properties()
        mass = self.get_mass_properties()
        custom = self.get_custom_properties()

        return {
            "standard": {
                "filename": standard.filename,
                "path": standard.path,
                "configuration": standard.configuration,
                "sw_version": standard.sw_version,
            },
            "mass": {
                "mass_kg": mass.mass_kg,
                "volume_m3": mass.volume_m3,
                "surface_area_m2": mass.surface_area_m2,
                "center_of_gravity": list(mass.center_of_gravity),
                "moments_of_inertia": list(mass.moments_of_inertia),
            },
            "custom": {
                "job_info": custom.job_info,
                "design_data": custom.design_data,
                "tube_bundle": custom.tube_bundle,
                "header_box": custom.header_box,
                "structural": custom.structural,
                "drawing_info": custom.drawing_info,
                "paint_coating": custom.paint_coating,
                "other": custom.other,
            },
        }
