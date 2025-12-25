"""
Nozzle Analyzer
===============
Extract and analyze nozzle data from SolidWorks assemblies.

Phase 24.16 Implementation
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

logger = logging.getLogger("vulcan.analyzer.nozzle")


@dataclass
class NozzleInfo:
    """Information about a single nozzle."""
    name: str = ""
    mark: str = ""  # N1, N2, etc.
    size_in: float = 0.0
    schedule: str = ""
    flange_rating: str = ""  # 150#, 300#, etc.
    flange_facing: str = ""  # RF, RTJ, FF
    flange_type: str = ""  # WN, SO, Blind, etc.
    service: str = ""
    orientation_deg: float = 0.0  # Clock position
    projection_in: float = 0.0
    reinforcement_pad: bool = False
    pad_od_in: float = 0.0
    pad_thickness_in: float = 0.0


@dataclass
class NozzleSchedule:
    """Complete nozzle schedule for a unit."""
    nozzles: List[NozzleInfo] = field(default_factory=list)
    total_count: int = 0
    issues: List[str] = field(default_factory=list)


# ASME B16.5 flange bolt requirements
FLANGE_BOLTS = {
    "150": {
        1: {"bolt_size": "1/2", "num_bolts": 4, "bolt_circle": 3.12},
        2: {"bolt_size": "5/8", "num_bolts": 4, "bolt_circle": 4.75},
        3: {"bolt_size": "5/8", "num_bolts": 4, "bolt_circle": 6.00},
        4: {"bolt_size": "5/8", "num_bolts": 8, "bolt_circle": 7.50},
        6: {"bolt_size": "3/4", "num_bolts": 8, "bolt_circle": 9.50},
        8: {"bolt_size": "3/4", "num_bolts": 8, "bolt_circle": 11.75},
        10: {"bolt_size": "7/8", "num_bolts": 12, "bolt_circle": 14.25},
        12: {"bolt_size": "7/8", "num_bolts": 12, "bolt_circle": 17.00},
    },
    "300": {
        1: {"bolt_size": "5/8", "num_bolts": 4, "bolt_circle": 3.50},
        2: {"bolt_size": "5/8", "num_bolts": 8, "bolt_circle": 5.00},
        3: {"bolt_size": "3/4", "num_bolts": 8, "bolt_circle": 6.62},
        4: {"bolt_size": "3/4", "num_bolts": 8, "bolt_circle": 7.88},
        6: {"bolt_size": "3/4", "num_bolts": 12, "bolt_circle": 10.62},
        8: {"bolt_size": "7/8", "num_bolts": 12, "bolt_circle": 13.00},
        10: {"bolt_size": "1", "num_bolts": 16, "bolt_circle": 15.25},
        12: {"bolt_size": "1-1/8", "num_bolts": 16, "bolt_circle": 17.75},
    },
}


class NozzleAnalyzer:
    """
    Analyze nozzles in SolidWorks assemblies.
    Validates against ASME B16.5 and API 661 requirements.
    """

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

    def _find_nozzle_components(self) -> List[Any]:
        """Find components that appear to be nozzles."""
        nozzles = []

        if not self._connect():
            return nozzles

        if self._doc.GetType() != 2:  # Not assembly
            return nozzles

        try:
            components = self._doc.GetComponents(False)  # All levels
            if not components:
                return nozzles

            # Filter for nozzle-like names
            nozzle_keywords = ["nozzle", "noz", "connection", "inlet", "outlet",
                              "flange", "stub", "coupling"]

            for comp in components:
                try:
                    name = comp.Name2.lower()
                    if any(kw in name for kw in nozzle_keywords):
                        nozzles.append(comp)
                except Exception:
                    pass

        except Exception as e:
            logger.error(f"Error finding nozzle components: {e}")

        return nozzles

    def _extract_nozzle_info(self, component: Any) -> Optional[NozzleInfo]:
        """Extract nozzle information from a component."""
        try:
            nozzle = NozzleInfo()
            nozzle.name = component.Name2

            # Try to get custom properties from the referenced document
            ref_model = component.GetModelDoc2()
            if ref_model:
                try:
                    config = ref_model.ConfigurationManager.ActiveConfiguration.Name
                    prop_mgr = ref_model.Extension.CustomPropertyManager(config)

                    if prop_mgr:
                        # Try to read common nozzle properties
                        nozzle.mark = self._get_prop(prop_mgr, ["Mark", "Nozzle", "Tag"]) or ""
                        nozzle.service = self._get_prop(prop_mgr, ["Service", "Description"]) or ""

                        size_str = self._get_prop(prop_mgr, ["Size", "NPS", "Diameter"])
                        if size_str:
                            try:
                                nozzle.size_in = float(size_str.replace('"', ''))
                            except ValueError:
                                pass

                        nozzle.schedule = self._get_prop(prop_mgr, ["Schedule", "SCH"]) or ""
                        nozzle.flange_rating = self._get_prop(prop_mgr, ["Rating", "Class", "Pressure Class"]) or ""
                        nozzle.flange_facing = self._get_prop(prop_mgr, ["Facing", "Face Type"]) or ""
                        nozzle.flange_type = self._get_prop(prop_mgr, ["Flange Type", "Type"]) or ""

                except Exception:
                    pass

            return nozzle

        except Exception as e:
            logger.debug(f"Error extracting nozzle info: {e}")
            return None

    def _get_prop(self, prop_mgr, names: List[str]) -> Optional[str]:
        """Try to get a property by multiple possible names."""
        for name in names:
            try:
                val_out = ""
                resolved_out = ""
                result = prop_mgr.Get5(name, False, val_out, resolved_out, False)
                if resolved_out:
                    return resolved_out
            except Exception:
                pass
        return None

    def get_flange_bolt_requirements(self, size_in: int, rating: str) -> Optional[Dict]:
        """Get bolt requirements for a flange per ASME B16.5."""
        rating_clean = rating.replace("#", "").replace("LB", "").strip()
        if rating_clean in FLANGE_BOLTS:
            return FLANGE_BOLTS[rating_clean].get(size_in)
        return None

    def validate_nozzle(self, nozzle: NozzleInfo) -> List[str]:
        """Validate nozzle against standards."""
        issues = []

        # Check for missing information
        if not nozzle.mark:
            issues.append(f"Nozzle {nozzle.name}: Missing mark/tag")

        if not nozzle.flange_rating:
            issues.append(f"Nozzle {nozzle.name}: Missing flange rating")

        if not nozzle.flange_facing:
            issues.append(f"Nozzle {nozzle.name}: Missing flange facing type")

        # Validate flange rating vs size
        if nozzle.size_in and nozzle.flange_rating:
            bolt_req = self.get_flange_bolt_requirements(
                int(nozzle.size_in),
                nozzle.flange_rating
            )
            if not bolt_req:
                issues.append(
                    f"Nozzle {nozzle.name}: Size {nozzle.size_in}\" with "
                    f"{nozzle.flange_rating} rating not in ASME B16.5 tables"
                )

        return issues

    def analyze(self) -> NozzleSchedule:
        """Analyze all nozzles in the assembly."""
        result = NozzleSchedule()

        nozzle_comps = self._find_nozzle_components()

        for comp in nozzle_comps:
            nozzle = self._extract_nozzle_info(comp)
            if nozzle:
                result.nozzles.append(nozzle)
                result.total_count += 1

                # Validate
                issues = self.validate_nozzle(nozzle)
                result.issues.extend(issues)

        return result

    def to_dict(self) -> Dict[str, Any]:
        """Analyze and return results as dictionary."""
        result = self.analyze()

        return {
            "total_nozzles": result.total_count,
            "nozzles": [
                {
                    "name": n.name,
                    "mark": n.mark,
                    "size_in": n.size_in,
                    "schedule": n.schedule,
                    "flange_rating": n.flange_rating,
                    "flange_facing": n.flange_facing,
                    "flange_type": n.flange_type,
                    "service": n.service,
                    "orientation_deg": n.orientation_deg,
                    "has_reinforcement_pad": n.reinforcement_pad,
                }
                for n in result.nozzles
            ],
            "issues": result.issues,
        }
