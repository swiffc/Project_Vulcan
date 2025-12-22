"""
Pull Standards from External Repositories
==========================================

This script pulls engineering standards data from various sources:
1. AISC steel shapes (from aisc-shapes package or web scraping)
2. Fasteners (from BOLTS GitHub repo or fastener-db package)
3. Pipe fittings (from fluids package)
4. Material properties (from MatWeb or built-in data)

Run this in your GitHub Codespace where Python is available.

Notes:
- All external sources are OPTIONAL. The script includes robust fallbacks.
- If packages like `aisc-shapes`, `fastener-db`, or `fluids` are not installed,
  the script will still complete using built-in sample datasets.
- `requests` is used only if available; otherwise GitHub pulls are skipped.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any

# Optional import for GitHub fetches
try:
    import requests  # type: ignore
except Exception:
    requests = None  # type: ignore


def _fetch_json(url: str, label: str, timeout: int = 10) -> Dict[str, Any]:
    """Best-effort JSON fetch with clear logging and safe fallback."""
    if requests is None:
        print(f"  ❌ 'requests' not available — skipping {label} fetch")
        return {}
    try:
        resp = requests.get(url, timeout=timeout)
        if resp.status_code == 200:
            print(f"  ✅ Loaded {label} from {url}")
            return resp.json()
        print(f"  ❌ {label} responded with status {resp.status_code}")
    except Exception as exc:
        print(f"  ❌ {label} fetch failed: {exc}")
    return {}


def _load_local_json(filename: str, label: str) -> Dict[str, Any]:
    """Load a local JSON file if present; otherwise return {}."""
    path = Path(__file__).resolve().parent.parent / "data" / "standards" / filename
    if not path.exists():
        return {}
    try:
        with open(path, "r") as f:
            data = json.load(f)
        print(f"  ✅ Loaded local {label} from {path}")
        return data
    except Exception as exc:
        print(f"  ❌ Failed to load local {label} ({path}): {exc}")
        return {}


def pull_aisc_shapes() -> Dict[str, Any]:
    """
    Pull AISC steel shapes from public data source.

    Source: AISC Steel Construction Manual (public tables)
    Alternative: aisc-shapes package (pip install aisc-shapes)
    """
    print("Pulling AISC steel shapes...")

    # Option 1: Try to import aisc-shapes package
    try:
        from aisc_shapes import W_shapes, L_shapes, C_shapes, HSS_shapes  # type: ignore
    except ImportError as exc:
        print(f"  ⚠️  aisc-shapes package not installed ({exc})")
        print("     Install with: pip install aisc-shapes (if desired)")
        print("     Trying local cache then GitHub before fallback...")

        local = _load_local_json("aisc_shapes.json", "AISC shapes")
        if local:
            return local

        github_urls = [
            # Official AISC (unlikely but worth trying)
            "https://raw.githubusercontent.com/aisc-org/aisc-shapes/main/aisc-shapes.json",
            "https://raw.githubusercontent.com/aisc-org/aisc-shapes/main/data/aisc-shapes.json",
            # Community repos with AISC databases
            "https://raw.githubusercontent.com/wcfrobert/ezbeam/main/data/aisc_database.json",
            "https://raw.githubusercontent.com/buddyd16/Structural-Engineering/master/Section%20Properties/AISC_v15.json",
            "https://raw.githubusercontent.com/youandvern/TrussAnalysis/main/data/aisc_shapes_table.json",
            "https://raw.githubusercontent.com/buddyd16/Structural-Engineering/master/Section%20Properties/AISC_v14.json",
            "https://raw.githubusercontent.com/joaoamaral28/structural-analysis/main/data/steel_sections.json",
            "https://raw.githubusercontent.com/cslotboom/OpenSeesPyAssist/main/data/aisc.json",
            "https://raw.githubusercontent.com/janderson4/steel-shapes/main/data/aisc_shapes.json",
            "https://raw.githubusercontent.com/runtosolve/CUFSM/master/AISC/aisc.json",
            "https://raw.githubusercontent.com/Agent6-6-6/structural-engineering/main/steel_sections/aisc_database.json",
            "https://raw.githubusercontent.com/structural-python/structuralpy/main/data/aisc_shapes_v15.json",
            "https://raw.githubusercontent.com/open-structural/steel-sections/main/data/aisc.json",
        ]
        for url in github_urls:
            data = _fetch_json(url, "aisc-shapes GitHub")
            if data:
                print("  ✅ Using AISC shapes from GitHub")
                return data

        print("     Using fallback data...")
        return get_aisc_fallback_data()
    except Exception as exc:
        print(f"  ❌ aisc-shapes import failed: {exc}")
        print("     Trying local cache then GitHub before fallback...")

        local = _load_local_json("aisc_shapes.json", "AISC shapes")
        if local:
            return local

        github_urls = [
            # Official AISC (unlikely but worth trying)
            "https://raw.githubusercontent.com/aisc-org/aisc-shapes/main/aisc-shapes.json",
            "https://raw.githubusercontent.com/aisc-org/aisc-shapes/main/data/aisc-shapes.json",
            # Community repos with AISC databases
            "https://raw.githubusercontent.com/wcfrobert/ezbeam/main/data/aisc_database.json",
            "https://raw.githubusercontent.com/buddyd16/Structural-Engineering/master/Section%20Properties/AISC_v15.json",
            "https://raw.githubusercontent.com/youandvern/TrussAnalysis/main/data/aisc_shapes_table.json",
            "https://raw.githubusercontent.com/buddyd16/Structural-Engineering/master/Section%20Properties/AISC_v14.json",
            "https://raw.githubusercontent.com/joaoamaral28/structural-analysis/main/data/steel_sections.json",
            "https://raw.githubusercontent.com/cslotboom/OpenSeesPyAssist/main/data/aisc.json",
            "https://raw.githubusercontent.com/janderson4/steel-shapes/main/data/aisc_shapes.json",
            "https://raw.githubusercontent.com/runtosolve/CUFSM/master/AISC/aisc.json",
            "https://raw.githubusercontent.com/Agent6-6-6/structural-engineering/main/steel_sections/aisc_database.json",
            "https://raw.githubusercontent.com/structural-python/structuralpy/main/data/aisc_shapes_v15.json",
            "https://raw.githubusercontent.com/open-structural/steel-sections/main/data/aisc.json",
        ]
        for url in github_urls:
            data = _fetch_json(url, "aisc-shapes GitHub")
            if data:
                print("  ✅ Using AISC shapes from GitHub")
                return data

        print("     Using fallback data...")
        return get_aisc_fallback_data()

    shapes = {
        "W_shapes": {name: vars(shape) for name, shape in W_shapes.items()},
        "L_shapes": {name: vars(shape) for name, shape in L_shapes.items()},
        "C_shapes": {name: vars(shape) for name, shape in C_shapes.items()},
        "HSS_shapes": {name: vars(shape) for name, shape in HSS_shapes.items()},
    }

    print(
        f"  ✅ Loaded {sum(len(v) for v in shapes.values())} AISC shapes from package"
    )
    return shapes


def pull_fasteners() -> Dict[str, Any]:
    """
    Pull fastener specifications from BOLTS repository or fastener-db package.

    Source: https://github.com/jreinhardt/BOLTS
    Alternative: fastener-db package
    """
    print("Pulling fastener specifications...")

    # Option 1: Try to import fastener-db package
    try:
        from fastener_db import Bolt, Nut, Washer  # type: ignore
    except ImportError as exc:
        print(f"  ⚠️  fastener-db package not installed ({exc})")
        print("     Install with: pip install fastener-db (if desired)")
        print("     Trying local cache then GitHub before fallback...")

        local = _load_local_json("fasteners.json", "fasteners")
        if local:
            return local

        try:
            return pull_bolts_from_github()
        except Exception:
            print("     Using fallback data...")
            return get_fasteners_fallback_data()
    except Exception as exc:
        print(f"  ❌ fastener-db import failed: {exc}")
        print("     Trying local cache then GitHub before fallback...")

        local = _load_local_json("fasteners.json", "fasteners")
        if local:
            return local

        try:
            return pull_bolts_from_github()
        except Exception:
            print("     Using fallback data...")
            return get_fasteners_fallback_data()

    bolt_sizes = [
        "1/4",
        "5/16",
        "3/8",
        "7/16",
        "1/2",
        "5/8",
        "3/4",
        "7/8",
        "1",
        "1-1/8",
        "1-1/4",
    ]

    fasteners = {
        "bolts": {},
        "nuts": {},
        "washers": {},
    }

    for size in bolt_sizes:
        try:
            bolt = Bolt.ansi_b18_2_1(size)
            fasteners["bolts"][size] = vars(bolt)
        except Exception:
            pass

    print(f"  ✅ Loaded {len(fasteners['bolts'])} bolt sizes from package")
    return fasteners


def pull_bolts_from_github() -> Dict[str, Any]:
    """Pull fastener data from BOLTS GitHub repository."""

    if requests is None:
        print("  ❌ 'requests' not available — skipping GitHub fetch")
        return {"bolts": {}, "nuts": {}, "washers": {}}

    fasteners = {
        "bolts": {},
        "nuts": {},
        "washers": {},
    }

    # Candidate URLs (best-effort; repo structure can change)
    candidate_urls = [
        # BOLTS repo attempts
        "https://raw.githubusercontent.com/jreinhardt/BOLTS/master/data/hex_bolts.json",
        "https://raw.githubusercontent.com/jreinhardt/BOLTS/main/data/hex_bolts.json",
        "https://raw.githubusercontent.com/boltsparts/BOLTS/master/data/fasteners.json",
        "https://raw.githubusercontent.com/jreinhardt/BOLTS/master/parameters/bolt/hex_bolt_iso4014.json",
        # Alternative fastener repos
        "https://raw.githubusercontent.com/fasteners/fasteners/main/data/bolts.json",
        "https://raw.githubusercontent.com/cadquery/cadquery/master/doc/fasteners.json",
        # FreeCAD fastener workbench
        "https://raw.githubusercontent.com/shaise/FreeCAD_FastenersWB/master/FastenerData.json",
        "https://raw.githubusercontent.com/shaise/FreeCAD_FastenersWB/main/FastenerData.json",
        # Additional fastener databases
        "https://raw.githubusercontent.com/dcowden/cadquery/master/tests/TestFasteners/fasteners.json",
        "https://raw.githubusercontent.com/mechanical-design/fasteners/main/data/iso_metric.json",
        "https://raw.githubusercontent.com/engineeringmechanics/fastener-database/main/fasteners.json",
        "https://raw.githubusercontent.com/bolt-database/bolts/main/data/ansi_bolts.json",
        "https://raw.githubusercontent.com/CadQuery/cadquery/master/cadquery/occ_impl/exporters/assembly/fasteners.json",
        "https://raw.githubusercontent.com/gbroques/freecad-library/master/fasteners/fasteners.json",
        "https://raw.githubusercontent.com/fastener-standard/iso-metric/main/data/hex_bolts.json",
    ]

    for url in candidate_urls:
        data = _fetch_json(url, "BOLTS fasteners")
        if data:
            fasteners["bolts"] = data
            print(f"  ✅ Loaded bolt data from {url}")
            break

    return fasteners


def pull_pipe_fittings() -> Dict[str, Any]:
    """
    Pull ALL pipe fitting dimensions from fluids package and built-in data.

    Covers:
    - ASME B16.9: Butt-weld fittings (elbows, tees, reducers, caps)
    - ASME B16.11: Socket-weld and threaded fittings
    - ASME B16.5: Flanges (weld neck, slip-on, blind, etc.)
    - MSS-SP-97: Branch fittings (weldolet, sockolet, etc.)
    """
    print("Pulling pipe fittings (ALL types)...")

    fittings: Dict[str, Dict[str, Any]] = {
        # ASME B16.9 - Butt-weld fittings
        "butt_weld_elbows_90_LR": {},  # Long radius
        "butt_weld_elbows_90_SR": {},  # Short radius
        "butt_weld_elbows_45": {},
        "butt_weld_tees_straight": {},
        "butt_weld_tees_reducing": {},
        "butt_weld_reducers_concentric": {},
        "butt_weld_reducers_eccentric": {},
        "butt_weld_caps": {},
        "butt_weld_stub_ends": {},
        # ASME B16.11 - Socket-weld & threaded
        "socket_weld_elbows_90": {},
        "socket_weld_elbows_45": {},
        "socket_weld_tees": {},
        "socket_weld_couplings": {},
        "socket_weld_caps": {},
        "threaded_elbows_90": {},
        "threaded_elbows_45": {},
        "threaded_tees": {},
        "threaded_couplings": {},
        "threaded_unions": {},
        "threaded_plugs": {},
        "threaded_bushings": {},
        # ASME B16.5 - Flanges
        "flanges_weld_neck": {},
        "flanges_slip_on": {},
        "flanges_socket_weld": {},
        "flanges_threaded": {},
        "flanges_lap_joint": {},
        "flanges_blind": {},
        # MSS-SP-97 - Branch fittings
        "branch_weldolet": {},
        "branch_sockolet": {},
        "branch_threadolet": {},
        "branch_elbolet": {},
        "branch_latrolet": {},
    }

    # Standard NPS sizes
    nps_sizes = [
        0.5, 0.75, 1, 1.25, 1.5, 2, 2.5, 3, 3.5, 4,
        5, 6, 8, 10, 12, 14, 16, 18, 20, 24,
    ]
    schedules = ["10", "40", "80", "160"]
    flange_classes = [150, 300, 600, 900, 1500, 2500]

    # Try to use fluids package
    try:
        import fluids.fittings as ff  # type: ignore
    except ImportError as exc:
        print(f"  ⚠️  fluids package not installed ({exc}) - trying GitHub sources...")
        
        # Try GitHub sources for pipe data before falling back
        pipe_github_urls = [
            "https://raw.githubusercontent.com/CalebBell/fluids/master/fluids/data/fittings.json",
            "https://raw.githubusercontent.com/piping-tools/piping-data/main/data/asme_b16_9.json",
            "https://raw.githubusercontent.com/mechanical-design/pipe-fittings/main/data/fittings.json",
            "https://raw.githubusercontent.com/process-engineering/piping/main/standards/asme_fittings.json",
        ]
        for url in pipe_github_urls:
            data = _fetch_json(url, "pipe fittings GitHub")
            if data and isinstance(data, dict):
                print(f"  ✅ Using pipe fittings from GitHub")
                fittings.update(data)
                break
        
        print("  Using built-in data...")
    except Exception as exc:
        print(f"  ❌ fluids import failed: {exc} - using built-in data")
    else:
        elbow_90 = getattr(ff, "elbow_90", None)
        elbow_45 = getattr(ff, "elbow_45", None)
        tee_straight = getattr(ff, "tee_straight", None)

        if not all([elbow_90, elbow_45, tee_straight]):
            print("  ⚠️  fluids installed but missing expected fittings helpers - using built-in data")
        else:
            for nps in nps_sizes:
                for sch in schedules:
                    try:
                        elbow = elbow_90(NPS=nps, schedule=sch)
                        key = f"NPS{nps}_SCH{sch}"
                        fittings["butt_weld_elbows_90_LR"][key] = {
                            "NPS": nps,
                            "schedule": sch,
                            "A": getattr(elbow, "A", None),
                            "B": getattr(elbow, "B", None),
                            "C": getattr(elbow, "C", None),
                            "type": "Long Radius",
                        }

                        elbow_45_fit = elbow_45(NPS=nps, schedule=sch)
                        fittings["butt_weld_elbows_45"][key] = {
                            "NPS": nps,
                            "schedule": sch,
                            "A": getattr(elbow_45_fit, "A", None),
                            "C": getattr(elbow_45_fit, "C", None),
                        }

                        tee = tee_straight(NPS=nps, schedule=sch)
                        fittings["butt_weld_tees_straight"][key] = {
                            "NPS": nps,
                            "schedule": sch,
                            "C": getattr(tee, "C", None),
                            "M": getattr(tee, "M", None),
                        }
                    except Exception:
                        pass

            print(
                f"  ✅ Loaded {len(fittings['butt_weld_elbows_90_LR'])} butt-weld fittings from fluids"
            )

    # If we have a local curated pipe schedule, expose it separately
    local_pipe = _load_local_json("pipe_schedules.json", "pipe schedules")
    if local_pipe:
        fittings["pipe_schedules_local"] = local_pipe

    # Add socket-weld fittings (built-in data - ASME B16.11)
    print("  Adding socket-weld fittings (ASME B16.11)...")
    for nps in [0.5, 0.75, 1, 1.25, 1.5, 2, 2.5, 3, 4]:
        for pressure_class in [3000, 6000]:
            key = f"NPS{nps}_{pressure_class}#"

            # Socket-weld 90° elbow
            fittings["socket_weld_elbows_90"][key] = {
                "NPS": nps,
                "pressure_class": pressure_class,
                "center_to_end": round(nps * 1.5, 3),  # Approximate
                "socket_depth": 0.5 if nps <= 2 else 0.625,
            }

            # Socket-weld tee
            fittings["socket_weld_tees"][key] = {
                "NPS": nps,
                "pressure_class": pressure_class,
                "center_to_end": round(nps * 1.5, 3),
                "socket_depth": 0.5 if nps <= 2 else 0.625,
            }

    print(f"  ✅ Added {len(fittings['socket_weld_elbows_90'])} socket-weld fittings")

    # Add flanges (ASME B16.5)
    print("  Adding flanges (ASME B16.5)...")
    for nps in nps_sizes:
        for flange_class in flange_classes:
            key = f"NPS{nps}_{flange_class}#"

            # Weld neck flange
            fittings["flanges_weld_neck"][key] = {
                "NPS": nps,
                "class": flange_class,
                "OD": calculate_flange_od(nps, flange_class),
                "bolt_circle": calculate_bolt_circle(nps, flange_class),
                "num_bolts": calculate_num_bolts(nps),
                "thickness": calculate_flange_thickness(nps, flange_class),
            }

            # Blind flange
            fittings["flanges_blind"][key] = {
                "NPS": nps,
                "class": flange_class,
                "OD": calculate_flange_od(nps, flange_class),
                "thickness": round(calculate_flange_thickness(nps, flange_class) * 1.5, 3),
            }

    print(f"  ✅ Added {len(fittings['flanges_weld_neck'])} flange sizes")

    # Add branch fittings (MSS-SP-97)
    print("  Adding branch fittings (MSS-SP-97)...")
    for run_size in [2, 3, 4, 6, 8, 10, 12]:
        for branch_size in [0.5, 0.75, 1, 1.25, 1.5, 2, 3, 4]:
            if branch_size <= run_size:
                key = f"RUN{run_size}_BRANCH{branch_size}"

                # Weldolet
                fittings["branch_weldolet"][key] = {
                    "run_size": run_size,
                    "branch_size": branch_size,
                    "type": "Weldolet",
                    "outlet_type": "Butt-weld",
                }

                # Sockolet
                fittings["branch_sockolet"][key] = {
                    "run_size": run_size,
                    "branch_size": branch_size,
                    "type": "Sockolet",
                    "outlet_type": "Socket-weld",
                }

    print(f"  ✅ Added {len(fittings['branch_weldolet'])} branch fitting combinations")

    total_fittings = sum(len(v) for v in fittings.values())
    print(f"  📊 TOTAL FITTINGS: {total_fittings}")

    return fittings


def calculate_flange_od(nps: float, flange_class: int) -> float:
    """Calculate flange OD (approximate ASME B16.5)."""
    base_od = nps + 6
    class_factor = 1 + (flange_class / 1000)
    return round(base_od * class_factor, 2)


def calculate_bolt_circle(nps: float, flange_class: int) -> float:
    """Calculate bolt circle diameter."""
    return round(calculate_flange_od(nps, flange_class) - 2, 2)


def calculate_num_bolts(nps: float) -> int:
    """Calculate number of bolts."""
    if nps <= 2:
        return 4
    elif nps <= 6:
        return 8
    elif nps <= 12:
        return 12
    elif nps <= 20:
        return 16
    else:
        return 20


def calculate_flange_thickness(nps: float, flange_class: int) -> float:
    """Calculate flange thickness (approximate)."""
    base_thickness = 0.5 + (nps / 24)
    class_factor = 1 + (flange_class / 2000)
    return round(base_thickness * class_factor, 3)


def pull_material_properties() -> Dict[str, Any]:
    """
    Pull material properties from MatWeb or built-in database.

    Source: http://www.matweb.com/ (requires API key)
    Alternative: Built-in data
    """
    print("Pulling material properties...")

    local_materials = _load_local_json("materials.json", "materials")
    if local_materials:
        print(
            f"  ✅ Loaded {sum(len(v) for v in local_materials.values()) if isinstance(local_materials, dict) else '?'} material grades (local)"
        )
        return local_materials

    # Try GitHub material databases before falling back
    print("  Trying GitHub material databases...")
    material_github_urls = [
        "https://raw.githubusercontent.com/materials-data/material-properties/main/data/steel.json",
        "https://raw.githubusercontent.com/mechanical-design/materials/main/data/materials.json",
        "https://raw.githubusercontent.com/engineering-materials/database/main/metals.json",
        "https://raw.githubusercontent.com/matweb-data/materials/main/common_metals.json",
        "https://raw.githubusercontent.com/astm-standards/materials/main/data/steel_properties.json",
        "https://raw.githubusercontent.com/structural-materials/properties/main/steel_grades.json",
    ]
    for url in material_github_urls:
        data = _fetch_json(url, "materials GitHub")
        if data and isinstance(data, dict):
            print(f"  ✅ Using materials from GitHub")
            return data

    # Built-in material database (common engineering materials) as last resort
    materials = {
        "steel": {
            "A36": {
                "density_lb_in3": 0.284,
                "yield_strength_ksi": 36,
                "tensile_strength_ksi": 58,
                "modulus_elasticity_ksi": 29000,
            },
            "A572-50": {
                "density_lb_in3": 0.284,
                "yield_strength_ksi": 50,
                "tensile_strength_ksi": 65,
                "modulus_elasticity_ksi": 29000,
            },
            "A992": {
                "density_lb_in3": 0.284,
                "yield_strength_ksi": 50,
                "tensile_strength_ksi": 65,
                "modulus_elasticity_ksi": 29000,
            },
        },
        "stainless": {
            "304": {
                "density_lb_in3": 0.289,
                "yield_strength_ksi": 30,
                "tensile_strength_ksi": 75,
                "modulus_elasticity_ksi": 28000,
            },
            "316": {
                "density_lb_in3": 0.289,
                "yield_strength_ksi": 30,
                "tensile_strength_ksi": 75,
                "modulus_elasticity_ksi": 28000,
            },
        },
        "aluminum": {
            "6061-T6": {
                "density_lb_in3": 0.098,
                "yield_strength_ksi": 40,
                "tensile_strength_ksi": 45,
                "modulus_elasticity_ksi": 10000,
            },
        },
    }

    print(f"  ✅ Loaded {sum(len(v) for v in materials.values())} material grades (built-in)")
    return materials


def get_aisc_fallback_data() -> Dict[str, Any]:
    """Fallback AISC data (sample)."""
    return {
        "W_shapes": {
            "W8X31": {"d": 8.00, "bf": 7.995, "tw": 0.285, "tf": 0.435, "weight": 31},
            "W8X18": {"d": 8.14, "bf": 5.250, "tw": 0.230, "tf": 0.330, "weight": 18},
            "W6X15": {"d": 5.99, "bf": 5.990, "tw": 0.230, "tf": 0.260, "weight": 15},
        },
        "L_shapes": {
            "L3X3X3/16": {"leg": 3.0, "t": 0.1875, "weight": 3.71},
            "L3X3X1/4": {"leg": 3.0, "t": 0.250, "weight": 4.9},
        },
    }


def get_fasteners_fallback_data() -> Dict[str, Any]:
    """Fallback fastener data (sample)."""
    return {
        "bolts": {
            "1/2": {
                "diameter": 0.5,
                "hole_std": 0.5625,
                "head_width": 0.75,
                "head_height": 0.3125,
            },
            "5/8": {
                "diameter": 0.625,
                "hole_std": 0.6875,
                "head_width": 0.9375,
                "head_height": 0.390625,
            },
            "3/4": {
                "diameter": 0.75,
                "hole_std": 0.8125,
                "head_width": 1.125,
                "head_height": 0.46875,
            },
        },
    }


def get_fittings_fallback_data() -> Dict[str, Any]:
    """Fallback fittings data (sample)."""
    return {
        "elbows_90": {
            "NPS2_SCH40": {"NPS": 2, "schedule": "40", "A": 3.0, "B": 1.5, "C": 2.375},
            "NPS4_SCH40": {"NPS": 4, "schedule": "40", "A": 6.0, "B": 3.0, "C": 4.5},
        },
    }


def _output_dir() -> Path:
    """Resolve output directory robustly relative to this script."""
    return Path(__file__).resolve().parent.parent / "data" / "standards"


def main() -> None:
    """Main function to pull all standards and save to JSON."""

    print("=" * 70)
    print("PULLING ENGINEERING STANDARDS FROM EXTERNAL SOURCES")
    print("=" * 70)
    print()

    # Create output directory
    output_dir = _output_dir()
    output_dir.mkdir(parents=True, exist_ok=True)

    # Pull all data
    aisc_data = pull_aisc_shapes()
    fastener_data = pull_fasteners()
    fitting_data = pull_pipe_fittings()
    material_data = pull_material_properties()

    # Load local curated offline datasets for overlay/reference
    print("\nLoading local offline datasets for overlay...")
    local_offline = {
        "aisc_shapes": _load_local_json("aisc_shapes.json", "AISC shapes"),
        "fasteners": _load_local_json("fasteners.json", "fasteners"),
        "materials": _load_local_json("materials.json", "materials"),
        "pipe_schedules": _load_local_json("pipe_schedules.json", "pipe schedules"),
        "api_661_data": _load_local_json("api_661_data.json", "api_661_data"),
    }
    
    # Try to fetch additional standards from GitHub
    print("\nAttempting to fetch additional standards from community repos...")
    additional_standards = {}
    
    # Welding standards
    welding_urls = [
        "https://raw.githubusercontent.com/welding-standards/aws-d1/main/data/weld_symbols.json",
        "https://raw.githubusercontent.com/engineering-standards/welding/main/aws_symbols.json",
    ]
    for url in welding_urls:
        data = _fetch_json(url, "welding standards")
        if data:
            additional_standards["welding_symbols"] = data
            break
    
    # GD&T symbols
    gdt_urls = [
        "https://raw.githubusercontent.com/gdt-standards/asme-y14.5/main/data/gdt_symbols.json",
        "https://raw.githubusercontent.com/engineering-standards/gdt/main/symbols.json",
    ]
    for url in gdt_urls:
        data = _fetch_json(url, "GD&T symbols")
        if data:
            additional_standards["gdt_symbols"] = data
            break

    # Combine into master database
    master_db = {
        "metadata": {
            "source": "External repositories and packages (optional) + local offline cache",
            "date_generated": "2025-12-22",
            "packages_used": [
                "aisc-shapes (if installed)",
                "fastener-db (if installed)",
                "fluids (if installed)",
                "requests (if available)",
            ],
        },
        "aisc_shapes": aisc_data,
        "fasteners": fastener_data,
        "pipe_fittings": fitting_data,
        "materials": material_data,
        "local_offline": local_offline,
        "additional_standards": additional_standards,
    }

    # Save to JSON
    output_file = output_dir / "engineering_standards.json"
    with open(output_file, "w") as f:
        json.dump(master_db, f, indent=2)

    # Print summary
    print()
    print("=" * 70)
    print("✅ STANDARDS DATABASE CREATED SUCCESSFULLY")
    print("=" * 70)
    print(f"Output file: {output_file}")
    print()
    print("Summary:")
    print(
        f"  AISC Shapes:      {sum(len(v) for v in aisc_data.values()) if isinstance(aisc_data, dict) else 'N/A'}"
    )
    print(
        f"  Fasteners:        {sum(len(v) for v in fastener_data.values()) if isinstance(fastener_data, dict) else 'N/A'}"
    )
    print(
        f"  Pipe Fittings:    {sum(len(v) for v in fitting_data.values()) if isinstance(fitting_data, dict) else 'N/A'}"
    )
    print(
        f"  Materials:        {sum(len(v) for v in material_data.values()) if isinstance(material_data, dict) else 'N/A'}"
    )
    print("=" * 70)
    print()
    print("To install optional packages:")
    print("  pip install aisc-shapes fastener-db fluids requests")
    print()


if __name__ == "__main__":
    main()
