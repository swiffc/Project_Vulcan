"""
Enhanced Standards Database with Offline JSON Lookups
=====================================================
Fast, offline engineering standards database using pre-built JSON files.
No API calls required - instant lookups from local data.

Features:
- AISC structural shapes (W, C, L, HSS)
- Fasteners (bolts, nuts, washers)
- Materials (steel, stainless, aluminum)
- Pipe schedules (NPS, OD, wall thickness)
- API 661 ACHE standards
- Sheet metal gauges
- All data cached in memory for performance

References:
- AISC Steel Manual v15
- AWS D1.1 Structural Welding
- ASME B16.5 Flanges
- API 661 Air-Cooled Heat Exchangers
- OSHA 1910 Safety Standards

Usage:
    from agents.cad_agent.adapters.standards_db_v2 import StandardsDB
    
    db = StandardsDB()
    
    # Instant lookups (no API calls!)
    beam = db.get_beam("W8X31")
    bolt = db.get_bolt("3/4")
    material = db.get_material("A36")
    pipe = db.get_pipe("6", schedule="40")
"""

import json
import logging
from pathlib import Path
from functools import lru_cache
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

logger = logging.getLogger("cad_agent.standards-db-v2")


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class BeamProperties:
    """AISC beam properties."""
    designation: str
    weight_per_ft: float
    area: float
    depth: float
    flange_width: float
    web_thickness: float
    flange_thickness: float
    Ix: float  # Strong axis moment of inertia
    Zx: float  # Plastic section modulus
    Sx: float  # Elastic section modulus
    rx: float  # Radius of gyration
    
    def calculate_weight(self, length_ft: float) -> float:
        """Calculate total weight for given length."""
        return self.weight_per_ft * length_ft


@dataclass
class BoltProperties:
    """Bolt specifications."""
    nominal_diameter: float
    threads_per_inch: int
    tensile_stress_area: float
    hole_size_standard: float
    edge_distance_min_sheared: float
    edge_distance_min_rolled: float
    A325_tensile_capacity_kips: float
    A490_tensile_capacity_kips: float


@dataclass
class MaterialProperties:
    """Material mechanical properties."""
    designation: str
    type: str
    yield_strength_ksi: float
    tensile_strength_ksi: float
    density_lb_in3: float
    max_temperature_F: float
    weldable: bool = True
    bend_radius_factor: float = 1.0


@dataclass
class PipeProperties:
    """Pipe dimensions and weight."""
    NPS: str
    OD: float
    schedule: str
    wall_thickness: float
    ID: float
    weight_per_ft: float


# =============================================================================
# STANDARDS DATABASE CLASS
# =============================================================================

