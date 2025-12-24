"""
Assembly Analyzer - AI-Powered Design Assistant
Analyzes assemblies to provide:
- Part purpose identification
- Design recommendations
- Best practices suggestions
- Learning from patterns
"""

import os
import json
import logging
import re
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import win32com.client
import pythoncom

router = APIRouter(prefix="/com/solidworks/analysis", tags=["assembly-analysis"])
logger = logging.getLogger(__name__)

# Knowledge base path
KNOWLEDGE_BASE_PATH = Path(__file__).parent.parent.parent / "data" / "design_knowledge"
KNOWLEDGE_BASE_PATH.mkdir(parents=True, exist_ok=True)

# Part type patterns for classification
PART_TYPE_PATTERNS = {
    "structural_frame": [
        r"frame", r"beam", r"channel", r"angle", r"tube", r"square.*tube",
        r"structural", r"support", r"column", r"post", r"rail"
    ],
    "panel": [
        r"panel", r"plate", r"sheet", r"skin", r"cover", r"shroud",
        r"enclosure", r"wall", r"deck", r"floor"
    ],
    "seal": [
        r"seal", r"gasket", r"o-ring", r"weather.*strip", r"air.*seal"
    ],
    "fastener": [
        r"bolt", r"screw", r"nut", r"washer", r"rivet", r"pin",
        r"stud", r"anchor", r"clip", r"clamp"
    ],
    "bracket": [
        r"bracket", r"mount", r"hanger", r"support", r"brace",
        r"gusset", r"stiffener", r"reinforcement"
    ],
    "weldment": [
        r"weldment", r"weld.*assy", r"welded", r"fabricat"
    ],
    "ring": [
        r"ring", r"collar", r"flange", r"hub", r"disc"
    ],
    "lifting": [
        r"lift", r"lug", r"eye", r"hook", r"handle"
    ],
    "fan_component": [
        r"fan", r"blade", r"impeller", r"rotor", r"shroud"
    ],
    "ductwork": [
        r"duct", r"plenum", r"transition", r"diffuser", r"damper"
    ]
}

# Design best practices by part type
DESIGN_BEST_PRACTICES = {
    "structural_frame": {
        "recommendations": [
            "Ensure adequate weld access for all joints",
            "Consider modular sub-assemblies for easier fabrication",
            "Verify load paths are continuous through connections",
            "Check for proper clearance for assembly tools",
            "Add lifting points for components over 50 lbs"
        ],
        "common_issues": [
            "Insufficient clearance for welding equipment",
            "Missing gussets at high-stress joints",
            "Unbraced lengths exceeding code limits"
        ]
    },
    "panel": {
        "recommendations": [
            "Use consistent hole patterns for interchangeability",
            "Add stiffening features for large unsupported areas",
            "Consider thermal expansion in panel sizing",
            "Ensure proper edge distances for fastener holes",
            "Add drain holes in outdoor panels"
        ],
        "common_issues": [
            "Panel flutter in high-wind applications",
            "Insufficient edge distance causing tear-out",
            "Missing access panels for maintenance"
        ]
    },
    "seal": {
        "recommendations": [
            "Ensure continuous seal path around perimeter",
            "Verify compression ratio is within seal specs (typically 15-25%)",
            "Add seal retainers where vibration is present",
            "Consider thermal expansion of mating surfaces",
            "Use redundant seals in critical applications"
        ],
        "common_issues": [
            "Gaps at corners due to improper mitering",
            "Over-compression causing seal extrusion",
            "Incompatible materials with operating environment"
        ]
    },
    "lifting": {
        "recommendations": [
            "Position lifting points to balance load",
            "Use safety factor of 4:1 minimum for lifting lugs",
            "Ensure lifting points are accessible with rigging",
            "Add witness marks for sling angle limits",
            "Consider shipping orientation vs installed orientation"
        ],
        "common_issues": [
            "Lifting points not aligned with center of gravity",
            "Insufficient weld size for lifting loads",
            "Interference with rigging hardware"
        ]
    },
    "weldment": {
        "recommendations": [
            "Group welds by position (flat, horizontal, vertical)",
            "Minimize weld distortion with proper sequencing",
            "Add weld symbols with full specifications",
            "Consider post-weld heat treatment if required",
            "Design for inspection access"
        ],
        "common_issues": [
            "Weld access blocked by adjacent components",
            "Distortion affecting mating surfaces",
            "Missing pre-heat or interpass requirements"
        ]
    }
}


