"""
Complete Drawing Package Validation Test
=========================================
Creates a full engineering drawing package for the ACHE bundle including:
- Title block, revision history
- Complete BOM with all parts
- All critical dimensions
- GD&T callouts (ASME Y14.5)
- Weld symbols and specifications
- Surface finish requirements
- Assembly notes and specifications

Then validates through ALL relevant Phase 25 validators.
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, List

BASE_URL = "http://localhost:8000"

# =============================================================================
# COMPLETE DRAWING PACKAGE DATA
# =============================================================================

DRAWING_PACKAGE = {
    # =========================================================================
    # SHEET 1: ASSEMBLY DRAWING
    # =========================================================================
    "sheet_1_assembly": {
        "title_block": {
            "drawing_number": "ACHE-150-001",
            "part_number": "ACHE-150-001",  # Same as drawing number
            "revision": "B",
            "title": "TUBE BUNDLE ASSEMBLY",
            "subtitle": "Hot Oil Cooler Unit 150",
            "scale": "1:10",
            "sheet": "1 of 5",
            "size": "D",  # 22x34
            "drawn_by": "JDS",
            "date": "2024-12-15",  # Changed from drawn_date
            "drawn_date": "2024-12-15",
            "checked_by": "RMT",
            "checked_date": "2024-12-18",
            "approved_by": "KLB",
            "approved_date": "2024-12-20",
            "client": "Refinery Corp",
            "project": "Hot Oil System Upgrade",
            "job_number": "J-2024-150",
            "po_number": "PO-78542",
            "material": "SEE BOM",
            "finish": "SSPC-SP10 + PAINT",
            "weight_lb": 8500,
            "third_angle_projection": True,
        },
        "revision_history": [
            {"rev": "A", "date": "2024-12-01", "description": "Initial Release", "by": "JDS"},
            {"rev": "B", "date": "2024-12-20", "description": "Added tube keepers, vents, drains per API 661", "by": "JDS"},
        ],
        "views": ["FRONT", "TOP", "RIGHT SIDE", "SECTION A-A", "DETAIL B"],
    },

    # =========================================================================
    # BILL OF MATERIALS (Complete)
    # =========================================================================
    "bom": [
        {"item": 1, "part_number": "TB-001", "description": "Finned Tube, 1\" OD x 12 BWG x 30'-0\" L-Foot Fins",
         "qty": 196, "material": "SA-179 / AL1100", "weight_ea": 28.5, "remarks": "10 FPI"},
        {"item": 2, "part_number": "TS-001", "description": "Tubesheet, 98\" x 12\" x 1.5\" THK",
         "qty": 2, "material": "SA-516-70", "weight_ea": 485, "remarks": "196 HOLES"},
        {"item": 3, "part_number": "HD-001", "description": "Header Box Weldment",
         "qty": 2, "material": "SA-516-70", "weight_ea": 320, "remarks": "SEE DWG ACHE-150-002"},
        {"item": 4, "part_number": "SF-001", "description": "Side Frame, C6x8.2 x 30'-0\"",
         "qty": 2, "material": "A36", "weight_ea": 246, "remarks": ""},
        {"item": 5, "part_number": "TS-002", "description": "Tube Support Plate, 96\" x 4\" x 0.25\"",
         "qty": 7, "material": "GALV STEEL", "weight_ea": 32, "remarks": "196 HOLES"},
        {"item": 6, "part_number": "TK-001", "description": "Tube Keeper, U-Bolt Type",
         "qty": 14, "material": "A36 GALV", "weight_ea": 2.5, "remarks": "2 PER SUPPORT"},
        {"item": 7, "part_number": "LL-001", "description": "Lifting Lug, 6\" x 4\" x 0.75\" THK",
         "qty": 4, "material": "SA-36", "weight_ea": 8, "remarks": "1.5\" HOLE"},
        {"item": 8, "part_number": "PL-001", "description": "Header Plug, 1.25\" Shoulder Type",
         "qty": 392, "material": "SA-105", "weight_ea": 0.8, "remarks": "196 EA END"},
        {"item": 9, "part_number": "GK-001", "description": "Plug Gasket, Spiral Wound",
         "qty": 392, "material": "SS316/GRAPHITE", "weight_ea": 0.05, "remarks": ""},
        {"item": 10, "part_number": "NZ-001", "description": "Nozzle, 6\" 150# RFWN",
         "qty": 4, "material": "SA-105", "weight_ea": 45, "remarks": "2 INLET, 2 OUTLET"},
        {"item": 11, "part_number": "NZ-002", "description": "Vent Connection, 3/4\" NPT",
         "qty": 2, "material": "SA-105", "weight_ea": 1.5, "remarks": "HIGH POINT"},
        {"item": 12, "part_number": "NZ-003", "description": "Drain Connection, 1\" NPT",
         "qty": 2, "material": "SA-105", "weight_ea": 2, "remarks": "LOW POINT"},
        {"item": 13, "part_number": "AS-001", "description": "Air Seal P-Strip",
         "qty": 8, "material": "ALUMINUM", "weight_ea": 3, "remarks": "FULL LENGTH"},
        {"item": 14, "part_number": "HW-001", "description": "Hex Bolt, 5/8-11 x 2\" Gr B7",
         "qty": 48, "material": "SA-193-B7", "weight_ea": 0.15, "remarks": "NOZZLE FLANGE"},
        {"item": 15, "part_number": "HW-002", "description": "Hex Nut, 5/8-11 Gr 2H",
         "qty": 48, "material": "SA-194-2H", "weight_ea": 0.05, "remarks": ""},
        {"item": 16, "part_number": "HW-003", "description": "Stud, 1/2-13 x 1.5\" Gr B7",
         "qty": 56, "material": "SA-193-B7", "weight_ea": 0.08, "remarks": "TUBE KEEPER"},
        {"item": 17, "part_number": "GK-002", "description": "Flange Gasket, 6\" 150# Spiral Wound",
         "qty": 4, "material": "SS316/GRAPHITE", "weight_ea": 0.5, "remarks": ""},
    ],

    # =========================================================================
    # CRITICAL DIMENSIONS
    # =========================================================================
    "dimensions": [
        # Overall dimensions
        {"feature": "Overall Length", "nominal": 360.0, "tolerance_plus": 0.25, "tolerance_minus": 0.25, "unit": "in"},
        {"feature": "Overall Width", "nominal": 98.0, "tolerance_plus": 0.125, "tolerance_minus": 0.125, "unit": "in"},
        {"feature": "Overall Height", "nominal": 24.0, "tolerance_plus": 0.125, "tolerance_minus": 0.125, "unit": "in"},

        # Tube layout
        {"feature": "Tube Pitch (Triangular)", "nominal": 2.5, "tolerance_plus": 0.03125, "tolerance_minus": 0.03125, "unit": "in"},
        {"feature": "Tube OD", "nominal": 1.0, "tolerance_plus": 0.005, "tolerance_minus": 0.005, "unit": "in"},
        {"feature": "Tube Length (Effective)", "nominal": 354.0, "tolerance_plus": 0.0625, "tolerance_minus": 0.0625, "unit": "in"},

        # Tubesheet
        {"feature": "Tubesheet Length", "nominal": 98.0, "tolerance_plus": 0.0625, "tolerance_minus": 0.0625, "unit": "in"},
        {"feature": "Tubesheet Width", "nominal": 12.0, "tolerance_plus": 0.03125, "tolerance_minus": 0.03125, "unit": "in"},
        {"feature": "Tubesheet Thickness", "nominal": 1.5, "tolerance_plus": 0.03125, "tolerance_minus": 0.0, "unit": "in"},
        {"feature": "Tube Hole Diameter", "nominal": 1.008, "tolerance_plus": 0.005, "tolerance_minus": 0.0, "unit": "in"},

        # Header box
        {"feature": "Header Box Length", "nominal": 98.0, "tolerance_plus": 0.0625, "tolerance_minus": 0.0625, "unit": "in"},
        {"feature": "Header Box Width", "nominal": 12.0, "tolerance_plus": 0.0625, "tolerance_minus": 0.0625, "unit": "in"},
        {"feature": "Header Box Height", "nominal": 8.0, "tolerance_plus": 0.0625, "tolerance_minus": 0.0625, "unit": "in"},
        {"feature": "Header Wall Thickness", "nominal": 0.75, "tolerance_plus": 0.03125, "tolerance_minus": 0.0, "unit": "in"},

        # Tube supports
        {"feature": "Tube Support Spacing", "nominal": 48.0, "tolerance_plus": 0.5, "tolerance_minus": 0.5, "unit": "in"},
        {"feature": "Support Plate Thickness", "nominal": 0.25, "tolerance_plus": 0.03125, "tolerance_minus": 0.0, "unit": "in"},

        # Nozzle locations
        {"feature": "Inlet Nozzle CL from End", "nominal": 24.0, "tolerance_plus": 0.125, "tolerance_minus": 0.125, "unit": "in"},
        {"feature": "Outlet Nozzle CL from End", "nominal": 24.0, "tolerance_plus": 0.125, "tolerance_minus": 0.125, "unit": "in"},
        {"feature": "Nozzle Projection", "nominal": 6.0, "tolerance_plus": 0.125, "tolerance_minus": 0.125, "unit": "in"},

        # Lifting lugs
        {"feature": "Lifting Lug CL from End", "nominal": 24.0, "tolerance_plus": 0.25, "tolerance_minus": 0.25, "unit": "in"},
        {"feature": "Lifting Lug Hole Diameter", "nominal": 1.5, "tolerance_plus": 0.03125, "tolerance_minus": 0.0, "unit": "in"},
    ],

    # =========================================================================
    # GD&T CALLOUTS (ASME Y14.5-2018)
    # =========================================================================
    "gdt": [
        # Tubesheet flatness
        {
            "feature": "Tubesheet Mating Surface",
            "tolerance_type": "flatness",
            "tolerance_value": 0.010,
            "datum": None,
            "material_condition": None,
            "unit": "in",
        },
        # Tube hole position
        {
            "feature": "Tube Holes (196x)",
            "tolerance_type": "position",
            "tolerance_value": 0.015,
            "datum": "A|B|C",
            "material_condition": "MMC",
            "bonus_tolerance": True,
            "unit": "in",
        },
        # Tubesheet perpendicularity
        {
            "feature": "Tubesheet to Header Box",
            "tolerance_type": "perpendicularity",
            "tolerance_value": 0.020,
            "datum": "A",
            "material_condition": None,
            "unit": "in",
        },
        # Header box parallelism
        {
            "feature": "Header Box Sides",
            "tolerance_type": "parallelism",
            "tolerance_value": 0.030,
            "datum": "A",
            "material_condition": None,
            "unit": "in",
        },
        # Nozzle position
        {
            "feature": "Nozzle Flange Face",
            "tolerance_type": "position",
            "tolerance_value": 0.060,
            "datum": "A|B",
            "material_condition": None,
            "unit": "in",
        },
        # Lifting lug hole position
        {
            "feature": "Lifting Lug Holes (4x)",
            "tolerance_type": "position",
            "tolerance_value": 0.030,
            "datum": "A|B|C",
            "material_condition": "MMC",
            "unit": "in",
        },
        # Side frame straightness
        {
            "feature": "Side Frame",
            "tolerance_type": "straightness",
            "tolerance_value": 0.125,
            "datum": None,
            "material_condition": None,
            "unit": "in",
        },
        # Tube support flatness
        {
            "feature": "Tube Support Plate",
            "tolerance_type": "flatness",
            "tolerance_value": 0.060,
            "datum": None,
            "material_condition": None,
            "unit": "in",
        },
    ],

    # =========================================================================
    # WELD SPECIFICATIONS
    # =========================================================================
    "welds": [
        # Tubesheet to header (critical)
        {
            "weld_id": "W1",
            "description": "Tubesheet to Header Box",
            "type": "groove",
            "process": "GTAW/SMAW",
            "size": 0.75,
            "length": 220,  # Perimeter
            "category": "critical",
            "nde": ["RT", "PT"],
            "procedure": "WPS-001",
            "filler": "E7018",
            "preheat_f": 200,
            "interpass_max_f": 450,
            "pwht_required": True,
        },
        # Header seams
        {
            "weld_id": "W2",
            "description": "Header Box Seam Welds",
            "type": "groove",
            "process": "SMAW",
            "size": 0.75,
            "length": 432,  # 4 seams x 98" + ends
            "category": "critical",
            "nde": ["RT"],
            "procedure": "WPS-001",
            "filler": "E7018",
            "preheat_f": 200,
            "interpass_max_f": 450,
            "pwht_required": True,
        },
        # Nozzle to header
        {
            "weld_id": "W3",
            "description": "Nozzle to Header",
            "type": "groove",
            "process": "SMAW",
            "size": 0.5,
            "length": 76,  # 4 nozzles x ~19" perimeter
            "category": "critical",
            "nde": ["RT", "PT"],
            "procedure": "WPS-002",
            "filler": "E7018",
            "preheat_f": 200,
            "interpass_max_f": 450,
            "pwht_required": True,
        },
        # Tube to tubesheet (roller expanded + seal weld)
        {
            "weld_id": "W4",
            "description": "Tube-to-Tubesheet Seal Weld",
            "type": "fillet",
            "process": "GTAW",
            "size": 0.125,
            "length": 616,  # 196 tubes x pi x 1" OD
            "category": "critical",
            "nde": ["PT", "LT"],
            "procedure": "WPS-003",
            "filler": "ER70S-2",
            "preheat_f": None,
            "interpass_max_f": 350,
            "pwht_required": True,
        },
        # Lifting lugs
        {
            "weld_id": "W5",
            "description": "Lifting Lug to Side Frame",
            "type": "fillet",
            "process": "SMAW",
            "size": 0.375,
            "length": 48,  # 4 lugs x 12" weld
            "category": "primary",
            "nde": ["VT", "MT"],
            "procedure": "WPS-004",
            "filler": "E7018",
            "preheat_f": None,
            "interpass_max_f": 450,
            "pwht_required": False,
        },
        # Side frame attachments
        {
            "weld_id": "W6",
            "description": "Side Frame to Tubesheet",
            "type": "fillet",
            "process": "SMAW",
            "size": 0.3125,
            "length": 48,  # 4 corners x 12"
            "category": "primary",
            "nde": ["VT"],
            "procedure": "WPS-004",
            "filler": "E7018",
            "preheat_f": None,
            "interpass_max_f": 450,
            "pwht_required": False,
        },
    ],

    # =========================================================================
    # SURFACE FINISH REQUIREMENTS
    # =========================================================================
    "surface_finish": [
        {"feature": "Tubesheet Mating Surface", "finish_ra": 125, "process": "Machine"},
        {"feature": "Header Gasket Surface", "finish_ra": 125, "process": "Machine"},
        {"feature": "Nozzle Flange Face", "finish_ra": 125, "process": "Machine (Serrated)"},
        {"feature": "Tube Holes", "finish_ra": 250, "process": "Drill/Ream"},
        {"feature": "Plug Threads", "finish_ra": 63, "process": "Machine"},
        {"feature": "Lifting Lug Holes", "finish_ra": 250, "process": "Drill"},
    ],

    # =========================================================================
    # GENERAL NOTES
    # =========================================================================
    "general_notes": [
        "1. INTERPRET DRAWING PER ASME Y14.5-2018.",
        "2. ALL DIMENSIONS IN INCHES UNLESS OTHERWISE NOTED.",
        "3. TOLERANCES UNLESS OTHERWISE SPECIFIED:",
        "   .X = +/- 0.1",
        "   .XX = +/- 0.03",
        "   .XXX = +/- 0.010",
        "   ANGLES = +/- 0.5 DEG",
        "4. ALL WELDS PER ASME SECTION IX AND AWS D1.1.",
        "5. WELD FILLER METAL: E7018 (SMAW), ER70S-2 (GTAW).",
        "6. WELD PROCEDURE SPECIFICATIONS: WPS-001 THRU WPS-004.",
        "7. PREHEAT 200F MIN FOR WELDS W1, W2, W3 (>0.5\" THK).",
        "8. PWHT: 1100F +/- 25F FOR 1 HR, HEAT/COOL 400F/HR MAX.",
        "9. NDE REQUIREMENTS:",
        "   - RT: 100% ON ALL PRESSURE WELDS (W1, W2, W3, W4)",
        "   - PT: ROOT AND FINAL ON GROOVE WELDS",
        "   - MT: LIFTING LUG WELDS",
        "   - VT: ALL WELDS",
        "10. HYDROSTATIC TEST: 225 PSIG FOR 30 MINUTES.",
        "11. SURFACE PREP: SSPC-SP10 NEAR WHITE BLAST.",
        "12. PAINT SYSTEM:",
        "    - PRIMER: ZINC-RICH EPOXY, 3.0 MILS DFT",
        "    - INTERMEDIATE: EPOXY, 5.0 MILS DFT",
        "    - TOPCOAT: POLYURETHANE, 2.0 MILS DFT",
        "    - TOTAL DFT: 10.0 MILS MIN",
        "13. DESIGN CONDITIONS:",
        "    - DESIGN PRESSURE: 150 PSIG",
        "    - DESIGN TEMPERATURE: 500F",
        "    - CORROSION ALLOWANCE: 0.0625\"",
        "14. MATERIAL TEST REPORTS (MTR) REQUIRED FOR ALL PRESSURE PARTS.",
        "15. TUBES ROLLER EXPANDED + SEAL WELDED TO TUBESHEET.",
        "16. ALL PLUGS SHALL BE SHOULDER TYPE PER API 661.",
        "17. LIFTING: USE ALL 4 LIFTING LUGS. MAX SLING ANGLE 60 DEG.",
        "18. TUBE KEEPERS BOLTED (NOT WELDED) TO SIDE FRAMES.",
    ],

    # =========================================================================
    # FLAG NOTES (Specific Callouts)
    # =========================================================================
    "flag_notes": [
        {"flag": "A", "note": "CRITICAL WELD - 100% RT REQUIRED"},
        {"flag": "B", "note": "MACHINE SURFACE 125 Ra FINISH"},
        {"flag": "C", "note": "POSITION TOLERANCE @ MMC - BONUS ALLOWED"},
        {"flag": "D", "note": "PWHT REQUIRED AFTER WELDING"},
        {"flag": "E", "note": "HYDRO TEST WITNESS POINT"},
        {"flag": "F", "note": "MTR REQUIRED"},
    ],
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


def run_drawing_package_validation():
    """Run complete drawing package validation."""

    print("=" * 80)
    print("COMPLETE DRAWING PACKAGE VALIDATION TEST")
    print("=" * 80)

    tb = DRAWING_PACKAGE["sheet_1_assembly"]["title_block"]
    print(f"\nDrawing: {tb['drawing_number']} Rev {tb['revision']}")
    print(f"Title: {tb['title']}")
    print(f"Client: {tb['client']}")
    print(f"Project: {tb['project']}")
    print(f"\nStarted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    results = {}
    all_issues = []

    # =========================================================================
    # 1. DOCUMENTATION COMPLETENESS
    # =========================================================================
    print("\n[1/8] DOCUMENTATION COMPLETENESS...")

    doc_payload = {
        "title_block": DRAWING_PACKAGE["sheet_1_assembly"]["title_block"],
        "notes": {
            "general_notes": DRAWING_PACKAGE["general_notes"],
            "local_notes": [],
            "flag_notes": [f["note"] for f in DRAWING_PACKAGE["flag_notes"]],
        },
        "drawing_type": "weldment",
        "documentation_level": "industrial",
        "bom": DRAWING_PACKAGE["bom"],
    }

    result = call_endpoint("Documentation", "/phase25/check-documentation", doc_payload)
    results["documentation"] = result

    if result["success"]:
        data = result["data"]
        print(f"   [PASS] {result['time_ms']:.0f}ms")
        print(f"   Title Block Complete: {data.get('title_block_complete', 'N/A')}")
        print(f"   BOM Items: {len(DRAWING_PACKAGE['bom'])}")
        print(f"   General Notes: {len(DRAWING_PACKAGE['general_notes'])}")
        if data.get("issues"):
            all_issues.extend([{"source": "Documentation", **i} for i in data["issues"]])
    else:
        print(f"   [FAIL] {result['error'][:60]}")

    # =========================================================================
    # 2. DIMENSION VALIDATION
    # =========================================================================
    print("\n[2/8] DIMENSION VALIDATION...")

    dim_payload = {
        "dimensions": DRAWING_PACKAGE["dimensions"],
        "tolerance_standard": "ASME Y14.5",
    }

    result = call_endpoint("Dimensions", "/phase25/check-dimensions", dim_payload)
    results["dimensions"] = result

    if result["success"]:
        data = result["data"]
        print(f"   [PASS] {result['time_ms']:.0f}ms")
        print(f"   Dimensions Checked: {len(DRAWING_PACKAGE['dimensions'])}")
        print(f"   Checks Passed: {data.get('passed', 0)}/{data.get('total_checks', 0)}")
        if data.get("issues"):
            all_issues.extend([{"source": "Dimensions", **i} for i in data["issues"]])
    else:
        print(f"   [FAIL] {result['error'][:60]}")

    # =========================================================================
    # 3. GD&T VALIDATION (ASME Y14.5-2018)
    # =========================================================================
    print("\n[3/8] GD&T VALIDATION (ASME Y14.5-2018)...")

    gdt_payload = {
        "features": []
    }

    for gdt in DRAWING_PACKAGE["gdt"]:
        feature = {
            "feature_name": gdt["feature"],
            "tolerance_type": gdt["tolerance_type"],
            "tolerance_value": gdt["tolerance_value"],
            "datum_reference": gdt.get("datum"),
            "material_condition": gdt.get("material_condition"),
        }
        gdt_payload["features"].append(feature)

    result = call_endpoint("GD&T", "/phase25/check-gdt", gdt_payload)
    results["gdt"] = result

    if result["success"]:
        data = result["data"]
        print(f"   [PASS] {result['time_ms']:.0f}ms")
        print(f"   GD&T Callouts: {len(DRAWING_PACKAGE['gdt'])}")
        print(f"   Checks Passed: {data.get('passed', 0)}/{data.get('total_checks', 0)}")
        if data.get("issues"):
            all_issues.extend([{"source": "GD&T", **i} for i in data["issues"]])
    else:
        print(f"   [FAIL] {result['error'][:60]}")

    # =========================================================================
    # 4. WELD VALIDATION
    # =========================================================================
    print("\n[4/8] WELD VALIDATION (AWS D1.1 / ASME IX)...")

    weld_payload = {
        "welds": [
            {
                "weld_id": w["weld_id"],
                "type": w["type"],
                "size": w["size"],
                "length": w["length"],
                "category": w["category"],
                "nde": w.get("nde", []),
                "procedure": w.get("procedure"),
                "filler": w.get("filler"),
            }
            for w in DRAWING_PACKAGE["welds"]
        ],
        "code": "AWS D1.1",
    }

    result = call_endpoint("Welds", "/phase25/check-weld", weld_payload)
    results["welds"] = result

    if result["success"]:
        data = result["data"]
        print(f"   [PASS] {result['time_ms']:.0f}ms")
        print(f"   Welds Specified: {len(DRAWING_PACKAGE['welds'])}")
        print(f"   Total Weld Length: {sum(w['length'] for w in DRAWING_PACKAGE['welds'])}\"")
        if data.get("issues"):
            all_issues.extend([{"source": "Welds", **i} for i in data["issues"]])
    else:
        print(f"   [FAIL] {result['error'][:60]}")

    # =========================================================================
    # 5. BOM VALIDATION
    # =========================================================================
    print("\n[5/8] BOM VALIDATION...")

    bom_payload = {
        "bom_items": DRAWING_PACKAGE["bom"],
        "drawing_number": tb["drawing_number"],
    }

    result = call_endpoint("BOM", "/phase25/check-bom", bom_payload)
    results["bom"] = result

    if result["success"]:
        data = result["data"]
        print(f"   [PASS] {result['time_ms']:.0f}ms")
        print(f"   BOM Items: {len(DRAWING_PACKAGE['bom'])}")
        total_weight = sum(item["qty"] * item["weight_ea"] for item in DRAWING_PACKAGE["bom"])
        print(f"   Calculated Weight: {total_weight:,.0f} lbs")
        if data.get("issues"):
            all_issues.extend([{"source": "BOM", **i} for i in data["issues"]])
    else:
        print(f"   [FAIL] {result['error'][:60]}")

    # =========================================================================
    # 6. INSPECTION/QC VALIDATION
    # =========================================================================
    print("\n[6/8] INSPECTION & QC REQUIREMENTS...")

    inspection_payload = {
        "drawing_number": tb["drawing_number"],
        "revision": tb["revision"],
        "code": "ASME IX",
        "welds": [
            {
                "type": w["type"],
                "size": w["size"],
                "length": w["length"],
                "category": w["category"],
                "nde": ",".join(w.get("nde", [])),
            }
            for w in DRAWING_PACKAGE["welds"]
        ],
        "pwht_required": True,
        "pwht_documented": True,
        "pwht_temp_f": 1100,
        "pwht_time_hr": 1,
        "hydro_test_pressure": 225,
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
    # 7. DRAWING COMPLETENESS
    # =========================================================================
    print("\n[7/8] DRAWING COMPLETENESS CHECK...")

    completeness_payload = {
        "drawing_number": tb["drawing_number"],
        "part_number": tb["part_number"],
        "revision": tb["revision"],
        "scale": tb["scale"],
        "title_block": tb,  # Include full title block
        "has_title_block": True,
        "has_revision_block": True,
        "has_bom": True,
        "has_general_notes": True,
        "has_dimensions": True,
        "has_tolerances": True,
        "has_gdt": True,
        "has_weld_symbols": True,
        "has_surface_finish": True,
        "has_material_callouts": True,
        "views": DRAWING_PACKAGE["sheet_1_assembly"]["views"],
    }

    result = call_endpoint("Completeness", "/phase25/check-completeness", completeness_payload)
    results["completeness"] = result

    if result["success"]:
        data = result["data"]
        print(f"   [PASS] {result['time_ms']:.0f}ms")
        print(f"   Views: {', '.join(DRAWING_PACKAGE['sheet_1_assembly']['views'])}")
        print(f"   Completeness: {data.get('completeness_pct', 0):.0f}%")
        if data.get("issues"):
            all_issues.extend([{"source": "Completeness", **i} for i in data["issues"]])
    else:
        print(f"   [FAIL] {result['error'][:60]}")

    # =========================================================================
    # 8. GENERATE COMPREHENSIVE REPORT
    # =========================================================================
    print("\n[8/8] GENERATING DRAWING PACKAGE REPORT...")

    validator_results = {}
    for name, res in results.items():
        if res["success"] and res["data"]:
            validator_results[name] = res["data"]

    report_payload = {
        "drawing_number": tb["drawing_number"],
        "drawing_revision": tb["revision"],
        "project_name": tb["project"],
        "validator_results": validator_results,
        "format": "json",
        "level": "detailed",
    }

    result = call_endpoint("Report", "/phase25/generate-report", report_payload)
    results["report"] = result

    if result["success"]:
        data = result["data"]
        print(f"   [PASS] {result['time_ms']:.0f}ms")
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
    # DRAWING PACKAGE SUMMARY
    # =========================================================================
    print("\n" + "=" * 80)
    print("DRAWING PACKAGE VALIDATION SUMMARY")
    print("=" * 80)

    total_tests = len(results)
    passed_tests = sum(1 for r in results.values() if r["success"])
    failed_tests = total_tests - passed_tests
    total_time = sum(r["time_ms"] for r in results.values())

    print(f"\nDrawing: {tb['drawing_number']} Rev {tb['revision']}")
    print(f"Title: {tb['title']}")

    print(f"\n{'-' * 40}")
    print("DRAWING PACKAGE CONTENTS:")
    print("-" * 40)
    print(f"  Title Block Fields:    {len(tb)}")
    print(f"  BOM Items:             {len(DRAWING_PACKAGE['bom'])}")
    print(f"  Dimensions:            {len(DRAWING_PACKAGE['dimensions'])}")
    print(f"  GD&T Callouts:         {len(DRAWING_PACKAGE['gdt'])}")
    print(f"  Weld Specifications:   {len(DRAWING_PACKAGE['welds'])}")
    print(f"  Surface Finishes:      {len(DRAWING_PACKAGE['surface_finish'])}")
    print(f"  General Notes:         {len(DRAWING_PACKAGE['general_notes'])}")
    print(f"  Flag Notes:            {len(DRAWING_PACKAGE['flag_notes'])}")
    print(f"  Drawing Views:         {len(DRAWING_PACKAGE['sheet_1_assembly']['views'])}")

    print(f"\n{'-' * 40}")
    print("VALIDATION RESULTS:")
    print("-" * 40)
    print(f"  Validators Run:     {total_tests}")
    print(f"  Passed:             {passed_tests}")
    print(f"  Failed:             {failed_tests}")
    print(f"  Total Time:         {total_time/1000:.1f} seconds")

    # Count issues by severity
    critical_issues = [i for i in all_issues if i.get("severity") == "critical"]
    warning_issues = [i for i in all_issues if i.get("severity") == "warning"]
    info_issues = [i for i in all_issues if i.get("severity") == "info"]

    print(f"\n{'-' * 40}")
    print("ISSUES FOUND:")
    print("-" * 40)
    print(f"  Critical:  {len(critical_issues)}")
    print(f"  Warnings:  {len(warning_issues)}")
    print(f"  Info:      {len(info_issues)}")
    print(f"  Total:     {len(all_issues)}")

    # Print issues
    if critical_issues:
        print(f"\n{'-' * 40}")
        print("CRITICAL ISSUES:")
        print("-" * 40)
        for i, issue in enumerate(critical_issues[:5], 1):
            msg = issue.get("message", issue.get("description", "Unknown"))[:65]
            msg = msg.encode('ascii', 'replace').decode('ascii')
            print(f"  {i}. [{issue.get('source', '?')}] {msg}")

    if warning_issues:
        print(f"\n{'-' * 40}")
        print("WARNINGS:")
        print("-" * 40)
        for i, issue in enumerate(warning_issues[:5], 1):
            msg = issue.get("message", issue.get("description", "Unknown"))[:65]
            msg = msg.encode('ascii', 'replace').decode('ascii')
            print(f"  {i}. [{issue.get('source', '?')}] {msg}")
        if len(warning_issues) > 5:
            print(f"  ... and {len(warning_issues) - 5} more")

    # Individual validator results
    print(f"\n{'-' * 40}")
    print("VALIDATOR DETAILS:")
    print("-" * 40)
    for name, res in results.items():
        status = "[OK]" if res["success"] else "[FAIL]"
        time_str = f"{res['time_ms']:.0f}ms"
        if res["success"] and res["data"]:
            checks = res["data"].get("total_checks", res["data"].get("checks", "-"))
            passed = res["data"].get("passed", "-")
            print(f"  {status} {name:15} {time_str:>8}  Checks: {passed}/{checks}")
        else:
            print(f"  {status} {name:15} {time_str:>8}")

    # Final verdict
    print("\n" + "=" * 80)
    if failed_tests == 0 and len(critical_issues) == 0:
        print("VERDICT: DRAWING PACKAGE APPROVED")
        print("         Ready for release to fabrication.")
    elif failed_tests == 0 and len(critical_issues) > 0:
        print("VERDICT: DRAWING PACKAGE REQUIRES REVISION")
        print(f"         {len(critical_issues)} critical issues must be resolved.")
    else:
        print("VERDICT: DRAWING PACKAGE VALIDATION INCOMPLETE")
        print(f"         {failed_tests} validators failed.")
    print("=" * 80)

    # Save report
    report_file = f"drawing_package_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, "w") as f:
        json.dump({
            "drawing": tb,
            "package_contents": {
                "bom_items": len(DRAWING_PACKAGE["bom"]),
                "dimensions": len(DRAWING_PACKAGE["dimensions"]),
                "gdt_callouts": len(DRAWING_PACKAGE["gdt"]),
                "welds": len(DRAWING_PACKAGE["welds"]),
                "surface_finishes": len(DRAWING_PACKAGE["surface_finish"]),
                "general_notes": len(DRAWING_PACKAGE["general_notes"]),
            },
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
    run_drawing_package_validation()
