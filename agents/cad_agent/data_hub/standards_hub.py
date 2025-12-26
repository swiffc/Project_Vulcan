"""
Unified Standards Hub
=====================
Single access point for all engineering standards with search capabilities.

Features:
- Unified search across all standards (AISC, ASME, AWS, API, TEMA, NEMA)
- Fuzzy matching for component lookups
- Standards cross-referencing
- Cached queries for performance
"""

import json
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional, Union
from functools import lru_cache
from enum import Enum


class StandardType(str, Enum):
    """Engineering standards supported."""
    AISC = "aisc"           # Structural steel
    ASME = "asme"           # Pressure vessels, piping
    AWS = "aws"             # Welding
    API = "api"             # Petroleum, heat exchangers
    TEMA = "tema"           # Shell & tube exchangers
    NEMA = "nema"           # Motors
    OSHA = "osha"           # Safety
    SSPC = "sspc"           # Coatings
    ASTM = "astm"           # Materials


@dataclass
class StandardsSearchResult:
    """Search result from standards database."""
    standard: str
    category: str
    item_type: str
    designation: str
    properties: Dict[str, Any]
    reference: Optional[str] = None
    relevance_score: float = 1.0


@dataclass
class StandardsReference:
    """Reference to a specific standard clause."""
    standard: str
    section: str
    title: str
    description: str
    values: Dict[str, Any] = field(default_factory=dict)
    notes: List[str] = field(default_factory=list)


