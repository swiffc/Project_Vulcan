import json
import logging
import os
import httpx
from typing import Any, Dict, List, Optional, Union
from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("vulcan-cad-mcp")

# Initialize FastMCP Server
mcp = FastMCP("vulcan-cad-mcp")

# Configuration
DESKTOP_SERVER_URL = os.environ.get("DESKTOP_SERVER_URL", "http://localhost:8000")


async def call_desktop(endpoint: str, payload: Dict[str, Any] = None) -> Dict[str, Any]:
    """Helper to call the desktop server endpoints."""
    url = f"{DESKTOP_SERVER_URL}{endpoint}"
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            logger.info(f"Calling Desktop: {url}")
            resp = await client.post(url, json=payload or {})
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPError as e:
            logger.error(f"Desktop API Error ({endpoint}): {e}")
            return {"error": str(e), "status": "failed"}
        except Exception as e:
            logger.error(f"Connection Error: {e}")
            return {"error": str(e), "status": "failed"}


async def process_sketch_entities(entities: List[Dict[str, Any]]):
    """Process a list of sketch entities (circles, lines, etc)."""
    for entity in entities:
        etype = entity.get("type", "").lower()

        if etype == "circle":
            await call_desktop(
                "/com/solidworks/draw_circle",
                {
                    "x": entity.get("x", 0),
                    "y": entity.get("y", 0),
                    "radius": entity.get("radius", 0),
                },
            )
        elif etype == "rectangle":
            await call_desktop(
                "/com/solidworks/draw_rectangle",
                {
                    "x1": entity.get("x1", 0),
                    "y1": entity.get("y1", 0),
                    "x2": entity.get("x2", 0),
                    "y2": entity.get("y2", 0),
                },
            )
        elif etype == "line":
            await call_desktop(
                "/com/solidworks/draw_line",
                {
                    "x1": entity.get("x1"),
                    "y1": entity.get("y1"),
                    "x2": entity.get("x2"),
                    "y2": entity.get("y2"),
                },
            )
        elif etype == "centerline":
            await call_desktop(
                "/com/solidworks/draw_centerline",
                {
                    "x1": entity.get("x1"),
                    "y1": entity.get("y1"),
                    "x2": entity.get("x2"),
                    "y2": entity.get("y2"),
                },
            )


@mcp.tool()
async def create_part(
    application: str, name: str, features: List[Dict[str, Any]]
) -> str:
    """
    Create a new CAD part by executing a sequence of features.

    Args:
        application: "solidworks" (currently only supported)
        name: Name of the part (will be saved with this name if referenced later)
        features: List of feature definitions.
                  Supported types: "extrude", "cut", "revolve", "fillet", "hole", "pattern_circular".

                  Example 'extrude':
                  {
                    "type": "extrude",
                    "sketch": { "plane": "Front", "entities": [{"type": "circle", "radius": 0.05, ...}] },
                    "depth": 0.02
                  }
    """
    if application.lower() != "solidworks":
        return "Error: currently only 'solidworks' is fully supported for automated creation."

    # 1. New Part
    logger.info("Creating new part...")
    res = await call_desktop("/com/solidworks/new_part")
    if "error" in res:
        return json.dumps(res)

    results = []

    # 2. Process Features
    for i, feat in enumerate(features):
        ftype = feat.get("type", "").lower()
        logger.info(f"Processing feature {i}: {ftype}")

        try:
            # --- BASE SKETCH LOGIC (Common to extrude/cut/revolve) ---
            if "sketch" in feat:
                sketch = feat["sketch"]
                # Create Sketch
                await call_desktop(
                    "/com/solidworks/create_sketch",
                    {"plane": sketch.get("plane", "Front")},
                )
                # Draw Entities
                await process_sketch_entities(sketch.get("entities", []))

            # --- FEATURE SPECIFIC LOGIC ---

            if ftype == "extrude":
                res = await call_desktop(
                    "/com/solidworks/extrude",
                    {"depth": feat.get("depth", 0.01), "direction": 0},
                )

            elif ftype == "cut" or ftype == "cut_extrude":
                res = await call_desktop(
                    "/com/solidworks/extrude_cut",
                    {"depth": feat.get("depth", 0.01)},  # 999 for through all
                )

            elif ftype == "revolve":
                res = await call_desktop(
                    "/com/solidworks/revolve", {"angle": feat.get("angle", 360.0)}
                )

            elif ftype == "fillet":
                # Fillet doesn't use a sketch, it applies to selected edges
                # (Complex selection logic simplified here - applies to 'last feature' edges often or manual select)
                # For now, simplistic approach:
                res = await call_desktop(
                    "/com/solidworks/fillet", {"radius": feat.get("radius", 0.005)}
                )

            elif ftype == "pattern_circular":
                res = await call_desktop(
                    "/com/solidworks/pattern_circular",
                    {
                        "count": feat.get("count", 4),
                        "spacing": feat.get("spacing", 1.57),  # Radians
                    },
                )

            elif ftype == "simple_hole":
                # Uses HoleWizard logic
                res = await call_desktop(
                    "/com/solidworks/simple_hole",
                    {
                        "x": feat.get("x", 0),
                        "y": feat.get("y", 0),
                        "z": feat.get("z", 0),
                        "diameter": feat.get("diameter", 0.01),
                    },
                )

            else:
                res = {"status": "skipped", "message": f"Unknown feature type: {ftype}"}

            results.append({"feature_index": i, "type": ftype, "result": res})

            # Clean up: Close sketch if we opened one and the operation didn't consume it automatically
            # (SolidWorks features usually consume the active sketch)

        except Exception as e:
            logger.error(f"Feature {i} failed: {e}")
            results.append({"feature_index": i, "error": str(e)})

    return json.dumps({"status": "completed", "results": results}, indent=2)


@mcp.tool()
async def get_mass_properties(path: str = "") -> str:
    """Get mass properties of the active document."""
    # Logic in desktop server uses active doc if path empty?
    # Actually server.py endpoint is /mass_properties but solidworks_com DOESNT HAVE IT exposed!
    # Checking solidworks_com.py... it is MISSING mass props endpoint.
    return "Status: Not implemented in desktop server yet."


if __name__ == "__main__":
    mcp.run()
