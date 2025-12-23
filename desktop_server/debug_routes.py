import sys
import os
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from desktop_server.server import app

print("Checking registered routes...")
for route in app.routes:
    if hasattr(route, "path"):
        methods = getattr(route, "methods", [])
        print(f"[{', '.join(methods)}] {route.path}")

print("\nRoute check complete.")