class StandardsHub:
    """
    Unified hub for all engineering standards data.

    Provides:
    - Component lookups (beams, bolts, pipes, etc.)
    - Standards references (clauses, tables, formulas)
    - Cross-standard search
    - Property validation
    """

    def __init__(self, data_dir: Optional[Path] = None):
        """Initialize with optional custom data directory."""
        if data_dir:
            self.data_dir = Path(data_dir)
        else:
            # Default to data/standards
            self.data_dir = Path(__file__).parent.parent.parent.parent.parent / "data" / "standards"

        self._cache: Dict[str, Any] = {}
        self._load_all_standards()

    def _load_all_standards(self):
        """Load all standards data into memory."""
        # AISC Shapes
        self._aisc_shapes = self._load_json("aisc_shapes.json", {})
        self._aisc_structural = self._load_json("aisc_structural_shapes.json", {})

        # Fasteners
        self._fasteners = self._load_json("fasteners.json", {})

        # Materials
        self._materials = self._load_json("materials.json", {})

        # Pipe schedules
        self._pipes = self._load_json("pipe_schedules.json", {})

        # API 661 ACHE data
        self._api661 = self._load_json("api_661_data.json", {})

        # Engineering standards
        self._engineering = self._load_json("engineering_standards.json", {})

        # Bend radius tables
        self._bend_radius = self._load_json("bend_radius_tables.json", {})

        # Build unified index
        self._build_search_index()

    def _load_json(self, filename: str, default: Any) -> Any:
        """Load JSON file with fallback."""
        filepath = self.data_dir / filename
        if filepath.exists():
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return default
        return default

    def _build_search_index(self):
        """Build searchable index across all standards."""
        self._index: Dict[str, List[StandardsSearchResult]] = {
            "beams": [],
            "bolts": [],
            "materials": [],
            "pipes": [],
            "flanges": [],
            "motors": [],
            "coatings": [],
        }

        # Index AISC shapes
        shapes = self._aisc_shapes.get("shapes", self._aisc_shapes)
        if isinstance(shapes, dict):
            for designation, props in shapes.items():
                self._index["beams"].append(StandardsSearchResult(
                    standard="AISC",
                    category="structural_shapes",
                    item_type="w_shape",
                    designation=designation,
                    properties=props if isinstance(props, dict) else {"value": props},
                    reference="AISC Steel Construction Manual"
                ))

        # Index fasteners
        bolts = self._fasteners.get("bolts", self._fasteners)
        if isinstance(bolts, dict):
            for size, props in bolts.items():
                self._index["bolts"].append(StandardsSearchResult(
                    standard="AISC",
                    category="fasteners",
                    item_type="bolt",
                    designation=size,
                    properties=props if isinstance(props, dict) else {"diameter": size},
                    reference="AISC Table J3.2"
                ))

        # Index materials
        mats = self._materials.get("steels", self._materials)
        if isinstance(mats, dict):
            for grade, props in mats.items():
                self._index["materials"].append(StandardsSearchResult(
                    standard="ASTM",
                    category="materials",
                    item_type="steel",
                    designation=grade,
                    properties=props if isinstance(props, dict) else {"grade": grade},
                    reference="ASTM Standards"
                ))

    # ==================== SEARCH METHODS ====================

    def search(self, query: str, standard: Optional[str] = None,
               category: Optional[str] = None, limit: int = 20) -> List[StandardsSearchResult]:
        """
        Search across all standards data.

        Args:
            query: Search term (designation, material, size, etc.)
            standard: Filter by standard (AISC, ASME, etc.)
            category: Filter by category (beams, bolts, materials)
            limit: Maximum results to return

        Returns:
            List of matching StandardsSearchResult objects
        """
        query_lower = query.lower()
        results: List[StandardsSearchResult] = []

        # Search all categories or specific one
        categories = [category] if category else list(self._index.keys())

        for cat in categories:
            if cat not in self._index:
                continue
            for item in self._index[cat]:
                # Filter by standard if specified
                if standard and item.standard.lower() != standard.lower():
                    continue

                # Score relevance
                score = self._calculate_relevance(query_lower, item)
                if score > 0:
                    item.relevance_score = score
                    results.append(item)

        # Sort by relevance and limit
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results[:limit]

    def _calculate_relevance(self, query: str, item: StandardsSearchResult) -> float:
        """Calculate relevance score for search result."""
        score = 0.0

        # Exact match on designation
        if query == item.designation.lower():
            score += 1.0
        # Partial match
        elif query in item.designation.lower():
            score += 0.7
        # Match in category
        elif query in item.category.lower():
            score += 0.3
        # Match in properties
        else:
            props_str = str(item.properties).lower()
            if query in props_str:
                score += 0.2

        return score

    # ==================== COMPONENT LOOKUPS ====================

    @lru_cache(maxsize=500)
    def get_beam(self, designation: str) -> Optional[Dict[str, Any]]:
        """
        Get W-shape beam properties.

        Args:
            designation: Beam designation (e.g., "W8X31", "W16X77")

        Returns:
            Dict with beam properties or None
        """
        designation = designation.upper().replace(" ", "")

        # Check aisc_shapes
        shapes = self._aisc_shapes.get("shapes", self._aisc_shapes)
        if isinstance(shapes, dict) and designation in shapes:
            return shapes[designation]

        # Check structural shapes
        if isinstance(self._aisc_structural, dict) and designation in self._aisc_structural:
            return self._aisc_structural[designation]

        return None

    @lru_cache(maxsize=200)
    def get_bolt(self, size: str) -> Optional[Dict[str, Any]]:
        """
        Get bolt properties.

        Args:
            size: Bolt size (e.g., "3/4", "1/2", "7/8")

        Returns:
            Dict with bolt properties or None
        """
        bolts = self._fasteners.get("bolts", self._fasteners)
        if isinstance(bolts, dict):
            return bolts.get(size)
        return None

    @lru_cache(maxsize=200)
    def get_material(self, grade: str) -> Optional[Dict[str, Any]]:
        """
        Get material properties.

        Args:
            grade: Material grade (e.g., "A36", "A992", "304")

        Returns:
            Dict with material properties or None
        """
        grade_upper = grade.upper()

        # Check steels
        steels = self._materials.get("steels", {})
        if grade_upper in steels:
            return steels[grade_upper]

        # Check stainless
        stainless = self._materials.get("stainless", {})
        if grade_upper in stainless:
            return stainless[grade_upper]

        # Check aluminum
        aluminum = self._materials.get("aluminum", {})
        if grade_upper in aluminum:
            return aluminum[grade_upper]

        return None

    @lru_cache(maxsize=300)
    def get_pipe(self, nps: str, schedule: str = "40") -> Optional[Dict[str, Any]]:
        """
        Get pipe dimensions per ASME B36.10.

        Args:
            nps: Nominal pipe size (e.g., "4", "6", "8")
            schedule: Pipe schedule (e.g., "40", "80", "160")

        Returns:
            Dict with pipe properties or None
        """
        pipes = self._pipes.get("schedules", self._pipes)
        if isinstance(pipes, dict):
            nps_data = pipes.get(nps, {})
            if isinstance(nps_data, dict):
                return nps_data.get(schedule)
        return None

    # ==================== STANDARDS REFERENCES ====================

    def get_standard_reference(self, standard: str, section: str) -> Optional[StandardsReference]:
        """
        Get reference to a specific standard clause.

        Args:
            standard: Standard name (e.g., "AISC", "AWS D1.1")
            section: Section reference (e.g., "J3.2", "5.8")

        Returns:
            StandardsReference object or None
        """
        refs = self._engineering.get("references", {})
        std_refs = refs.get(standard.upper(), {})
        if section in std_refs:
            ref_data = std_refs[section]
            return StandardsReference(
                standard=standard,
                section=section,
                title=ref_data.get("title", ""),
                description=ref_data.get("description", ""),
                values=ref_data.get("values", {}),
                notes=ref_data.get("notes", [])
            )
        return None

    def get_allowable_stress(self, material: str, temp_f: float = 100) -> Optional[float]:
        """
        Get allowable stress for material at temperature.

        Args:
            material: Material grade
            temp_f: Design temperature in Fahrenheit

        Returns:
            Allowable stress in psi or None
        """
        # Common allowable stresses (psi) at 100F
        ALLOWABLE_STRESSES = {
            "A36": 21600,
            "A992": 30000,
            "A572-50": 30000,
            "A572-65": 39000,
            "A106-B": 20000,
            "A516-70": 20000,
            "A312-304": 16700,
            "A312-316": 16700,
            "304": 16700,
            "316": 16700,
        }

        material_upper = material.upper().replace(" ", "")
        base_stress = ALLOWABLE_STRESSES.get(material_upper)

        if base_stress and temp_f > 100:
            # Temperature derating (simplified)
            if temp_f > 700:
                return base_stress * 0.7
            elif temp_f > 500:
                return base_stress * 0.85
            elif temp_f > 300:
                return base_stress * 0.95

        return base_stress

    # ==================== VALIDATION HELPERS ====================

    def validate_bolt_spacing(self, bolt_size: str, spacing: float) -> Dict[str, Any]:
        """
        Validate bolt spacing per AISC J3.3.

        Args:
            bolt_size: Bolt diameter (e.g., "3/4")
            spacing: Actual spacing in inches

        Returns:
            Dict with valid status, minimum required, and reference
        """
        bolt = self.get_bolt(bolt_size)
        if not bolt:
            return {"valid": False, "error": f"Unknown bolt size: {bolt_size}"}

        diameter = bolt.get("nominal_diameter", 0.75)
        min_spacing = 2.67 * diameter  # AISC J3.3

        return {
            "valid": spacing >= min_spacing,
            "actual": spacing,
            "minimum_required": round(min_spacing, 3),
            "bolt_diameter": diameter,
            "reference": "AISC 360-16 Section J3.3"
        }

    def validate_edge_distance(self, bolt_size: str, edge_dist: float,
                               edge_type: str = "rolled") -> Dict[str, Any]:
        """
        Validate edge distance per AISC J3.4.

        Args:
            bolt_size: Bolt diameter
            edge_dist: Actual edge distance in inches
            edge_type: "rolled" or "sheared"

        Returns:
            Dict with valid status and requirements
        """
        bolt = self.get_bolt(bolt_size)
        if not bolt:
            return {"valid": False, "error": f"Unknown bolt size: {bolt_size}"}

        edges = bolt.get("edge_distances", {})
        min_edge = edges.get(edge_type, edges.get("rolled", 1.0))

        return {
            "valid": edge_dist >= min_edge,
            "actual": edge_dist,
            "minimum_required": min_edge,
            "edge_type": edge_type,
            "reference": "AISC 360-16 Table J3.4"
        }

    def get_minimum_fillet_weld(self, thickness: float) -> Dict[str, Any]:
        """
        Get minimum fillet weld size per AWS D1.1 Table 5.8.

        Args:
            thickness: Base metal thickness in inches

        Returns:
            Dict with minimum weld size and reference
        """
        # AWS D1.1 Table 5.8
        if thickness <= 0.25:
            min_weld = 0.125  # 1/8"
        elif thickness <= 0.5:
            min_weld = 0.1875  # 3/16"
        elif thickness <= 0.75:
            min_weld = 0.25  # 1/4"
        else:
            min_weld = 0.3125  # 5/16"

        return {
            "base_metal_thickness": thickness,
            "minimum_fillet_size": min_weld,
            "minimum_fillet_size_fraction": self._to_fraction(min_weld),
            "reference": "AWS D1.1 Table 5.8"
        }

    def _to_fraction(self, decimal: float) -> str:
        """Convert decimal to fraction string."""
        fractions = {
            0.125: "1/8",
            0.1875: "3/16",
            0.25: "1/4",
            0.3125: "5/16",
            0.375: "3/8",
            0.5: "1/2",
            0.625: "5/8",
            0.75: "3/4",
        }
        return fractions.get(decimal, str(decimal))

    # ==================== EXPORT / SERIALIZATION ====================

    def to_dict(self) -> Dict[str, Any]:
        """Export standards summary as dictionary."""
        return {
            "standards_loaded": {
                "aisc_shapes": len(self._aisc_shapes.get("shapes", self._aisc_shapes)),
                "fasteners": len(self._fasteners.get("bolts", self._fasteners)),
                "materials": len(self._materials),
                "pipes": len(self._pipes.get("schedules", self._pipes)),
            },
            "index_counts": {k: len(v) for k, v in self._index.items()},
            "data_directory": str(self.data_dir),
        }


# Singleton instance
_standards_hub: Optional[StandardsHub] = None


def get_standards_hub() -> StandardsHub:
    """Get or create singleton StandardsHub instance."""
    global _standards_hub
    if _standards_hub is None:
        _standards_hub = StandardsHub()
    return _standards_hub