class PartAnalysis(BaseModel):
    part_number: str
    part_type: str
    purpose: str
    recommendations: List[str]
    potential_issues: List[str]
    related_parts: List[str]
    confidence: float


class AssemblyAnalysisRequest(BaseModel):
    include_geometry: bool = False
    depth: int = 1  # How deep to analyze sub-assemblies


class DesignPattern(BaseModel):
    pattern_id: str
    pattern_type: str
    description: str
    examples: List[str]
    learned_from: str
    confidence: float
    created_at: str


def classify_part_type(part_name: str, file_path: str = "", properties: Dict = None, geometry: Dict = None) -> tuple:
    """Classify a part based on its name, properties, and geometry."""
    part_name_lower = part_name.lower()
    properties = properties or {}
    geometry = geometry or {}

    best_match = ("unknown", 0.0)

    # First pass: Name-based classification
    for part_type, patterns in PART_TYPE_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, part_name_lower):
                confidence = 0.7 + (len(pattern) / 20) * 0.3
                confidence = min(confidence, 0.95)
                if confidence > best_match[1]:
                    best_match = (part_type, confidence)

    # Second pass: Property-based classification (boosts confidence)
    if properties:
        desc = str(properties.get("Description", "")).lower()
        material = str(properties.get("Material", "")).lower()

        # Check description for type hints
        for part_type, patterns in PART_TYPE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, desc):
                    if part_type == best_match[0]:
                        best_match = (best_match[0], min(best_match[1] + 0.15, 0.98))
                    elif best_match[1] < 0.5:
                        best_match = (part_type, 0.65)

        # Material hints
        if "rubber" in material or "epdm" in material or "neoprene" in material:
            if best_match[0] == "unknown":
                best_match = ("seal", 0.75)
            elif best_match[0] == "seal":
                best_match = ("seal", min(best_match[1] + 0.1, 0.98))

        if "steel" in material or "aluminum" in material:
            if best_match[0] == "structural_frame":
                best_match = (best_match[0], min(best_match[1] + 0.05, 0.98))

    # Third pass: Geometry-based classification
    if geometry:
        mass = geometry.get("mass", 0)
        volume = geometry.get("volume", 0)
        surface_area = geometry.get("surface_area", 0)

        # Large mass + high surface/volume ratio = likely panel
        if volume > 0 and surface_area > 0:
            sv_ratio = surface_area / volume
            if sv_ratio > 1000 and mass > 0.5:  # Thin, large part
                if best_match[0] == "unknown":
                    best_match = ("panel", 0.6)
                elif best_match[0] == "panel":
                    best_match = ("panel", min(best_match[1] + 0.1, 0.98))

        # Very low mass = likely seal or gasket
        if 0 < mass < 0.1:
            if best_match[0] == "unknown":
                best_match = ("seal", 0.55)

        # Small bounding box = likely fastener
        bbox = geometry.get("bounding_box", {})
        if bbox:
            max_dim = max(bbox.get("x", 0), bbox.get("y", 0), bbox.get("z", 0))
            if max_dim < 0.05 and mass > 0:  # Less than 50mm
                if best_match[0] == "unknown":
                    best_match = ("fastener", 0.6)

    # File extension boost
    if file_path:
        if ".SLDASM" in file_path.upper() and best_match[0] == "weldment":
            best_match = (best_match[0], min(best_match[1] + 0.1, 0.98))

    return best_match


