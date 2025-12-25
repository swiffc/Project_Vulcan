
import sys
import os
import time
import threading
import asyncio
from pathlib import Path
import httpx
import uvicorn

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import the app
from desktop_server.server import app

def run_server():
    # Use a different port to avoid conflicts
    uvicorn.run(app, host="127.0.0.1", port=8002, log_level="error")

async def run_tests():
    print("--- Starting Live Integration Test (Port 8002) ---")
    
    # Start server in a background thread
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    print("Waiting for server to start...")
    time.sleep(8)  # Give it more time for standards DB and COM initialization
    
    async with httpx.AsyncClient(base_url="http://127.0.0.1:8002", timeout=10.0) as client:
        # 1. Base Health
        print("\n[TEST 1] Testing [/health]...")
        try:
            resp = await client.get("/health")
            print(f"Status: {resp.status_code}, Body: {resp.json()}")
        except Exception as e:
            print(f"Health test failed: {e}")

        # 2. Window List
        print("\n[TEST 2] Testing [/window/list]...")
        try:
            resp = await client.get("/window/list")
            print(f"Status: {resp.status_code}")
            if resp.status_code == 200:
                windows = resp.json().get("windows", [])
                print(f"Success: Found {len(windows)} active windows.")
        except Exception as e:
            print(f"Window list failed: {e}")

        # 3. Recorder
        print("\n[TEST 3] Testing [/recorder/status]...")
        try:
            resp = await client.get("/recorder/status")
            print(f"Status: {resp.status_code}, Body: {resp.json()}")
        except Exception as e:
            print(f"Recorder failed: {e}")

        # 4. Verifier
        print("\n[TEST 4] Testing [/verifier/last_result]...")
        try:
            resp = await client.get("/verifier/last_result")
            print(f"Status: {resp.status_code}, Body: {resp.json()}")
        except Exception as e:
            print(f"Verifier failed: {e}")

        # 5. CAD (Optional)
        print("\n[TEST 5] Testing [/com/solidworks/status]...")
        try:
            resp = await client.get("/com/solidworks/status")
            print(f"Status: {resp.status_code}, Body: {resp.json()}")
        except Exception as e:
            print(f"CAD status failed (Expected if SW not running): {e}")

    print("\n--- Live Integration Test Complete ---")

if __name__ == "__main__":
    asyncio.run(run_tests())
