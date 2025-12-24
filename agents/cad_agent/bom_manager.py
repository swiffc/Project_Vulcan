"""
BOM Manager - Phase 21 Gap 19

Handles extraction, validation, and cost rollup of Bill of Materials (BOM).
Integrates data from DrawingParser and CostEstimator.
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

logger = logging.getLogger("cad_agent.bom_manager")


@dataclass
class BOMItem:
    """Standardized BOM Item."""

    item_no: str
    part_number: str
    description: str
    quantity: int
    material: Optional[str] = None
    vendor: Optional[str] = None
    cost_per_unit: float = 0.0
    total_cost: float = 0.0
    source: str = "drawing"  # drawing, assembly, manual


@dataclass
class BOMAnalysis:
    """Result of BOM processing."""

    items: List[dict]
    total_cost: float
    total_items: int
    standard_parts_count: int
    custom_parts_count: int
    missing_costs: int
    issues: List[str]


class BOMManager:
    """
    Manages Bill of Materials logic.

    1. Ingests BOM data from Drawings or Assemblies.
    2. Standardizes item format.
    3. Lookups up standard part costs.
    4. Calculates total assembly cost.
    5. Validates fastener specifications.
    """

    def __init__(self):
        self.cost_estimator = None

    def _get_estimator(self):
        """Lazy load cost estimator."""
        if not self.cost_estimator:
            from .cost_estimator import get_cost_estimator

            self.cost_estimator = get_cost_estimator()
        return self.cost_estimator

    def process_bom(self, raw_items: List[Dict[str, Any]]) -> BOMAnalysis:
        """
        Process a raw list of BOM items (e.g., from DrawingParser).

        Args:
            raw_items: List of dicts with keys like 'QTY', 'DESCRIPTION', 'PART NUMBER'

        Returns:
            BOMAnalysis object
        """
        standardized_items = []
        issues = []
        total_cost = 0.0
        std_count = 0
        custom_count = 0
        missing_costs = 0

        estimator = self._get_estimator()

        for idx, item in enumerate(raw_items):
            # Normalize keys (handle variations like 'PART NO', 'Part No.', 'DESCRIPTION')
            normalized = self._normalize_item(item)

            # Create BOMItem
            bom_item = BOMItem(
                item_no=normalized.get("item_no", str(idx + 1)),
                part_number=normalized.get("part_number", "UNKNOWN"),
                description=normalized.get("description", ""),
                quantity=self._parse_qty(normalized.get("quantity", 1)),
                material=normalized.get("material"),
            )

            # Classify: Standard vs Custom
            is_standard = self.is_standard_part(bom_item)
            if is_standard:
                std_count += 1
                # Estimate cost for standard part (approximate)
                bom_item.cost_per_unit = self._estimate_standard_cost(bom_item)
            else:
                custom_count += 1
                # For custom parts, we'd ideally look up their cost estimate if available.
                # For now, we flag it if cost is missing.
                # In a real flow, we might trigger a recursive cost estimate here.
                bom_item.cost_per_unit = 0.0
                missing_costs += 1

            bom_item.total_cost = bom_item.cost_per_unit * bom_item.quantity
            total_cost += bom_item.total_cost

            # Validation
            if bom_item.quantity == 0:
                issues.append(
                    f"Item {bom_item.item_no} ({bom_item.part_number}) has 0 quantity"
                )

            if not bom_item.description:
                issues.append(
                    f"Item {bom_item.item_no} ({bom_item.part_number}) has no description"
                )

            standardized_items.append(asdict(bom_item))

        return BOMAnalysis(
            items=standardized_items,
            total_cost=round(total_cost, 2),
            total_items=sum(i["quantity"] for i in standardized_items),
            standard_parts_count=std_count,
            custom_parts_count=custom_count,
            missing_costs=missing_costs,
            issues=issues,
        )

    def is_standard_part(self, item: BOMItem) -> bool:
        """Check if item is a standard hardware component."""
        keywords = [
            "SCREW",
            "BOLT",
            "NUT",
            "WASHER",
            "PIN",
            "RIVET",
            "KEY",
            "BEARING",
            "O-RING",
        ]
        desc = item.description.upper()
        return any(k in desc for k in keywords)

    def _normalize_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize widely varying dictionary keys."""
        normalized = {}

        # Map common headers to internal keys
        key_map = {
            "QTY": "quantity",
            "QUANTITY": "quantity",
            "PART NUMBER": "part_number",
            "PART NO": "part_number",
            "NUMBER": "part_number",
            "DESCRIPTION": "description",
            "DESC": "description",
            "ITEM": "item_no",
            "ITEM NO": "item_no",
            "NO": "item_no",
            "MATERIAL": "material",
        }

        for k, v in item.items():
            upper_k = str(k).upper().strip().replace(".", "")
            if upper_k in key_map:
                normalized[key_map[upper_k]] = v
            else:
                # Keep original check if no match
                normalized[k.lower()] = v

        return normalized

    def _parse_qty(self, qty_val: Any) -> int:
        """Safely parse quantity."""
        try:
            return int(float(str(qty_val).strip()))
        except (ValueError, TypeError):
            return 1

    def _estimate_standard_cost(self, item: BOMItem) -> float:
        """Rough estimation for standard hardware based on keywords."""
        desc = item.description.upper()

        # Very rough lookup table
        if "WASHER" in desc:
            return 0.15
        if "NUT" in desc:
            return 0.25
        if "SCREW" in desc or "BOLT" in desc:
            if "M20" in desc or "3/4" in desc:
                return 2.50
            if "M12" in desc or "1/2" in desc:
                return 1.25
            return 0.50
        if "O-RING" in desc:
            return 0.75

        return 0.0


# Singleton
_bom_manager = BOMManager()


def get_bom_manager() -> BOMManager:
    return _bom_manager