def generate_suggested_name(part_name: str, part_type: str, geometry: Dict = None, material: Dict = None, properties: Dict = None) -> str:
    """Generate a suggested proper name for a part based on its function."""
    geometry = geometry or {}
    material = material or {}
    properties = properties or {}

    # Get size category
    bbox = geometry.get("bounding_box", {})
    max_dim = max(bbox.get("x", 0), bbox.get("y", 0), bbox.get("z", 0)) * 1000  # mm

    size_prefix = ""
    if max_dim > 0:
        if max_dim < 50:
            size_prefix = "SM"  # Small
        elif max_dim < 200:
            size_prefix = "MD"  # Medium
        elif max_dim < 500:
            size_prefix = "LG"  # Large
        else:
            size_prefix = "XL"  # Extra Large

    # Get material abbreviation
    mat_name = material.get("name", "").upper()
    mat_abbrev = ""
    if "STEEL" in mat_name or "1018" in mat_name or "1020" in mat_name:
        mat_abbrev = "STL"
    elif "STAINLESS" in mat_name or "304" in mat_name or "316" in mat_name:
        mat_abbrev = "SS"
    elif "ALUMINUM" in mat_name or "6061" in mat_name or "5052" in mat_name:
        mat_abbrev = "AL"
    elif "RUBBER" in mat_name or "EPDM" in mat_name or "NEOPRENE" in mat_name:
        mat_abbrev = "RBR"
    elif "PLASTIC" in mat_name or "HDPE" in mat_name or "ABS" in mat_name:
        mat_abbrev = "PLS"

    # Type-based naming patterns
    type_patterns = {
        "structural_frame": ["FRAME", "STRUCT", "SUPPORT", "BEAM"],
        "panel": ["PNL", "PANEL", "COVER", "ENCL"],
        "seal": ["SEAL", "GSKT", "GASKET"],
        "fastener": ["FSTNR", "BOLT", "SCREW", "NUT"],
        "bracket": ["BRKT", "BRACKET", "MNT", "MOUNT"],
        "weldment": ["WLDMT", "WELD-ASSY", "FAB"],
        "ring": ["RING", "COLLAR", "FLANGE"],
        "lifting": ["LIFT-LUG", "LIFTING", "EYE"],
        "fan_component": ["FAN", "IMPELLER", "BLADE"],
        "ductwork": ["DUCT", "PLENUM", "TRANS"],
    }

    # Build suggested name
    type_name = type_patterns.get(part_type, ["PART"])[0]

    # Try to extract useful info from existing name
    existing_nums = re.findall(r'\d+', part_name)
    sequence = existing_nums[-1] if existing_nums else "001"

    # Construct name parts
    name_parts = []
    if size_prefix:
        name_parts.append(size_prefix)
    if mat_abbrev:
        name_parts.append(mat_abbrev)
    name_parts.append(type_name)
    name_parts.append(sequence.zfill(3))

    suggested = "-".join(name_parts)

    # If the current name already follows a good pattern, keep it
    if re.match(r'^[A-Z]{2,4}-[A-Z]{2,6}-\d{3}', part_name.upper()):
        return part_name  # Already well-named

    return suggested


def generate_part_purpose(part_name: str, part_type: str, context: Dict = None) -> str:
    """Generate a description of the part's purpose in the assembly."""

    purposes = {
        "structural_frame": f"Provides structural support and load-bearing capacity. {part_name} forms part of the main framework that maintains assembly geometry and transfers loads.",
        "panel": f"Serves as an enclosure or barrier element. {part_name} provides protection, containment, or aesthetic coverage for the assembly.",
        "seal": f"Creates an environmental barrier. {part_name} prevents air, water, or contaminant infiltration between mating components.",
        "fastener": f"Mechanically joins components. {part_name} provides a removable or permanent connection between assembly parts.",
        "bracket": f"Connects and supports secondary components. {part_name} transfers loads between the main structure and attached equipment.",
        "weldment": f"Pre-fabricated welded sub-assembly. {part_name} combines multiple structural elements into a single manufacturable unit.",
        "ring": f"Provides circumferential support or sealing. {part_name} distributes loads or creates a sealed interface around a circular feature.",
        "lifting": f"Enables safe handling during assembly and maintenance. {part_name} provides attachment points for lifting equipment.",
        "fan_component": f"Part of the air movement system. {part_name} contributes to airflow generation or direction within the assembly.",
        "ductwork": f"Directs airflow through the system. {part_name} contains and guides air movement between components.",
        "unknown": f"{part_name} serves a functional role in the assembly. Further analysis of geometry and relationships needed to determine specific purpose."
    }

    return purposes.get(part_type, purposes["unknown"])


