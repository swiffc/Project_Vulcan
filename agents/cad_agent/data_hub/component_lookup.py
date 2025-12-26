"""
Component Lookup Service
========================
Searchable database for engineering components with fuzzy matching.

Supports:
- Structural steel shapes (W, HSS, L, C)
- Fasteners (bolts, nuts, washers)
- Pipe schedules
- Flanges
- Materials
"""

import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from functools import lru_cache
from enum import Enum
import re


class ComponentCategory(str, Enum):
    """Component categories."""
    BEAM = "beam"
    COLUMN = "column"
    ANGLE = "angle"
    CHANNEL = "channel"
    HSS = "hss"
    PIPE = "pipe"
    BOLT = "bolt"
    NUT = "nut"
    WASHER = "washer"
    FLANGE = "flange"
    PLATE = "plate"
    SHEET = "sheet"


@dataclass
class ComponentSpec:
    """Specification for an engineering component."""
    category: str
    designation: str
    properties: Dict[str, Any]
    weight_per_ft: Optional[float] = None
    material: Optional[str] = None
    standard: Optional[str] = None
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "category": self.category,
            "designation": self.designation,
            "properties": self.properties,
            "weight_per_ft": self.weight_per_ft,
            "material": self.material,
            "standard": self.standard,
            "notes": self.notes,
        }


