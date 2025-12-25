import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

print("Testing imports...")
try:
    from desktop_server.controllers import recorder_router, verifier_router

    print("SUCCESS: recorder_router and verifier_router imported.")

    from desktop_server.com import (
        solidworks_router,
        solidworks_drawings_router,
        inventor_imates_router,
        solidworks_mate_refs_router,
    )

    print("SUCCESS: CAD routers imported.")

    print("\nVerified Routes in recorder_router:")
    for route in recorder_router.routes:
        print(f" - {route.path}")

    print("\nVerified Routes in verifier_router:")
    for route in verifier_router.routes:
        print(f" - {route.path}")

except Exception as e:
    print(f"FAILED: {e}")
    import traceback

    traceback.print_exc()