def get_recommendations_for_part(part_type: str, part_name: str, context: Dict = None) -> tuple:
    """Get design recommendations and potential issues for a part type."""

    practices = DESIGN_BEST_PRACTICES.get(part_type, {})
    recommendations = practices.get("recommendations", [
        "Review part for compliance with assembly requirements",
        "Verify all mating surfaces are properly defined",
        "Check for interference with adjacent components"
    ])

    issues = practices.get("common_issues", [
        "Verify clearances for assembly and maintenance",
        "Check material compatibility with environment"
    ])

    return recommendations, issues


def find_related_parts(part_name: str, all_parts: List[Dict]) -> List[str]:
    """Find parts that are likely related based on naming patterns."""
    related = []

    # Extract base name (remove suffixes like -1, -2, etc.)
    base_pattern = re.sub(r'[-_]\d+$', '', part_name)

    for part in all_parts:
        other_name = part.get("part_number", "")
        if other_name != part_name:
            other_base = re.sub(r'[-_]\d+$', '', other_name)

            # Check for similar base names
            if base_pattern in other_name or other_base in part_name:
                related.append(other_name)

            # Check for common prefixes
            if len(base_pattern) > 5 and base_pattern[:5] == other_base[:5]:
                if other_name not in related:
                    related.append(other_name)

    return related[:5]  # Limit to top 5 related parts


def get_mass_properties(ref_model) -> Dict:
    """Extract mass properties from a SolidWorks model."""
    geometry = {}
    try:
        if ref_model and hasattr(ref_model, 'Extension'):
            ext = ref_model.Extension
            if hasattr(ext, 'GetMassProperties2'):
                props = ext.GetMassProperties2(1, 0)  # 1 = include hidden bodies
                if props and len(props) >= 5:
                    geometry = {
                        "mass": props[0] if props[0] else 0,
                        "volume": props[1] if props[1] else 0,
                        "surface_area": props[2] if props[2] else 0,
                        "center_of_mass": {
                            "x": props[3] if len(props) > 3 else 0,
                            "y": props[4] if len(props) > 4 else 0,
                            "z": props[5] if len(props) > 5 else 0
                        }
                    }
    except Exception as e:
        logger.debug(f"Could not get mass properties: {e}")
    return geometry


def get_bounding_box(ref_model) -> Dict:
    """Get bounding box dimensions from a SolidWorks model."""
    bbox = {}
    try:
        if ref_model:
            # Try to get bounding box from part
            box = ref_model.GetPartBox()
            if box and len(box) >= 6:
                bbox = {
                    "x": abs(box[3] - box[0]),
                    "y": abs(box[4] - box[1]),
                    "z": abs(box[5] - box[2]),
                    "min": {"x": box[0], "y": box[1], "z": box[2]},
                    "max": {"x": box[3], "y": box[4], "z": box[5]}
                }
    except Exception as e:
        logger.debug(f"Could not get bounding box: {e}")
    return bbox


def get_material_info(ref_model) -> Dict:
    """Extract material information from a SolidWorks model."""
    material = {}
    try:
        if ref_model:
            # Get material name
            mat_name = None
            if hasattr(ref_model, 'MaterialIdName'):
                mat_name = ref_model.MaterialIdName
            elif hasattr(ref_model, 'GetMaterialPropertyName'):
                mat_name = ref_model.GetMaterialPropertyName("")

            if mat_name:
                material["name"] = str(mat_name)

            # Try to get material properties
            if hasattr(ref_model, 'MaterialPropertyValues'):
                mat_props = ref_model.MaterialPropertyValues
                if mat_props:
                    material["density"] = mat_props[0] if len(mat_props) > 0 else None
                    material["modulus"] = mat_props[1] if len(mat_props) > 1 else None
    except Exception as e:
        logger.debug(f"Could not get material info: {e}")
    return material