class ComponentLookup:
    """
    Searchable component database.

    Features:
    - Fuzzy matching for designations
    - Property-based filtering
    - Weight calculations
    - Cross-referencing
    """

    # AISC W-Shape Database (common sizes)
    W_SHAPES: Dict[str, Dict[str, float]] = {
        "W4X13": {"d": 4.16, "bf": 4.06, "tf": 0.345, "tw": 0.28, "wt": 13, "Ix": 11.3, "Zx": 5.46, "Sx": 5.43, "rx": 1.72},
        "W6X15": {"d": 5.99, "bf": 5.99, "tf": 0.26, "tw": 0.23, "wt": 15, "Ix": 29.1, "Zx": 10.8, "Sx": 9.72, "rx": 2.56},
        "W8X31": {"d": 8.00, "bf": 7.995, "tf": 0.435, "tw": 0.285, "wt": 31, "Ix": 110, "Zx": 30.4, "Sx": 27.5, "rx": 3.47},
        "W8X40": {"d": 8.25, "bf": 8.070, "tf": 0.560, "tw": 0.360, "wt": 40, "Ix": 146, "Zx": 39.8, "Sx": 35.5, "rx": 3.53},
        "W10X49": {"d": 9.98, "bf": 10.00, "tf": 0.56, "tw": 0.34, "wt": 49, "Ix": 272, "Zx": 60.4, "Sx": 54.6, "rx": 4.35},
        "W12X65": {"d": 12.12, "bf": 12.00, "tf": 0.605, "tw": 0.39, "wt": 65, "Ix": 533, "Zx": 96.8, "Sx": 87.9, "rx": 5.28},
        "W14X68": {"d": 14.04, "bf": 10.035, "tf": 0.72, "tw": 0.415, "wt": 68, "Ix": 723, "Zx": 115, "Sx": 103, "rx": 6.01},
        "W14X90": {"d": 14.02, "bf": 14.520, "tf": 0.71, "tw": 0.44, "wt": 90, "Ix": 999, "Zx": 157, "Sx": 143, "rx": 6.14},
        "W16X77": {"d": 16.52, "bf": 10.295, "tf": 0.76, "tw": 0.455, "wt": 77, "Ix": 1110, "Zx": 150, "Sx": 134, "rx": 7.00},
        "W16X100": {"d": 16.97, "bf": 10.425, "tf": 0.985, "tw": 0.585, "wt": 100, "Ix": 1490, "Zx": 198, "Sx": 175, "rx": 7.10},
        "W18X97": {"d": 18.59, "bf": 11.145, "tf": 0.87, "tw": 0.535, "wt": 97, "Ix": 1750, "Zx": 211, "Sx": 188, "rx": 7.82},
        "W21X111": {"d": 21.51, "bf": 12.340, "tf": 0.875, "tw": 0.55, "wt": 111, "Ix": 2670, "Zx": 279, "Sx": 249, "rx": 9.02},
        "W24X131": {"d": 24.48, "bf": 12.855, "tf": 0.96, "tw": 0.605, "wt": 131, "Ix": 4020, "Zx": 370, "Sx": 329, "rx": 10.2},
        "W27X146": {"d": 27.38, "bf": 13.965, "tf": 0.975, "tw": 0.605, "wt": 146, "Ix": 5630, "Zx": 464, "Sx": 411, "rx": 11.4},
        "W30X173": {"d": 30.44, "bf": 14.985, "tf": 1.065, "tw": 0.655, "wt": 173, "Ix": 8200, "Zx": 607, "Sx": 539, "rx": 12.7},
        "W36X300": {"d": 36.74, "bf": 16.655, "tf": 1.68, "tw": 0.945, "wt": 300, "Ix": 20300, "Zx": 1260, "Sx": 1110, "rx": 15.2},
    }

    # Bolt specifications
    BOLTS: Dict[str, Dict[str, Any]] = {
        "1/2": {"nominal_diameter": 0.5, "tpi": 13, "stress_area": 0.1419, "std_hole": 0.5625, "edge_rolled": 0.75, "edge_sheared": 0.875},
        "5/8": {"nominal_diameter": 0.625, "tpi": 11, "stress_area": 0.2260, "std_hole": 0.6875, "edge_rolled": 0.875, "edge_sheared": 1.125},
        "3/4": {"nominal_diameter": 0.75, "tpi": 10, "stress_area": 0.3340, "std_hole": 0.8125, "edge_rolled": 1.0, "edge_sheared": 1.25},
        "7/8": {"nominal_diameter": 0.875, "tpi": 9, "stress_area": 0.4617, "std_hole": 0.9375, "edge_rolled": 1.125, "edge_sheared": 1.5},
        "1": {"nominal_diameter": 1.0, "tpi": 8, "stress_area": 0.6057, "std_hole": 1.0625, "edge_rolled": 1.25, "edge_sheared": 1.75},
        "1-1/8": {"nominal_diameter": 1.125, "tpi": 7, "stress_area": 0.7633, "std_hole": 1.25, "edge_rolled": 1.5, "edge_sheared": 2.0},
        "1-1/4": {"nominal_diameter": 1.25, "tpi": 7, "stress_area": 0.9691, "std_hole": 1.375, "edge_rolled": 1.625, "edge_sheared": 2.25},
    }

    # Pipe schedules (NPS, OD, Schedule -> wall thickness)
    PIPE_SCHEDULES: Dict[str, Dict[str, Dict[str, float]]] = {
        "1/2": {"od": 0.840, "40": 0.109, "80": 0.147, "160": 0.187},
        "3/4": {"od": 1.050, "40": 0.113, "80": 0.154, "160": 0.218},
        "1": {"od": 1.315, "40": 0.133, "80": 0.179, "160": 0.250},
        "1-1/2": {"od": 1.900, "40": 0.145, "80": 0.200, "160": 0.281},
        "2": {"od": 2.375, "40": 0.154, "80": 0.218, "160": 0.343},
        "3": {"od": 3.500, "40": 0.216, "80": 0.300, "160": 0.437},
        "4": {"od": 4.500, "40": 0.237, "80": 0.337, "160": 0.531},
        "6": {"od": 6.625, "40": 0.280, "80": 0.432, "160": 0.718},
        "8": {"od": 8.625, "40": 0.322, "80": 0.500, "160": 0.906},
        "10": {"od": 10.75, "40": 0.365, "80": 0.593, "160": 1.125},
        "12": {"od": 12.75, "40": 0.406, "80": 0.687, "160": 1.312},
    }

    # Materials database
    MATERIALS: Dict[str, Dict[str, Any]] = {
        "A36": {"type": "carbon_steel", "Fy": 36000, "Fu": 58000, "E": 29000000, "density": 490},
        "A572-50": {"type": "carbon_steel", "Fy": 50000, "Fu": 65000, "E": 29000000, "density": 490},
        "A572-65": {"type": "carbon_steel", "Fy": 65000, "Fu": 80000, "E": 29000000, "density": 490},
        "A992": {"type": "carbon_steel", "Fy": 50000, "Fu": 65000, "E": 29000000, "density": 490},
        "A500B": {"type": "carbon_steel", "Fy": 42000, "Fu": 58000, "E": 29000000, "density": 490},
        "A106-B": {"type": "pipe_steel", "Fy": 35000, "Fu": 60000, "E": 29000000, "density": 490},
        "A516-70": {"type": "pressure_vessel", "Fy": 38000, "Fu": 70000, "E": 29000000, "density": 490},
        "304": {"type": "stainless", "Fy": 30000, "Fu": 75000, "E": 28000000, "density": 501},
        "316": {"type": "stainless", "Fy": 30000, "Fu": 75000, "E": 28000000, "density": 501},
        "6061-T6": {"type": "aluminum", "Fy": 35000, "Fu": 42000, "E": 10000000, "density": 169},
    }

    # Sheet metal gauges
    SHEET_GAUGES: Dict[str, float] = {
        "7": 0.1793, "8": 0.1644, "9": 0.1495, "10": 0.1345,
        "11": 0.1196, "12": 0.1046, "13": 0.0897, "14": 0.0747,
        "16": 0.0598, "18": 0.0478, "20": 0.0359, "22": 0.0299,
        "24": 0.0239, "26": 0.0179,
    }

    def __init__(self):
        """Initialize component lookup."""
        self._components: Dict[str, ComponentSpec] = {}
        self._build_component_index()

    def _build_component_index(self):
        """Build searchable index of all components."""
        # Index W-shapes
        for designation, props in self.W_SHAPES.items():
            self._components[designation] = ComponentSpec(
                category="beam",
                designation=designation,
                properties=props,
                weight_per_ft=props.get("wt"),
                material="A992",
                standard="AISC 360-16"
            )

        # Index bolts
        for size, props in self.BOLTS.items():
            self._components[f"BOLT-{size}"] = ComponentSpec(
                category="bolt",
                designation=size,
                properties=props,
                standard="AISC J3"
            )

        # Index materials
        for grade, props in self.MATERIALS.items():
            self._components[f"MAT-{grade}"] = ComponentSpec(
                category="material",
                designation=grade,
                properties=props,
                standard="ASTM"
            )

    # ==================== SEARCH METHODS ====================

    def search(self, query: str, category: Optional[str] = None) -> List[ComponentSpec]:
        """
        Search for components by designation or properties.

        Args:
            query: Search term
            category: Optional category filter

        Returns:
            List of matching ComponentSpec objects
        """
        query_upper = query.upper().replace(" ", "")
        results: List[Tuple[float, ComponentSpec]] = []

        for key, spec in self._components.items():
            if category and spec.category != category:
                continue

            score = self._match_score(query_upper, key, spec)
            if score > 0:
                results.append((score, spec))

        results.sort(key=lambda x: x[0], reverse=True)
        return [spec for _, spec in results]

    def _match_score(self, query: str, key: str, spec: ComponentSpec) -> float:
        """Calculate match score."""
        # Exact match
        if query == key or query == spec.designation.upper():
            return 1.0
        # Partial match
        if query in key or query in spec.designation.upper():
            return 0.7
        # Property match
        props_str = str(spec.properties).upper()
        if query in props_str:
            return 0.3
        return 0.0

    def fuzzy_search(self, query: str, threshold: float = 0.5) -> List[ComponentSpec]:
        """
        Fuzzy search with tolerance for typos.

        Args:
            query: Search term
            threshold: Minimum similarity score (0-1)

        Returns:
            List of matching ComponentSpec objects
        """
        query_upper = query.upper().replace(" ", "").replace("X", "X")
        results: List[Tuple[float, ComponentSpec]] = []

        for key, spec in self._components.items():
            designation = spec.designation.upper().replace(" ", "")

            # Calculate similarity
            similarity = self._levenshtein_similarity(query_upper, designation)

            if similarity >= threshold:
                results.append((similarity, spec))

        results.sort(key=lambda x: x[0], reverse=True)
        return [spec for _, spec in results[:10]]

    def _levenshtein_similarity(self, s1: str, s2: str) -> float:
        """Calculate Levenshtein similarity (0-1)."""
        if s1 == s2:
            return 1.0
        len1, len2 = len(s1), len(s2)
        if len1 == 0 or len2 == 0:
            return 0.0

        # Create distance matrix
        d = [[0] * (len2 + 1) for _ in range(len1 + 1)]
        for i in range(len1 + 1):
            d[i][0] = i
        for j in range(len2 + 1):
            d[0][j] = j

        for i in range(1, len1 + 1):
            for j in range(1, len2 + 1):
                cost = 0 if s1[i-1] == s2[j-1] else 1
                d[i][j] = min(d[i-1][j] + 1, d[i][j-1] + 1, d[i-1][j-1] + cost)

        distance = d[len1][len2]
        max_len = max(len1, len2)
        return 1.0 - (distance / max_len)

    # ==================== DIRECT LOOKUPS ====================

    @lru_cache(maxsize=200)
    def get_beam(self, designation: str) -> Optional[ComponentSpec]:
        """Get beam by designation."""
        key = designation.upper().replace(" ", "")
        return self._components.get(key)

    @lru_cache(maxsize=100)
    def get_bolt(self, size: str) -> Optional[ComponentSpec]:
        """Get bolt by size."""
        return self._components.get(f"BOLT-{size}")

    @lru_cache(maxsize=100)
    def get_material(self, grade: str) -> Optional[ComponentSpec]:
        """Get material by grade."""
        return self._components.get(f"MAT-{grade.upper()}")

    def get_pipe(self, nps: str, schedule: str = "40") -> Optional[Dict[str, float]]:
        """Get pipe dimensions."""
        nps_data = self.PIPE_SCHEDULES.get(nps)
        if nps_data:
            wall = nps_data.get(schedule)
            if wall:
                od = nps_data["od"]
                id_val = od - 2 * wall
                return {
                    "nps": nps,
                    "schedule": schedule,
                    "od": od,
                    "wall": wall,
                    "id": round(id_val, 4),
                }
        return None

    def get_gauge_thickness(self, gauge: str) -> Optional[float]:
        """Get sheet metal gauge thickness."""
        return self.SHEET_GAUGES.get(str(gauge))

    # ==================== WEIGHT CALCULATIONS ====================

    def calculate_beam_weight(self, designation: str, length_ft: float) -> Optional[Dict[str, float]]:
        """Calculate beam weight for given length."""
        spec = self.get_beam(designation)
        if spec and spec.weight_per_ft:
            total_weight = spec.weight_per_ft * length_ft
            return {
                "designation": designation,
                "weight_per_ft": spec.weight_per_ft,
                "length_ft": length_ft,
                "total_weight_lbs": round(total_weight, 1),
            }
        return None

    def calculate_pipe_weight(self, nps: str, schedule: str, length_ft: float,
                              material: str = "A106-B") -> Optional[Dict[str, float]]:
        """Calculate pipe weight."""
        pipe = self.get_pipe(nps, schedule)
        mat = self.MATERIALS.get(material.upper(), self.MATERIALS["A106-B"])

        if pipe:
            od = pipe["od"]
            id_val = pipe["id"]
            # Cross-sectional area (in^2)
            area = 3.14159 * (od**2 - id_val**2) / 4
            # Weight per foot (lbs/ft) = area * 12 * density / 1728
            weight_per_ft = area * 12 * mat["density"] / 1728
            total_weight = weight_per_ft * length_ft

            return {
                "nps": nps,
                "schedule": schedule,
                "od": od,
                "id": id_val,
                "weight_per_ft": round(weight_per_ft, 2),
                "length_ft": length_ft,
                "total_weight_lbs": round(total_weight, 1),
            }
        return None

    # ==================== LISTING ====================

    def list_beams(self) -> List[str]:
        """List all available beam designations."""
        return sorted(self.W_SHAPES.keys())

    def list_bolts(self) -> List[str]:
        """List all available bolt sizes."""
        return sorted(self.BOLTS.keys())

    def list_materials(self) -> List[str]:
        """List all available materials."""
        return sorted(self.MATERIALS.keys())

    def list_pipe_sizes(self) -> List[str]:
        """List all available pipe NPS sizes."""
        return sorted(self.PIPE_SCHEDULES.keys(), key=lambda x: float(x.split("-")[0]) if "-" not in x else float(x.split("-")[0]) + 0.5)

    def list_gauges(self) -> List[str]:
        """List all available sheet gauges."""
        return sorted(self.SHEET_GAUGES.keys(), key=int)
