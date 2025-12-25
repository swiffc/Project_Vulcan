"""
Mates & Constraints Analyzer
============================
Analyze assembly mates and detect issues.

Phase 24.9 Implementation
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger("vulcan.analyzer.mates")


class MateStatus(Enum):
    """Status of a mate constraint."""
    SATISFIED = "satisfied"
    OVER_DEFINED = "over_defined"
    BROKEN = "broken"
    UNKNOWN = "unknown"


class MateType(Enum):
    """Types of mates in SolidWorks."""
    COINCIDENT = "coincident"
    CONCENTRIC = "concentric"
    DISTANCE = "distance"
    ANGLE = "angle"
    PARALLEL = "parallel"
    PERPENDICULAR = "perpendicular"
    TANGENT = "tangent"
    LOCK = "lock"
    WIDTH = "width"
    GEAR = "gear"
    RACK_PINION = "rack_pinion"
    CAM = "cam"
    SLOT = "slot"
    HINGE = "hinge"
    SCREW = "screw"
    LINEAR_COUPLER = "linear_coupler"
    PATH = "path"
    UNKNOWN = "unknown"


@dataclass
class MateInfo:
    """Information about a single mate."""
    name: str = ""
    mate_type: MateType = MateType.UNKNOWN
    status: MateStatus = MateStatus.UNKNOWN
    component1: str = ""
    component2: str = ""
    value: Optional[float] = None  # Distance/angle value if applicable
    is_suppressed: bool = False
    error_message: str = ""


@dataclass
class MatesAnalysisResult:
    """Complete mates analysis results."""
    total_mates: int = 0
    satisfied: int = 0
    over_defined: int = 0
    broken: int = 0
    suppressed: int = 0
    mates: List[MateInfo] = field(default_factory=list)
    mate_counts_by_type: Dict[str, int] = field(default_factory=dict)
    issues: List[str] = field(default_factory=list)
    fix_suggestions: List[Dict[str, str]] = field(default_factory=list)
    redundant_mates: List[Dict[str, Any]] = field(default_factory=list)


class MatesAnalyzer:
    """
    Analyze assembly mates and detect issues.
    Provides suggestions for fixing broken/over-defined mates.
    """

    # Map SolidWorks mate type constants to enum
    MATE_TYPE_MAP = {
        0: MateType.COINCIDENT,
        1: MateType.CONCENTRIC,
        2: MateType.PERPENDICULAR,
        3: MateType.PARALLEL,
        4: MateType.TANGENT,
        5: MateType.DISTANCE,
        6: MateType.ANGLE,
        7: MateType.UNKNOWN,
        8: MateType.CAM,
        9: MateType.GEAR,
        10: MateType.WIDTH,
        11: MateType.LOCK,
        12: MateType.SCREW,
        13: MateType.LINEAR_COUPLER,
        14: MateType.PATH,
        15: MateType.RACK_PINION,
        16: MateType.HINGE,
        17: MateType.SLOT,
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
            return self._doc is not None and self._doc.GetType() == 2  # Assembly
        except Exception as e:
            logger.error(f"Failed to connect to SolidWorks: {e}")
            return False

    def _get_mate_status(self, mate_feature: Any) -> MateStatus:
        """Determine the status of a mate."""
        try:
            # Check if suppressed
            if mate_feature.IsSuppressed():
                return MateStatus.SATISFIED  # Suppressed mates don't count as broken

            # Get mate definition
            mate_def = mate_feature.GetDefinition()
            if not mate_def:
                return MateStatus.UNKNOWN

            # Check error status
            error_code = mate_def.ErrorStatus
            if error_code == 0:
                return MateStatus.SATISFIED
            elif error_code == 1:
                return MateStatus.OVER_DEFINED
            elif error_code == 2:
                return MateStatus.BROKEN
            else:
                return MateStatus.UNKNOWN

        except Exception:
            return MateStatus.UNKNOWN

    def _get_mate_type(self, mate_feature: Any) -> MateType:
        """Get the type of mate."""
        try:
            mate_def = mate_feature.GetDefinition()
            if mate_def:
                type_val = mate_def.Type
                return self.MATE_TYPE_MAP.get(type_val, MateType.UNKNOWN)
        except Exception:
            pass
        return MateType.UNKNOWN

    def _get_mated_components(self, mate_feature: Any) -> tuple:
        """Get the two components involved in a mate."""
        comp1, comp2 = "", ""
        try:
            mate_def = mate_feature.GetDefinition()
            if mate_def:
                entities = mate_def.MateEntities
                if entities and len(entities) >= 2:
                    # Get component from entity
                    for i, entity in enumerate(entities[:2]):
                        try:
                            comp = entity.ReferenceComponent
                            if comp:
                                if i == 0:
                                    comp1 = comp.Name2
                                else:
                                    comp2 = comp.Name2
                        except Exception:
                            pass
        except Exception:
            pass
        return comp1, comp2

    def _generate_fix_suggestion(self, mate: MateInfo) -> Optional[Dict[str, str]]:
        """Generate a fix suggestion for a problematic mate."""
        if mate.status == MateStatus.BROKEN:
            return {
                "mate": mate.name,
                "issue": "Broken mate",
                "suggestion": f"Check if components '{mate.component1}' and '{mate.component2}' "
                             f"still have the referenced faces/edges. The geometry may have changed.",
                "action": "suppress_or_delete",
            }
        elif mate.status == MateStatus.OVER_DEFINED:
            return {
                "mate": mate.name,
                "issue": "Over-defined",
                "suggestion": f"This mate conflicts with other constraints. Consider suppressing "
                             f"redundant mates or using a different mate type.",
                "action": "review_mates",
            }
        return None

    def _detect_redundant_mates(self, mates: List[MateInfo]) -> List[Dict[str, Any]]:
        """Detect potentially redundant mates between same component pairs."""
        redundant = []

        # Group mates by component pair
        comp_pair_mates: Dict[tuple, List[MateInfo]] = {}
        for mate in mates:
            if mate.is_suppressed:
                continue
            # Create sorted tuple for consistent pair identification
            pair = tuple(sorted([mate.component1, mate.component2]))
            if pair not in comp_pair_mates:
                comp_pair_mates[pair] = []
            comp_pair_mates[pair].append(mate)

        # Check for redundancy patterns
        for pair, pair_mates in comp_pair_mates.items():
            if len(pair_mates) > 3:  # More than 3 mates between same parts is suspicious
                redundant.append({
                    "components": list(pair),
                    "mate_count": len(pair_mates),
                    "mates": [m.name for m in pair_mates],
                    "suggestion": f"Components have {len(pair_mates)} mates. Consider if all are necessary.",
                })

            # Check for conflicting mate types
            mate_types = [m.mate_type for m in pair_mates]
            if MateType.LOCK in mate_types and len(mate_types) > 1:
                redundant.append({
                    "components": list(pair),
                    "issue": "Lock mate with additional mates",
                    "mates": [m.name for m in pair_mates],
                    "suggestion": "Lock mate fully constrains - other mates may be redundant.",
                })

            # Check for duplicate coincident mates on same face type
            coincident_count = sum(1 for m in pair_mates if m.mate_type == MateType.COINCIDENT)
            if coincident_count > 2:
                redundant.append({
                    "components": list(pair),
                    "issue": f"{coincident_count} coincident mates",
                    "mates": [m.name for m in pair_mates if m.mate_type == MateType.COINCIDENT],
                    "suggestion": "Multiple coincident mates may be redundant.",
                })

        return redundant

    def analyze(self) -> MatesAnalysisResult:
        """Analyze all mates in the assembly."""
        result = MatesAnalysisResult()

        if not self._connect():
            logger.warning("Not connected to a SolidWorks assembly")
            return result

        try:
            # Get the MateGroup feature (contains all mates)
            feat = self._doc.FirstFeature()
            while feat:
                if feat.GetTypeName2() == "MateGroup":
                    # Get sub-features (individual mates)
                    sub_feat = feat.GetFirstSubFeature()
                    while sub_feat:
                        if "Mate" in sub_feat.GetTypeName2():
                            mate_info = MateInfo()
                            mate_info.name = sub_feat.Name
                            mate_info.mate_type = self._get_mate_type(sub_feat)
                            mate_info.status = self._get_mate_status(sub_feat)
                            mate_info.is_suppressed = sub_feat.IsSuppressed()

                            comp1, comp2 = self._get_mated_components(sub_feat)
                            mate_info.component1 = comp1
                            mate_info.component2 = comp2

                            result.mates.append(mate_info)
                            result.total_mates += 1

                            # Count by status
                            if mate_info.is_suppressed:
                                result.suppressed += 1
                            elif mate_info.status == MateStatus.SATISFIED:
                                result.satisfied += 1
                            elif mate_info.status == MateStatus.OVER_DEFINED:
                                result.over_defined += 1
                                result.issues.append(f"Over-defined: {mate_info.name}")
                            elif mate_info.status == MateStatus.BROKEN:
                                result.broken += 1
                                result.issues.append(f"Broken: {mate_info.name}")

                            # Count by type
                            type_name = mate_info.mate_type.value
                            result.mate_counts_by_type[type_name] = \
                                result.mate_counts_by_type.get(type_name, 0) + 1

                            # Generate fix suggestions
                            if mate_info.status in [MateStatus.BROKEN, MateStatus.OVER_DEFINED]:
                                suggestion = self._generate_fix_suggestion(mate_info)
                                if suggestion:
                                    result.fix_suggestions.append(suggestion)

                        sub_feat = sub_feat.GetNextSubFeature()
                    break  # Only one MateGroup
                feat = feat.GetNextFeature()

            # Detect redundant mates (Phase 24.9)
            result.redundant_mates = self._detect_redundant_mates(result.mates)

        except Exception as e:
            logger.error(f"Error analyzing mates: {e}")

        return result

    def to_dict(self) -> Dict[str, Any]:
        """Analyze and return results as dictionary."""
        result = self.analyze()

        return {
            "total_mates": result.total_mates,
            "satisfied": result.satisfied,
            "over_defined": result.over_defined,
            "broken": result.broken,
            "suppressed": result.suppressed,
            "mate_counts_by_type": result.mate_counts_by_type,
            "mates": [
                {
                    "name": m.name,
                    "type": m.mate_type.value,
                    "status": m.status.value,
                    "component1": m.component1,
                    "component2": m.component2,
                    "is_suppressed": m.is_suppressed,
                }
                for m in result.mates
            ],
            "issues": result.issues,
            "fix_suggestions": result.fix_suggestions,
        }