def get_feature_summary(ref_model) -> Dict:
    """Analyze the feature tree of a SolidWorks model."""
    features = {
        "total_features": 0,
        "holes": [],
        "fillets": [],
        "chamfers": [],
        "extrusions": [],
        "cuts": [],
        "patterns": [],
        "sketches": 0
    }

    try:
        if not ref_model:
            return features

        feat = ref_model.FirstFeature
        while feat:
            try:
                feat_type = feat.GetTypeName2
                if callable(feat_type):
                    feat_type = feat_type()

                feat_name = feat.Name if hasattr(feat, 'Name') else "Unknown"
                features["total_features"] += 1

                # Categorize feature types
                if feat_type in ["HoleWzd", "Hole", "HoleSeries"]:
                    hole_info = {"name": feat_name, "type": feat_type}
                    # Try to get hole parameters
                    try:
                        feat_def = feat.GetDefinition()
                        if feat_def and hasattr(feat_def, 'HoleDiameter'):
                            hole_info["diameter"] = feat_def.HoleDiameter * 1000  # mm
                    except:
                        pass
                    features["holes"].append(hole_info)

                elif feat_type in ["Fillet", "FullRoundFillet", "ConstRadiusFillet"]:
                    features["fillets"].append({"name": feat_name, "type": feat_type})

                elif feat_type in ["Chamfer"]:
                    features["chamfers"].append({"name": feat_name, "type": feat_type})

                elif feat_type in ["Extrusion", "Boss-Extrude"]:
                    features["extrusions"].append({"name": feat_name})

                elif feat_type in ["Cut-Extrude", "CutExtrude"]:
                    features["cuts"].append({"name": feat_name})

                elif feat_type in ["LPattern", "CirPattern", "DerivedLPattern", "DerivedCirPattern"]:
                    features["patterns"].append({"name": feat_name, "type": feat_type})

                elif feat_type == "ProfileFeature":
                    features["sketches"] += 1

            except Exception as e:
                logger.debug(f"Error processing feature: {e}")

            # Next feature
            try:
                feat = feat.GetNextFeature()
            except:
                break

    except Exception as e:
        logger.debug(f"Could not analyze features: {e}")

    return features


def get_mates_info(comp) -> List[Dict]:
    """Get mate information for a component."""
    mates = []
    try:
        if not comp:
            return mates

        # Get mates from component
        mate_count = comp.GetMateCount()
        if mate_count and mate_count > 0:
            for i in range(mate_count):
                try:
                    mate = comp.GetMate(i)
                    if mate:
                        mate_info = {
                            "type": mate.Type if hasattr(mate, 'Type') else "Unknown",
                            "name": mate.Name if hasattr(mate, 'Name') else f"Mate{i}"
                        }
                        mates.append(mate_info)
                except:
                    continue
    except Exception as e:
        logger.debug(f"Could not get mates: {e}")
    return mates


def save_learned_pattern(pattern: Dict):
    """Save a learned design pattern to the knowledge base."""
    patterns_file = KNOWLEDGE_BASE_PATH / "learned_patterns.json"

    patterns = []
    if patterns_file.exists():
        try:
            with open(patterns_file, 'r') as f:
                patterns = json.load(f)
        except:
            patterns = []

    patterns.append(pattern)

    with open(patterns_file, 'w') as f:
        json.dump(patterns, f, indent=2)


def load_learned_patterns() -> List[Dict]:
    """Load previously learned patterns."""
    patterns_file = KNOWLEDGE_BASE_PATH / "learned_patterns.json"

    if patterns_file.exists():
        try:
            with open(patterns_file, 'r') as f:
                return json.load(f)
        except:
            return []
    return []