class StandardsDB:
    """
    Fast offline standards database with JSON file caching.
    
    All data is loaded once and cached in memory for instant lookups.
    No external API calls required.
    """
    
    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialize standards database.
        
        Args:
            data_dir: Path to standards JSON files (defaults to project data/standards/)
        """
        if data_dir is None:
            # Default to project data directory
            data_dir = Path(__file__).parent.parent.parent.parent / "data" / "standards"
        
        self.data_dir = Path(data_dir)
        
        if not self.data_dir.exists():
            logger.warning(f"Standards directory not found: {self.data_dir}")
            logger.warning("Run scripts/build_standards_database.py to create it")
        
        logger.info(f"Standards database initialized: {self.data_dir}")
    
    # =========================================================================
    # AISC STRUCTURAL SHAPES
    # =========================================================================
    
    @lru_cache(maxsize=1)
    def _load_aisc_shapes(self) -> Dict[str, Any]:
        """Load AISC shapes database (cached)."""
        try:
            with open(self.data_dir / "aisc_shapes.json") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error("aisc_shapes.json not found")
            return {}
    
    def get_beam(self, designation: str) -> Optional[BeamProperties]:
        """
        Get AISC beam properties.
        
        Args:
            designation: Beam designation (e.g., "W8X31", "W8x31")
        
        Returns:
            BeamProperties or None if not found
        
        Example:
            >>> db = StandardsDB()
            >>> beam = db.get_beam("W8X31")
            >>> print(f"Weight: {beam.weight_per_ft} lb/ft")
            Weight: 31.0 lb/ft
        """
        shapes = self._load_aisc_shapes()
        normalized = designation.upper().replace("X", "X")
        
        data = shapes.get(normalized)
        if data:
            return BeamProperties(**{
                k: v for k, v in data.items()
                if k in BeamProperties.__annotations__
            })
        return None
    
    def verify_beam_weight(
        self,
        designation: str,
        length_ft: float,
        tolerance_pct: float = 5.0
    ) -> Dict[str, Any]:
        """
        Verify beam weight against calculated value.
        
        Args:
            designation: Beam size (e.g., "W8X31")
            length_ft: Beam length in feet
            tolerance_pct: Acceptable variance (default 5%)
        
        Returns:
            Dictionary with expected weight, tolerance, and pass/fail
        """
        beam = self.get_beam(designation)
        if not beam:
            return {
                "error": f"Unknown beam designation: {designation}",
                "pass": False
            }
        
        expected = beam.calculate_weight(length_ft)
        tol = expected * (tolerance_pct / 100.0)
        
        return {
            "expected_weight_lb": round(expected, 2),
            "tolerance_lb": round(tol, 2),
            "min_acceptable_lb": round(expected - tol, 2),
            "max_acceptable_lb": round(expected + tol, 2),
            "tolerance_pct": tolerance_pct
        }
    
    # =========================================================================
    # FASTENERS (BOLTS, NUTS, WASHERS)
    # =========================================================================
    
    @lru_cache(maxsize=1)
    def _load_fasteners(self) -> Dict[str, Any]:
        """Load fastener specifications (cached)."""
        try:
            with open(self.data_dir / "fasteners.json") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error("fasteners.json not found")
            return {"bolts": {}, "torque_specs": {}}
    
    def get_bolt(self, size: str) -> Optional[BoltProperties]:
        """
        Get bolt specifications.
        
        Args:
            size: Bolt size (e.g., "3/4", "1/2", "1")
        
        Returns:
            BoltProperties or None if not found
        
        Example:
            >>> db = StandardsDB()
            >>> bolt = db.get_bolt("3/4")
            >>> print(f"Hole size: {bolt.hole_size_standard}")
            Hole size: 0.8125
        """
        fasteners = self._load_fasteners()
        data = fasteners.get("bolts", {}).get(size)
        
        if data:
            return BoltProperties(**{
                k: v for k, v in data.items()
                if k in BoltProperties.__annotations__
            })
        return None
    
    def get_edge_distance(
        self,
        bolt_size: str,
        edge_type: str = "rolled"
    ) -> Optional[float]:
        """
        Get minimum edge distance for a bolt.
        
        Args:
            bolt_size: Bolt size (e.g., "3/4")
            edge_type: "rolled" or "sheared" edge
        
        Returns:
            Minimum edge distance in inches
        """
        bolt = self.get_bolt(bolt_size)
        if not bolt:
            return None
        
        if edge_type.lower() == "rolled":
            return bolt.edge_distance_min_rolled
        else:
            return bolt.edge_distance_min_sheared
    
    def get_torque_spec(self, size: str, lubricated: bool = True) -> Optional[float]:
        """
        Get recommended bolt torque.
        
        Args:
            size: Bolt size
            lubricated: True if threads are lubricated
        
        Returns:
            Torque in ft-lbs
        """
        fasteners = self._load_fasteners()
        spec = fasteners.get("torque_specs", {}).get(size)
        
        if spec:
            return spec.get("lubricated_ftlb" if lubricated else "dry_ftlb")
        return None
    
    # =========================================================================
    # MATERIALS
    # =========================================================================
    
    @lru_cache(maxsize=1)
    def _load_materials(self) -> Dict[str, Any]:
        """Load material properties (cached)."""
        try:
            with open(self.data_dir / "materials.json") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error("materials.json not found")
            return {}
    
    def get_material(self, designation: str) -> Optional[MaterialProperties]:
        """
        Get material properties.
        
        Args:
            designation: Material grade (e.g., "A36", "304", "A572-50")
        
        Returns:
            MaterialProperties or None if not found
        
        Example:
            >>> db = StandardsDB()
            >>> mat = db.get_material("A36")
            >>> print(f"Yield: {mat.yield_strength_ksi} ksi")
            Yield: 36 ksi
        """
        materials = self._load_materials()
        
        # Search across all material categories
        for category in materials.values():
            if isinstance(category, dict):
                for key, data in category.items():
                    if key.upper() == designation.upper() or \
                       data.get("designation", "").upper() == designation.upper():
                        return MaterialProperties(**{
                            k: v for k, v in data.items()
                            if k in MaterialProperties.__annotations__
                        })
        return None
    
    def get_density(self, material: str) -> Optional[float]:
        """Get material density in lb/in³."""
        mat = self.get_material(material)
        return mat.density_lb_in3 if mat else None
    
    def get_bend_factor(self, material: str) -> float:
        """Get bend radius factor (multiplier × thickness)."""
        mat = self.get_material(material)
        return mat.bend_radius_factor if mat else 1.0
    
    def get_sheet_gauge_thickness(self, gauge: str) -> Optional[float]:
        """
        Get sheet metal thickness for a gauge.
        
        Args:
            gauge: Gauge number (e.g., "10GA", "12GA", "14")
        
        Returns:
            Thickness in inches
        """
        materials = self._load_materials()
        gauges = materials.get("sheet_gauges", {})
        
        # Normalize gauge format
        gauge_str = str(gauge).upper().replace("GA", "").strip() + "GA"
        
        spec = gauges.get(gauge_str)
        return spec.get("thickness_in") if spec else None
    
    # =========================================================================
    # PIPE SCHEDULES
    # =========================================================================
    
    @lru_cache(maxsize=1)
    def _load_pipe_schedules(self) -> Dict[str, Any]:
        """Load pipe schedule data (cached)."""
        try:
            with open(self.data_dir / "pipe_schedules.json") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error("pipe_schedules.json not found")
            return {"pipe_sizes": {}}
    
    def get_pipe(
        self,
        nps: str,
        schedule: str = "40"
    ) -> Optional[PipeProperties]:
        """
        Get pipe dimensions and weight.
        
        Args:
            nps: Nominal pipe size (e.g., "6", "8", "1/2")
            schedule: Pipe schedule ("40", "80", "160", "XXS")
        
        Returns:
            PipeProperties or None if not found
        
        Example:
            >>> db = StandardsDB()
            >>> pipe = db.get_pipe("6", schedule="40")
            >>> print(f"OD: {pipe.OD}, Wall: {pipe.wall_thickness}")
            OD: 6.625, Wall: 0.280
        """
        pipes = self._load_pipe_schedules()
        pipe_data = pipes.get("pipe_sizes", {}).get(nps)
        
        if not pipe_data:
            return None
        
        sched_data = pipe_data.get("schedules", {}).get(schedule)
        if not sched_data:
            return None
        
        return PipeProperties(
            NPS=nps,
            OD=pipe_data["OD"],
            schedule=schedule,
            **sched_data
        )
    
    # =========================================================================
    # API 661 ACHE STANDARDS
    # =========================================================================
    
    @lru_cache(maxsize=1)
    def _load_api_661(self) -> Dict[str, Any]:
        """Load API 661 data (cached)."""
        try:
            with open(self.data_dir / "api_661_data.json") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error("api_661_data.json not found")
            return {}
    
    def get_fan_tip_clearance(self, fan_diameter_ft: float) -> Optional[float]:
        """
        Get maximum fan tip clearance per API 661.
        
        Args:
            fan_diameter_ft: Fan diameter in feet
        
        Returns:
            Maximum clearance in inches
        """
        api_data = self._load_api_661()
        clearances = api_data.get("fan_tip_clearances", {})
        
        for key, spec in clearances.items():
            if spec["min_dia_ft"] <= fan_diameter_ft <= spec["max_dia_ft"]:
                return spec["max_clearance_in"]
        
        return None
    
    def get_osha_requirements(self, component: str) -> Optional[Dict[str, Any]]:
        """
        Get OSHA requirements for platforms, ladders, stairs.
        
        Args:
            component: "platforms", "ladders", or "stairs"
        
        Returns:
            Dictionary of OSHA requirements
        """
        api_data = self._load_api_661()
        return api_data.get("osha_requirements", {}).get(component)
    
    # =========================================================================
    # VALIDATION HELPERS
    # =========================================================================
    
    def validate_weight(
        self,
        item_type: str,
        designation: str,
        length_ft: float,
        actual_weight_lb: float,
        tolerance_pct: float = 5.0
    ) -> Dict[str, Any]:
        """
        Validate weight against standard.
        
        Args:
            item_type: "beam", "pipe", etc.
            designation: Item designation
            length_ft: Length in feet
            actual_weight_lb: Actual weight from drawing
            tolerance_pct: Acceptable variance
        
        Returns:
            Validation result with pass/fail
        """
        if item_type.lower() == "beam":
            result = self.verify_beam_weight(designation, length_ft, tolerance_pct)
            if "error" not in result:
                result["actual_weight_lb"] = actual_weight_lb
                result["pass"] = (
                    result["min_acceptable_lb"] <= actual_weight_lb <= result["max_acceptable_lb"]
                )
                result["difference_lb"] = round(actual_weight_lb - result["expected_weight_lb"], 2)
                result["difference_pct"] = round(
                    (result["difference_lb"] / result["expected_weight_lb"]) * 100, 2
                )
            return result
        
        return {"error": f"Unknown item type: {item_type}"}
    
    def list_available_beams(self) -> List[str]:
        """Get list of all available beam designations."""
        shapes = self._load_aisc_shapes()
        return sorted(shapes.keys())
    
    def list_available_materials(self) -> Dict[str, List[str]]:
        """Get list of all available materials by category."""
        materials = self._load_materials()
        result = {}
        
        for category, items in materials.items():
            if isinstance(items, dict) and category != "sheet_gauges":
                result[category] = list(items.keys())
        
        return result


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

_standards_db_instance: Optional[StandardsDB] = None


def get_standards_db(data_dir: Optional[Path] = None) -> StandardsDB:
    """
    Get singleton standards database instance.
    
    Args:
        data_dir: Optional custom data directory
    
    Returns:
        StandardsDB instance
    """
    global _standards_db_instance
    
    if _standards_db_instance is None:
        _standards_db_instance = StandardsDB(data_dir)
    
    return _standards_db_instance


# =============================================================================
# CONVENIENCE FUNCTIONS (for backward compatibility)
# =============================================================================

def get_beam_properties(designation: str) -> Optional[Dict[str, Any]]:
    """Get beam properties (backward compatible)."""
    db = get_standards_db()
    beam = db.get_beam(designation)
    return beam.__dict__ if beam else None


def get_edge_distance(bolt_size: str, edge_type: str = "rolled") -> Optional[float]:
    """Get minimum edge distance (backward compatible)."""
    db = get_standards_db()
    return db.get_edge_distance(bolt_size, edge_type)


def get_density(material: str) -> float:
    """Get material density (backward compatible)."""
    db = get_standards_db()
    density = db.get_density(material)
    return density if density is not None else 0.284  # Default to steel


def calculate_beam_weight(designation: str, length_ft: float) -> Optional[float]:
    """Calculate beam weight (backward compatible)."""
    db = get_standards_db()
    beam = db.get_beam(designation)
    return beam.calculate_weight(length_ft) if beam else None


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "StandardsDB",
    "get_standards_db",
    "BeamProperties",
    "BoltProperties",
    "MaterialProperties",
    "PipeProperties",
    # Backward compatible functions
    "get_beam_properties",
    "get_edge_distance",
    "get_density",
    "calculate_beam_weight",
]
