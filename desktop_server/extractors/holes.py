"""
Hole Pattern Extractor
======================
Extract and analyze hole patterns for tube sheets and header boxes.

Phase 24.7 Implementation
"""

import logging
import math
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

logger = logging.getLogger("vulcan.extractor.holes")


@dataclass
class HoleInfo:
    """Information about a single hole."""
    feature_name: str = ""
    diameter_m: float = 0.0
    depth_m: float = 0.0
    center_x: float = 0.0
    center_y: float = 0.0
    center_z: float = 0.0
    hole_type: str = "simple"  # simple, counterbore, countersink, tapped


@dataclass
class HolePattern:
    """A pattern of holes (linear, circular, or irregular)."""
    pattern_type: str = "irregular"  # linear, circular, irregular
    holes: List[HoleInfo] = field(default_factory=list)
    pitch_x: Optional[float] = None
    pitch_y: Optional[float] = None
    bolt_circle_diameter: Optional[float] = None
    count: int = 0


@dataclass
class HoleAnalysisResult:
    """Complete hole analysis for a document."""
    total_holes: int = 0
    patterns: List[HolePattern] = field(default_factory=list)
    edge_distance_violations: List[Dict] = field(default_factory=list)
    ligament_violations: List[Dict] = field(default_factory=list)
    alignment_issues: List[Dict] = field(default_factory=list)


class HolePatternExtractor:
    """
    Extract hole patterns from SolidWorks parts.
    Analyzes for ACHE tube sheet and header box requirements.
    """

    # TEMA minimum edge distance factor (times hole diameter)
    MIN_EDGE_DISTANCE_FACTOR = 1.5

    # TEMA minimum ligament factor (between holes)
    MIN_LIGAMENT_FACTOR = 0.25  # Of pitch

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

    def _get_hole_features(self) -> List[Any]:
        """Get all hole wizard features from the model."""
        holes = []
        if not self._connect():
            return holes

        try:
            feat = self._doc.FirstFeature()
            while feat:
                feat_type = feat.GetTypeName2()
                if feat_type in ["HoleWzd", "Hole", "HoleWzdSimple"]:
                    holes.append(feat)
                feat = feat.GetNextFeature()
        except Exception as e:
            logger.error(f"Error getting hole features: {e}")

        return holes

    def _extract_hole_info(self, feat: Any) -> Optional[HoleInfo]:
        """Extract detailed info from a hole feature."""
        try:
            hole = HoleInfo()
            hole.feature_name = feat.Name

            # Get hole wizard data if available
            hw_data = feat.GetDefinition()
            if hw_data:
                hole.diameter_m = hw_data.Diameter
                hole.depth_m = hw_data.Depth if hasattr(hw_data, "Depth") else 0

            return hole
        except Exception as e:
            logger.debug(f"Could not extract hole info: {e}")
            return None

    def _detect_pattern_type(self, holes: List[HoleInfo]) -> str:
        """Detect if holes form a linear, circular, or irregular pattern."""
        if len(holes) < 2:
            return "irregular"

        # Check for circular pattern (bolt circle)
        centers = [(h.center_x, h.center_y) for h in holes]
        if self._is_circular_pattern(centers):
            return "circular"

        # Check for linear pattern
        if self._is_linear_pattern(centers):
            return "linear"

        return "irregular"

    def _is_circular_pattern(self, centers: List[tuple], tolerance: float = 0.001) -> bool:
        """Check if points form a circular pattern."""
        if len(centers) < 3:
            return False

        # Calculate centroid
        cx = sum(p[0] for p in centers) / len(centers)
        cy = sum(p[1] for p in centers) / len(centers)

        # Check if all points are equidistant from centroid
        distances = [math.sqrt((p[0] - cx) ** 2 + (p[1] - cy) ** 2) for p in centers]
        avg_dist = sum(distances) / len(distances)

        return all(abs(d - avg_dist) < tolerance for d in distances)

    def _is_linear_pattern(self, centers: List[tuple], tolerance: float = 0.001) -> bool:
        """Check if points form a linear pattern."""
        if len(centers) < 2:
            return True

        # Check collinearity
        if len(centers) == 2:
            return True

        x1, y1 = centers[0]
        x2, y2 = centers[1]

        for x, y in centers[2:]:
            # Cross product should be near zero for collinear points
            cross = abs((y2 - y1) * (x - x1) - (x2 - x1) * (y - y1))
            if cross > tolerance:
                return False

        return True

    def check_edge_distances(
        self, holes: List[HoleInfo], part_bounds: tuple
    ) -> List[Dict]:
        """Check if holes meet minimum edge distance requirements."""
        violations = []
        min_x, min_y, max_x, max_y = part_bounds

        for hole in holes:
            min_edge_dist = hole.diameter_m * self.MIN_EDGE_DISTANCE_FACTOR

            # Check distance to each edge
            edge_dists = [
                ("left", hole.center_x - min_x),
                ("right", max_x - hole.center_x),
                ("bottom", hole.center_y - min_y),
                ("top", max_y - hole.center_y),
            ]

            for edge_name, dist in edge_dists:
                if dist < min_edge_dist:
                    violations.append({
                        "hole": hole.feature_name,
                        "edge": edge_name,
                        "actual_distance": dist,
                        "required_distance": min_edge_dist,
                        "shortage": min_edge_dist - dist,
                    })

        return violations

    def check_ligaments(self, holes: List[HoleInfo]) -> List[Dict]:
        """Check ligament (metal between holes) meets TEMA requirements."""
        violations = []

        for i, h1 in enumerate(holes):
            for h2 in holes[i + 1:]:
                # Distance between centers
                dist = math.sqrt(
                    (h2.center_x - h1.center_x) ** 2 +
                    (h2.center_y - h1.center_y) ** 2
                )

                # Ligament = distance - both radii
                ligament = dist - (h1.diameter_m / 2) - (h2.diameter_m / 2)

                # Minimum ligament based on larger hole
                min_ligament = max(h1.diameter_m, h2.diameter_m) * self.MIN_LIGAMENT_FACTOR

                if ligament < min_ligament:
                    violations.append({
                        "hole1": h1.feature_name,
                        "hole2": h2.feature_name,
                        "actual_ligament": ligament,
                        "required_ligament": min_ligament,
                        "shortage": min_ligament - ligament,
                    })

        return violations

    def analyze(self) -> HoleAnalysisResult:
        """Perform complete hole analysis on active document."""
        result = HoleAnalysisResult()

        hole_features = self._get_hole_features()
        holes = []

        for feat in hole_features:
            hole_info = self._extract_hole_info(feat)
            if hole_info:
                holes.append(hole_info)

        result.total_holes = len(holes)

        if holes:
            pattern = HolePattern()
            pattern.holes = holes
            pattern.count = len(holes)
            pattern.pattern_type = self._detect_pattern_type(holes)
            result.patterns.append(pattern)

            # Run checks
            result.ligament_violations = self.check_ligaments(holes)

        return result

    def to_dict(self) -> Dict[str, Any]:
        """Analyze and return results as dictionary."""
        result = self.analyze()
        return {
            "total_holes": result.total_holes,
            "patterns": [
                {
                    "type": p.pattern_type,
                    "count": p.count,
                    "pitch_x": p.pitch_x,
                    "pitch_y": p.pitch_y,
                    "bolt_circle_diameter": p.bolt_circle_diameter,
                }
                for p in result.patterns
            ],
            "edge_distance_violations": result.edge_distance_violations,
            "ligament_violations": result.ligament_violations,
            "alignment_issues": result.alignment_issues,
        }