def _analyze_assembly_sync():
    """Synchronous assembly analysis - runs in COM thread context."""
    pythoncom.CoInitialize()
    try:
        app = win32com.client.Dispatch("SldWorks.Application")
        model = app.ActiveDoc

        if not model:
            return {"error": "No active document", "status_code": 400}

        doc_type = model.GetType
        if doc_type != 2:  # swDocASSEMBLY = 2
            return {"error": "Active document is not an assembly", "status_code": 400}

        # Get assembly name
        assembly_name = model.GetTitle if hasattr(model, 'GetTitle') else "Unknown"
        if callable(assembly_name):
            assembly_name = assembly_name()

        # Get all components
        config_mgr = model.ConfigurationManager
        active_config = config_mgr.ActiveConfiguration
        root_component = active_config.GetRootComponent3(True)

        parts_data = []
        analyses = []

        if root_component:
            children = root_component.GetChildren
            if callable(children):
                children = children()

            if children:
                # First pass: collect all part info with models
                seen_parts = {}
                for comp in children:
                    try:
                        comp_name = None
                        for attr in ['Name2', 'Name', 'GetName']:
                            try:
                                val = getattr(comp, attr, None)
                                if val is not None:
                                    comp_name = val() if callable(val) else val
                                    if comp_name:
                                        break
                            except:
                                continue

                        if not comp_name:
                            continue

                        # Remove instance suffix
                        part_number = comp_name
                        if "<" in str(part_number):
                            part_number = str(part_number).split("<")[0]

                        if part_number not in seen_parts:
                            # Get file path and ref_model
                            file_path = ""
                            ref_model = None
                            custom_props = {}

                            try:
                                ref_model = comp.GetModelDoc2()
                                if ref_model:
                                    path_name = getattr(ref_model, 'GetPathName', None)
                                    if path_name:
                                        file_path = path_name() if callable(path_name) else path_name

                                    # Get custom properties
                                    try:
                                        ext = ref_model.Extension
                                        if ext:
                                            cpm = ext.CustomPropertyManager("")
                                            if cpm:
                                                prop_names = cpm.GetNames
                                                if callable(prop_names):
                                                    prop_names = prop_names()
                                                if prop_names:
                                                    for name in prop_names:
                                                        try:
                                                            result = cpm.Get3(name, False)
                                                            if result:
                                                                val = result[0] if result[0] else result[1]
                                                                if val:
                                                                    custom_props[name] = str(val)
                                                        except:
                                                            continue
                                    except:
                                        pass
                            except:
                                pass

                            seen_parts[part_number] = {
                                "part_number": part_number,
                                "file_path": file_path,
                                "ref_model": ref_model,
                                "component": comp,
                                "properties": custom_props
                            }
                    except Exception as e:
                        logger.warning(f"Error processing component: {e}")
                        continue

                parts_data = list(seen_parts.values())

                # Second pass: analyze each part with ALL data
                for part in parts_data:
                    part_number = part["part_number"]
                    file_path = part.get("file_path", "")
                    ref_model = part.get("ref_model")
                    comp = part.get("component")

                    # Get geometry data
                    geometry = get_mass_properties(ref_model)
                    bbox = get_bounding_box(ref_model)
                    if bbox:
                        geometry["bounding_box"] = bbox

                    # Get material info
                    material = get_material_info(ref_model)

                    # Get feature summary
                    features = get_feature_summary(ref_model)

                    # Get custom properties
                    custom_props = part.get("properties", {})

                    # Get mate info
                    mates = get_mates_info(comp)

                    # Classify part type using ALL data
                    part_type, confidence = classify_part_type(
                        part_number, file_path, custom_props, geometry
                    )

                    # Generate purpose description
                    purpose = generate_part_purpose(part_number, part_type)

                    # Get recommendations
                    recommendations, issues = get_recommendations_for_part(part_type, part_number)

                    # Add geometry-specific recommendations
                    if features.get("holes") and len(features["holes"]) > 5:
                        recommendations.append("Consider using hole patterns for consistent spacing")
                    if not features.get("fillets") and features.get("cuts"):
                        issues.append("Sharp edges on cut features - consider adding fillets for handling")

                    # Find related parts
                    related = find_related_parts(part_number, parts_data)

                    # Generate suggested name
                    suggested_name = generate_suggested_name(
                        part_number, part_type, geometry, material, custom_props
                    )

                    analyses.append({
                        "part_number": part_number,
                        "suggested_name": suggested_name,
                        "part_type": part_type,
                        "purpose": purpose,
                        "recommendations": recommendations[:5],  # Top 5
                        "potential_issues": issues[:3],  # Top 3
                        "related_parts": related,
                        "confidence": confidence,
                        "geometry": {
                            "mass_kg": round(geometry.get("mass", 0), 3),
                            "volume_m3": round(geometry.get("volume", 0), 6),
                            "surface_area_m2": round(geometry.get("surface_area", 0), 4),
                            "bounding_box": bbox
                        },
                        "material": material,
                        "features": {
                            "total": features.get("total_features", 0),
                            "holes": len(features.get("holes", [])),
                            "fillets": len(features.get("fillets", [])),
                            "chamfers": len(features.get("chamfers", [])),
                            "patterns": len(features.get("patterns", [])),
                            "hole_details": features.get("holes", [])[:5]  # First 5 holes
                        },
                        "mates": mates[:5]  # First 5 mates
                    })

        # Generate assembly-level insights
        assembly_insights = generate_assembly_insights(analyses, assembly_name)

        # Save analysis to knowledge base
        save_analysis_report(assembly_name, analyses, assembly_insights)

        return {
            "status": "ok",
            "assembly_name": assembly_name,
            "total_parts_analyzed": len(analyses),
            "part_analyses": analyses,
            "assembly_insights": assembly_insights,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error analyzing assembly: {e}")
        return {"error": f"Failed to analyze assembly: {e}", "status_code": 500}
    finally:
        pythoncom.CoUninitialize()


def generate_assembly_insights(analyses: List[Dict], assembly_name: str) -> Dict:
    """Generate high-level insights about the assembly design."""

    # Count part types
    type_counts = {}
    for analysis in analyses:
        pt = analysis.get("part_type", "unknown")
        type_counts[pt] = type_counts.get(pt, 0) + 1

    # Identify dominant part types
    sorted_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)

    # Determine assembly category
    assembly_category = "general"
    if type_counts.get("fan_component", 0) > 0 or "fan" in assembly_name.lower():
        assembly_category = "hvac_equipment"
    elif type_counts.get("ductwork", 0) > 0:
        assembly_category = "ductwork_system"
    elif type_counts.get("structural_frame", 0) > 3:
        assembly_category = "structural_frame"
    elif type_counts.get("weldment", 0) > 2:
        assembly_category = "fabricated_assembly"

    # Generate recommendations based on assembly type
    assembly_recommendations = []

    if assembly_category == "hvac_equipment":
        assembly_recommendations = [
            "Verify vibration isolation for fan components",
            "Check airflow path for obstructions",
            "Ensure adequate service access for maintenance",
            "Verify lifting provisions meet weight requirements",
            "Check seal continuity around air path"
        ]
    elif assembly_category == "structural_frame":
        assembly_recommendations = [
            "Verify all load paths are continuous",
            "Check connection capacity at joints",
            "Ensure proper bracing for lateral loads",
            "Verify bolt patterns allow for field adjustment",
            "Add alignment features for sub-assembly fit-up"
        ]
    elif assembly_category == "fabricated_assembly":
        assembly_recommendations = [
            "Optimize weld sequence to minimize distortion",
            "Group similar weld positions together",
            "Verify weld access for all joints",
            "Add machining allowances where required",
            "Consider shipping and handling constraints"
        ]
    else:
        assembly_recommendations = [
            "Review overall assembly for interference",
            "Verify maintenance access to all serviceable components",
            "Check fastener standardization across assembly",
            "Ensure proper documentation for fabrication",
            "Verify assembly sequence is achievable"
        ]

    # Identify potential design improvements
    improvements = []

    # Check for missing seals where panels meet frames
    if type_counts.get("panel", 0) > 0 and type_counts.get("seal", 0) == 0:
        improvements.append({
            "area": "Sealing",
            "suggestion": "Consider adding seals at panel-to-frame interfaces for weather protection",
            "priority": "medium"
        })

    # Check for lifting provisions
    if type_counts.get("lifting", 0) == 0 and len(analyses) > 10:
        improvements.append({
            "area": "Handling",
            "suggestion": "Add lifting lugs or provisions for safe handling of assembly",
            "priority": "high"
        })

    # Check for proper bracing
    if type_counts.get("structural_frame", 0) > 2 and type_counts.get("bracket", 0) < 2:
        improvements.append({
            "area": "Structure",
            "suggestion": "Consider adding gussets or brackets at frame connections for rigidity",
            "priority": "medium"
        })

    return {
        "assembly_category": assembly_category,
        "part_type_distribution": type_counts,
        "dominant_types": sorted_types[:3],
        "recommendations": assembly_recommendations,
        "suggested_improvements": improvements,
        "complexity_score": min(len(analyses) / 10, 10)  # 0-10 scale
    }


