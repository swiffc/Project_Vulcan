"""
Cost Estimator
==============
Estimates manufacturing costs based on CAD geometry and material data.

Features:
- Material cost calculation (Volume * Density * Price)
- Machining time estimation (Feature based)
- Welding cost estimation (Weld volume * rate)
- BOM roll-ups
"""

import logging
from typing import Dict, List

logger = logging.getLogger("vulcan.cad.cost_estimator")

# Base material prices ($/lb) - Should be updated via API or user input
MATERIAL_PRICES = {
    "steel": 0.85,
    "carbon_steel": 0.85,
    "aluminum": 2.50,
    "stainless": 3.75,
    "ss304": 3.75,
    "ss316": 4.50,
    "brass": 5.00,
}

# Process rates ($/hr)
LABOR_RATES = {
    "machining": 85.00,
    "welding": 95.00,
    "assembly": 65.00,
    "cutting": 75.00,
}


class CostEstimator:
    """Calculates estimated costs for parts and assemblies."""

    def __init__(self):
        pass

    def estimate_material_cost(
        self, volume_in3: float, material: str, density_lb_in3: float
    ) -> float:
        """Calculate raw material cost."""
        weight = volume_in3 * density_lb_in3
        price_per_lb = MATERIAL_PRICES.get(
            material.lower(), 1.00
        )  # Default to $1/lb if unknown
        return round(weight * price_per_lb, 2)

    def estimate_machining_cost(
        self, complexity_score: int, volume_in3: float
    ) -> float:
        """
        Rough order magnitude estimate for machining.
        Complexity 1-10.
        """
        # Heuristic: Base setup time + run time proportional to volume removal
        base_setup_hrs = 1.0 + (complexity_score * 0.5)
        run_time_hrs = (volume_in3 * 0.1) * (1 + complexity_score * 0.2)

        total_hrs = base_setup_hrs + run_time_hrs
        return round(total_hrs * LABOR_RATES["machining"], 2)

    def estimate_part_cost(self, part_data: Dict) -> Dict[str, float]:
        """
        Full cost rollup for a single part.
        Expecting part_data to have: material, volume, density, complexity
        """
        mat_cost = self.estimate_material_cost(
            part_data.get("volume", 0),
            part_data.get("material", "steel"),
            part_data.get("density", 0.284),
        )

        mfg_cost = self.estimate_machining_cost(
            part_data.get("complexity", 1), part_data.get("volume", 0)
        )

        return {
            "material_cost": mat_cost,
            "manufacturing_cost": mfg_cost,
            "total_cost": round(mat_cost + mfg_cost, 2),
        }


# Factory
def get_cost_estimator() -> CostEstimator:
    return CostEstimator()
