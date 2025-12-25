"""
Cost Estimator
==============
Estimate manufacturing costs for ACHE components.

Phase 24.28 Implementation
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

logger = logging.getLogger("vulcan.analyzer.cost")


# Material costs ($/lb) - simplified reference prices
MATERIAL_COSTS = {
    "SA-516-70": 0.85,      # Carbon steel plate
    "SA-516-60": 0.80,
    "SA-240-304": 2.50,     # Stainless 304
    "SA-240-316": 3.50,     # Stainless 316
    "SA-179": 1.20,         # Heat exchanger tubes
    "SA-214": 1.15,         # ERW tubes
    "SA-213-TP304": 4.00,   # SS tubes
    "SA-213-TP316": 5.00,
    "SA-105": 1.00,         # Forged fittings
    "SA-182-F304": 3.00,
    "SA-182-F316": 4.00,
    "ALUMINUM": 1.50,       # Fins
    "GALVANIZED": 1.10,     # Steel fins
}

# Labor rates ($/hr) - typical shop rates
LABOR_RATES = {
    "welding": 85.00,
    "machining": 75.00,
    "assembly": 55.00,
    "inspection": 65.00,
    "painting": 45.00,
    "testing": 60.00,
}

# Weld deposition rates (lbs/hr)
WELD_DEPOSITION_RATES = {
    "smaw": 2.5,
    "gmaw": 6.0,
    "fcaw": 8.0,
    "saw": 15.0,
    "gtaw": 1.5,
}


@dataclass
class MaterialCost:
    """Material cost breakdown."""
    material: str = ""
    weight_lbs: float = 0.0
    unit_cost: float = 0.0
    total_cost: float = 0.0


@dataclass
class LaborCost:
    """Labor cost breakdown."""
    operation: str = ""
    hours: float = 0.0
    rate: float = 0.0
    total_cost: float = 0.0


@dataclass
class CostEstimate:
    """Complete cost estimate."""
    materials: List[MaterialCost] = field(default_factory=list)
    labor: List[LaborCost] = field(default_factory=list)
    total_material_cost: float = 0.0
    total_labor_cost: float = 0.0
    overhead_factor: float = 1.25  # 25% overhead
    overhead_cost: float = 0.0
    total_cost: float = 0.0
    notes: List[str] = field(default_factory=list)


class CostEstimator:
    """
    Estimate manufacturing costs for ACHE components.
    """

    def __init__(self):
        pass

    def get_material_cost(self, material: str) -> float:
        """Get cost per lb for material."""
        mat_upper = material.upper()

        # Try exact match first
        if mat_upper in MATERIAL_COSTS:
            return MATERIAL_COSTS[mat_upper]

        # Try partial match
        for key, cost in MATERIAL_COSTS.items():
            if key in mat_upper or mat_upper in key:
                return cost

        # Default to carbon steel
        logger.warning(f"Material {material} not in database, using default cost")
        return 0.85

    def estimate_material_cost(
        self,
        material: str,
        weight_lbs: float,
    ) -> MaterialCost:
        """Estimate material cost."""
        unit_cost = self.get_material_cost(material)
        return MaterialCost(
            material=material,
            weight_lbs=weight_lbs,
            unit_cost=unit_cost,
            total_cost=weight_lbs * unit_cost,
        )

    def estimate_welding_hours(
        self,
        weld_weight_lbs: float,
        process: str = "gmaw",
    ) -> float:
        """Estimate welding hours based on weld metal weight."""
        deposition_rate = WELD_DEPOSITION_RATES.get(process.lower(), 6.0)
        return weld_weight_lbs / deposition_rate

    def estimate_machining_hours(
        self,
        num_holes: int,
        hole_diameter_in: float,
        plate_thickness_in: float,
    ) -> float:
        """Estimate machining hours for drilling/boring."""
        # Rough estimate: 2-5 min per hole depending on size
        minutes_per_hole = 2 + (hole_diameter_in * 0.5) + (plate_thickness_in * 0.3)
        return (num_holes * minutes_per_hole) / 60

    def estimate_assembly_hours(
        self,
        num_components: int,
        complexity: str = "medium",
    ) -> float:
        """Estimate assembly hours."""
        hours_per_component = {
            "simple": 0.25,
            "medium": 0.5,
            "complex": 1.0,
        }
        factor = hours_per_component.get(complexity, 0.5)
        return num_components * factor

    def estimate_testing_hours(
        self,
        test_type: str = "hydro",
        vessel_volume_gal: float = 100,
    ) -> float:
        """Estimate testing hours."""
        base_hours = {
            "hydro": 4.0,
            "pneumatic": 3.0,
            "leak": 2.0,
        }
        base = base_hours.get(test_type, 4.0)
        # Add time for larger vessels
        volume_factor = 1 + (vessel_volume_gal / 500)
        return base * min(volume_factor, 3.0)

    def estimate_painting_hours(
        self,
        surface_area_sqft: float,
    ) -> float:
        """Estimate painting/coating hours."""
        # Rough estimate: 50-100 sqft/hr
        return surface_area_sqft / 75

    def create_estimate(self, model_data: Dict[str, Any]) -> CostEstimate:
        """Create a complete cost estimate from model data."""
        estimate = CostEstimate()

        # Material costs
        mass = model_data.get("mass_properties", {})
        weight_lbs = mass.get("mass_lbs", 0)
        if weight_lbs > 0:
            material = model_data.get("material", "SA-516-70")
            mat_cost = self.estimate_material_cost(material, weight_lbs)
            estimate.materials.append(mat_cost)
            estimate.total_material_cost += mat_cost.total_cost

        # Labor costs
        # Welding
        weld_weight = model_data.get("weld_weight_lbs", weight_lbs * 0.02)  # ~2% of total
        if weld_weight > 0:
            weld_hours = self.estimate_welding_hours(weld_weight)
            estimate.labor.append(LaborCost(
                operation="Welding",
                hours=weld_hours,
                rate=LABOR_RATES["welding"],
                total_cost=weld_hours * LABOR_RATES["welding"],
            ))

        # Machining (holes)
        num_holes = model_data.get("total_holes", 0)
        if num_holes > 0:
            machine_hours = self.estimate_machining_hours(
                num_holes,
                model_data.get("avg_hole_diameter_in", 1.0),
                model_data.get("plate_thickness_in", 1.0),
            )
            estimate.labor.append(LaborCost(
                operation="Machining",
                hours=machine_hours,
                rate=LABOR_RATES["machining"],
                total_cost=machine_hours * LABOR_RATES["machining"],
            ))

        # Assembly
        num_components = model_data.get("component_count", 10)
        assembly_hours = self.estimate_assembly_hours(num_components)
        estimate.labor.append(LaborCost(
            operation="Assembly",
            hours=assembly_hours,
            rate=LABOR_RATES["assembly"],
            total_cost=assembly_hours * LABOR_RATES["assembly"],
        ))

        # Testing
        test_hours = self.estimate_testing_hours("hydro")
        estimate.labor.append(LaborCost(
            operation="Testing",
            hours=test_hours,
            rate=LABOR_RATES["testing"],
            total_cost=test_hours * LABOR_RATES["testing"],
        ))

        # Painting
        surface_area = mass.get("surface_area_m2", 10) * 10.764  # Convert to sqft
        paint_hours = self.estimate_painting_hours(surface_area)
        estimate.labor.append(LaborCost(
            operation="Painting",
            hours=paint_hours,
            rate=LABOR_RATES["painting"],
            total_cost=paint_hours * LABOR_RATES["painting"],
        ))

        # Calculate totals
        estimate.total_labor_cost = sum(l.total_cost for l in estimate.labor)
        estimate.overhead_cost = (estimate.total_material_cost + estimate.total_labor_cost) * (estimate.overhead_factor - 1)
        estimate.total_cost = estimate.total_material_cost + estimate.total_labor_cost + estimate.overhead_cost

        # Add notes
        estimate.notes.append("Estimate based on standard shop rates")
        estimate.notes.append("Material costs based on current market prices")
        estimate.notes.append(f"Overhead factor: {estimate.overhead_factor * 100 - 100:.0f}%")

        return estimate

    def to_dict(self, model_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create estimate and return as dictionary."""
        estimate = self.create_estimate(model_data)

        return {
            "materials": [
                {
                    "material": m.material,
                    "weight_lbs": round(m.weight_lbs, 1),
                    "unit_cost": round(m.unit_cost, 2),
                    "total_cost": round(m.total_cost, 2),
                }
                for m in estimate.materials
            ],
            "labor": [
                {
                    "operation": l.operation,
                    "hours": round(l.hours, 1),
                    "rate": round(l.rate, 2),
                    "total_cost": round(l.total_cost, 2),
                }
                for l in estimate.labor
            ],
            "summary": {
                "total_material_cost": round(estimate.total_material_cost, 2),
                "total_labor_cost": round(estimate.total_labor_cost, 2),
                "overhead_cost": round(estimate.overhead_cost, 2),
                "total_cost": round(estimate.total_cost, 2),
            },
            "notes": estimate.notes,
        }