def save_analysis_report(assembly_name: str, analyses: List[Dict], insights: Dict):
    """Save the analysis report to the knowledge base."""

    report_dir = KNOWLEDGE_BASE_PATH / "assembly_reports"
    report_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = re.sub(r'[^\w\-]', '_', assembly_name)
    report_file = report_dir / f"{safe_name}_{timestamp}.json"

    report = {
        "assembly_name": assembly_name,
        "analyzed_at": datetime.now().isoformat(),
        "part_count": len(analyses),
        "analyses": analyses,
        "insights": insights
    }

    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)

    logger.info(f"Saved analysis report: {report_file}")

    # Also learn patterns from this assembly
    learn_from_assembly(assembly_name, analyses, insights)


def learn_from_assembly(assembly_name: str, analyses: List[Dict], insights: Dict):
    """Extract and save learnable patterns from the assembly."""

    # Look for naming patterns
    naming_patterns = {}
    for analysis in analyses:
        pn = analysis["part_number"]
        pt = analysis["part_type"]

        # Extract prefix patterns
        parts = re.split(r'[-_]', pn)
        if len(parts) > 1:
            prefix = parts[0]
            if prefix not in naming_patterns:
                naming_patterns[prefix] = {"types": {}, "count": 0}
            naming_patterns[prefix]["count"] += 1
            naming_patterns[prefix]["types"][pt] = naming_patterns[prefix]["types"].get(pt, 0) + 1

    # Save significant patterns
    for prefix, data in naming_patterns.items():
        if data["count"] >= 3:  # Pattern appears at least 3 times
            pattern = {
                "pattern_id": f"naming_{prefix}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "pattern_type": "naming_convention",
                "description": f"Parts with prefix '{prefix}' are typically: {', '.join(data['types'].keys())}",
                "examples": [a["part_number"] for a in analyses if a["part_number"].startswith(prefix)][:5],
                "learned_from": assembly_name,
                "confidence": min(data["count"] / 10, 0.9),
                "created_at": datetime.now().isoformat()
            }
            save_learned_pattern(pattern)


