"""
BOM Cross-Checker Adapter
=========================
Verify Bill of Materials (BOM) against actual drawings.
Ensures all parts listed in BOM exist and match drawing specifications.

Key Features:
- BOM completeness check (all parts accounted)
- Part number matching
- Weight verification (BOM vs drawing)
- Material matching
- Quantity verification
- Missing/extra parts detection

References:
- ACHE_CHECKLIST.md: BOM verification requirements
- VERIFICATION_REQUIREMENTS.md: Cross-check workflow

Usage:
    from agents.cad_agent.adapters.bom_cross_checker import BOMChecker

    checker = BOMChecker()
    result = checker.verify_bom(bom_items, drawing_parts)
"""

import re
import logging
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum

logger = logging.getLogger("cad_agent.bom-cross-checker")


# =============================================================================
# ENUMS & DATA MODELS
# =============================================================================

class MatchStatus(Enum):
    """Status of BOM item match."""
    MATCH = "match"
    PARTIAL = "partial"
    MISMATCH = "mismatch"
    MISSING = "missing"
    EXTRA = "extra"


class CheckResult(Enum):
    """Overall check result."""
    PASS = "pass"
    WARNING = "warning"
    FAIL = "fail"


@dataclass
class BOMItem:
    """Single item from Bill of Materials."""
    item_number: int
    part_number: str
    description: str = ""
    quantity: int = 1
    material: str = ""
    weight_each: Optional[float] = None
    weight_total: Optional[float] = None
    finish: str = ""
    notes: str = ""
    reference: str = ""  # Drawing reference


@dataclass
class DrawingPart:
    """Part extracted from a drawing."""
    part_number: str
    description: str = ""
    material: str = ""
    weight: Optional[float] = None
    finish: str = ""
    revision: str = ""
    page_number: int = 0


@dataclass
class ItemMatch:
    """Result of matching BOM item to drawing part."""
    bom_item: Optional[BOMItem]
    drawing_part: Optional[DrawingPart]
    status: MatchStatus
    issues: list[str] = field(default_factory=list)
    score: float = 0.0  # Match quality 0-1


@dataclass
class BOMCheckResult:
    """Complete BOM verification result."""
    status: CheckResult
    matches: list[ItemMatch] = field(default_factory=list)
    missing_from_drawings: list[BOMItem] = field(default_factory=list)
    missing_from_bom: list[DrawingPart] = field(default_factory=list)
    total_bom_items: int = 0
    total_drawing_parts: int = 0
    match_count: int = 0
    partial_count: int = 0
    mismatch_count: int = 0
    summary: str = ""

    @property
    def match_rate(self) -> float:
        if self.total_bom_items == 0:
            return 0.0
        return self.match_count / self.total_bom_items

    def to_dict(self) -> dict:
        return {
            "status": self.status.value,
            "total_bom_items": self.total_bom_items,
            "total_drawing_parts": self.total_drawing_parts,
            "match_count": self.match_count,
            "partial_count": self.partial_count,
            "mismatch_count": self.mismatch_count,
            "missing_from_drawings": len(self.missing_from_drawings),
            "missing_from_bom": len(self.missing_from_bom),
            "match_rate": self.match_rate,
            "summary": self.summary,
        }


# =============================================================================
# BOM CROSS-CHECKER
# =============================================================================

