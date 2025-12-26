"""
SolidWorks Materials Library API
================================
Complete material management including:
- Material library browsing
- Material assignment
- Custom material creation
- Material properties access
"""

import logging
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

try:
    import win32com.client
    import pythoncom
    COM_AVAILABLE = True
except ImportError:
    COM_AVAILABLE = False


# Built-in material database for common materials
MATERIAL_DATABASE = {
    # Steels
    "1020 Steel": {"density": 7900, "yield": 351.6e6, "tensile": 420.5e6, "modulus": 200e9, "poisson": 0.29, "category": "Steel"},
    "1045 Steel": {"density": 7850, "yield": 530e6, "tensile": 625e6, "modulus": 205e9, "poisson": 0.29, "category": "Steel"},
    "4140 Steel": {"density": 7850, "yield": 655e6, "tensile": 1020e6, "modulus": 210e9, "poisson": 0.29, "category": "Steel"},
    "A36 Steel": {"density": 7850, "yield": 250e6, "tensile": 400e6, "modulus": 200e9, "poisson": 0.26, "category": "Steel"},
    "304 Stainless": {"density": 8000, "yield": 215e6, "tensile": 505e6, "modulus": 193e9, "poisson": 0.29, "category": "Stainless Steel"},
    "316 Stainless": {"density": 8000, "yield": 205e6, "tensile": 515e6, "modulus": 193e9, "poisson": 0.30, "category": "Stainless Steel"},

    # Aluminum
    "6061-T6": {"density": 2700, "yield": 276e6, "tensile": 310e6, "modulus": 68.9e9, "poisson": 0.33, "category": "Aluminum"},
    "7075-T6": {"density": 2810, "yield": 503e6, "tensile": 572e6, "modulus": 71.7e9, "poisson": 0.33, "category": "Aluminum"},
    "2024-T3": {"density": 2780, "yield": 345e6, "tensile": 483e6, "modulus": 73.1e9, "poisson": 0.33, "category": "Aluminum"},

    # Other metals
    "Copper": {"density": 8960, "yield": 70e6, "tensile": 220e6, "modulus": 110e9, "poisson": 0.34, "category": "Copper"},
    "Brass": {"density": 8500, "yield": 200e6, "tensile": 350e6, "modulus": 100e9, "poisson": 0.34, "category": "Copper"},
    "Titanium Ti-6Al-4V": {"density": 4430, "yield": 880e6, "tensile": 950e6, "modulus": 113.8e9, "poisson": 0.34, "category": "Titanium"},

    # Plastics
    "ABS": {"density": 1020, "yield": 40e6, "tensile": 45e6, "modulus": 2.3e9, "poisson": 0.39, "category": "Plastic"},
    "Nylon 6": {"density": 1130, "yield": 75e6, "tensile": 85e6, "modulus": 2.9e9, "poisson": 0.39, "category": "Plastic"},
    "PEEK": {"density": 1310, "yield": 100e6, "tensile": 100e6, "modulus": 3.6e9, "poisson": 0.40, "category": "Plastic"},
    "Polycarbonate": {"density": 1200, "yield": 60e6, "tensile": 65e6, "modulus": 2.4e9, "poisson": 0.37, "category": "Plastic"},
}


# Pydantic models
class AssignMaterialRequest(BaseModel):
    material_name: str
    body_name: Optional[str] = None  # None = all bodies


class CreateMaterialRequest(BaseModel):
    name: str
    density: float  # kg/m³
    elastic_modulus: float  # Pa
    poisson_ratio: float
    yield_strength: Optional[float] = None  # Pa
    tensile_strength: Optional[float] = None  # Pa
    thermal_conductivity: Optional[float] = None  # W/(m·K)
    specific_heat: Optional[float] = None  # J/(kg·K)
    category: str = "Custom"


router = APIRouter(prefix="/solidworks-materials", tags=["solidworks-materials"])


def get_solidworks():
    """Get active SolidWorks application."""
    if not COM_AVAILABLE:
        raise HTTPException(status_code=501, detail="COM not available")
    pythoncom.CoInitialize()
    try:
        return win32com.client.GetActiveObject("SldWorks.Application")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SolidWorks not running: {e}")


# =============================================================================
# Material Library
# =============================================================================