@router.get("/analyze")
async def analyze_assembly():
    """Analyze the current assembly and provide design insights."""
    import asyncio
    import concurrent.futures

    logger.info("Starting assembly analysis")

    loop = asyncio.get_event_loop()
    with concurrent.futures.ThreadPoolExecutor() as pool:
        result = await loop.run_in_executor(pool, _analyze_assembly_sync)

    if "error" in result:
        raise HTTPException(status_code=result.get("status_code", 500), detail=result["error"])

    return result


@router.get("/patterns")
async def get_learned_patterns():
    """Get all learned design patterns."""
    patterns = load_learned_patterns()
    return {
        "status": "ok",
        "total_patterns": len(patterns),
        "patterns": patterns
    }


@router.get("/reports")
async def get_analysis_reports():
    """Get list of saved analysis reports."""
    report_dir = KNOWLEDGE_BASE_PATH / "assembly_reports"

    if not report_dir.exists():
        return {"status": "ok", "reports": []}

    reports = []
    for report_file in sorted(report_dir.glob("*.json"), reverse=True)[:20]:
        try:
            with open(report_file, 'r') as f:
                data = json.load(f)
                reports.append({
                    "filename": report_file.name,
                    "assembly_name": data.get("assembly_name"),
                    "analyzed_at": data.get("analyzed_at"),
                    "part_count": data.get("part_count")
                })
        except:
            continue

    return {"status": "ok", "reports": reports}


@router.get("/reports/{filename}")
async def get_analysis_report(filename: str):
    """Get a specific analysis report."""
    report_file = KNOWLEDGE_BASE_PATH / "assembly_reports" / filename

    if not report_file.exists():
        raise HTTPException(status_code=404, detail="Report not found")

    with open(report_file, 'r') as f:
        return json.load(f)
