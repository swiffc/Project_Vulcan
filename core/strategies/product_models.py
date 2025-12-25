"""
Digital Twin Product Models - Phase 20 Task 15

Defines schema for CAD part "digital twins" (successful strategies).
Supports Weldment, Sheet Metal, and Machining product types.
"""

from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
import json


class ProductType(str, Enum):
    """Types of CAD products."""
    WELDMENT = "weldment"
    SHEET_METAL = "sheet_metal"
    MACHINING = "machining"
    CASTING = "casting"
    ASSEMBLY = "assembly"
    SOLID = "solid"


class FeatureType(str, Enum):
    """CAD feature types."""
    EXTRUDE = "extrude"
    REVOLVE = "revolve"
    SWEEP = "sweep"
    LOFT = "loft"
    FILLET = "fillet"
    CHAMFER = "chamfer"
    HOLE = "hole"
    PATTERN = "pattern"
    MIRROR = "mirror"
    SHELL = "shell"
    RIB = "rib"
    DRAFT = "draft"
    CUT = "cut"
    BEND = "bend"
    FLANGE = "flange"
    WELD = "weld"


class MaterialSpec(BaseModel):
    """Material specification."""
    name: str = "AISI 304"
    grade: Optional[str] = None
    density: float = 7850.0  # kg/m³
    yield_strength: Optional[float] = None  # MPa
    tensile_strength: Optional[float] = None  # MPa
    cost_per_kg: Optional[float] = None  # USD


class Dimension(BaseModel):
    """Dimension with tolerance."""
    nominal: float
    upper_tolerance: float = 0.0
    lower_tolerance: float = 0.0
    unit: str = "mm"

    @property
    def max_value(self) -> float:
        return self.nominal + self.upper_tolerance

    @property
    def min_value(self) -> float:
        return self.nominal + self.lower_tolerance


class Constraint(BaseModel):
    """Design constraint."""
    name: str
    type: Literal["dimensional", "geometric", "material", "process"]
    value: Any
    standard: Optional[str] = None  # e.g., "ASME Y14.5"
    is_critical: bool = False


class Feature(BaseModel):
    """Base feature definition."""
    name: str
    type: FeatureType
    parameters: Dict[str, Any] = {}
    sequence: int = 0  # Build order
    depends_on: List[str] = []  # Feature dependencies


class SuccessMetrics(BaseModel):
    """Metrics for tracking strategy success."""
    validation_pass_rate: float = 0.0  # 0-100%
    average_build_time: float = 0.0  # seconds
    error_count: int = 0
    usage_count: int = 0
    last_used: Optional[datetime] = None
    user_rating: Optional[float] = None  # 1-5 stars