class BOMChecker:
    """
    Cross-check BOM against actual drawings.

    Features:
    - Fuzzy part number matching
    - Weight verification
    - Material comparison
    - Quantity tracking
    """

    def __init__(
        self,
        weight_tolerance: float = 0.10,
        strict_material_match: bool = False,
    ):
        self.weight_tolerance = weight_tolerance
        self.strict_material_match = strict_material_match

    def verify_bom(
        self,
        bom_items: list[BOMItem],
        drawing_parts: list[DrawingPart],
    ) -> BOMCheckResult:
        """
        Verify BOM against drawing parts.

        Args:
            bom_items: List of BOM items
            drawing_parts: List of parts from drawings

        Returns:
            Complete verification result
        """
        logger.info(f"Verifying BOM: {len(bom_items)} items vs {len(drawing_parts)} drawings")

        matches = []
        used_drawings = set()
        missing_from_drawings = []
        missing_from_bom = []

        # Match each BOM item to a drawing
        for bom_item in bom_items:
            best_match = None
            best_score = 0.0

            for i, drawing in enumerate(drawing_parts):
                if i in used_drawings:
                    continue

                score = self._calculate_match_score(bom_item, drawing)
                if score > best_score:
                    best_score = score
                    best_match = (i, drawing)

            if best_match and best_score >= 0.5:
                idx, drawing = best_match
                used_drawings.add(idx)

                # Determine match status and issues
                status, issues = self._evaluate_match(bom_item, drawing)

                matches.append(ItemMatch(
                    bom_item=bom_item,
                    drawing_part=drawing,
                    status=status,
                    issues=issues,
                    score=best_score,
                ))
            else:
                # No matching drawing found
                missing_from_drawings.append(bom_item)
                matches.append(ItemMatch(
                    bom_item=bom_item,
                    drawing_part=None,
                    status=MatchStatus.MISSING,
                    issues=["No matching drawing found"],
                    score=0.0,
                ))

        # Find drawings not in BOM
        for i, drawing in enumerate(drawing_parts):
            if i not in used_drawings:
                missing_from_bom.append(drawing)

        # Calculate statistics
        match_count = sum(1 for m in matches if m.status == MatchStatus.MATCH)
        partial_count = sum(1 for m in matches if m.status == MatchStatus.PARTIAL)
        mismatch_count = sum(1 for m in matches if m.status == MatchStatus.MISMATCH)

        # Determine overall status
        if len(missing_from_drawings) == 0 and mismatch_count == 0:
            if partial_count == 0 and len(missing_from_bom) == 0:
                status = CheckResult.PASS
                summary = f"All {len(bom_items)} BOM items verified"
            else:
                status = CheckResult.WARNING
                issues = []
                if partial_count > 0:
                    issues.append(f"{partial_count} partial matches")
                if len(missing_from_bom) > 0:
                    issues.append(f"{len(missing_from_bom)} extra drawings")
                summary = "; ".join(issues)
        else:
            status = CheckResult.FAIL
            issues = []
            if len(missing_from_drawings) > 0:
                issues.append(f"{len(missing_from_drawings)} missing from drawings")
            if mismatch_count > 0:
                issues.append(f"{mismatch_count} mismatches")
            summary = "; ".join(issues)

        return BOMCheckResult(
            status=status,
            matches=matches,
            missing_from_drawings=missing_from_drawings,
            missing_from_bom=missing_from_bom,
            total_bom_items=len(bom_items),
            total_drawing_parts=len(drawing_parts),
            match_count=match_count,
            partial_count=partial_count,
            mismatch_count=mismatch_count,
            summary=summary,
        )

    def _calculate_match_score(
        self,
        bom_item: BOMItem,
        drawing: DrawingPart,
    ) -> float:
        """Calculate how well a BOM item matches a drawing."""
        score = 0.0
        max_score = 0.0

        # Part number match (highest weight)
        max_score += 50
        pn_score = self._compare_part_numbers(bom_item.part_number, drawing.part_number)
        score += pn_score * 50

        # Description match
        max_score += 20
        desc_score = self._compare_descriptions(bom_item.description, drawing.description)
        score += desc_score * 20

        # Material match
        max_score += 15
        if bom_item.material and drawing.material:
            mat_score = self._compare_materials(bom_item.material, drawing.material)
            score += mat_score * 15

        # Weight match
        max_score += 10
        if bom_item.weight_each and drawing.weight:
            diff = abs(bom_item.weight_each - drawing.weight)
            diff_pct = diff / bom_item.weight_each if bom_item.weight_each > 0 else 1.0
            if diff_pct <= 0.05:
                score += 10
            elif diff_pct <= 0.15:
                score += 5

        # Finish match
        max_score += 5
        if bom_item.finish and drawing.finish:
            if self._normalize(bom_item.finish) == self._normalize(drawing.finish):
                score += 5

        return score / max_score if max_score > 0 else 0.0

    def _evaluate_match(
        self,
        bom_item: BOMItem,
        drawing: DrawingPart,
    ) -> tuple[MatchStatus, list[str]]:
        """Evaluate match quality and identify issues."""
        issues = []
        has_critical_issue = False

        # Check part number
        pn_score = self._compare_part_numbers(bom_item.part_number, drawing.part_number)
        if pn_score < 0.8:
            issues.append(f"Part number differs: BOM '{bom_item.part_number}' vs Drawing '{drawing.part_number}'")
            has_critical_issue = True

        # Check material
        if bom_item.material and drawing.material:
            mat_score = self._compare_materials(bom_item.material, drawing.material)
            if mat_score < 0.8:
                issues.append(f"Material differs: BOM '{bom_item.material}' vs Drawing '{drawing.material}'")
                if self.strict_material_match:
                    has_critical_issue = True

        # Check weight
        if bom_item.weight_each and drawing.weight:
            diff = abs(bom_item.weight_each - drawing.weight)
            diff_pct = diff / bom_item.weight_each if bom_item.weight_each > 0 else 1.0

            if diff_pct > self.weight_tolerance:
                issues.append(
                    f"Weight differs: BOM {bom_item.weight_each:.1f} lb vs Drawing {drawing.weight:.1f} lb "
                    f"({diff_pct*100:.1f}%)"
                )
                if diff_pct > 0.20:
                    has_critical_issue = True

        # Check finish
        if bom_item.finish and drawing.finish:
            if self._normalize(bom_item.finish) != self._normalize(drawing.finish):
                issues.append(f"Finish differs: BOM '{bom_item.finish}' vs Drawing '{drawing.finish}'")

        # Determine status
        if has_critical_issue:
            return MatchStatus.MISMATCH, issues
        elif issues:
            return MatchStatus.PARTIAL, issues
        else:
            return MatchStatus.MATCH, []

    def _compare_part_numbers(self, pn1: str, pn2: str) -> float:
        """Compare two part numbers with fuzzy matching."""
        # Normalize
        n1 = self._normalize_part_number(pn1)
        n2 = self._normalize_part_number(pn2)

        if n1 == n2:
            return 1.0

        # Check if one contains the other
        if n1 in n2 or n2 in n1:
            return 0.9

        # Check prefix match (common for revisions)
        min_len = min(len(n1), len(n2))
        matching = sum(1 for a, b in zip(n1, n2) if a == b)
        if matching >= min_len * 0.8:
            return 0.8

        return matching / max(len(n1), len(n2)) if max(len(n1), len(n2)) > 0 else 0

    def _compare_descriptions(self, desc1: str, desc2: str) -> float:
        """Compare descriptions with fuzzy matching."""
        n1 = self._normalize(desc1)
        n2 = self._normalize(desc2)

        if not n1 or not n2:
            return 0.5  # Can't compare

        if n1 == n2:
            return 1.0

        # Word-based comparison
        words1 = set(n1.split())
        words2 = set(n2.split())

        if not words1 or not words2:
            return 0.5

        intersection = words1 & words2
        union = words1 | words2

        return len(intersection) / len(union) if union else 0

    def _compare_materials(self, mat1: str, mat2: str) -> float:
        """Compare materials with fuzzy matching."""
        n1 = self._normalize(mat1)
        n2 = self._normalize(mat2)

        if n1 == n2:
            return 1.0

        # Common material aliases
        aliases = {
            "a36": ["a36", "hr", "hot rolled", "crs"],
            "a572": ["a572", "hsla", "high strength"],
            "ss304": ["ss304", "304", "stainless 304", "18-8"],
            "ss316": ["ss316", "316", "stainless 316"],
            "al6061": ["al6061", "6061", "aluminum 6061"],
            "galv": ["galv", "galvanized", "hdg", "g90"],
        }

        # Check aliases
        for base, alts in aliases.items():
            in1 = any(a in n1 for a in alts)
            in2 = any(a in n2 for a in alts)
            if in1 and in2:
                return 0.9

        # Check for common words
        if any(word in n2 for word in n1.split()):
            return 0.7

        return 0.0

    def _normalize(self, text: str) -> str:
        """Normalize text for comparison."""
        return re.sub(r'[^a-z0-9]', '', text.lower())

    def _normalize_part_number(self, pn: str) -> str:
        """Normalize part number."""
        return re.sub(r'[^a-z0-9\-]', '', pn.lower())

    # -------------------------------------------------------------------------
    # CONVENIENCE METHODS
    # -------------------------------------------------------------------------

    def quick_check(
        self,
        bom_part_numbers: list[str],
        drawing_part_numbers: list[str],
    ) -> dict:
        """
        Quick check if part numbers match between BOM and drawings.

        Args:
            bom_part_numbers: List of part numbers from BOM
            drawing_part_numbers: List of part numbers from drawings

        Returns:
            Dict with match statistics
        """
        bom_set = {self._normalize_part_number(pn) for pn in bom_part_numbers}
        drw_set = {self._normalize_part_number(pn) for pn in drawing_part_numbers}

        in_both = bom_set & drw_set
        only_in_bom = bom_set - drw_set
        only_in_drawings = drw_set - bom_set

        return {
            "total_bom": len(bom_set),
            "total_drawings": len(drw_set),
            "matched": len(in_both),
            "missing_drawings": list(only_in_bom),
            "extra_drawings": list(only_in_drawings),
            "match_rate": len(in_both) / len(bom_set) if bom_set else 0,
            "is_complete": len(only_in_bom) == 0,
        }

    def verify_quantities(
        self,
        bom_items: list[BOMItem],
    ) -> list[dict]:
        """
        Check BOM quantities for issues.

        Returns list of parts with quantity concerns.
        """
        concerns = []

        for item in bom_items:
            if item.quantity <= 0:
                concerns.append({
                    "part_number": item.part_number,
                    "issue": "Invalid quantity",
                    "quantity": item.quantity,
                })
            elif item.quantity > 100:
                concerns.append({
                    "part_number": item.part_number,
                    "issue": "Unusually high quantity",
                    "quantity": item.quantity,
                })

            # Check weight consistency
            if item.weight_each and item.weight_total:
                expected = item.weight_each * item.quantity
                if abs(expected - item.weight_total) > expected * 0.01:
                    concerns.append({
                        "part_number": item.part_number,
                        "issue": "Weight × qty doesn't match total",
                        "expected_total": expected,
                        "actual_total": item.weight_total,
                    })

        return concerns

    def generate_report(self, result: BOMCheckResult) -> str:
        """Generate a text report from check result."""
        lines = [
            "=" * 60,
            "BOM VERIFICATION REPORT",
            "=" * 60,
            "",
            f"Status: {result.status.value.upper()}",
            f"BOM Items: {result.total_bom_items}",
            f"Drawing Parts: {result.total_drawing_parts}",
            "",
            f"Matches: {result.match_count}",
            f"Partial: {result.partial_count}",
            f"Mismatches: {result.mismatch_count}",
            f"Match Rate: {result.match_rate * 100:.1f}%",
            "",
        ]

        if result.missing_from_drawings:
            lines.append("-" * 40)
            lines.append("MISSING FROM DRAWINGS:")
            for item in result.missing_from_drawings:
                lines.append(f"  - {item.part_number}: {item.description}")

        if result.missing_from_bom:
            lines.append("-" * 40)
            lines.append("EXTRA DRAWINGS (not in BOM):")
            for part in result.missing_from_bom:
                lines.append(f"  - {part.part_number}: {part.description}")

        if any(m.issues for m in result.matches):
            lines.append("-" * 40)
            lines.append("ISSUES FOUND:")
            for match in result.matches:
                if match.issues:
                    lines.append(f"  {match.bom_item.part_number if match.bom_item else 'Unknown'}:")
                    for issue in match.issues:
                        lines.append(f"    - {issue}")

        lines.extend(["", "=" * 60])
        return "\n".join(lines)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "BOMChecker",
    "BOMItem",
    "DrawingPart",
    "ItemMatch",
    "BOMCheckResult",
    "MatchStatus",
    "CheckResult",
]