@router.get("/library")
async def list_material_library():
    """
    List all materials in the built-in database.
    """
    materials = []
    for name, props in MATERIAL_DATABASE.items():
        materials.append({
            "name": name,
            "category": props["category"],
            "density_kg_m3": props["density"],
            "yield_strength_MPa": props["yield"] / 1e6,
            "tensile_strength_MPa": props["tensile"] / 1e6,
            "elastic_modulus_GPa": props["modulus"] / 1e9,
            "poisson_ratio": props["poisson"]
        })

    # Group by category
    categories = {}
    for mat in materials:
        cat = mat["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(mat["name"])

    return {
        "count": len(materials),
        "categories": categories,
        "materials": materials
    }


@router.get("/library/{category}")
async def list_materials_by_category(category: str):
    """
    List materials in a specific category.
    """
    materials = []
    for name, props in MATERIAL_DATABASE.items():
        if props["category"].lower() == category.lower():
            materials.append({
                "name": name,
                "density_kg_m3": props["density"],
                "yield_strength_MPa": props["yield"] / 1e6,
                "tensile_strength_MPa": props["tensile"] / 1e6
            })

    return {
        "category": category,
        "count": len(materials),
        "materials": materials
    }


@router.get("/properties/{material_name}")
async def get_material_properties(material_name: str):
    """
    Get detailed properties for a material.
    """
    props = MATERIAL_DATABASE.get(material_name)
    if not props:
        raise HTTPException(status_code=404, detail=f"Material '{material_name}' not found")

    return {
        "name": material_name,
        "category": props["category"],
        "mechanical": {
            "density_kg_m3": props["density"],
            "yield_strength_MPa": props["yield"] / 1e6,
            "tensile_strength_MPa": props["tensile"] / 1e6,
            "elastic_modulus_GPa": props["modulus"] / 1e9,
            "poisson_ratio": props["poisson"],
            "shear_modulus_GPa": round(props["modulus"] / (2 * (1 + props["poisson"])) / 1e9, 2)
        },
        "derived": {
            "specific_stiffness": round(props["modulus"] / props["density"] / 1e6, 2),
            "specific_strength": round(props["yield"] / props["density"], 2)
        }
    }


# =============================================================================
# Material Assignment
# =============================================================================

@router.post("/assign")
async def assign_material(request: AssignMaterialRequest):
    """
    Assign a material to the active part or specific body.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        if doc.GetType() != 1:  # Part
            raise HTTPException(status_code=400, detail="Material assignment requires a part document")

        # Get material properties
        mat_props = MATERIAL_DATABASE.get(request.material_name)

        # Try SolidWorks material database first
        result = doc.SetMaterialPropertyName2("", "", request.material_name)

        if not result and mat_props:
            # Apply custom material properties
            ext = doc.Extension
            if ext:
                # Set material by property values
                doc.SetMaterialPropertyValues2(
                    mat_props["density"],
                    mat_props["modulus"],
                    mat_props["modulus"] / (2 * (1 + mat_props["poisson"])),  # Shear modulus
                    mat_props["poisson"],
                    0,  # Thermal expansion
                    0,  # Thermal conductivity
                    0,  # Specific heat
                    0,  # Electrical resistivity
                    True
                )
                result = True

        doc.EditRebuild3()

        return {
            "success": result,
            "material": request.material_name,
            "body": request.body_name or "all bodies",
            "message": f"Material '{request.material_name}' assigned"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Assign material failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.get("/current")
async def get_current_material():
    """
    Get the currently assigned material.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        # Get material name
        mat_name = doc.GetMaterialPropertyName2("", "")

        # Get material properties
        density = 0
        try:
            mass_props = doc.Extension.CreateMassProperty()
            if mass_props:
                # Calculate density from mass and volume
                mass = mass_props.Mass
                volume = mass_props.Volume
                if volume > 0:
                    density = mass / volume
        except Exception:
            pass

        return {
            "material_name": mat_name or "Not assigned",
            "calculated_density_kg_m3": round(density, 2) if density > 0 else None
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get current material failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.delete("/remove")
async def remove_material():
    """
    Remove material assignment from part.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        doc.SetMaterialPropertyName2("", "", "")
        doc.EditRebuild3()

        return {"success": True, "message": "Material removed"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Remove material failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


# =============================================================================
# Custom Materials
# =============================================================================

@router.post("/create")
async def create_custom_material(request: CreateMaterialRequest):
    """
    Create a custom material (stored in local database).
    """
    try:
        # Add to local database
        MATERIAL_DATABASE[request.name] = {
            "density": request.density,
            "yield": request.yield_strength or 0,
            "tensile": request.tensile_strength or 0,
            "modulus": request.elastic_modulus,
            "poisson": request.poisson_ratio,
            "category": request.category
        }

        return {
            "success": True,
            "name": request.name,
            "category": request.category,
            "message": f"Custom material '{request.name}' created"
        }
    except Exception as e:
        logger.error(f"Create material failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Material Calculations
# =============================================================================

@router.post("/calculate-weight")
async def calculate_weight(material_name: str, volume_m3: float):
    """
    Calculate weight given material and volume.
    """
    props = MATERIAL_DATABASE.get(material_name)
    if not props:
        raise HTTPException(status_code=404, detail=f"Material '{material_name}' not found")

    mass_kg = props["density"] * volume_m3

    return {
        "material": material_name,
        "volume_m3": volume_m3,
        "volume_mm3": volume_m3 * 1e9,
        "density_kg_m3": props["density"],
        "mass_kg": round(mass_kg, 4),
        "mass_lb": round(mass_kg * 2.20462, 4)
    }


@router.post("/compare")
async def compare_materials(material_names: List[str]):
    """
    Compare properties of multiple materials.
    """
    comparison = []
    for name in material_names:
        props = MATERIAL_DATABASE.get(name)
        if props:
            comparison.append({
                "name": name,
                "category": props["category"],
                "density_kg_m3": props["density"],
                "yield_MPa": props["yield"] / 1e6,
                "tensile_MPa": props["tensile"] / 1e6,
                "modulus_GPa": props["modulus"] / 1e9,
                "specific_strength": round(props["yield"] / props["density"], 2),
                "specific_stiffness": round(props["modulus"] / props["density"] / 1e6, 2)
            })

    # Sort by specific strength
    comparison.sort(key=lambda x: x["specific_strength"], reverse=True)

    return {
        "count": len(comparison),
        "comparison": comparison,
        "best_specific_strength": comparison[0]["name"] if comparison else None,
        "lightest": min(comparison, key=lambda x: x["density_kg_m3"])["name"] if comparison else None,
        "strongest": max(comparison, key=lambda x: x["yield_MPa"])["name"] if comparison else None
    }


@router.get("/search/{query}")
async def search_materials(query: str):
    """
    Search materials by name or category.
    """
    query_lower = query.lower()
    matches = []

    for name, props in MATERIAL_DATABASE.items():
        if query_lower in name.lower() or query_lower in props["category"].lower():
            matches.append({
                "name": name,
                "category": props["category"],
                "density_kg_m3": props["density"]
            })

    return {
        "query": query,
        "count": len(matches),
        "matches": matches
    }


__all__ = ["router"]
