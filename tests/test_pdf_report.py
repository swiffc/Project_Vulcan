"""
PDF Report Generation Test
===========================
Tests the PDF report generation functionality.
"""

import requests
import base64
import json
import time
from pathlib import Path

BASE_URL = "http://localhost:8000"

def test_pdf_generation():
    """Test PDF report generation with sample validator results."""

    print("=" * 70)
    print("PDF REPORT GENERATION TEST")
    print("=" * 70)

    # Sample validator results (simulated)
    validator_results = {
        "fabrication": {
            "total_checks": 12,
            "passed": 10,
            "failed": 1,
            "warnings": 1,
            "critical_failures": 0,
            "issues": [
                {
                    "severity": "warning",
                    "check_type": "hole_spacing",
                    "message": "Hole spacing of 2.5in is close to minimum (2x diameter)",
                    "suggestion": "Consider increasing to 3x diameter for better edge clearance",
                    "standard_reference": "AISC 14th Ed. Table J3.3"
                },
                {
                    "severity": "error",
                    "check_type": "slot_width",
                    "message": "Slot width 0.4in is below minimum for 0.5in plate",
                    "suggestion": "Increase slot width to minimum 0.5in",
                    "standard_reference": "DFM Guidelines"
                }
            ]
        },
        "materials": {
            "total_checks": 8,
            "passed": 8,
            "failed": 0,
            "warnings": 0,
            "critical_failures": 0,
            "issues": []
        },
        "fasteners": {
            "total_checks": 15,
            "passed": 14,
            "failed": 0,
            "warnings": 1,
            "critical_failures": 0,
            "issues": [
                {
                    "severity": "warning",
                    "check_type": "bolt_length",
                    "message": "Bolt length leaves minimal thread engagement",
                    "suggestion": "Use next longer bolt size",
                    "standard_reference": "RCSC Guide"
                }
            ]
        },
        "rigging": {
            "total_checks": 10,
            "passed": 9,
            "failed": 0,
            "warnings": 1,
            "critical_failures": 0,
            "issues": [
                {
                    "severity": "warning",
                    "check_type": "cg_location",
                    "message": "CG offset 2.3in from geometric center",
                    "suggestion": "Mark CG location on part for rigging"
                }
            ]
        },
        "gdt": {
            "total_checks": 20,
            "passed": 18,
            "failed": 1,
            "warnings": 1,
            "critical_failures": 0,
            "issues": [
                {
                    "severity": "error",
                    "check_type": "position_tolerance",
                    "message": "Position tolerance 0.005in may not be achievable with standard machining",
                    "suggestion": "Relax to 0.010in or specify grinding operation",
                    "standard_reference": "ASME Y14.5-2018"
                },
                {
                    "severity": "warning",
                    "check_type": "datum_feature",
                    "message": "Datum A surface finish not specified",
                    "suggestion": "Add surface finish requirement for datum feature"
                }
            ]
        },
        "documentation": {
            "total_checks": 25,
            "passed": 23,
            "failed": 1,
            "warnings": 1,
            "critical_failures": 0,
            "issues": [
                {
                    "severity": "error",
                    "check_type": "title_block",
                    "message": "Missing approval signature",
                    "suggestion": "Obtain approval signature before release"
                },
                {
                    "severity": "warning",
                    "check_type": "revision_block",
                    "message": "Revision history incomplete",
                    "suggestion": "Add description for Rev A changes"
                }
            ]
        }
    }

    # Test 1: Full PDF Report
    print("\n[1] Testing Full PDF Report Generation...")
    start = time.perf_counter()

    try:
        response = requests.post(
            f"{BASE_URL}/phase25/generate-pdf-report",
            json={
                "drawing_number": "DWG-12345",
                "drawing_revision": "C",
                "project_name": "ACHE Bundle Assembly",
                "validator_results": validator_results,
                "level": "detailed",
                "include_charts": True,
                "summary_only": False
            },
            timeout=30
        )

        elapsed = (time.perf_counter() - start) * 1000

        if response.status_code == 200:
            result = response.json()
            print(f"    [PASS] Full PDF generated in {elapsed:.1f}ms")
            print(f"    - Filename: {result['filename']}")
            print(f"    - Size: {result['size_bytes']:,} bytes")
            print(f"    - Status: {result['overall_status']}")
            print(f"    - Pass Rate: {result['pass_rate']}%")

            # Save PDF to file
            pdf_bytes = base64.b64decode(result['content_base64'])
            output_path = Path(__file__).parent / "output" / result['filename']
            output_path.parent.mkdir(exist_ok=True)
            output_path.write_bytes(pdf_bytes)
            print(f"    - Saved to: {output_path}")
        else:
            print(f"    [FAIL] Status {response.status_code}: {response.text[:100]}")

    except Exception as e:
        print(f"    [FAIL] Error: {e}")

    # Test 2: Summary PDF
    print("\n[2] Testing Summary PDF Generation...")
    start = time.perf_counter()

    try:
        response = requests.post(
            f"{BASE_URL}/phase25/generate-pdf-report",
            json={
                "drawing_number": "DWG-12345",
                "drawing_revision": "C",
                "project_name": "ACHE Bundle Assembly",
                "validator_results": validator_results,
                "summary_only": True
            },
            timeout=30
        )

        elapsed = (time.perf_counter() - start) * 1000

        if response.status_code == 200:
            result = response.json()
            print(f"    [PASS] Summary PDF generated in {elapsed:.1f}ms")
            print(f"    - Size: {result['size_bytes']:,} bytes")

            # Save PDF
            pdf_bytes = base64.b64decode(result['content_base64'])
            output_path = Path(__file__).parent / "output" / "validation_summary_DWG-12345.pdf"
            output_path.write_bytes(pdf_bytes)
            print(f"    - Saved to: {output_path}")
        else:
            print(f"    [FAIL] Status {response.status_code}: {response.text[:100]}")

    except Exception as e:
        print(f"    [FAIL] Error: {e}")

    # Test 3: JSON Report (for comparison)
    print("\n[3] Testing JSON Report Generation...")
    start = time.perf_counter()

    try:
        response = requests.post(
            f"{BASE_URL}/phase25/generate-report",
            json={
                "drawing_number": "DWG-12345",
                "drawing_revision": "C",
                "validator_results": validator_results,
                "format": "json",
                "level": "standard"
            },
            timeout=30
        )

        elapsed = (time.perf_counter() - start) * 1000

        if response.status_code == 200:
            result = response.json()
            content = json.loads(result['content']) if isinstance(result['content'], str) else result['content']
            print(f"    [PASS] JSON report generated in {elapsed:.1f}ms")
            print(f"    - Status: {content.get('overall_status')}")
            print(f"    - Pass Rate: {content.get('overall_pass_rate')}%")
            print(f"    - Total Checks: {content.get('statistics', {}).get('total_checks')}")
        else:
            print(f"    [FAIL] Status {response.status_code}")

    except Exception as e:
        print(f"    [FAIL] Error: {e}")

    # Test 4: HTML Report
    print("\n[4] Testing HTML Report Generation...")
    start = time.perf_counter()

    try:
        response = requests.post(
            f"{BASE_URL}/phase25/generate-report",
            json={
                "drawing_number": "DWG-12345",
                "drawing_revision": "C",
                "validator_results": validator_results,
                "format": "html"
            },
            timeout=30
        )

        elapsed = (time.perf_counter() - start) * 1000

        if response.status_code == 200:
            result = response.json()
            html_content = result['content']
            print(f"    [PASS] HTML report generated in {elapsed:.1f}ms")
            print(f"    - Size: {len(html_content):,} chars")

            # Save HTML
            output_path = Path(__file__).parent / "output" / "validation_report_DWG-12345.html"
            output_path.write_text(html_content)
            print(f"    - Saved to: {output_path}")
        else:
            print(f"    [FAIL] Status {response.status_code}")

    except Exception as e:
        print(f"    [FAIL] Error: {e}")

    print("\n" + "=" * 70)
    print("PDF REPORT TESTS COMPLETE")
    print("=" * 70)
    print("\nCheck the tests/output/ folder for generated reports")


if __name__ == "__main__":
    test_pdf_generation()
