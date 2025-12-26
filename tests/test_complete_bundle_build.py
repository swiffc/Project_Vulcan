"""
Complete ACHE Bundle Build Test
===============================
Simulates designing and validating a complete Air-Cooled Heat Exchanger bundle
through ALL Phase 25 validators. This is what the chatbot would do when asked
to "build a bundle and check for errors".

Bundle Spec: API 661 Induced Draft ACHE
- Service: Hot oil cooling
- Design Pressure: 150 psig
- Design Temperature: 450°F
- Tube Bundle: 4-pass, 1" OD x 12 BWG tubes
- Headers: Plug type, carbon steel
- Fins: Aluminum L-foot, 10 FPI
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, List

BASE_URL = "http://localhost:8000"

# =============================================================================
# BUNDLE DESIGN DATA
# =============================================================================

BUNDLE_DESIGN = {
    "project": {
        "name": "Hot Oil Cooler - Unit 150",
        "drawing_number": "ACHE-150-001",
        "revision": "B",  # Updated revision after fixes
        "client": "Refinery Corp",
        "service": "Hot Oil Cooling",
    },

    "process_conditions": {
        "fluid": "Thermal Oil",
        "flow_rate_lb_hr": 250000,
        "inlet_temp_f": 450,
        "outlet_temp_f": 200,
        "design_pressure_psig": 150,
        "design_temp_f": 500,
        "corrosion_allowance_in": 0.0625,
    },

    "tube_bundle": {
        "tube_od_in": 1.0,
        "tube_bwg": 12,
        "tube_wall_in": 0.109,
        "tube_length_ft": 30,
        "tube_pitch_in": 2.5,
        "tube_pattern": "triangular",
        "tube_count": 196,
        "passes": 4,
        "tube_material": "SA-179",
        "fin_material": "Aluminum 1100",
        "fin_type": "l_footed",
        "fin_height_in": 0.625,
        "fin_thickness_in": 0.016,
        "fins_per_inch": 10,
        # FIX: Added tube keepers and support details
        "tube_keepers": True,
        "keeper_type": "U-bolt",
        "tube_support_spacing_in": 48,
        "lateral_movement_provision": True,
        "expansion_provision": "floating_tubesheet",
    },

    "headers": {
        "type": "plug",
        "material": "SA-516-70",
        "thickness_in": 0.75,
        "width_in": 12,
        "length_in": 98,
        "tubesheet_thickness_in": 1.5,
        "tubesheet_material": "SA-516-70",
        "plug_material": "SA-105",
        "plug_size_in": 1.25,
        "plug_type": "shoulder",  # FIX: Specified shoulder type plugs
        "gasket_type": "spiral_wound",
        "nozzle_size_in": 6,
        "nozzle_rating": "150#",
        # FIX: Added vent and drain connections
        "vent_connection": "3/4\" NPT",
        "drain_connection": "1\" NPT",
        "vent_location": "high_point",
        "drain_location": "low_point",
    },

    "structural": {
        "tube_support_spacing_in": 48,  # FIX: Explicitly specified
        "tube_supports": 7,
        "support_material": "SA-36",
        "side_frame_size": "C6x8.2",
        "bundle_weight_lb": 8500,
        "lifting_lugs": 4,
        "lug_plate_thickness_in": 0.75,
        "lug_hole_diameter_in": 1.5,
        # FIX: Added air seals
        "air_seals": True,
        "seal_type": "P-strips",
        "seal_material": "Aluminum",
    },

    "fabrication": {
        "weld_procedure": "WPS-001",
        "weld_filler": "E7018",
        "pwht_required": True,
        "pwht_temp_f": 1100,
        "pwht_time_hr": 1,
        "pwht_documented": True,  # FIX: PWHT documentation
        "hydro_test_pressure_psig": 225,
        "nde_requirements": ["RT", "PT", "VT"],
        # FIX: Added RT for pressure welds
        "rt_pressure_welds": True,
        "rt_coverage": "100%",
    },

    "coatings": {
        "surface_prep": "SSPC-SP10",
        "primer": "Zinc-rich epoxy",
        "primer_dft_mils": 3,
        "intermediate": "Epoxy",
        "intermediate_dft_mils": 5,
        "topcoat": "Polyurethane",
        "topcoat_dft_mils": 2,
        "total_dft_mils": 10,
    },
}


def call_endpoint(name: str, endpoint: str, payload: Dict) -> Dict:
    """Call an endpoint and return results."""
    url = f"{BASE_URL}{endpoint}"
    start = time.perf_counter()

    try:
        response = requests.post(url, json=payload, timeout=30)
        elapsed_ms = (time.perf_counter() - start) * 1000

        if response.status_code == 200:
            return {
                "success": True,
                "time_ms": elapsed_ms,
                "data": response.json(),
                "error": None
            }
        else:
            return {
                "success": False,
                "time_ms": elapsed_ms,
                "data": None,
                "error": f"HTTP {response.status_code}: {response.text[:200]}"
            }
    except Exception as e:
        return {
            "success": False,
            "time_ms": (time.perf_counter() - start) * 1000,
            "data": None,
            "error": str(e)
        }


def run_complete_bundle_validation():
    """Run complete bundle validation through all endpoints."""

    print("=" * 80)
    print("COMPLETE ACHE BUNDLE BUILD & VALIDATION TEST")
    print("=" * 80)
    print(f"\nProject: {BUNDLE_DESIGN['project']['name']}")
    print(f"Drawing: {BUNDLE_DESIGN['project']['drawing_number']} Rev {BUNDLE_DESIGN['project']['revision']}")
    print(f"Service: {BUNDLE_DESIGN['project']['service']}")
    print(f"Design: {BUNDLE_DESIGN['process_conditions']['design_pressure_psig']} psig @ {BUNDLE_DESIGN['process_conditions']['design_temp_f']}°F")
    print(f"\nStarted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    results = {}
    all_issues = []

    # =========================================================================
    # 1. API 661 BUNDLE VALIDATION
    # =========================================================================
    print("\n[1/12] API 661 BUNDLE VALIDATION...")

    bundle_payload = {
        "tube_od": BUNDLE_DESIGN["tube_bundle"]["tube_od_in"],
        "tube_wall": BUNDLE_DESIGN["tube_bundle"]["tube_wall_in"],
        "tube_pitch": BUNDLE_DESIGN["tube_bundle"]["tube_pitch_in"],
        "tube_length": BUNDLE_DESIGN["tube_bundle"]["tube_length_ft"],
        "tube_material": BUNDLE_DESIGN["tube_bundle"]["tube_material"],
        "fin_height": BUNDLE_DESIGN["tube_bundle"]["fin_height_in"],
        "fin_density": BUNDLE_DESIGN["tube_bundle"]["fins_per_inch"],
        "header_type": BUNDLE_DESIGN["headers"]["type"],
        "design_pressure": BUNDLE_DESIGN["process_conditions"]["design_pressure_psig"],
        "design_temp": BUNDLE_DESIGN["process_conditions"]["design_temp_f"],
        # FIX: Added tube keeper and support details
        "tube_keepers": BUNDLE_DESIGN["tube_bundle"]["tube_keepers"],
        "tube_support_spacing": BUNDLE_DESIGN["tube_bundle"]["tube_support_spacing_in"],
        "lateral_movement_provision": BUNDLE_DESIGN["tube_bundle"]["lateral_movement_provision"],
        "plug_type": BUNDLE_DESIGN["headers"]["plug_type"],
        "vent_connection": BUNDLE_DESIGN["headers"]["vent_connection"],
        "drain_connection": BUNDLE_DESIGN["headers"]["drain_connection"],
    }

    result = call_endpoint("API661 Bundle", "/phase25/check-api661-bundle", bundle_payload)
    results["api661_bundle"] = result

    if result["success"]:
        data = result["data"]
        print(f"   [PASS] {result['time_ms']:.0f}ms")
        print(f"   Tube Pressure Rating: {data.get('tube_pressure_rating_psi', 'N/A')} psi")
        print(f"   Checks: {data.get('total_checks', 0)}, Passed: {data.get('passed', 0)}")
        if data.get("issues"):
            all_issues.extend([{"source": "API661 Bundle", **i} for i in data["issues"]])
    else:
        print(f"   [FAIL] {result['error'][:60]}")

    # =========================================================================
    # 2. API 661 FULL SCOPE VALIDATION
    # =========================================================================
    print("\n[2/12] API 661 FULL SCOPE VALIDATION...")

    full_payload = {
        "unit_type": "induced",
        "service": BUNDLE_DESIGN["project"]["service"],
        "design_pressure_psig": BUNDLE_DESIGN["process_conditions"]["design_pressure_psig"],
        "design_temp_f": BUNDLE_DESIGN["process_conditions"]["design_temp_f"],
        "tube_od_in": BUNDLE_DESIGN["tube_bundle"]["tube_od_in"],
        "tube_material": BUNDLE_DESIGN["tube_bundle"]["tube_material"],
        "header_type": BUNDLE_DESIGN["headers"]["type"],
        "header_material": BUNDLE_DESIGN["headers"]["material"],
        "fin_type": BUNDLE_DESIGN["tube_bundle"]["fin_type"],
        "fin_material": BUNDLE_DESIGN["tube_bundle"]["fin_material"],
        # FIX: Added air seals and thermal expansion
        "air_seals": BUNDLE_DESIGN["structural"]["air_seals"],
        "seal_type": BUNDLE_DESIGN["structural"]["seal_type"],
        "thermal_expansion_provision": BUNDLE_DESIGN["tube_bundle"]["expansion_provision"],
    }

    result = call_endpoint("API661 Full", "/phase25/check-api661-full", full_payload)
    results["api661_full"] = result

    if result["success"]:
        data = result["data"]
        print(f"   [PASS] {result['time_ms']:.0f}ms")
        print(f"   Checks: {data.get('total_checks', 0)}, Passed: {data.get('passed', 0)}, Warnings: {data.get('warnings', 0)}")
        if data.get("issues"):
            all_issues.extend([{"source": "API661 Full", **i} for i in data["issues"]])
    else:
        print(f"   [FAIL] {result['error'][:60]}")

    # =========================================================================
    # 3. ASME VIII PRESSURE VESSEL (Headers)
    # =========================================================================
    print("\n[3/12] ASME VIII HEADER VALIDATION...")

    asme_payload = {
        "inside_diameter_in": BUNDLE_DESIGN["headers"]["width_in"],
        "wall_thickness_in": BUNDLE_DESIGN["headers"]["thickness_in"],
        "design_pressure_psi": BUNDLE_DESIGN["process_conditions"]["design_pressure_psig"],
        "design_temp_f": BUNDLE_DESIGN["process_conditions"]["design_temp_f"],
        "material": BUNDLE_DESIGN["headers"]["material"],
        "corrosion_allowance_in": BUNDLE_DESIGN["process_conditions"]["corrosion_allowance_in"],
    }

    result = call_endpoint("ASME VIII", "/phase25/check-asme-viii", asme_payload)
    results["asme_viii"] = result

    if result["success"]:
        data = result["data"]
        print(f"   [PASS] {result['time_ms']:.0f}ms")
        print(f"   Required Thickness: {data.get('required_thickness_in', 'N/A')}\"")
        print(f"   MAWP: {data.get('mawp_psi', 'N/A')} psi")
        if data.get("issues"):
            all_issues.extend([{"source": "ASME VIII", **i} for i in data["issues"]])
    else:
        print(f"   [FAIL] {result['error'][:60]}")

    # =========================================================================
    # 4. MATERIALS & FINISHING VALIDATION
    # =========================================================================
    print("\n[4/12] MATERIALS & FINISHING VALIDATION...")

    materials_payload = {
        "material_spec": BUNDLE_DESIGN["headers"]["material"],
        "thickness_in": BUNDLE_DESIGN["headers"]["thickness_in"],
        "coating_system": "C3",  # Severe service
        "surface_prep": BUNDLE_DESIGN["coatings"]["surface_prep"],
        "service_environment": "severe",
        "service_life_years": 20,
        "mtr_required": True,
        "application": "pressure_vessel",
    }

    result = call_endpoint("Materials", "/phase25/check-materials", materials_payload)
    results["materials"] = result

    if result["success"]:
        data = result["data"]
        print(f"   [PASS] {result['time_ms']:.0f}ms")
        print(f"   Material Compatible: {data.get('material_compatible', 'N/A')}")
        print(f"   Weldability: {data.get('weldability_ok', 'N/A')}")
        if data.get("issues"):
            all_issues.extend([{"source": "Materials", **i} for i in data["issues"]])
    else:
        print(f"   [FAIL] {result['error'][:60]}")

    # =========================================================================
    # 5. SSPC COATING VALIDATION
    # =========================================================================
    print("\n[5/12] SSPC COATING VALIDATION...")

    coating_payload = {
        "surface_prep": BUNDLE_DESIGN["coatings"]["surface_prep"],
        "primer_type": "zinc_rich_epoxy",
        "primer_dft_mils": BUNDLE_DESIGN["coatings"]["primer_dft_mils"],
        "topcoat_type": "polyurethane",
        "topcoat_dft_mils": BUNDLE_DESIGN["coatings"]["topcoat_dft_mils"],
        "total_dft_mils": BUNDLE_DESIGN["coatings"]["total_dft_mils"],
        "environment": "C5-I",  # Industrial severe
        "substrate": "carbon_steel",
    }

    result = call_endpoint("SSPC Coating", "/phase25/check-sspc-coating", coating_payload)
    results["sspc_coating"] = result

    if result["success"]:
        data = result["data"]
        print(f"   [PASS] {result['time_ms']:.0f}ms")
        print(f"   System Adequate: {data.get('system_adequate', 'N/A')}")
        if data.get("issues"):
            all_issues.extend([{"source": "SSPC Coating", **i} for i in data["issues"]])
    else:
        print(f"   [FAIL] {result['error'][:60]}")

    # =========================================================================
    # 6. FABRICATION FEASIBILITY
    # =========================================================================
    print("\n[6/12] FABRICATION FEASIBILITY...")

    # Header plate fabrication
    fab_payload = {
        "thickness_in": BUNDLE_DESIGN["headers"]["thickness_in"],
        "length_in": BUNDLE_DESIGN["headers"]["length_in"],
        "width_in": BUNDLE_DESIGN["headers"]["width_in"],
        "holes": [
            # Tube holes (simplified - 196 tubes in pattern)
            {"diameter": BUNDLE_DESIGN["tube_bundle"]["tube_od_in"] + 0.0625, "x": i*2.5, "y": j*2.5}
            for i in range(14) for j in range(14)
        ],
        "slots": [],
        "bends": [],
        "notches": [],
        "process": "plasma",
    }

    result = call_endpoint("Fabrication", "/phase25/check-fabrication", fab_payload)
    results["fabrication"] = result

    if result["success"]:
        data = result["data"]
        print(f"   [PASS] {result['time_ms']:.0f}ms")
        print(f"   Checks: {data.get('total_checks', 0)}, Passed: {data.get('passed', 0)}")
        print(f"   Processed {len(fab_payload['holes'])} tube holes")
        if data.get("issues"):
            all_issues.extend([{"source": "Fabrication", **i} for i in data["issues"]])
    else:
        print(f"   [FAIL] {result['error'][:60]}")

    # =========================================================================
    # 7. STRUCTURAL CAPACITY (Side Frames)
    # =========================================================================
    print("\n[7/12] STRUCTURAL CAPACITY VALIDATION...")

    structural_payload = {
        "member_type": "channel",
        "member_size": BUNDLE_DESIGN["structural"]["side_frame_size"],
        "span_ft": BUNDLE_DESIGN["tube_bundle"]["tube_length_ft"],
        "load_type": "uniform",
        "load_value": BUNDLE_DESIGN["structural"]["bundle_weight_lb"] / 2,  # Per side
        "support_condition": "simple",
        "steel_grade": "A36",
        "unbraced_length_ft": 10,
    }

    result = call_endpoint("Structural", "/phase25/check-structural", structural_payload)
    results["structural"] = result

    if result["success"]:
        data = result["data"]
        print(f"   [PASS] {result['time_ms']:.0f}ms")
        print(f"   Utilization: {data.get('utilization_ratio', 0)*100:.1f}%")
        if data.get("issues"):
            all_issues.extend([{"source": "Structural", **i} for i in data["issues"]])
    else:
        print(f"   [FAIL] {result['error'][:60]}")

    # =========================================================================
    # 8. FASTENER VALIDATION (Plug Bolts)
    # =========================================================================
    print("\n[8/12] FASTENER VALIDATION...")

    fastener_payload = {
        "bolts": [
            {"diameter": 0.625, "grade": "A193-B7", "connection_type": "bearing", "hole_type": "STD"}
            for _ in range(BUNDLE_DESIGN["tube_bundle"]["tube_count"])  # One plug per tube
        ],
        "connection": {
            "grip_length": BUNDLE_DESIGN["headers"]["thickness_in"] + 0.25,
            "load_kips": BUNDLE_DESIGN["process_conditions"]["design_pressure_psig"] * 0.785 * 1.0**2 / 1000,
            "load_type": "tension",
            "edge_distance": 1.25,
            "bolt_spacing": 2.5,
        }
    }

    result = call_endpoint("Fasteners", "/phase25/check-fasteners", fastener_payload)
    results["fasteners"] = result

    if result["success"]:
        data = result["data"]
        print(f"   [PASS] {result['time_ms']:.0f}ms")
        print(f"   Torque: {data.get('calculated_torque_ft_lb', 0):.0f} ft-lb")
        print(f"   Validated {len(fastener_payload['bolts'])} plug bolts")
        if data.get("issues"):
            all_issues.extend([{"source": "Fasteners", **i} for i in data["issues"]])
    else:
        print(f"   [FAIL] {result['error'][:60]}")

    # =========================================================================
    # 9. RIGGING VALIDATION (Lifting Lugs)
    # =========================================================================
    print("\n[9/12] RIGGING & LIFTING VALIDATION...")

    rigging_payload = {
        "lug": {
            "plate_thickness": BUNDLE_DESIGN["structural"]["lug_plate_thickness_in"],
            "plate_width": 6,
            "hole_diameter": BUNDLE_DESIGN["structural"]["lug_hole_diameter_in"],
            "edge_distance": 2.25,
            "throat_width": 4,
            "material": "A36",
            "rated_load_lbs": BUNDLE_DESIGN["structural"]["bundle_weight_lb"] / BUNDLE_DESIGN["structural"]["lifting_lugs"] * 2,  # 2:1 factor
            "sling_angle_deg": 60,
            "weld_size": 0.375,
            "weld_length": 12,
            "load_class": "B",
        },
        "rigging": {
            "total_load_lbs": BUNDLE_DESIGN["structural"]["bundle_weight_lb"],
            "center_of_gravity": [BUNDLE_DESIGN["tube_bundle"]["tube_length_ft"] * 12 / 2,
                                  BUNDLE_DESIGN["headers"]["width_in"] / 2,
                                  12],
            "lift_points": [
                [24, 0, 0],
                [BUNDLE_DESIGN["tube_bundle"]["tube_length_ft"] * 12 - 24, 0, 0],
                [24, BUNDLE_DESIGN["headers"]["width_in"], 0],
                [BUNDLE_DESIGN["tube_bundle"]["tube_length_ft"] * 12 - 24, BUNDLE_DESIGN["headers"]["width_in"], 0],
            ]
        }
    }

    result = call_endpoint("Rigging", "/phase25/check-rigging", rigging_payload)
    results["rigging"] = result

    if result["success"]:
        data = result["data"]
        print(f"   [PASS] {result['time_ms']:.0f}ms")
        print(f"   Lug Capacity: {data.get('lug_capacity_lbs', 0):,.0f} lbs")
        print(f"   Design Factor: {data.get('design_factor', 0)}")
        if data.get("issues"):
            all_issues.extend([{"source": "Rigging", **i} for i in data["issues"]])
    else:
        print(f"   [FAIL] {result['error'][:60]}")

    # =========================================================================
    # 10. INSPECTION & QC VALIDATION
    # =========================================================================
    print("\n[10/12] INSPECTION & QC VALIDATION...")

    inspection_payload = {
        "drawing_number": BUNDLE_DESIGN["project"]["drawing_number"],
        "revision": BUNDLE_DESIGN["project"]["revision"],
        "code": "ASME IX",
        "welds": [
            {"type": "groove", "size": 0.75, "length": BUNDLE_DESIGN["headers"]["length_in"], "category": "critical"},  # Header seam
            {"type": "fillet", "size": 0.375, "length": 12 * BUNDLE_DESIGN["structural"]["lifting_lugs"], "category": "primary"},  # Lug welds
            {"type": "groove", "size": BUNDLE_DESIGN["tube_bundle"]["tube_wall_in"], "length": 3.14 * BUNDLE_DESIGN["tube_bundle"]["tube_od_in"] * BUNDLE_DESIGN["tube_bundle"]["tube_count"], "category": "critical"},  # Tube-to-tubesheet
        ]
    }

    result = call_endpoint("Inspection", "/phase25/check-inspection", inspection_payload)
    results["inspection"] = result

    if result["success"]:
        data = result["data"]
        print(f"   [PASS] {result['time_ms']:.0f}ms")
        print(f"   Checks: {data.get('total_checks', 0)}, Passed: {data.get('passed', 0)}")
        if data.get("issues"):
            all_issues.extend([{"source": "Inspection", **i} for i in data["issues"]])
    else:
        print(f"   [FAIL] {result['error'][:60]}")

    # =========================================================================
    # 11. DOCUMENTATION VALIDATION
    # =========================================================================
    print("\n[11/12] DOCUMENTATION VALIDATION...")

    doc_payload = {
        "title_block": {
            "drawing_number": BUNDLE_DESIGN["project"]["drawing_number"],
            "revision": BUNDLE_DESIGN["project"]["revision"],
            "title": f"{BUNDLE_DESIGN['project']['name']} - Tube Bundle Assembly",
            "scale": "1:10",
            "sheet": "1 of 5",
            "drawn_by": "CAD",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "checked_by": "ENG",
            "approved_by": "PM",
            "material": BUNDLE_DESIGN["headers"]["material"],
            "finish": "SSPC-SP10 + Paint",
        },
        "notes": {
            "general_notes": [
                "1. All dimensions in inches unless noted.",
                "2. All welds per ASME IX, WPS-001.",
                "3. Radiograph all pressure-retaining welds per ASME VIII.",
                "4. PWHT at 1100°F for 1 hour after welding.",
                "5. Hydrostatic test at 225 psig for 30 minutes.",
                "6. Surface prep SSPC-SP10, paint per spec.",
                f"7. Design pressure: {BUNDLE_DESIGN['process_conditions']['design_pressure_psig']} psig",
                f"8. Design temperature: {BUNDLE_DESIGN['process_conditions']['design_temp_f']}°F",
            ],
            "local_notes": [],
            "flag_notes": ["A - Critical weld, 100% RT required"],
        },
        "drawing_type": "weldment",
        "documentation_level": "industrial",
        "bom": [
            {"item": 1, "part_number": "TB-001", "description": "Finned Tube", "qty": BUNDLE_DESIGN["tube_bundle"]["tube_count"], "material": BUNDLE_DESIGN["tube_bundle"]["tube_material"]},
            {"item": 2, "part_number": "TS-001", "description": "Tubesheet", "qty": 2, "material": BUNDLE_DESIGN["headers"]["tubesheet_material"]},
            {"item": 3, "part_number": "HD-001", "description": "Header Box", "qty": 2, "material": BUNDLE_DESIGN["headers"]["material"]},
            {"item": 4, "part_number": "SF-001", "description": "Side Frame", "qty": 2, "material": BUNDLE_DESIGN["structural"]["support_material"]},
            {"item": 5, "part_number": "LL-001", "description": "Lifting Lug", "qty": BUNDLE_DESIGN["structural"]["lifting_lugs"], "material": "SA-36"},
            {"item": 6, "part_number": "PL-001", "description": "Header Plug", "qty": BUNDLE_DESIGN["tube_bundle"]["tube_count"], "material": BUNDLE_DESIGN["headers"]["plug_material"]},
            {"item": 7, "part_number": "GK-001", "description": "Plug Gasket", "qty": BUNDLE_DESIGN["tube_bundle"]["tube_count"], "material": "Spiral Wound"},
            {"item": 8, "part_number": "TS-002", "description": "Tube Support", "qty": BUNDLE_DESIGN["structural"]["tube_supports"], "material": "Galvanized Steel"},
        ]
    }

    result = call_endpoint("Documentation", "/phase25/check-documentation", doc_payload)
    results["documentation"] = result

    if result["success"]:
        data = result["data"]
        print(f"   [PASS] {result['time_ms']:.0f}ms")
        print(f"   Title Block Complete: {data.get('title_block_complete', 'N/A')}")
        print(f"   BOM Items: {len(doc_payload['bom'])}")
        if data.get("issues"):
            all_issues.extend([{"source": "Documentation", **i} for i in data["issues"]])
    else:
        print(f"   [FAIL] {result['error'][:60]}")

    # =========================================================================
    # 12. GENERATE COMPREHENSIVE REPORT
    # =========================================================================
    print("\n[12/12] GENERATING COMPREHENSIVE REPORT...")

    # Collect all successful validator results
    validator_results = {}
    for name, res in results.items():
        if res["success"] and res["data"]:
            validator_results[name] = res["data"]

    report_payload = {
        "drawing_number": BUNDLE_DESIGN["project"]["drawing_number"],
        "drawing_revision": BUNDLE_DESIGN["project"]["revision"],
        "project_name": BUNDLE_DESIGN["project"]["name"],
        "validator_results": validator_results,
        "format": "json",
        "level": "detailed",
    }

    result = call_endpoint("Report", "/phase25/generate-report", report_payload)
    results["report"] = result

    if result["success"]:
        data = result["data"]
        print(f"   [PASS] {result['time_ms']:.0f}ms")

        # Parse report content
        content = data.get("content", {})
        if isinstance(content, str):
            try:
                content = json.loads(content)
            except:
                content = {}

        print(f"   Overall Status: {content.get('overall_status', data.get('overall_status', 'N/A'))}")
        print(f"   Pass Rate: {content.get('overall_pass_rate', data.get('overall_pass_rate', 0)):.1f}%")
    else:
        print(f"   [FAIL] {result['error'][:60]}")

    # =========================================================================
    # FINAL SUMMARY
    # =========================================================================
    print("\n" + "=" * 80)
    print("BUNDLE BUILD VALIDATION SUMMARY")
    print("=" * 80)

    total_tests = len(results)
    passed_tests = sum(1 for r in results.values() if r["success"])
    failed_tests = total_tests - passed_tests
    total_time = sum(r["time_ms"] for r in results.values())

    print(f"\nProject: {BUNDLE_DESIGN['project']['name']}")
    print(f"Drawing: {BUNDLE_DESIGN['project']['drawing_number']} Rev {BUNDLE_DESIGN['project']['revision']}")
    print(f"\n{'-' * 40}")
    print(f"Validators Run:     {total_tests}")
    print(f"Passed:             {passed_tests}")
    print(f"Failed:             {failed_tests}")
    print(f"Total Time:         {total_time/1000:.1f} seconds")
    print(f"{'-' * 40}")

    # Count issues by severity
    critical_issues = [i for i in all_issues if i.get("severity") == "critical"]
    warning_issues = [i for i in all_issues if i.get("severity") == "warning"]
    info_issues = [i for i in all_issues if i.get("severity") == "info"]

    print(f"\nIssues Found:")
    print(f"  Critical:  {len(critical_issues)}")
    print(f"  Warnings:  {len(warning_issues)}")
    print(f"  Info:      {len(info_issues)}")
    print(f"  Total:     {len(all_issues)}")

    # List critical issues
    if critical_issues:
        print(f"\n{'-' * 40}")
        print("CRITICAL ISSUES (Must Fix):")
        print("-" * 40)
        for i, issue in enumerate(critical_issues[:10], 1):
            msg = issue.get("message", issue.get("description", "Unknown"))[:70]
            print(f"  {i}. [{issue.get('source', 'Unknown')}] {msg}")
        if len(critical_issues) > 10:
            print(f"  ... and {len(critical_issues) - 10} more")

    # List warnings
    if warning_issues:
        print(f"\n{'-' * 40}")
        print("WARNINGS (Should Review):")
        print("-" * 40)
        for i, issue in enumerate(warning_issues[:5], 1):
            msg = issue.get("message", issue.get("description", "Unknown"))[:70]
            print(f"  {i}. [{issue.get('source', 'Unknown')}] {msg}")
        if len(warning_issues) > 5:
            print(f"  ... and {len(warning_issues) - 5} more")

    # Validation summary by category
    print(f"\n{'-' * 40}")
    print("VALIDATION BY CATEGORY:")
    print("-" * 40)

    categories = [
        ("Process Design", ["api661_bundle", "api661_full"]),
        ("Pressure Integrity", ["asme_viii"]),
        ("Materials & Coatings", ["materials", "sspc_coating"]),
        ("Fabrication", ["fabrication", "fasteners"]),
        ("Structural", ["structural", "rigging"]),
        ("Quality", ["inspection", "documentation"]),
    ]

    for cat_name, cat_keys in categories:
        cat_results = [results.get(k, {}) for k in cat_keys if k in results]
        cat_passed = sum(1 for r in cat_results if r.get("success"))
        cat_total = len(cat_results)
        status = "[OK]" if cat_passed == cat_total else "[!!]"
        print(f"  {status} {cat_name:25} {cat_passed}/{cat_total} passed")

    # Final verdict
    print(f"\n{'=' * 80}")
    if failed_tests == 0 and len(critical_issues) == 0:
        print("VERDICT: BUNDLE DESIGN APPROVED FOR FABRICATION")
        print("         All checks passed. Proceed to shop drawings.")
    elif failed_tests == 0 and len(critical_issues) > 0:
        print("VERDICT: BUNDLE DESIGN REQUIRES CORRECTIONS")
        print(f"         {len(critical_issues)} critical issues must be resolved.")
    else:
        print("VERDICT: BUNDLE VALIDATION INCOMPLETE")
        print(f"         {failed_tests} validators failed. Check server/endpoints.")
    print("=" * 80)

    # Save detailed report
    report_file = f"bundle_validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, "w") as f:
        json.dump({
            "project": BUNDLE_DESIGN["project"],
            "design": BUNDLE_DESIGN,
            "validation_results": {k: {**v, "data": v["data"] if v["success"] else None} for k, v in results.items()},
            "all_issues": all_issues,
            "summary": {
                "total_validators": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "critical_issues": len(critical_issues),
                "warnings": len(warning_issues),
                "total_time_ms": total_time,
            }
        }, f, indent=2, default=str)

    print(f"\nDetailed report saved to: {report_file}")

    return results, all_issues


if __name__ == "__main__":
    run_complete_bundle_validation()
