"""
Bend Radius Analyzer
====================
Analyze sheet metal bend radii against material-based minimums.

Phase 24.6 Implementation
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

logger = logging.getLogger("vulcan.analyzer.bend_radius")


@dataclass
class BendInfo:
    """Information about a single bend."""
    feature_name: str = ""
    radius_m: float = 0.0
    angle_deg: float = 0.0
    thickness_m: float = 0.0
    k_factor: float = 0.0
    bend_allowance_m: float = 0.0


@dataclass
class BendViolation:
    """A bend radius violation."""
    feature_name: str
    actual_radius_m: float
    minimum_radius_m: float
    material: str
    suggested_radius_m: float


@dataclass
class BendAnalysisResult:
    """Complete bend analysis results."""
    total_bends: int = 0
    bends: List[BendInfo] = field(default_factory=list)
    violations: List[BendViolation] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    k_factor_used: float = 0.0
    grain_direction_warning: bool = False


class BendRadiusAnalyzer:
    """
    Analyze sheet metal bends against material-based minimum radii.
    Provides recommendations for manufacturability.
    """

    # Default minimum bend radius multipliers (times thickness)
    DEFAULT_MIN_RADIUS = {
        "mild_steel": 1.0,
        "stainless_304": 1.5,
        "stainless_316": 1.5,
        "aluminum_6061": 1.0,
        "aluminum_5052": 0.5,
        "copper": 0.5,
        "brass": 0.5,
    }

    # K-factors by material
    DEFAULT_K_FACTORS = {
        "mild_steel": 0.44,
        "stainless_304": 0.45,
        "stainless_316": 0.45,
        "aluminum_6061": 0.40,
        "aluminum_5052": 0.40,
        "copper": 0.38,
        "brass": 0.38,
    }

    def __init__(self):
        self._sw_app = None
        self._doc = None
        self._bend_tables = self._load_bend_tables()

    def _load_bend_tables(self) -> Dict[str, Any]:
        """Load bend radius tables from data/standards."""
        tables_path = Path(__file__).parent.parent.parent / "data" / "standards" / "bend_radius_tables.json"
        if tables_path.exists():
            try:
                with open(tables_path) as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load bend tables: {e}")
        return {}

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

    def _get_sheet_metal_features(self) -> List[Any]:
        """Get all sheet metal bend features."""
        bends = []
        if not self._connect():
            return bends

        try:
            feat = self._doc.FirstFeature()
            while feat:
                feat_type = feat.GetTypeName2()
                if feat_type in ["EdgeFlange", "BaseFlangeTab", "SketchBend", "MiterFlange"]:
                    bends.append(feat)
                feat = feat.GetNextFeature()
        except Exception as e:
            logger.error(f"Error getting sheet metal features: {e}")

        return bends

    def _get_material(self) -> str:
        """Get the material of the active part."""
        if not self._doc:
            return "mild_steel"

        try:
            config = self._doc.ConfigurationManager.ActiveConfiguration.Name
            material = self._doc.GetMaterialPropertyName2(config, "")
            if material:
                material_lower = material.lower()
                if "stainless" in material_lower and "316" in material_lower:
                    return "stainless_316"
                if "stainless" in material_lower:
                    return "stainless_304"
                if "aluminum" in material_lower and "6061" in material_lower:
                    return "aluminum_6061"
                if "aluminum" in material_lower:
                    return "aluminum_5052"
                if "copper" in material_lower:
                    return "copper"
                if "brass" in material_lower:
                    return "brass"
        except Exception:
            pass

        return "mild_steel"

    def _get_thickness(self) -> float:
        """Get the sheet metal thickness."""
        if not self._doc:
            return 0.003  # Default 3mm

        try:
            feat = self._doc.FirstFeature()
            while feat:
                if feat.GetTypeName2() == "SheetMetal":
                    sm_data = feat.GetDefinition()
                    if sm_data:
                        return sm_data.Thickness
                feat = feat.GetNextFeature()
        except Exception:
            pass

        return 0.003

    def get_minimum_radius(self, material: str, thickness: float) -> float:
        """Get minimum bend radius for material and thickness."""
        # Check loaded tables first
        if material in self._bend_tables:
            table = self._bend_tables[material]
            # Find closest thickness
            for entry in table:
                if abs(entry.get("thickness", 0) - thickness) < 0.0001:
                    return entry.get("min_radius", thickness)

        # Fall back to multiplier
        multiplier = self.DEFAULT_MIN_RADIUS.get(material, 1.0)
        return thickness * multiplier

    def get_k_factor(self, material: str) -> float:
        """Get K-factor for material."""
        if material in self._bend_tables:
            table = self._bend_tables[material]
            if table and "k_factor" in table[0]:
                return table[0]["k_factor"]

        return self.DEFAULT_K_FACTORS.get(material, 0.44)

    def analyze(self) -> BendAnalysisResult:
        """Analyze all bends in the active sheet metal part."""
        result = BendAnalysisResult()

        if not self._connect():
            return result

        material = self._get_material()
        thickness = self._get_thickness()
        min_radius = self.get_minimum_radius(material, thickness)
        result.k_factor_used = self.get_k_factor(material)

        bend_features = self._get_sheet_metal_features()

        for feat in bend_features:
            try:
                bend_info = BendInfo()
                bend_info.feature_name = feat.Name
                bend_info.thickness_m = thickness
                bend_info.k_factor = result.k_factor_used

                # Get bend radius from definition
                definition = feat.GetDefinition()
                if definition and hasattr(definition, "BendRadius"):
                    bend_info.radius_m = definition.BendRadius
                if definition and hasattr(definition, "Angle"):
                    bend_info.angle_deg = definition.Angle

                result.bends.append(bend_info)
                result.total_bends += 1

                # Check against minimum
                if bend_info.radius_m < min_radius:
                    result.violations.append(BendViolation(
                        feature_name=bend_info.feature_name,
                        actual_radius_m=bend_info.radius_m,
                        minimum_radius_m=min_radius,
                        material=material,
                        suggested_radius_m=min_radius,
                    ))
            except Exception as e:
                logger.debug(f"Could not analyze bend {feat.Name}: {e}")

        # Add grain direction warning if many bends
        if result.total_bends > 4:
            result.grain_direction_warning = True
            result.warnings.append(
                "Multiple bends detected. Verify grain direction for optimal strength."
            )

        return result

    def to_dict(self) -> Dict[str, Any]:
        """Analyze and return results as dictionary."""
        result = self.analyze()
        return {
            "total_bends": result.total_bends,
            "k_factor_used": result.k_factor_used,
            "grain_direction_warning": result.grain_direction_warning,
            "bends": [
                {
                    "name": b.feature_name,
                    "radius_m": b.radius_m,
                    "angle_deg": b.angle_deg,
                    "thickness_m": b.thickness_m,
                }
                for b in result.bends
            ],
            "violations": [
                {
                    "name": v.feature_name,
                    "actual_radius_m": v.actual_radius_m,
                    "minimum_radius_m": v.minimum_radius_m,
                    "material": v.material,
                    "suggested_radius_m": v.suggested_radius_m,
                }
                for v in result.violations
            ],
            "warnings": result.warnings,
        }