class BaseProduct(BaseModel):
    """Abstract base for all CAD product types."""
    name: str
    product_type: ProductType
    description: Optional[str] = None
    material: MaterialSpec = Field(default_factory=MaterialSpec)
    features: List[Feature] = []
    constraints: List[Constraint] = []
    success_metrics: SuccessMetrics = Field(default_factory=SuccessMetrics)

    # Metadata
    version: int = 1
    is_experimental: bool = False  # Sandbox flag
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str = "system"
    tags: List[str] = []

    def estimate_volume(self) -> float:
        """Estimate volume without opening CAD."""
        raise NotImplementedError("Subclasses must implement")

    def estimate_weight(self) -> float:
        """Estimate weight based on volume and material density."""
        volume_m3 = self.estimate_volume() / 1e9  # mm³ to m³
        return volume_m3 * self.material.density

    def to_json(self) -> str:
        """Serialize to JSON."""
        return self.model_dump_json(indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> "BaseProduct":
        """Deserialize from JSON."""
        return cls.model_validate_json(json_str)

    def validate_constraints(self) -> List[Dict[str, Any]]:
        """Validate all constraints and return violations."""
        violations = []
        for constraint in self.constraints:
            if constraint.is_critical:
                # Placeholder for actual validation logic
                pass
        return violations


class WeldmentStrategy(BaseProduct):
    """Strategy for weldment (structural steel) parts."""
    product_type: ProductType = ProductType.WELDMENT

    # Weldment-specific fields
    structural_members: List[Dict[str, Any]] = []  # Beams, tubes, channels
    weld_joints: List[Dict[str, Any]] = []  # Weld specifications
    cut_list: List[Dict[str, Any]] = []  # Material cut list

    # Standards
    weld_standard: str = "AWS D1.1"
    structural_standard: str = "AISC"

    def estimate_volume(self) -> float:
        """Estimate total volume of structural members."""
        total_volume = 0.0
        for member in self.structural_members:
            # Simplified: length * cross_section_area
            length = member.get("length", 0)
            area = member.get("cross_section_area", 0)
            total_volume += length * area
        return total_volume

    def get_cut_list_summary(self) -> Dict[str, Any]:
        """Generate cut list summary for fabrication."""
        summary = {}
        for item in self.cut_list:
            profile = item.get("profile", "unknown")
            if profile not in summary:
                summary[profile] = {"count": 0, "total_length": 0}
            summary[profile]["count"] += 1
            summary[profile]["total_length"] += item.get("length", 0)
        return summary


class SheetMetalStrategy(BaseProduct):
    """Strategy for sheet metal parts."""
    product_type: ProductType = ProductType.SHEET_METAL

    # Sheet metal-specific fields
    thickness: Dimension = Field(default_factory=lambda: Dimension(nominal=1.5))
    bend_radius: float = 1.0  # mm (typically = thickness)
    k_factor: float = 0.44  # Bend allowance factor

    bends: List[Dict[str, Any]] = []  # Bend sequence
    flat_pattern: Optional[Dict[str, Any]] = None  # Developed length

    # Process parameters
    bend_sequence: List[int] = []  # Order of bends
    grain_direction: Optional[str] = None

    def estimate_volume(self) -> float:
        """Estimate volume from flat pattern area * thickness."""
        if self.flat_pattern:
            area = self.flat_pattern.get("area", 0)
            return area * self.thickness.nominal
        return 0.0

    def calculate_flat_pattern_size(self) -> Dict[str, float]:
        """Calculate flat pattern dimensions."""
        if self.flat_pattern:
            return {
                "width": self.flat_pattern.get("width", 0),
                "height": self.flat_pattern.get("height", 0),
                "area": self.flat_pattern.get("area", 0)
            }
        return {"width": 0, "height": 0, "area": 0}

    def get_bend_sequence(self) -> List[Dict[str, Any]]:
        """Get optimized bend sequence for fabrication."""
        # Sort bends by sequence number
        return sorted(self.bends, key=lambda x: x.get("sequence", 0))


class MachiningStrategy(BaseProduct):
    """Strategy for machined parts."""
    product_type: ProductType = ProductType.MACHINING

    # Machining-specific fields
    stock_size: Dict[str, float] = {"x": 100, "y": 100, "z": 50}  # mm
    stock_material: str = "6061-T6 Aluminum"

    operations: List[Dict[str, Any]] = []  # Machining operations
    tooling: List[Dict[str, Any]] = []  # Required tools

    # Process parameters
    setup_count: int = 1  # Number of setups required
    estimated_cycle_time: float = 0.0  # minutes

    def estimate_volume(self) -> float:
        """Estimate final part volume (stock - removed material)."""
        stock_volume = self.stock_size["x"] * self.stock_size["y"] * self.stock_size["z"]
        removed = sum(op.get("volume_removed", 0) for op in self.operations)
        return stock_volume - removed

    def get_operation_sequence(self) -> List[Dict[str, Any]]:
        """Get machining operations in sequence."""
        return sorted(self.operations, key=lambda x: x.get("sequence", 0))

    def estimate_machining_time(self) -> float:
        """Estimate total machining time."""
        return sum(op.get("cycle_time", 0) for op in self.operations)


class AssemblyStrategy(BaseProduct):
    """Strategy for assemblies."""
    product_type: ProductType = ProductType.ASSEMBLY

    # Assembly-specific fields
    components: List[Dict[str, Any]] = []  # Child components
    mates: List[Dict[str, Any]] = []  # Assembly constraints

    # BOM
    bom: List[Dict[str, Any]] = []

    def estimate_volume(self) -> float:
        """Sum of all component volumes."""
        return sum(comp.get("volume", 0) for comp in self.components)

    def get_bom(self) -> List[Dict[str, Any]]:
        """Get Bill of Materials."""
        return self.bom

    def validate_assembly(self) -> List[str]:
        """Check for assembly issues."""
        issues = []
        # Check for missing mates
        for comp in self.components:
            if not any(m.get("component") == comp.get("name") for m in self.mates):
                issues.append(f"Component {comp.get('name')} has no mates")
        return issues


class SolidStrategy(BaseProduct):
    """Strategy for general solid parts."""
    product_type: ProductType = ProductType.SOLID

    # Geometry
    bounding_box: Dict[str, float] = {"x": 0, "y": 0, "z": 0}

    def estimate_volume(self) -> float:
        """Estimate from features."""
        import math
        total = 0.0
        for feature in self.features:
            params = feature.parameters
            if feature.type == FeatureType.EXTRUDE:
                # Cylinder approximation
                radius = params.get("radius", 10)
                depth = params.get("depth", 10)
                total += math.pi * radius**2 * depth
            elif feature.type == FeatureType.REVOLVE:
                # Torus/ring approximation
                pass
        return total


# Factory function
def create_strategy(product_type: str, **kwargs) -> BaseProduct:
    """Factory to create appropriate strategy type."""
    type_map = {
        "weldment": WeldmentStrategy,
        "sheet_metal": SheetMetalStrategy,
        "machining": MachiningStrategy,
        "assembly": AssemblyStrategy,
        "solid": SolidStrategy,
    }

    strategy_class = type_map.get(product_type.lower(), SolidStrategy)
    return strategy_class(**kwargs)


# Export all models
__all__ = [
    "ProductType",
    "FeatureType",
    "MaterialSpec",
    "Dimension",
    "Constraint",
    "Feature",
    "SuccessMetrics",
    "BaseProduct",
    "WeldmentStrategy",
    "SheetMetalStrategy",
    "MachiningStrategy",
    "AssemblyStrategy",
    "SolidStrategy",
    "create_strategy",
]
