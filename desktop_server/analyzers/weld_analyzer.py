"""
Weld Analyzer
=============
Extract and analyze weld symbols and specifications from drawings.

Phase 24.17 Implementation
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

logger = logging.getLogger("vulcan.analyzer.weld")


@dataclass
class WeldSymbol:
    """Information about a single weld symbol."""
    weld_type: str = ""  # fillet, groove, butt, etc.
    arrow_side_size: str = ""
    other_side_size: str = ""
    length: str = ""
    pitch: str = ""
    contour: str = ""  # flush, convex, concave
    finish_symbol: str = ""
    tail_reference: str = ""  # WPS reference
    all_around: bool = False
    field_weld: bool = False
    staggered: bool = False


@dataclass
class WeldAnalysisResult:
    """Complete weld analysis results."""
    total_welds: int = 0
    welds: List[WeldSymbol] = field(default_factory=list)
    total_weld_length_mm: float = 0.0
    weld_volume_estimate_mm3: float = 0.0
    wps_references: List[str] = field(default_factory=list)
    nde_requirements: List[str] = field(default_factory=list)
    issues: List[str] = field(default_factory=list)


class WeldAnalyzer:
    """
    Analyze weld symbols in SolidWorks drawings.
    Validates against AWS D1.1 requirements.
    """

    # Minimum fillet weld sizes per material thickness (AWS D1.1)
    MIN_FILLET_SIZES = {
        6.35: 3.0,   # Up to 1/4" → 1/8" min
        12.7: 5.0,   # Up to 1/2" → 3/16" min
        19.05: 6.0,  # Up to 3/4" → 1/4" min
        38.1: 8.0,   # Up to 1-1/2" → 5/16" min
        57.15: 10.0, # Up to 2-1/4" → 3/8" min
        152.4: 13.0, # Over 6" → 1/2" min
    }

    def __init__(self):
        self._sw_app = None
        self._doc = None

    def _connect(self) -> bool:
        """Connect to SolidWorks COM interface."""
        try:
            import win32com.client
            self._sw_app = win32com.client.GetActiveObject("SldWorks.Application")
            self._doc = self._sw_app.ActiveDoc
            return self._doc is not None and self._doc.GetType() == 3  # Drawing
        except Exception as e:
            logger.error(f"Failed to connect to SolidWorks: {e}")
            return False

    def _get_weld_annotations(self) -> List[Any]:
        """Get all weld symbol annotations from drawing."""
        welds = []

        if not self._connect():
            return welds

        try:
            # Get active sheet
            sheet = self._doc.GetCurrentSheet()
            if not sheet:
                return welds

            # Get all views
            views = sheet.GetViews()
            if not views:
                return welds

            for view in views:
                try:
                    # Get annotations in view
                    annots = view.GetAnnotations()
                    if annots:
                        for annot in annots:
                            if annot.GetType() == 5:  # swWeldSymbol
                                welds.append(annot)
                except Exception:
                    pass

        except Exception as e:
            logger.error(f"Error getting weld annotations: {e}")

        return welds

    def _parse_weld_symbol(self, annot: Any) -> Optional[WeldSymbol]:
        """Parse a weld symbol annotation."""
        try:
            weld = WeldSymbol()

            # Get weld symbol data
            weld_data = annot.GetWeldSymbolData()
            if not weld_data:
                return None

            # Parse weld type
            weld_type_map = {
                0: "fillet",
                1: "groove",
                2: "plug_slot",
                3: "spot",
                4: "seam",
                5: "back",
                6: "surfacing",
                7: "edge",
            }
            weld.weld_type = weld_type_map.get(weld_data.WeldType, "unknown")

            # Get sizes
            weld.arrow_side_size = str(weld_data.ArrowSideSize or "")
            weld.other_side_size = str(weld_data.OtherSideSize or "")
            weld.length = str(weld_data.WeldLength or "")
            weld.pitch = str(weld_data.Pitch or "")

            # Get symbols
            weld.all_around = weld_data.AllAroundSymbol
            weld.field_weld = weld_data.FieldWeldSymbol
            weld.staggered = weld_data.StaggeredSymbol

            # Get tail reference (WPS)
            weld.tail_reference = str(weld_data.TailText or "")
            if weld.tail_reference:
                weld.tail_reference = weld.tail_reference.strip()

            return weld

        except Exception as e:
            logger.debug(f"Error parsing weld symbol: {e}")
            return None

    def get_minimum_fillet_size(self, thickness_mm: float) -> float:
        """Get minimum fillet weld size for material thickness per AWS D1.1."""
        for max_thickness, min_size in sorted(self.MIN_FILLET_SIZES.items()):
            if thickness_mm <= max_thickness:
                return min_size
        return 13.0  # Default for thick material

    def check_weld_sizing(self, weld: WeldSymbol, base_thickness_mm: float) -> List[str]:
        """Check if weld sizing meets AWS D1.1 minimums."""
        issues = []

        if weld.weld_type == "fillet" and weld.arrow_side_size:
            try:
                # Parse size (handle fractions)
                size_str = weld.arrow_side_size.replace('"', '').strip()
                if "/" in size_str:
                    parts = size_str.split("/")
                    size_mm = (float(parts[0]) / float(parts[1])) * 25.4
                else:
                    size_mm = float(size_str) * 25.4

                min_size = self.get_minimum_fillet_size(base_thickness_mm)
                if size_mm < min_size:
                    issues.append(
                        f"Fillet weld size {weld.arrow_side_size} is below "
                        f"AWS D1.1 minimum of {min_size:.1f}mm for {base_thickness_mm:.1f}mm material"
                    )
            except ValueError:
                pass

        return issues

    def analyze(self) -> WeldAnalysisResult:
        """Analyze all welds in the active drawing."""
        result = WeldAnalysisResult()

        weld_annots = self._get_weld_annotations()

        for annot in weld_annots:
            weld = self._parse_weld_symbol(annot)
            if weld:
                result.welds.append(weld)
                result.total_welds += 1

                # Collect WPS references
                if weld.tail_reference and weld.tail_reference not in result.wps_references:
                    result.wps_references.append(weld.tail_reference)

        return result

    def to_dict(self) -> Dict[str, Any]:
        """Analyze and return results as dictionary."""
        result = self.analyze()

        return {
            "total_welds": result.total_welds,
            "welds": [
                {
                    "type": w.weld_type,
                    "arrow_side_size": w.arrow_side_size,
                    "other_side_size": w.other_side_size,
                    "length": w.length,
                    "pitch": w.pitch,
                    "all_around": w.all_around,
                    "field_weld": w.field_weld,
                    "wps_reference": w.tail_reference,
                }
                for w in result.welds
            ],
            "wps_references": result.wps_references,
            "issues": result.issues,
        }
