import sys
import os
import time
import threading
import asyncio
from pathlib import Path
import httpx
import uvicorn
from typing import List, Dict, Any

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import the app
from desktop_server.server import app

TEST_PORT = 8003
BASE_URL = f"http://127.0.0.1:{TEST_PORT}"


def run_server():
    uvicorn.run(app, host="127.0.0.1", port=TEST_PORT, log_level="error")


async def test_endpoint(
    client: httpx.AsyncClient, name: str, method: str, path: str, body: Dict = None
):
    print(f"\n[TEST] {name} ({method} {path})...")
    try:
        if method == "GET":
            resp = await client.get(path)
        else:
            resp = await client.post(path, json=body or {})

        print(f"  Status: {resp.status_code}")
        if resp.status_code < 300:
            print(f"  Success: {resp.json()}")
            return True, resp.json()
        else:
            print(f"  Failed: {resp.text}")
            return False, resp.text
    except Exception as e:
        print(f"  Error: {e}")
        return False, str(e)


async def run_verification():
    print("=" * 60)
    print("PROJECT VULCAN - CAD VERIFICATION SUITE")
    print("=" * 60)

    # Start server in background
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    print(f"Waiting for server to initialize on port {TEST_PORT}...")
    await asyncio.sleep(5)

    results = []

    async with httpx.AsyncClient(base_url=BASE_URL, timeout=15.0) as client:
        # Phase 1: Core System Health
        results.append(await test_endpoint(client, "Base Health", "GET", "/health"))

        # Phase 2: SolidWorks Tool Connectivity
        results.append(
            await test_endpoint(client, "SW Status", "GET", "/com/solidworks/status")
        )

        # Phase 3: Advanced Tool Schemas (Smoke Test)
        # We test if the routes exist, even if SW isn't running (should return 400 with "No active document" or similar)

        # Reference Geometry
        results.append(
            await test_endpoint(
                client,
                "Ref Plane Schema",
                "POST",
                "/com/solidworks/create_plane_offset",
                {"base_name": "Front Plane", "distance": 0.1},
            )
        )

        # Sheet Metal
        results.append(
            await test_endpoint(
                client,
                "Sheet Metal Base Schema",
                "POST",
                "/com/solidworks/sheet_metal_base",
                {"thickness": 0.002, "radius": 0.001},
            )
        )

        # Configurations
        results.append(
            await test_endpoint(
                client,
                "Add Configuration Schema",
                "POST",
                "/com/solidworks/add_configuration",
                {"name": "Version_A", "description": "Test Config"},
            )
        )

        # Weldments
        results.append(
            await test_endpoint(
                client,
                "Structural Member Schema",
                "POST",
                "/com/solidworks/add_structural_member",
                {"type": "pipe", "size": "0.5 skip sch 40", "path_segments": ["Line1"]},
            )
        )

        # Phase 4: Inventor Tool Connectivity
        results.append(
            await test_endpoint(
                client, "Inventor Status", "GET", "/com/inventor/status"
            )
        )

        # Phase 5: Custom Properties
        results.append(
            await test_endpoint(
                client,
                "SW Custom Props",
                "POST",
                "/com/solidworks/set_custom_property",
                {"name": "Project", "value": "Vulcan"},
            )
        )

    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)

    total = len(results)
    passed = sum(1 for r in results if r[0])

    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")

    if passed == total:
        print(
            "\nSUCCESS: All CAD infrastructure routes are active and responding correctly."
        )
    else:
        print("\nWARNING: Some tests failed. Ensure dependencies are installed.")


if __name__ == "__main__":
    asyncio.run(run_verification())
