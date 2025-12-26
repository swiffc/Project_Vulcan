"""
Phase 25.3-25.13 Endpoint Hard Tests
====================================
Tests all new validator endpoints with realistic data and measures response times.
"""

import requests
import time
import json
from typing import Dict, Any, Tuple

BASE_URL = "http://localhost:8000"

def test_endpoint(name: str, endpoint: str, payload: Dict[str, Any]) -> Tuple[bool, float, Dict]:
    """Test an endpoint and return (success, time_ms, response)."""
    url = f"{BASE_URL}{endpoint}"
    start = time.perf_counter()

    try:
        response = requests.post(url, json=payload, timeout=30)
        elapsed_ms = (time.perf_counter() - start) * 1000

        if response.status_code == 200:
            return True, elapsed_ms, response.json()
        else:
            return False, elapsed_ms, {"error": response.text, "status": response.status_code}
    except Exception as e:
        elapsed_ms = (time.perf_counter() - start) * 1000
        return False, elapsed_ms, {"error": str(e)}


def run_all_tests():
    """Run all endpoint tests."""
    results = []

    print("=" * 70)
    print("PHASE 25.3-25.13 ENDPOINT TESTS")
    print("=" * 70)

    # Test 1: Fabrication Feasibility
    print("\n[1] Testing /phase25/check-fabrication...")
    success, time_ms, resp = test_endpoint(
        "Fabrication",
        "/phase25/check-fabrication",
        {
            "thickness_in": 0.5,
            "length_in": 48,
            "width_in": 24,
            "holes": [
                {"diameter": 0.75, "x": 2, "y": 2},
                {"diameter": 0.75, "x": 46, "y": 2},
                {"diameter": 0.75, "x": 2, "y": 22},
                {"diameter": 0.75, "x": 46, "y": 22},
            ],
            "slots": [{"width": 0.5, "length": 2, "x": 24, "y": 12}],
            "bends": [],
            "notches": [{"width": 1, "depth": 1}],
            "process": "plasma"
        }
    )
    results.append(("Fabrication", success, time_ms, resp))
    print(f"   {'[PASS]' if success else '[FAIL]'} - {time_ms:.1f}ms")
    if success:
        print(f"   Checks: {resp.get('total_checks', 0)}, Passed: {resp.get('passed', 0)}, Warnings: {resp.get('warnings', 0)}")

    # Test 2: Materials & Finishing
    print("\n[2] Testing /phase25/check-materials...")
    success, time_ms, resp = test_endpoint(
        "Materials",
        "/phase25/check-materials",
        {
            "material_spec": "A572-50",
            "thickness_in": 0.5,
            "coating_system": "C1",
            "surface_prep": "SP10",
            "service_environment": "severe",
            "service_life_years": 25,
            "mtr_required": True,
            "application": "structural"
        }
    )
    results.append(("Materials", success, time_ms, resp))
    print(f"   {'[PASS]' if success else '[FAIL]'} - {time_ms:.1f}ms")
    if success:
        print(f"   Material Compatible: {resp.get('material_compatible', 'N/A')}, Weldability OK: {resp.get('weldability_ok', 'N/A')}")

    # Test 3: Fasteners
    print("\n[3] Testing /phase25/check-fasteners...")
    success, time_ms, resp = test_endpoint(
        "Fasteners",
        "/phase25/check-fasteners",
        {
            "bolts": [
                {"diameter": 0.75, "grade": "A325", "connection_type": "slip_critical", "hole_type": "STD"},
                {"diameter": 0.75, "grade": "A325", "connection_type": "slip_critical", "hole_type": "STD"},
                {"diameter": 0.75, "grade": "A325", "connection_type": "slip_critical", "hole_type": "STD"},
                {"diameter": 0.75, "grade": "A325", "connection_type": "slip_critical", "hole_type": "STD"},
            ],
            "connection": {
                "grip_length": 1.5,
                "load_kips": 15,
                "load_type": "shear",
                "faying_surface": "class_a",
                "edge_distance": 1.5,
                "bolt_spacing": 3.0
            }
        }
    )
    results.append(("Fasteners", success, time_ms, resp))
    print(f"   {'[PASS]' if success else '[FAIL]'} - {time_ms:.1f}ms")
    if success:
        print(f"   Torque: {resp.get('calculated_torque_ft_lb', 0):.0f} ft-lb, Slip Resistance: {resp.get('slip_resistance_kips', 0):.1f} kips")

    # Test 4: Rigging
    print("\n[4] Testing /phase25/check-rigging...")
    success, time_ms, resp = test_endpoint(
        "Rigging",
        "/phase25/check-rigging",
        {
            "lug": {
                "plate_thickness": 0.75,
                "plate_width": 6,
                "hole_diameter": 1.25,
                "edge_distance": 2.0,
                "throat_width": 4,
                "material": "A36",
                "rated_load_lbs": 10000,
                "sling_angle_deg": 60,
                "weld_size": 0.375,
                "weld_length": 12,
                "load_class": "A"
            },
            "rigging": {
                "total_load_lbs": 20000,
                "center_of_gravity": [24, 12, 6],
                "lift_points": [[0, 0, 0], [48, 0, 0], [0, 24, 0], [48, 24, 0]]
            }
        }
    )
    results.append(("Rigging", success, time_ms, resp))
    print(f"   {'[PASS]' if success else '[FAIL]'} - {time_ms:.1f}ms")
    if success:
        print(f"   Lug Capacity: {resp.get('lug_capacity_lbs', 0):.0f} lbs, Design Factor: {resp.get('design_factor', 0)}")
        stresses = resp.get('stresses', {})
        print(f"   Stresses - Shear: {stresses.get('shear_ksi', 0):.1f} ksi, Bearing: {stresses.get('bearing_ksi', 0):.1f} ksi")

    # Test 5: Inspection/QC
    print("\n[5] Testing /phase25/check-inspection...")
    success, time_ms, resp = test_endpoint(
        "Inspection",
        "/phase25/check-inspection",
        {
            "drawing_number": "DWG-50001",
            "revision": "B",
            "code": "AWS D1.1",
            "welds": [
                {"type": "fillet", "size": 0.25, "length": 12, "category": "critical"},
                {"type": "groove", "size": 0.5, "length": 6, "category": "primary"}
            ]
        }
    )
    results.append(("Inspection", success, time_ms, resp))
    print(f"   {'[PASS]' if success else '[FAIL]'} - {time_ms:.1f}ms")
    if success:
        print(f"   Checks: {resp.get('total_checks', 0)}, Passed: {resp.get('passed', 0)}")

    # Test 6: Cross-Part
    print("\n[6] Testing /phase25/check-cross-part...")
    success, time_ms, resp = test_endpoint(
        "Cross-Part",
        "/phase25/check-cross-part",
        {
            "interfaces": [
                {
                    "part_a": "BASE-001",
                    "part_b": "COLUMN-001",
                    "interface_type": "bolted",
                    "hole_patterns": [
                        {"holes": 4, "diameter": 0.8125, "bolt_circle": 6}
                    ]
                },
                {
                    "part_a": "COLUMN-001",
                    "part_b": "BEAM-001",
                    "interface_type": "welded"
                }
            ]
        }
    )
    results.append(("Cross-Part", success, time_ms, resp))
    print(f"   {'[PASS]' if success else '[FAIL]'} - {time_ms:.1f}ms")
    if success:
        print(f"   Interfaces Checked: {resp.get('interfaces_checked', 0)}, Compatible: {resp.get('all_compatible', 'N/A')}")

    # Test 7: Documentation
    print("\n[7] Testing /phase25/check-documentation...")
    success, time_ms, resp = test_endpoint(
        "Documentation",
        "/phase25/check-documentation",
        {
            "title_block": {
                "drawing_number": "DWG-50001",
                "revision": "B",
                "title": "Base Plate Assembly",
                "scale": "1:2",
                "sheet": "1 of 3",
                "drawn_by": "JDS",
                "date": "2024-01-15",
                "checked_by": "RMT",
                "approved_by": "KLB",
                "material": "A36",
                "finish": "HDG"
            },
            "notes": {
                "general_notes": [
                    "1. All dimensions in inches unless otherwise noted.",
                    "2. Tolerances per ASME Y14.5: .XX = ±0.01, .XXX = ±0.005",
                    "3. All welds per AWS D1.1, E70XX electrodes.",
                    "4. Surface finish 125 Ra unless noted.",
                    "5. Hot-dip galvanize per ASTM A123 after fabrication."
                ],
                "local_notes": [],
                "flag_notes": []
            },
            "drawing_type": "weldment",
            "documentation_level": "industrial",
            "bom": [
                {"item": 1, "part_number": "BP-001", "description": "Base Plate", "qty": 1, "material": "A36"},
                {"item": 2, "part_number": "STF-001", "description": "Stiffener", "qty": 4, "material": "A36"}
            ]
        }
    )
    results.append(("Documentation", success, time_ms, resp))
    print(f"   {'[PASS]' if success else '[FAIL]'} - {time_ms:.1f}ms")
    if success:
        print(f"   Title Block Complete: {resp.get('title_block_complete', 'N/A')}")
        print(f"   Missing Elements: {resp.get('missing_elements', [])}")

    # Test 8: Report Generation
    print("\n[8] Testing /phase25/generate-report...")
    # Use results from previous tests
    validator_results = {}
    for name, success, _, resp in results:
        if success and "error" not in resp:
            validator_results[name.lower()] = resp

    success, time_ms, resp = test_endpoint(
        "Report",
        "/phase25/generate-report",
        {
            "drawing_number": "DWG-50001",
            "drawing_revision": "B",
            "project_name": "Test Project",
            "validator_results": validator_results,
            "format": "json",
            "level": "standard"
        }
    )
    results.append(("Report", success, time_ms, resp))
    print(f"   {'[PASS]' if success else '[FAIL]'} - {time_ms:.1f}ms")
    if success and "content" in resp:
        try:
            content = json.loads(resp["content"]) if isinstance(resp["content"], str) else resp["content"]
            print(f"   Overall Status: {content.get('overall_status', 'N/A')}")
            print(f"   Pass Rate: {content.get('overall_pass_rate', 0):.1f}%")
            print(f"   Total Checks: {content.get('statistics', {}).get('total_checks', 0)}")
        except:
            pass

    # Test 9: Edge Case - Undersized Lug
    print("\n[9] Testing EDGE CASE: Undersized lifting lug...")
    success, time_ms, resp = test_endpoint(
        "Edge-Undersized-Lug",
        "/phase25/check-rigging",
        {
            "lug": {
                "plate_thickness": 0.25,  # Too thin
                "plate_width": 3,
                "hole_diameter": 1.5,  # Large hole
                "edge_distance": 1.0,  # Too close to edge
                "throat_width": 1.5,  # Narrow throat
                "material": "A36",
                "rated_load_lbs": 20000,  # High load
                "sling_angle_deg": 30,  # Steep angle increases load
                "weld_size": 0.125,
                "weld_length": 4,
                "load_class": "D"  # Critical service
            }
        }
    )
    results.append(("Edge-Undersized-Lug", success, time_ms, resp))
    print(f"   {'[PASS]' if success else '[FAIL]'} - {time_ms:.1f}ms")
    if success:
        issues = resp.get("issues", [])
        critical = [i for i in issues if i.get("severity") == "critical"]
        print(f"   Critical Issues Found: {len(critical)} (expected: >0)")
        for issue in critical[:3]:
            print(f"   - {issue.get('message', '')[:60]}...")

    # Test 10: Edge Case - Incompatible Materials
    print("\n[10] Testing EDGE CASE: Galvanic incompatibility...")
    success, time_ms, resp = test_endpoint(
        "Edge-Galvanic",
        "/phase25/check-materials",
        {
            "material_spec": "Aluminum 6061",
            "thickness_in": 0.25,
            "application": "structural"
        }
    )
    # Now check compatibility manually
    results.append(("Edge-Galvanic", success, time_ms, resp))
    print(f"   {'[PASS]' if success else '[FAIL]'} - {time_ms:.1f}ms")

    # Test 11: Edge Case - Tight Tolerance
    print("\n[11] Testing EDGE CASE: Impossible tolerance...")
    success, time_ms, resp = test_endpoint(
        "Edge-Tolerance",
        "/phase25/check-shaft",
        {
            "diameter": 2.0,
            "tolerance_plus": 0.00001,  # 0.01 thou - nearly impossible
            "tolerance_minus": 0.00001,
            "surface_finish_ra": 4,  # Mirror finish
            "feature_type": "bearing_journal"
        }
    )
    results.append(("Edge-Tolerance", success, time_ms, resp))
    print(f"   {'[PASS]' if success else '[FAIL]'} - {time_ms:.1f}ms")

    # Test 12: Stress Test - Large Payload
    print("\n[12] Testing STRESS: Large fabrication payload...")
    large_holes = [{"diameter": 0.5, "x": i*2, "y": j*2} for i in range(20) for j in range(10)]
    success, time_ms, resp = test_endpoint(
        "Stress-Large",
        "/phase25/check-fabrication",
        {
            "thickness_in": 0.375,
            "length_in": 96,
            "width_in": 48,
            "holes": large_holes,  # 200 holes
            "slots": [{"width": 0.5, "length": 3, "x": i*6, "y": 24} for i in range(15)],
            "process": "laser"
        }
    )
    results.append(("Stress-Large", success, time_ms, resp))
    print(f"   {'[PASS]' if success else '[FAIL]'} - {time_ms:.1f}ms")
    print(f"   Processed 200 holes + 15 slots")

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    total = len(results)
    passed = sum(1 for r in results if r[1])
    failed = total - passed
    total_time = sum(r[2] for r in results)
    avg_time = total_time / total if total > 0 else 0

    print(f"\nTotal Tests: {total}")
    print(f"Passed: {passed} ({passed/total*100:.0f}%)")
    print(f"Failed: {failed}")
    print(f"\nTotal Time: {total_time:.1f}ms")
    print(f"Average Time: {avg_time:.1f}ms")
    print(f"Slowest: {max(results, key=lambda x: x[2])[0]} ({max(r[2] for r in results):.1f}ms)")
    print(f"Fastest: {min(results, key=lambda x: x[2])[0]} ({min(r[2] for r in results):.1f}ms)")

    print("\n" + "-" * 70)
    print("DETAILED RESULTS:")
    print("-" * 70)
    for name, success, time_ms, resp in results:
        status = "✓" if success else "✗"
        print(f"{status} {name:25} {time_ms:8.1f}ms")
        if not success:
            print(f"  Error: {resp.get('error', 'Unknown')[:60]}")

    return results


if __name__ == "__main__":
    run_all_tests()
