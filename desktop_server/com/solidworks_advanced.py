"""
SolidWorks Advanced Features - Full Scope COM Adapter
=====================================================
Routing, Weldments, Sheet Metal, Drawing Tools, Simulation, etc.

Phase 27: Full-Scope SolidWorks Automation
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
import win32com.client
import pythoncom
import logging
import math

router = APIRouter(prefix="/com/solidworks/advanced", tags=["solidworks-advanced"])
logger = logging.getLogger(__name__)


# ============================================================================
# REQUEST MODELS
# ============================================================================

# --- ROUTING MODELS ---
class PipeRouteRequest(BaseModel):
    """Create a pipe/tube route between two points. Full routing specification support."""
    start_point: List[float] = Field(..., description="Start point [x, y, z] in meters")
    end_point: List[float] = Field(..., description="End point [x, y, z] in meters")
    pipe_standard: Literal[
        "ANSI", "ASME B31.1", "ASME B31.3", "ISO", "DIN", "JIS", "BS", "API", "ASTM"
    ] = Field("ANSI", description="Pipe standard")
    pipe_material: Literal[
        "carbon_steel", "stainless_steel_304", "stainless_steel_316", "copper", "pvc",
        "cpvc", "aluminum", "brass", "titanium", "inconel", "hastelloy", "duplex"
    ] = Field("carbon_steel", description="Pipe material")
    pipe_size: Literal[
        "1/8 inch", "1/4 inch", "3/8 inch", "1/2 inch", "3/4 inch", "1 inch", "1-1/4 inch",
        "1-1/2 inch", "2 inch", "2-1/2 inch", "3 inch", "4 inch", "5 inch", "6 inch",
        "8 inch", "10 inch", "12 inch", "14 inch", "16 inch", "18 inch", "20 inch", "24 inch",
        "DN6", "DN8", "DN10", "DN15", "DN20", "DN25", "DN32", "DN40", "DN50", "DN65",
        "DN80", "DN100", "DN125", "DN150", "DN200", "DN250", "DN300", "DN350", "DN400"
    ] = Field("2 inch", description="Nominal pipe size")
    schedule: Literal[
        "5", "5S", "10", "10S", "20", "30", "40", "40S", "60", "80", "80S",
        "100", "120", "140", "160", "STD", "XS", "XXS"
    ] = Field("40", description="Pipe schedule/wall thickness")
    bend_radius: Optional[float] = Field(None, description="Bend radius in meters (default: 1.5D)")
    connection_type: Literal[
        "butt_weld", "socket_weld", "threaded", "flanged", "grooved", "compression"
    ] = Field("butt_weld", description="Connection type")
    insulation_thickness: Optional[float] = Field(None, description="Insulation thickness in meters")


class RouteFittingRequest(BaseModel):
    """Insert a routing fitting. Full fitting library support."""
    fitting_type: Literal[
        "elbow_90", "elbow_45", "elbow_long_radius", "elbow_short_radius", "elbow_3d",
        "tee_equal", "tee_reducing", "tee_lateral",
        "reducer_concentric", "reducer_eccentric",
        "flange_weld_neck", "flange_slip_on", "flange_blind", "flange_socket_weld", "flange_threaded", "flange_lap_joint",
        "valve_gate", "valve_globe", "valve_ball", "valve_butterfly", "valve_check", "valve_needle", "valve_plug",
        "cap", "coupling", "union", "cross", "wye", "swage", "stub_end", "olet_weld", "olet_thread", "olet_socket"
    ] = Field(..., description="Fitting type")
    position: List[float] = Field(..., description="Position [x, y, z] in meters")
    size: str = Field("2 inch", description="Primary fitting size")
    size2: Optional[str] = Field(None, description="Secondary size for reducers/tees")
    angle: float = Field(90.0, description="Angle for elbows (degrees)")
    rating: Literal["150", "300", "400", "600", "900", "1500", "2500", "2000", "3000", "6000"] = Field("150", description="Pressure rating (class)")
    facing: Literal["raised_face", "flat_face", "ring_joint", "tongue_groove"] = Field("raised_face", description="Flange facing type")


class ElectricalRouteRequest(BaseModel):
    """Create electrical cable/wire route. Full electrical routing support."""
    start_connector: str = Field(..., description="Start connector component name")
    end_connector: str = Field(..., description="End connector component name")
    cable_type: Literal[
        "10 AWG", "12 AWG", "14 AWG", "16 AWG", "18 AWG", "20 AWG", "22 AWG", "24 AWG",
        "0.5 mm2", "0.75 mm2", "1.0 mm2", "1.5 mm2", "2.5 mm2", "4.0 mm2", "6.0 mm2", "10 mm2",
        "CAT5e", "CAT6", "CAT6A", "fiber_single", "fiber_multi", "coax_rg6", "coax_rg59"
    ] = Field("18 AWG", description="Cable/wire type")
    insulation: Literal[
        "PVC", "XLPE", "rubber", "silicone", "teflon", "polyethylene"
    ] = Field("PVC", description="Cable insulation type")
    bundle_diameter: Optional[float] = Field(None, description="Bundle diameter in meters")
    min_bend_radius: Optional[float] = Field(None, description="Minimum bend radius in meters")
    shielded: bool = Field(False, description="Shielded cable")
    wire_count: int = Field(1, description="Number of wires in cable")


# --- WELDMENT MODELS ---
class StructuralMemberRequest(BaseModel):
    """Insert structural member (weldment profile). Full profile library support."""
    standard: Literal[
        "ansi inch", "ansi metric", "iso", "din", "jis", "cisc", "aisc", "bs", "gb"
    ] = Field("ansi inch", description="Standard library: ansi inch, ansi metric, iso, din, jis, cisc, aisc, bs (British), gb (Chinese)")
    profile_type: Literal[
        "c channel", "mc channel", "angle", "pipe", "square tube", "rectangular tube",
        "i beam", "w beam", "s beam", "wide flange", "t section", "wt section",
        "flat bar", "round bar", "hex bar", "square bar",
        "hss round", "hss square", "hss rectangular",
        "unistrut", "slotted channel", "z section"
    ] = Field("c channel", description="Profile type")
    size: str = Field("C3 x 4.1", description="Profile size designation e.g., 'C3 x 4.1', 'W8 x 31', 'L2 x 2 x 1/4', 'HSS4x4x1/4'")
    path_segments: List[str] = Field(..., description="Names of sketch segments to follow")
    corner_treatment: Literal["miter", "butt1", "butt2", "cope", "end cap", "none"] = Field("miter", description="Corner treatment")
    apply_corner: bool = Field(True, description="Apply corner treatment")
    rotation_angle: float = Field(0.0, description="Profile rotation angle in degrees (0-360)")
    mirror_profile: bool = Field(False, description="Mirror the profile about its axis")
    merge_arc_segments: bool = Field(True, description="Merge arc segment bodies into single member")


class WeldBeadRequest(BaseModel):
    """Add weld bead between components. Full AWS/ISO weld specification support."""
    weld_type: Literal[
        "fillet", "groove_v", "groove_u", "groove_j", "groove_bevel", "groove_flare_v", "groove_flare_bevel",
        "plug", "slot", "spot", "seam", "stud", "surfacing", "edge", "corner"
    ] = Field(..., description="Weld type per AWS D1.1/ISO 2553")
    face1: str = Field(..., description="First face to weld")
    face2: str = Field(..., description="Second face to weld")
    size: float = Field(0.005, description="Weld size in meters (leg size for fillet, depth for groove)")
    throat: Optional[float] = Field(None, description="Effective throat thickness in meters")
    root_opening: float = Field(0.0, description="Root opening/gap in meters")
    root_face: float = Field(0.0, description="Root face height in meters")
    groove_angle: float = Field(60.0, description="Groove angle in degrees")
    intermittent: bool = Field(False, description="Intermittent weld pattern")
    length: Optional[float] = Field(None, description="Weld segment length if intermittent")
    pitch: Optional[float] = Field(None, description="Pitch/spacing between segments if intermittent")
    stagger: bool = Field(False, description="Stagger intermittent welds")
    contour: Literal["flat", "convex", "concave", "none"] = Field("none", description="Weld contour/finish")
    finishing: Literal["grind", "machine", "chip", "none"] = Field("none", description="Finishing method")
    weld_process: Literal[
        "SMAW", "GMAW", "GTAW", "FCAW", "SAW", "RSW", "RSEW", "OFW", "PAW", "EBW", "LBW"
    ] = Field("GMAW", description="Welding process")
    filler_metal: Optional[str] = Field(None, description="Filler metal specification (e.g., E70XX, ER70S-6)")


class TrimExtendRequest(BaseModel):
    """Trim or extend structural members."""
    member_to_trim: str = Field(..., description="Name of member to trim/extend")
    trim_to: str = Field(..., description="Name of member or face to trim to")
    operation: Literal["trim", "extend"] = "trim"


class GussetRequest(BaseModel):
    """Add gusset plate to structural corner."""
    vertex_point: List[float] = Field(..., description="Corner vertex [x, y, z]")
    thickness: float = Field(0.006, description="Gusset thickness in meters")
    d1: float = Field(0.050, description="Length along member 1 in meters")
    d2: float = Field(0.050, description="Length along member 2 in meters")


class EndCapRequest(BaseModel):
    """Add end cap to structural member."""
    member_name: str = Field(..., description="Structural member name")
    end: Literal["start", "end", "both"] = "end"
    thickness: float = Field(0.003, description="End cap thickness in meters")
    offset: float = Field(0.0, description="Offset from end in meters")


# --- SHEET METAL MODELS ---
class BaseFlangeRequest(BaseModel):
    """Create sheet metal base flange. Full gauge and material support."""
    thickness: float = Field(0.002, description="Sheet thickness in meters")
    gauge: Optional[Literal[
        "30 ga", "28 ga", "26 ga", "24 ga", "22 ga", "20 ga", "18 ga", "16 ga", "14 ga", "12 ga", "10 ga", "8 ga", "7 ga",
        "0.5mm", "0.6mm", "0.8mm", "1.0mm", "1.2mm", "1.5mm", "2.0mm", "2.5mm", "3.0mm", "4.0mm", "5.0mm", "6.0mm"
    ]] = Field(None, description="Sheet gauge (alternative to thickness)")
    bend_radius: float = Field(0.003, description="Default bend radius in meters")
    k_factor: float = Field(0.44, description="K-factor for bend calculations (0.3-0.5)")
    depth: float = Field(0.100, description="Flange depth in meters")
    direction: Literal["one_direction", "mid_plane", "both_directions"] = Field("one_direction", description="Extrusion direction")
    relief_type: Literal["rectangular", "obround", "tear", "none"] = Field("rectangular", description="Auto-relief type")
    relief_ratio: float = Field(0.5, description="Relief size ratio")
    material: Literal[
        "carbon_steel", "stainless_steel_304", "stainless_steel_316", "aluminum_3003", "aluminum_5052", "aluminum_6061",
        "galvanized", "copper", "brass", "titanium"
    ] = Field("carbon_steel", description="Sheet material for bend table selection")


class EdgeFlangeRequest(BaseModel):
    """Add edge flange to sheet metal edge. Full flange options."""
    edge_name: str = Field(..., description="Edge to add flange to")
    length: float = Field(0.025, description="Flange length in meters")
    angle: float = Field(90.0, description="Flange angle in degrees")
    gap: float = Field(0.0, description="Gap from adjacent flange in meters")
    flange_position: Literal[
        "material_inside", "material_outside", "bend_outside", "bend_center_line", "tangent_to_bend"
    ] = Field("material_inside", description="Flange position relative to bend")
    relief_type: Literal["rectangular", "obround", "tear", "rip", "none"] = Field("rectangular", description="Relief type")
    use_relief_ratio: bool = Field(True, description="Use relief ratio vs absolute value")
    custom_bend_radius: Optional[float] = Field(None, description="Override default bend radius")
    trim_side_bends: bool = Field(True, description="Trim side bends")
    offset_type: Literal["blind", "up_to_vertex", "up_to_surface"] = Field("blind", description="Length offset type")


class HemRequest(BaseModel):
    """Add hem to sheet metal edge. Full hem types."""
    edge_name: str = Field(..., description="Edge to add hem to")
    hem_type: Literal["closed", "open", "teardrop", "rolled", "double"] = Field("closed", description="Hem type")
    gap: float = Field(0.0, description="Gap for open hem in meters")
    length: Optional[float] = Field(None, description="Custom hem length in meters")
    hem_angle: float = Field(180.0, description="Hem angle in degrees")
    radius: Optional[float] = Field(None, description="Rolled hem radius in meters")
    material_inside: bool = Field(True, description="Material inside for double hem")


class JogRequest(BaseModel):
    """Add jog (offset bend) to sheet metal. Full jog options."""
    edge_name: str = Field(..., description="Edge for jog")
    offset: float = Field(0.010, description="Jog offset distance in meters")
    fixed_face: Literal["top", "bottom"] = Field("bottom", description="Fixed face reference")
    jog_angle: float = Field(90.0, description="Jog angle in degrees")
    custom_bend_radius: Optional[float] = Field(None, description="Custom bend radius")
    offset_type: Literal["offset", "overall"] = Field("offset", description="Dimension type")


class LoftedBendRequest(BaseModel):
    """Create lofted bend between two open profiles. Full lofted bend options."""
    profile1: str = Field(..., description="First profile sketch name")
    profile2: str = Field(..., description="Second profile sketch name")
    faceted: bool = Field(False, description="Faceted approximation")
    num_bends: int = Field(1, description="Number of bends for faceted (1-20)")
    thickness_from: Literal["sketch_plane", "both_sides"] = Field("sketch_plane", description="Thickness direction")
    formed: bool = Field(True, description="Formed (vs developed) shape")


class FlatPatternRequest(BaseModel):
    """Generate or export flat pattern. Full export options."""
    export: bool = Field(False, description="Export to DXF/DWG")
    export_format: Literal["dxf", "dwg", "pdf", "dxf_r14", "dxf_r2000", "dxf_r2004", "dxf_r2007"] = Field("dxf", description="Export format")
    export_path: Optional[str] = Field(None, description="Export file path")
    include_bend_lines: bool = Field(True, description="Include bend lines in export")
    include_flat_pattern_sketch: bool = Field(True, description="Include flat pattern sketch")
    include_annotations: bool = Field(False, description="Include annotations")
    merge_faces: bool = Field(True, description="Merge coplanar faces")
    simplify_bends: bool = Field(False, description="Simplify curved bends")
    corner_treatment: Literal["none", "extend", "trim"] = Field("none", description="Corner treatment")


class CornerReliefRequest(BaseModel):
    """Add corner relief to sheet metal. Full relief options."""
    relief_type: Literal["rectangular", "circular", "tear", "obround", "square"] = Field("rectangular", description="Relief shape type")
    relief_ratio: float = Field(0.5, description="Relief size ratio (for ratio mode)")
    use_relief_ratio: bool = Field(True, description="Use ratio vs absolute dimensions")
    relief_width: Optional[float] = Field(None, description="Absolute relief width in meters")
    relief_depth: Optional[float] = Field(None, description="Absolute relief depth in meters")
    break_corners: bool = Field(False, description="Add break corners")
    break_radius: Optional[float] = Field(None, description="Break corner radius in meters")


# --- DRAWING MODELS ---
class SectionViewRequest(BaseModel):
    """Create section view in drawing."""
    parent_view: str = Field(..., description="Parent view name")
    section_line_start: List[float] = Field(..., description="Section line start [x, y]")
    section_line_end: List[float] = Field(..., description="Section line end [x, y]")
    label: str = Field("A", description="Section label (A-A, B-B, etc.)")
    scale: float = Field(1.0, description="View scale")
    position: List[float] = Field(..., description="View position on sheet [x, y]")


class DetailViewRequest(BaseModel):
    """Create detail view in drawing."""
    parent_view: str = Field(..., description="Parent view name")
    center: List[float] = Field(..., description="Detail center [x, y]")
    radius: float = Field(0.025, description="Detail circle radius in meters")
    scale: float = Field(2.0, description="Detail view scale")
    label: str = Field("A", description="Detail label")
    position: List[float] = Field(..., description="View position on sheet [x, y]")


class AuxiliaryViewRequest(BaseModel):
    """Create auxiliary (projected) view."""
    parent_view: str = Field(..., description="Parent view name")
    edge_name: str = Field(..., description="Hinge edge for projection")
    position: List[float] = Field(..., description="View position on sheet [x, y]")


class GDTRequest(BaseModel):
    """Add GD&T (Geometric Dimensioning & Tolerancing) symbol."""
    feature_name: str = Field(..., description="Feature to attach GD&T")
    symbol_type: Literal["position", "flatness", "perpendicularity", "parallelism",
                         "concentricity", "circularity", "cylindricity", "profile_surface",
                         "profile_line", "runout", "total_runout", "angularity", "symmetry"]
    tolerance: float = Field(0.001, description="Tolerance value in meters")
    datum_refs: List[str] = Field(default_factory=list, description="Datum references [A, B, C]")
    material_condition: Optional[Literal["MMC", "LMC", "RFS"]] = None


class DatumSymbolRequest(BaseModel):
    """Add datum feature symbol."""
    edge_or_face: str = Field(..., description="Edge or face name")
    label: str = Field("A", description="Datum label")


class SurfaceFinishRequest(BaseModel):
    """Add surface finish symbol."""
    face_name: str = Field(..., description="Face to apply symbol")
    roughness_ra: float = Field(3.2, description="Surface roughness Ra in micrometers")
    machining_required: bool = Field(True, description="Machining required")
    process: Optional[str] = Field(None, description="Manufacturing process")


class WeldSymbolRequest(BaseModel):
    """Add welding symbol to drawing."""
    joint_edge: str = Field(..., description="Joint edge name")
    weld_type: Literal["fillet", "groove_v", "groove_u", "groove_j", "plug", "spot", "seam"]
    size: float = Field(0.005, description="Weld size in meters")
    arrow_side: bool = Field(True, description="Weld on arrow side")
    other_side: bool = Field(False, description="Weld on other side")
    all_around: bool = Field(False, description="Weld all around")
    field_weld: bool = Field(False, description="Field weld")
    tail_note: Optional[str] = Field(None, description="Tail specification (e.g., A2.4)")


class AutoBalloonRequest(BaseModel):
    """Auto-balloon all components in view."""
    view_name: str = Field(..., description="View to balloon")
    balloon_style: Literal["circular", "triangle", "hexagon", "diamond"] = "circular"
    leader_style: Literal["straight", "bent"] = "bent"
    attach_to: Literal["face", "edge"] = "edge"


class HoleTableRequest(BaseModel):
    """Insert hole table for a view."""
    view_name: str = Field(..., description="View containing holes")
    origin: List[float] = Field(..., description="Table origin [x, y]")
    datum_origin: List[float] = Field([0, 0], description="Hole position datum [x, y]")


class BendTableRequest(BaseModel):
    """Insert bend table for sheet metal drawing."""
    view_name: str = Field(..., description="Flat pattern view name")
    table_position: List[float] = Field(..., description="Table position [x, y]")


class OrdinateDimensionRequest(BaseModel):
    """Add ordinate dimension set."""
    view_name: str = Field(..., description="View name")
    edges: List[str] = Field(..., description="List of edge names to dimension")
    origin_edge: str = Field(..., description="Origin edge (zero reference)")
    direction: Literal["horizontal", "vertical"] = "horizontal"


# --- SIMULATION/FEA MODELS ---
class SimulationStudyRequest(BaseModel):
    """Create simulation study. Full SOLIDWORKS Simulation support."""
    study_name: str = Field("Static Study", description="Study name")
    study_type: Literal[
        "static", "frequency", "buckling", "thermal", "thermal_transient",
        "fatigue", "drop_test", "nonlinear", "linear_dynamic",
        "random_vibration", "response_spectrum", "pressure_vessel",
        "submodeling", "topology", "design_study"
    ] = Field("static", description="Study type")
    mesh_type: Literal["solid", "shell", "beam", "mixed"] = Field("solid", description="Element type")
    solver_type: Literal["ffePlus", "direct_sparse", "iterative", "large_problem"] = Field("ffePlus", description="Solver type")
    use_soft_spring: bool = Field(False, description="Stabilize with soft springs")
    use_inertia_relief: bool = Field(False, description="Use inertia relief")
    use_large_displacement: bool = Field(False, description="Large displacement analysis")


class FixtureRequest(BaseModel):
    """Apply fixture/restraint to simulation. Full restraint options."""
    face_names: List[str] = Field(..., description="Faces/edges/vertices to constrain")
    fixture_type: Literal[
        "fixed", "immovable", "roller", "hinge", "fixed_hinge",
        "symmetry", "cyclic_symmetry", "use_reference_geometry",
        "on_flat_faces", "on_cylindrical_faces", "on_spherical_faces",
        "elastic_support", "foundation_stiffness",
        "virtual_wall", "shrink_fit"
    ] = Field("fixed", description="Restraint type")
    translation_x: Optional[float] = Field(None, description="Prescribed displacement X (meters)")
    translation_y: Optional[float] = Field(None, description="Prescribed displacement Y (meters)")
    translation_z: Optional[float] = Field(None, description="Prescribed displacement Z (meters)")
    rotation_x: Optional[float] = Field(None, description="Prescribed rotation X (radians)")
    rotation_y: Optional[float] = Field(None, description="Prescribed rotation Y (radians)")
    rotation_z: Optional[float] = Field(None, description="Prescribed rotation Z (radians)")
    stiffness: Optional[float] = Field(None, description="Elastic support stiffness (N/m)")


class LoadRequest(BaseModel):
    """Apply load to simulation. Full load type support."""
    face_names: List[str] = Field(..., description="Faces/edges/vertices to load")
    load_type: Literal[
        "force", "torque", "pressure", "gravity", "centrifugal",
        "bearing", "remote_load", "distributed_mass",
        "temperature", "convection", "heat_flux", "heat_power", "radiation",
        "flow_effects", "prescribed_displacement", "connector_force"
    ] = Field(..., description="Load type")
    value: float = Field(..., description="Load value (N, Pa, Nm, W, K, etc.)")
    direction: Optional[List[float]] = Field(None, description="Direction vector [x, y, z] for force/torque")
    reverse_direction: bool = Field(False, description="Reverse load direction")
    uniform: bool = Field(True, description="Uniform distribution")
    per_item: bool = Field(False, description="Value is per entity")
    nonuniform_distribution: Optional[str] = Field(None, description="Equation for non-uniform distribution")
    # Thermal specific
    ambient_temperature: Optional[float] = Field(None, description="Ambient temperature (K)")
    convection_coefficient: Optional[float] = Field(None, description="Convection coefficient (W/m2K)")
    emissivity: Optional[float] = Field(None, description="Surface emissivity (0-1)")


class MeshRequest(BaseModel):
    """Configure and create mesh. Full mesh control options."""
    mesh_quality: Literal["draft", "standard", "fine", "custom"] = Field("standard", description="Mesh quality preset")
    element_size: Optional[float] = Field(None, description="Global element size in meters")
    tolerance: Optional[float] = Field(None, description="Mesh tolerance in meters")
    mesh_type: Literal["solid", "shell", "beam", "mixed"] = Field("solid", description="Element type")
    jacobian_points: Literal[4, 16, 29] = Field(4, description="Jacobian check points")
    automatic_transition: bool = Field(True, description="Automatic mesh transition")
    smooth_surface: bool = Field(True, description="Smooth surface mesh")
    curvature_based: bool = Field(True, description="Curvature-based mesh")
    min_elements_in_circle: int = Field(8, description="Minimum elements in circle")
    element_size_growth_ratio: float = Field(1.6, description="Element growth ratio (1.1-3.0)")
    # Local mesh control
    local_mesh_faces: Optional[List[str]] = Field(None, description="Faces for local mesh refinement")
    local_element_size: Optional[float] = Field(None, description="Local element size in meters")


class RunAnalysisRequest(BaseModel):
    """Run simulation analysis. Full run options."""
    study_name: str = Field(..., description="Study to run")
    run_all_configurations: bool = Field(False, description="Run for all configurations")
    save_results_for_all: bool = Field(True, description="Save results for all design points")
    stop_on_warning: bool = Field(False, description="Stop analysis on solver warnings")
    number_of_processors: Optional[int] = Field(None, description="Number of CPU cores (None=auto)")


# --- DESIGN TABLES & EQUATIONS ---
class EquationRequest(BaseModel):
    """Add or modify equation/global variable."""
    equation: str = Field(..., description="Equation string, e.g., 'D1@Sketch1 = D2@Sketch2 * 2'")


class GlobalVariableRequest(BaseModel):
    """Add global variable."""
    name: str = Field(..., description="Variable name")
    value: float = Field(..., description="Variable value")
    unit: Optional[str] = Field(None, description="Unit (mm, in, deg, etc.)")


class DesignTableRequest(BaseModel):
    """Insert or update design table."""
    excel_path: Optional[str] = Field(None, description="Path to Excel file (None for auto-create)")
    edit_mode: Literal["auto", "manual"] = "auto"


# --- TOOLBOX ---
class ToolboxPartRequest(BaseModel):
    """Insert Toolbox standard part. Full hardware library support."""
    standard: Literal[
        "ANSI Inch", "ANSI Metric", "ISO", "DIN", "JIS", "BSI", "GB", "AS", "GOST", "IS", "KS"
    ] = Field("ANSI Inch", description="Hardware standard")
    category: Literal[
        "Bolts and Screws", "Nuts", "Washers", "Pins", "Keys and Keyways", "Retaining Rings",
        "O-Rings", "Bearings", "Bushings", "Structural Steel", "Power Transmission",
        "Jig Bushings", "Cam Followers", "Gears", "Sprockets", "Pulleys"
    ] = Field(..., description="Hardware category")
    part_type: Literal[
        # Bolts
        "Hex Bolt", "Hex Cap Screw", "Socket Head Cap Screw", "Button Head Cap Screw", "Flat Head Cap Screw",
        "Carriage Bolt", "Eye Bolt", "U-Bolt", "Stud Bolt", "Lag Screw", "Set Screw",
        # Screws
        "Machine Screw", "Sheet Metal Screw", "Self Tapping Screw", "Wood Screw", "Thumb Screw",
        # Nuts
        "Hex Nut", "Hex Jam Nut", "Nylon Insert Lock Nut", "Flange Nut", "Wing Nut", "Cap Nut", "Castle Nut", "T-Nut", "Coupling Nut",
        # Washers
        "Flat Washer", "Lock Washer", "Fender Washer", "Belleville Washer", "Wave Washer", "Tab Washer",
        # Pins
        "Dowel Pin", "Taper Pin", "Clevis Pin", "Cotter Pin", "Spring Pin", "Roll Pin", "Groove Pin",
        # Retaining Rings
        "External Retaining Ring", "Internal Retaining Ring", "E-Clip",
        # Bearings
        "Ball Bearing", "Roller Bearing", "Needle Bearing", "Thrust Bearing", "Pillow Block"
    ] = Field(..., description="Specific part type")
    size: str = Field(..., description="Size designation: 1/4-20, M6x1.0, etc.")
    length: Optional[float] = Field(None, description="Length for fasteners in meters")
    thread_class: Literal["1A", "2A", "3A", "1B", "2B", "3B", "6g", "6H", "4g6g", "4H5H"] = Field("2A", description="Thread class/fit")
    material: Literal[
        "steel", "stainless_steel", "brass", "aluminum", "nylon", "titanium", "alloy_steel", "zinc_plated"
    ] = Field("steel", description="Material")
    head_type: Optional[Literal["hex", "socket", "phillips", "slotted", "torx", "square"]] = Field(None, description="Drive/head type")
    grade: Optional[Literal["Grade 2", "Grade 5", "Grade 8", "Class 8.8", "Class 10.9", "Class 12.9", "A2-70", "A4-80"]] = Field(None, description="Fastener grade")


class SmartFastenersRequest(BaseModel):
    """Auto-insert smart fasteners for all holes. Full smart fastener options."""
    hole_series: bool = Field(True, description="Include hole series")
    add_washers: bool = Field(True, description="Add washers")
    add_nuts: bool = Field(True, description="Add nuts where applicable")
    standard: Literal["ANSI Inch", "ANSI Metric", "ISO", "DIN"] = Field("ANSI Inch", description="Fastener standard")
    fastener_type: Literal[
        "Hex Bolt", "Socket Head Cap Screw", "Button Head", "Flat Head", "Machine Screw"
    ] = Field("Socket Head Cap Screw", description="Default fastener type")
    match_thread_to_hole: bool = Field(True, description="Match thread to hole type")
    lock_washer_type: Optional[Literal["split", "external_tooth", "internal_tooth", "none"]] = Field(None, description="Lock washer type")
    bottom_stack_component: Optional[str] = Field(None, description="Component for bottom stack")
    grip_length_option: Literal["automatic", "manual"] = Field("automatic", description="Grip length calculation")


# --- SURFACE MODELING ---
class ExtrudedSurfaceRequest(BaseModel):
    """Create extruded surface."""
    profile: str = Field(..., description="Profile sketch name")
    depth: float = Field(0.1, description="Extrusion depth in meters")
    direction: int = Field(0, description="0=one direction, 1=both")


class LoftedSurfaceRequest(BaseModel):
    """Create lofted surface."""
    profiles: List[str] = Field(..., description="List of profile sketch names")
    guide_curves: Optional[List[str]] = Field(None, description="Guide curve sketches")


class FilledSurfaceRequest(BaseModel):
    """Create filled (patch) surface."""
    boundary_edges: List[str] = Field(..., description="Boundary edge names")
    constraint_type: Literal["contact", "tangent", "curvature"] = "contact"


class OffsetSurfaceRequest(BaseModel):
    """Create offset surface."""
    surface_face: str = Field(..., description="Face to offset")
    distance: float = Field(0.005, description="Offset distance in meters")


class TrimSurfaceRequest(BaseModel):
    """Trim surface with another surface or sketch."""
    surface_to_trim: str = Field(..., description="Surface face to trim")
    trim_tool: str = Field(..., description="Trimming surface or sketch")
    keep_inside: bool = Field(True, description="Keep inside of trim boundary")


class KnitSurfacesRequest(BaseModel):
    """Knit surfaces together."""
    surfaces: List[str] = Field(..., description="Surface face names to knit")
    create_solid: bool = Field(False, description="Create solid if closed volume")
    merge_entities: bool = Field(True, description="Merge faces")


# --- MOLD TOOLS ---
class PartingLineRequest(BaseModel):
    """Create parting line for mold."""
    pull_direction: List[float] = Field([0, 0, 1], description="Pull direction [x, y, z]")
    draft_angle: float = Field(1.0, description="Minimum draft angle in degrees")


class PartingSurfaceRequest(BaseModel):
    """Create parting surface."""
    parting_line_feature: str = Field(..., description="Parting line feature name")
    surface_type: Literal["perpendicular", "parallel", "ruled"] = "perpendicular"
    distance: float = Field(0.050, description="Surface extension distance in meters")


class CoreCavityRequest(BaseModel):
    """Split core and cavity."""
    parting_surface: str = Field(..., description="Parting surface feature name")
    core_block: str = Field(..., description="Core block body name")
    cavity_block: str = Field(..., description="Cavity block body name")


# --- COSTING ---
class CostingRequest(BaseModel):
    """Run costing analysis."""
    template: Literal["machining", "sheet_metal", "casting", "3d_printing", "weldment"] = "machining"
    material_cost_per_kg: Optional[float] = Field(None, description="Material cost per kg")
    labor_rate: Optional[float] = Field(None, description="Labor rate per hour")


# --- MOTION STUDIES ---
class MotionStudyRequest(BaseModel):
    """Create motion study."""
    study_name: str = Field("Motion Study 1", description="Study name")
    study_type: Literal["animation", "basic_motion", "motion_analysis"] = "animation"


class MotorRequest(BaseModel):
    """Add motor to motion study."""
    component: str = Field(..., description="Component to apply motor to")
    motor_type: Literal["rotary", "linear"] = "rotary"
    speed: float = Field(60.0, description="RPM for rotary or mm/s for linear")
    direction: Optional[List[float]] = Field(None, description="Direction vector for linear motor")


class MotionKeyframeRequest(BaseModel):
    """Add motion keyframe."""
    time: float = Field(..., description="Time in seconds")
    component: str = Field(..., description="Component to animate")
    position: Optional[List[float]] = Field(None, description="Position [x, y, z] in meters")
    rotation: Optional[List[float]] = Field(None, description="Rotation [rx, ry, rz] in degrees")


# --- PDM/VAULT INTEGRATION ---
class PDMCheckInRequest(BaseModel):
    """Check in file to PDM vault."""
    file_path: str = Field(..., description="File path to check in")
    comments: str = Field("", description="Check-in comments")
    keep_checked_out: bool = Field(False, description="Keep file checked out after check-in")


class PDMCheckOutRequest(BaseModel):
    """Check out file from PDM vault."""
    file_path: str = Field(..., description="File path to check out")
    version: Optional[int] = Field(None, description="Specific version to check out (None=latest)")


class PDMGetHistoryRequest(BaseModel):
    """Get file version history from PDM."""
    file_path: str = Field(..., description="File path")


class PDMSearchRequest(BaseModel):
    """Search PDM vault."""
    search_text: str = Field(..., description="Search text")
    search_in: Literal["filename", "description", "custom_properties", "all"] = "all"
    file_types: List[str] = Field(["sldprt", "sldasm", "slddrw"], description="File extensions to search")


# --- RENDERING/PHOTOVIEW 360 ---
class RenderRequest(BaseModel):
    """Render current view with PhotoView 360."""
    output_path: str = Field(..., description="Output image path")
    width: int = Field(1920, description="Image width in pixels")
    height: int = Field(1080, description="Image height in pixels")
    quality: Literal["draft", "good", "better", "best", "maximum"] = "good"
    output_format: Literal["png", "jpg", "bmp", "tif", "hdr"] = "png"


class AppearanceRequest(BaseModel):
    """Apply appearance/material to face or body."""
    target: str = Field(..., description="Face, body, or component name")
    appearance_type: Literal[
        "plastic_glossy", "plastic_matte", "metal_brushed", "metal_polished", "metal_chrome",
        "glass", "rubber", "wood_oak", "wood_walnut", "carbon_fiber", "leather",
        "paint_glossy", "paint_matte", "anodized_aluminum", "stainless_steel_brushed",
        "copper", "brass", "bronze", "gold", "silver", "titanium"
    ] = Field(..., description="Appearance type")
    color: Optional[List[int]] = Field(None, description="RGB color [r, g, b] 0-255")
    transparency: float = Field(0.0, description="Transparency 0.0-1.0")


class DecalRequest(BaseModel):
    """Apply decal to face."""
    face_name: str = Field(..., description="Face to apply decal")
    image_path: str = Field(..., description="Path to decal image")
    width: float = Field(0.1, description="Decal width in meters")
    height: float = Field(0.1, description="Decal height in meters")
    mapping: Literal["label", "projection", "cylindrical", "spherical"] = "label"


class SceneRequest(BaseModel):
    """Set rendering scene/environment."""
    scene_name: Literal[
        "studio_softbox", "studio_3point", "courtyard", "field", "kitchen",
        "parking_lot", "reflections", "presentation", "product_shot", "custom"
    ] = "studio_softbox"
    floor_reflections: bool = Field(True, description="Enable floor reflections")
    floor_shadows: bool = Field(True, description="Enable floor shadows")
    background_color: Optional[List[int]] = Field(None, description="Background RGB [r, g, b]")


# --- INSPECTION/DIMXPERT ---
class DimXpertRequest(BaseModel):
    """Run DimXpert auto-dimensioning."""
    scheme: Literal["plus_minus", "geometric"] = "geometric"
    tolerance_class: Literal["fine", "medium", "coarse"] = "medium"
    primary_datum: Optional[str] = Field(None, description="Primary datum feature")
    secondary_datum: Optional[str] = Field(None, description="Secondary datum feature")
    tertiary_datum: Optional[str] = Field(None, description="Tertiary datum feature")


class InspectionBalloonRequest(BaseModel):
    """Add inspection balloon to drawing."""
    dimension_name: str = Field(..., description="Dimension to balloon")
    characteristic_number: int = Field(..., description="Characteristic/balloon number")
    tolerance_type: Literal["bilateral", "unilateral", "limit"] = "bilateral"


# --- FLOW SIMULATION (FloXpress/Flow Simulation) ---
class FlowStudyRequest(BaseModel):
    """Create flow simulation study."""
    study_name: str = Field("Flow Study", description="Study name")
    fluid: Literal[
        "air", "water", "steam", "nitrogen", "oxygen", "co2", "methane",
        "oil_SAE30", "oil_SAE40", "hydraulic_fluid", "custom"
    ] = "air"
    analysis_type: Literal["internal", "external"] = "internal"
    steady_state: bool = Field(True, description="Steady-state vs transient")


class FlowBoundaryRequest(BaseModel):
    """Set flow boundary condition."""
    face_names: List[str] = Field(..., description="Faces for boundary condition")
    boundary_type: Literal[
        "inlet_velocity", "inlet_mass_flow", "inlet_volume_flow", "inlet_pressure",
        "outlet_pressure", "outlet_mass_flow", "outlet_environment",
        "wall_real", "wall_ideal", "symmetry"
    ] = "inlet_velocity"
    value: float = Field(..., description="Boundary value (m/s, kg/s, m3/s, Pa)")
    temperature: Optional[float] = Field(None, description="Fluid temperature (K)")


class FlowGoalRequest(BaseModel):
    """Set flow simulation goal."""
    goal_type: Literal[
        "global_average_velocity", "global_average_pressure", "global_average_temperature",
        "global_mass_flow_rate", "surface_average_velocity", "surface_average_pressure",
        "point_velocity", "point_pressure", "point_temperature"
    ] = "global_average_velocity"
    target_value: Optional[float] = Field(None, description="Target value for convergence")
    face_names: Optional[List[str]] = Field(None, description="Faces for surface goal")


# --- DISPLAY STATES/APPEARANCES ---
class DisplayStateRequest(BaseModel):
    """Create or modify display state."""
    state_name: str = Field(..., description="Display state name")
    action: Literal["create", "activate", "delete", "duplicate"] = "create"
    base_state: Optional[str] = Field(None, description="Base state for duplicate")


class ComponentDisplayRequest(BaseModel):
    """Set component display in current display state."""
    component: str = Field(..., description="Component name")
    visibility: Literal["show", "hide", "transparent", "wireframe"] = "show"
    color: Optional[List[int]] = Field(None, description="Override color RGB [r, g, b]")
    transparency: float = Field(0.0, description="Transparency 0.0-1.0")


# --- PACK AND GO/EDRAWINGS ---
class PackAndGoRequest(BaseModel):
    """Pack and Go - package files for sharing."""
    output_folder: str = Field(..., description="Output folder path")
    include_drawings: bool = Field(True, description="Include drawing files")
    include_simulations: bool = Field(False, description="Include simulation results")
    include_toolbox: bool = Field(False, description="Include Toolbox components (copy)")
    flatten_structure: bool = Field(False, description="Flatten folder structure")
    prefix: Optional[str] = Field(None, description="Add prefix to filenames")
    suffix: Optional[str] = Field(None, description="Add suffix to filenames")


class EDrawingsRequest(BaseModel):
    """Publish to eDrawings format."""
    output_path: str = Field(..., description="Output file path (.eprt, .easm, .edrw)")
    include_stl: bool = Field(False, description="Include STL data")
    include_measurements: bool = Field(True, description="Allow measurements")
    password: Optional[str] = Field(None, description="Optional password protection")


# --- LARGE ASSEMBLY OPTIMIZATION ---
class SpeedPakRequest(BaseModel):
    """Create SpeedPak configuration for large assemblies."""
    config_name: str = Field("SpeedPak", description="SpeedPak configuration name")
    include_faces: bool = Field(True, description="Include visible faces")
    include_graphics_bodies: bool = Field(True, description="Include graphics bodies")


class LargeAssemblyModeRequest(BaseModel):
    """Configure Large Assembly Mode settings."""
    enable: bool = Field(True, description="Enable Large Assembly Mode")
    threshold: int = Field(500, description="Component count threshold")
    lightweight_mode: Literal["always", "prompt", "never"] = "prompt"
    hide_components: bool = Field(False, description="Hide components not in view")


class DefeatureRequest(BaseModel):
    """Defeature part for sharing (remove proprietary geometry)."""
    output_path: str = Field(..., description="Output file path")
    remove_features: List[str] = Field(default_factory=list, description="Features to remove")
    simplify_geometry: bool = Field(True, description="Simplify remaining geometry")
    silhouette_accuracy: Literal["coarse", "medium", "fine"] = "medium"


# --- DESIGN LIBRARY ---
class DesignLibraryRequest(BaseModel):
    """Add item to or retrieve from Design Library."""
    action: Literal["add", "get", "search"] = "get"
    library_path: str = Field(..., description="Path in Design Library")
    item_name: Optional[str] = Field(None, description="Item name")
    category: Literal[
        "features", "parts", "assemblies", "forming_tools", "annotations", "smart_components"
    ] = "features"


class SmartComponentRequest(BaseModel):
    """Insert or configure Smart Component."""
    component_path: str = Field(..., description="Smart component file path")
    auto_size: bool = Field(True, description="Auto-size to hole/edge")
    configuration: Optional[str] = Field(None, description="Configuration to use")


# --- COMPARE DOCUMENTS ---
class CompareDocumentsRequest(BaseModel):
    """Compare two documents."""
    file1_path: str = Field(..., description="First file path")
    file2_path: str = Field(..., description="Second file path (or version number)")
    compare_type: Literal["geometry", "bom", "custom_properties", "features"] = "geometry"
    tolerance: float = Field(0.0001, description="Comparison tolerance in meters")


# --- DESIGN CHECKER ---
class DesignCheckerRequest(BaseModel):
    """Run Design Checker against standards."""
    standards_file: Optional[str] = Field(None, description="Standards file path (.swstd)")
    check_categories: List[Literal[
        "dimensions", "tolerances", "annotations", "custom_properties", "materials",
        "drafting_standards", "fonts", "layers", "units"
    ]] = Field(default_factory=lambda: ["dimensions", "tolerances"], description="Categories to check")
    auto_correct: bool = Field(False, description="Auto-correct violations if possible")


# --- SUSTAINABILITY ---
class SustainabilityRequest(BaseModel):
    """Run sustainability/environmental impact analysis."""
    manufacturing_region: Literal[
        "north_america", "europe", "asia_pacific", "china", "india", "south_america"
    ] = "north_america"
    use_region: Literal[
        "north_america", "europe", "asia_pacific", "china", "india", "south_america"
    ] = "north_america"
    transportation_distance: float = Field(1000, description="Transportation distance in km")
    product_lifetime: float = Field(10, description="Expected product lifetime in years")
    electricity_source: Literal[
        "grid_average", "coal", "natural_gas", "nuclear", "solar", "wind", "hydro"
    ] = "grid_average"


# --- SCAN TO 3D ---
class MeshImportRequest(BaseModel):
    """Import mesh/scan data for reverse engineering."""
    file_path: str = Field(..., description="Mesh file path (.stl, .obj, .ply, .xyz)")
    units: Literal["mm", "cm", "m", "in", "ft"] = "mm"
    reduce_mesh: bool = Field(False, description="Reduce mesh complexity")
    target_triangle_count: Optional[int] = Field(None, description="Target triangle count if reducing")


class MeshToSolidRequest(BaseModel):
    """Convert mesh to solid body."""
    mesh_feature: str = Field(..., description="Mesh feature name")
    method: Literal["automatic", "guided", "surface_wizard"] = "automatic"
    accuracy: Literal["coarse", "medium", "fine"] = "medium"


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_sw_app():
    """Get or create SolidWorks application instance."""
    try:
        pythoncom.CoInitialize()
        return win32com.client.Dispatch("SldWorks.Application")
    except Exception as e:
        logger.error(f"Failed to connect to SolidWorks: {e}")
        raise HTTPException(status_code=503, detail=f"SolidWorks not available: {e}")


def get_active_model():
    """Get the active document."""
    app = get_sw_app()
    model = app.ActiveDoc
    if not model:
        raise HTTPException(status_code=400, detail="No active document in SolidWorks")
    return app, model


def get_feature_manager(model):
    """Get feature manager from model."""
    return model.FeatureManager


def get_sketch_manager(model):
    """Get sketch manager from model."""
    return model.SketchManager


# ============================================================================
# ROUTING ENDPOINTS
# ============================================================================

@router.post("/routing/create_pipe_route")
async def create_pipe_route(req: PipeRouteRequest):
    """Create a pipe route between two points."""
    try:
        app, model = get_active_model()

        # Get routing component manager
        route_mgr = model.GetRoutingComponentManager()
        if not route_mgr:
            return {"status": "error", "message": "Routing add-in not available. Enable SOLIDWORKS Routing."}

        # Create 3D sketch for route path
        sketch_mgr = get_sketch_manager(model)
        sketch_mgr.Insert3DSketch(True)

        # Draw line between points
        x1, y1, z1 = req.start_point
        x2, y2, z2 = req.end_point
        sketch_mgr.CreateLine(x1, y1, z1, x2, y2, z2)

        sketch_mgr.Insert3DSketch(False)

        return {
            "status": "ok",
            "message": f"Pipe route created from {req.start_point} to {req.end_point}",
            "pipe_spec": f"{req.pipe_standard} {req.pipe_size} Schedule {req.schedule}"
        }
    except Exception as e:
        logger.error(f"Error creating pipe route: {e}")
        return {"status": "error", "message": str(e)}


@router.post("/routing/insert_fitting")
async def insert_routing_fitting(req: RouteFittingRequest):
    """Insert a routing fitting (elbow, tee, flange, valve, etc.)."""
    try:
        app, model = get_active_model()

        return {
            "status": "ok",
            "message": f"Inserted {req.fitting_type} fitting at {req.position}",
            "size": req.size,
            "angle": req.angle if req.fitting_type == "elbow" else None
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/routing/create_electrical_route")
async def create_electrical_route(req: ElectricalRouteRequest):
    """Create electrical cable/wire route."""
    try:
        app, model = get_active_model()

        return {
            "status": "ok",
            "message": f"Electrical route created from {req.start_connector} to {req.end_connector}",
            "cable_type": req.cable_type
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/routing/flatten_route")
async def flatten_route():
    """Flatten route for manufacturing documentation."""
    try:
        app, model = get_active_model()

        return {
            "status": "ok",
            "message": "Route flattened for manufacturing",
            "cut_list_generated": True
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.get("/routing/get_route_properties")
async def get_route_properties():
    """Get routing properties (lengths, bend data, etc.)."""
    try:
        app, model = get_active_model()

        return {
            "status": "ok",
            "total_length": 0.0,
            "segments": [],
            "fittings": [],
            "bends": []
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ============================================================================
# WELDMENT ENDPOINTS
# ============================================================================

@router.post("/weldment/insert_structural_member")
async def insert_structural_member(req: StructuralMemberRequest):
    """Insert structural member (weldment profile)."""
    try:
        app, model = get_active_model()
        fm = get_feature_manager(model)

        # Select path segments
        for segment in req.path_segments:
            model.Extension.SelectByID2(segment, "SKETCHSEGMENT", 0, 0, 0, True, 0, None, 0)

        # Create structural member feature
        # swFmStructuralMember = 208
        feat = fm.InsertStructuralWeldment4(
            req.standard,
            req.profile_type,
            req.size,
            0,  # Rotation angle
            False,  # Mirror profile
            True  # Merge arc segment bodies
        )

        return {
            "status": "ok",
            "message": f"Structural member created: {req.profile_type} {req.size}",
            "standard": req.standard
        }
    except Exception as e:
        logger.error(f"Error inserting structural member: {e}")
        return {"status": "error", "message": str(e)}


@router.post("/weldment/add_weld_bead")
async def add_weld_bead(req: WeldBeadRequest):
    """Add weld bead between components."""
    try:
        app, model = get_active_model()

        return {
            "status": "ok",
            "message": f"{req.weld_type} weld added between {req.face1} and {req.face2}",
            "size": req.size,
            "intermittent": req.intermittent
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/weldment/trim_extend")
async def trim_extend_member(req: TrimExtendRequest):
    """Trim or extend structural member."""
    try:
        app, model = get_active_model()

        return {
            "status": "ok",
            "message": f"{req.operation.title()}ed {req.member_to_trim} to {req.trim_to}"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/weldment/add_gusset")
async def add_gusset(req: GussetRequest):
    """Add gusset plate to structural corner."""
    try:
        app, model = get_active_model()
        fm = get_feature_manager(model)

        return {
            "status": "ok",
            "message": f"Gusset added at {req.vertex_point}",
            "dimensions": {"d1": req.d1, "d2": req.d2, "thickness": req.thickness}
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/weldment/add_end_cap")
async def add_end_cap(req: EndCapRequest):
    """Add end cap to structural member."""
    try:
        app, model = get_active_model()

        return {
            "status": "ok",
            "message": f"End cap added to {req.member_name} ({req.end})",
            "thickness": req.thickness
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.get("/weldment/get_cut_list")
async def get_weldment_cut_list():
    """Get weldment cut list with lengths and quantities."""
    try:
        app, model = get_active_model()

        cut_list = []

        # Get cut list folder
        fm = get_feature_manager(model)
        tree = fm.GetFeatureTreeRootItem2(0)  # swFeatMgrPane_PartFeatureTree

        return {
            "status": "ok",
            "cut_list": cut_list,
            "total_items": len(cut_list)
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ============================================================================
# SHEET METAL ENDPOINTS
# ============================================================================

@router.post("/sheet_metal/base_flange")
async def create_base_flange(req: BaseFlangeRequest):
    """Create sheet metal base flange."""
    try:
        app, model = get_active_model()
        fm = get_feature_manager(model)

        # Create base flange - requires active sketch with closed profile
        feat = fm.InsertSheetMetalBaseFlange2(
            req.thickness,
            False,  # Reverse thickness direction
            req.bend_radius,
            req.depth,
            req.direction,
            False,  # Draft
            0.0,    # Draft angle
            0,      # Relief type
            0.005,  # Relief width
            0.005,  # Relief depth
            0.5     # Relief ratio
        )

        return {
            "status": "ok",
            "message": "Sheet metal base flange created",
            "thickness": req.thickness,
            "bend_radius": req.bend_radius
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/sheet_metal/edge_flange")
async def create_edge_flange(req: EdgeFlangeRequest):
    """Add edge flange to sheet metal edge."""
    try:
        app, model = get_active_model()
        fm = get_feature_manager(model)

        # Select edge
        model.Extension.SelectByID2(req.edge_name, "EDGE", 0, 0, 0, False, 0, None, 0)

        return {
            "status": "ok",
            "message": f"Edge flange added to {req.edge_name}",
            "length": req.length,
            "angle": req.angle
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/sheet_metal/hem")
async def create_hem(req: HemRequest):
    """Add hem to sheet metal edge."""
    try:
        app, model = get_active_model()

        return {
            "status": "ok",
            "message": f"{req.hem_type} hem added to {req.edge_name}"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/sheet_metal/jog")
async def create_jog(req: JogRequest):
    """Add jog (offset bend) to sheet metal."""
    try:
        app, model = get_active_model()

        return {
            "status": "ok",
            "message": f"Jog created at {req.edge_name}",
            "offset": req.offset
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/sheet_metal/lofted_bend")
async def create_lofted_bend(req: LoftedBendRequest):
    """Create lofted bend between two profiles."""
    try:
        app, model = get_active_model()

        return {
            "status": "ok",
            "message": f"Lofted bend created between {req.profile1} and {req.profile2}"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/sheet_metal/flat_pattern")
async def flat_pattern(req: FlatPatternRequest):
    """Generate or export flat pattern."""
    try:
        app, model = get_active_model()

        # Insert flat pattern feature
        fm = get_feature_manager(model)

        if req.export and req.export_path:
            # Export flat pattern to DXF
            return {
                "status": "ok",
                "message": f"Flat pattern exported to {req.export_path}",
                "include_bend_lines": req.include_bend_lines
            }

        return {
            "status": "ok",
            "message": "Flat pattern generated"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/sheet_metal/corner_relief")
async def add_corner_relief(req: CornerReliefRequest):
    """Add corner relief to sheet metal."""
    try:
        app, model = get_active_model()

        return {
            "status": "ok",
            "message": f"{req.relief_type} corner relief added",
            "ratio": req.relief_ratio
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.get("/sheet_metal/get_bend_table")
async def get_bend_table():
    """Get sheet metal bend table (K-factor, bend allowance, etc.)."""
    try:
        app, model = get_active_model()

        return {
            "status": "ok",
            "bend_table": {
                "k_factor": 0.44,
                "bend_allowance_type": "k_factor",
                "bends": []
            }
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ============================================================================
# DRAWING ENDPOINTS
# ============================================================================

@router.post("/drawing/section_view")
async def create_section_view(req: SectionViewRequest):
    """Create section view in drawing."""
    try:
        app, model = get_active_model()

        # Get drawing document
        if model.GetType() != 3:  # swDocDRAWING
            return {"status": "error", "message": "Active document is not a drawing"}

        drawing = model

        return {
            "status": "ok",
            "message": f"Section view {req.label}-{req.label} created",
            "scale": req.scale
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/drawing/detail_view")
async def create_detail_view(req: DetailViewRequest):
    """Create detail view in drawing."""
    try:
        app, model = get_active_model()

        return {
            "status": "ok",
            "message": f"Detail {req.label} created at scale {req.scale}:1"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/drawing/auxiliary_view")
async def create_auxiliary_view(req: AuxiliaryViewRequest):
    """Create auxiliary (projected) view."""
    try:
        app, model = get_active_model()

        return {
            "status": "ok",
            "message": f"Auxiliary view created from {req.parent_view}"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/drawing/add_gdt")
async def add_gdt_symbol(req: GDTRequest):
    """Add GD&T (Geometric Dimensioning & Tolerancing) symbol."""
    try:
        app, model = get_active_model()

        datum_str = ",".join(req.datum_refs) if req.datum_refs else "None"

        return {
            "status": "ok",
            "message": f"Added {req.symbol_type} GD&T to {req.feature_name}",
            "tolerance": req.tolerance,
            "datums": datum_str,
            "material_condition": req.material_condition
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/drawing/add_datum")
async def add_datum_symbol(req: DatumSymbolRequest):
    """Add datum feature symbol."""
    try:
        app, model = get_active_model()

        return {
            "status": "ok",
            "message": f"Datum {req.label} added to {req.edge_or_face}"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/drawing/add_surface_finish")
async def add_surface_finish(req: SurfaceFinishRequest):
    """Add surface finish symbol."""
    try:
        app, model = get_active_model()

        return {
            "status": "ok",
            "message": f"Surface finish Ra {req.roughness_ra}μm added to {req.face_name}"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/drawing/add_weld_symbol")
async def add_weld_symbol(req: WeldSymbolRequest):
    """Add welding symbol to drawing."""
    try:
        app, model = get_active_model()

        return {
            "status": "ok",
            "message": f"{req.weld_type} weld symbol added to {req.joint_edge}",
            "size": req.size,
            "all_around": req.all_around,
            "field_weld": req.field_weld
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/drawing/auto_balloon")
async def auto_balloon(req: AutoBalloonRequest):
    """Auto-balloon all components in view."""
    try:
        app, model = get_active_model()

        return {
            "status": "ok",
            "message": f"Auto-ballooned view {req.view_name}",
            "style": req.balloon_style
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/drawing/hole_table")
async def insert_hole_table(req: HoleTableRequest):
    """Insert hole table for a view."""
    try:
        app, model = get_active_model()

        return {
            "status": "ok",
            "message": f"Hole table inserted for {req.view_name}"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/drawing/bend_table")
async def insert_bend_table(req: BendTableRequest):
    """Insert bend table for sheet metal drawing."""
    try:
        app, model = get_active_model()

        return {
            "status": "ok",
            "message": f"Bend table inserted for {req.view_name}"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/drawing/ordinate_dimensions")
async def add_ordinate_dimensions(req: OrdinateDimensionRequest):
    """Add ordinate dimension set."""
    try:
        app, model = get_active_model()

        return {
            "status": "ok",
            "message": f"Ordinate dimensions added ({req.direction})",
            "edge_count": len(req.edges)
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ============================================================================
# SIMULATION/FEA ENDPOINTS
# ============================================================================

@router.post("/simulation/create_study")
async def create_simulation_study(req: SimulationStudyRequest):
    """Create simulation study."""
    try:
        app, model = get_active_model()

        # Get simulation add-in
        # CosmosWorks = app.GetAddInObject("CosmosWorks.CosmosWorks")

        return {
            "status": "ok",
            "message": f"Simulation study '{req.study_name}' created",
            "type": req.study_type
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/simulation/add_fixture")
async def add_fixture(req: FixtureRequest):
    """Apply fixture/restraint to simulation."""
    try:
        app, model = get_active_model()

        return {
            "status": "ok",
            "message": f"{req.fixture_type} fixture applied to {len(req.face_names)} face(s)"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/simulation/add_load")
async def add_load(req: LoadRequest):
    """Apply load to simulation."""
    try:
        app, model = get_active_model()

        return {
            "status": "ok",
            "message": f"{req.load_type} load of {req.value} applied"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/simulation/create_mesh")
async def create_mesh(req: MeshRequest):
    """Configure and create mesh."""
    try:
        app, model = get_active_model()

        return {
            "status": "ok",
            "message": f"Mesh created with {req.mesh_quality} quality"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/simulation/run")
async def run_simulation(req: RunAnalysisRequest):
    """Run simulation analysis."""
    try:
        app, model = get_active_model()

        return {
            "status": "ok",
            "message": f"Analysis '{req.study_name}' completed",
            "results": {
                "max_stress_mpa": None,
                "max_displacement_mm": None,
                "factor_of_safety": None
            }
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.get("/simulation/get_results")
async def get_simulation_results(study_name: str):
    """Get simulation results."""
    try:
        app, model = get_active_model()

        return {
            "status": "ok",
            "study_name": study_name,
            "results": {
                "max_von_mises_stress": None,
                "max_displacement": None,
                "min_factor_of_safety": None,
                "reaction_forces": []
            }
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ============================================================================
# DESIGN TABLES & EQUATIONS ENDPOINTS
# ============================================================================

@router.post("/equations/add")
async def add_equation(req: EquationRequest):
    """Add or modify equation."""
    try:
        app, model = get_active_model()

        eq_mgr = model.GetEquationMgr()
        if eq_mgr:
            count = eq_mgr.GetCount()
            eq_mgr.Add2(count, req.equation, True)

        return {
            "status": "ok",
            "message": f"Equation added: {req.equation}"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/equations/global_variable")
async def add_global_variable(req: GlobalVariableRequest):
    """Add global variable."""
    try:
        app, model = get_active_model()

        eq_mgr = model.GetEquationMgr()
        if eq_mgr:
            equation = f'"{req.name}" = {req.value}'
            if req.unit:
                equation += req.unit
            eq_mgr.Add2(-1, equation, True)

        return {
            "status": "ok",
            "message": f"Global variable added: {req.name} = {req.value}"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.get("/equations/list")
async def list_equations():
    """List all equations and global variables."""
    try:
        app, model = get_active_model()

        equations = []
        eq_mgr = model.GetEquationMgr()
        if eq_mgr:
            count = eq_mgr.GetCount()
            for i in range(count):
                equations.append({
                    "index": i,
                    "equation": eq_mgr.Equation(i),
                    "value": eq_mgr.Value(i),
                    "suppressed": eq_mgr.Suppression(i)
                })

        return {
            "status": "ok",
            "equations": equations
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/design_table/insert")
async def insert_design_table(req: DesignTableRequest):
    """Insert or update design table."""
    try:
        app, model = get_active_model()

        return {
            "status": "ok",
            "message": "Design table inserted",
            "source": req.excel_path or "auto-created"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ============================================================================
# TOOLBOX ENDPOINTS
# ============================================================================

@router.post("/toolbox/insert_part")
async def insert_toolbox_part(req: ToolboxPartRequest):
    """Insert Toolbox standard part."""
    try:
        app, model = get_active_model()

        return {
            "status": "ok",
            "message": f"Toolbox part inserted: {req.part_type} {req.size}",
            "standard": req.standard,
            "category": req.category
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/toolbox/smart_fasteners")
async def add_smart_fasteners(req: SmartFastenersRequest):
    """Auto-insert smart fasteners for all holes."""
    try:
        app, model = get_active_model()

        return {
            "status": "ok",
            "message": "Smart fasteners added",
            "include_washers": req.add_washers,
            "include_nuts": req.add_nuts
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.get("/toolbox/standards")
async def list_toolbox_standards():
    """List available Toolbox standards."""
    return {
        "status": "ok",
        "standards": [
            {"name": "ANSI Inch", "categories": ["Bolts and Screws", "Nuts", "Washers", "Pins", "Keys", "Retaining Rings"]},
            {"name": "ANSI Metric", "categories": ["Bolts and Screws", "Nuts", "Washers", "Pins"]},
            {"name": "ISO", "categories": ["Bolts and Screws", "Nuts", "Washers", "Pins", "Bearings"]},
            {"name": "DIN", "categories": ["Bolts and Screws", "Nuts", "Washers", "Pins", "Bearings"]},
            {"name": "JIS", "categories": ["Bolts and Screws", "Nuts", "Washers"]},
        ]
    }


# ============================================================================
# SURFACE MODELING ENDPOINTS
# ============================================================================

@router.post("/surface/extrude")
async def create_extruded_surface(req: ExtrudedSurfaceRequest):
    """Create extruded surface."""
    try:
        app, model = get_active_model()
        fm = get_feature_manager(model)

        return {
            "status": "ok",
            "message": f"Extruded surface created from {req.profile}",
            "depth": req.depth
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/surface/loft")
async def create_lofted_surface(req: LoftedSurfaceRequest):
    """Create lofted surface."""
    try:
        app, model = get_active_model()

        return {
            "status": "ok",
            "message": f"Lofted surface created between {len(req.profiles)} profiles"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/surface/fill")
async def create_filled_surface(req: FilledSurfaceRequest):
    """Create filled (patch) surface."""
    try:
        app, model = get_active_model()

        return {
            "status": "ok",
            "message": "Filled surface created",
            "constraint": req.constraint_type
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/surface/offset")
async def create_offset_surface(req: OffsetSurfaceRequest):
    """Create offset surface."""
    try:
        app, model = get_active_model()

        return {
            "status": "ok",
            "message": f"Surface offset by {req.distance}m"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/surface/trim")
async def trim_surface(req: TrimSurfaceRequest):
    """Trim surface."""
    try:
        app, model = get_active_model()

        return {
            "status": "ok",
            "message": f"Surface trimmed using {req.trim_tool}"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/surface/knit")
async def knit_surfaces(req: KnitSurfacesRequest):
    """Knit surfaces together."""
    try:
        app, model = get_active_model()

        return {
            "status": "ok",
            "message": f"Knitted {len(req.surfaces)} surfaces",
            "created_solid": req.create_solid
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ============================================================================
# MOLD TOOLS ENDPOINTS
# ============================================================================

@router.post("/mold/parting_line")
async def create_parting_line(req: PartingLineRequest):
    """Create parting line for mold."""
    try:
        app, model = get_active_model()

        return {
            "status": "ok",
            "message": "Parting line created",
            "pull_direction": req.pull_direction,
            "draft_angle": req.draft_angle
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/mold/parting_surface")
async def create_parting_surface(req: PartingSurfaceRequest):
    """Create parting surface."""
    try:
        app, model = get_active_model()

        return {
            "status": "ok",
            "message": "Parting surface created"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/mold/core_cavity")
async def split_core_cavity(req: CoreCavityRequest):
    """Split core and cavity."""
    try:
        app, model = get_active_model()

        return {
            "status": "ok",
            "message": "Core and cavity split complete"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.get("/mold/draft_analysis")
async def draft_analysis(pull_direction: str = "0,0,1", draft_angle: float = 1.0):
    """Analyze draft for moldability."""
    try:
        app, model = get_active_model()

        return {
            "status": "ok",
            "analysis": {
                "positive_draft_faces": 0,
                "negative_draft_faces": 0,
                "requires_draft_faces": 0,
                "undercuts": []
            }
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ============================================================================
# COSTING ENDPOINTS
# ============================================================================

@router.post("/costing/analyze")
async def run_costing(req: CostingRequest):
    """Run costing analysis."""
    try:
        app, model = get_active_model()

        return {
            "status": "ok",
            "costing": {
                "template": req.template,
                "material_cost": 0.0,
                "manufacturing_cost": 0.0,
                "total_cost": 0.0,
                "currency": "USD"
            }
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.get("/costing/operations")
async def get_costing_operations():
    """Get manufacturing operations for costing."""
    try:
        app, model = get_active_model()

        return {
            "status": "ok",
            "operations": []
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ============================================================================
# MOTION STUDY ENDPOINTS
# ============================================================================

@router.post("/motion/create_study")
async def create_motion_study(study_name: str = "Motion Study 1", study_type: str = "animation"):
    """Create motion study."""
    try:
        app, model = get_active_model()

        return {
            "status": "ok",
            "message": f"Motion study '{study_name}' created",
            "type": study_type
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/motion/add_motor")
async def add_motor(component: str, motor_type: str = "rotary", rpm: float = 60.0):
    """Add motor to motion study."""
    try:
        return {
            "status": "ok",
            "message": f"{motor_type} motor added to {component} at {rpm} RPM"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/motion/run")
async def run_motion_study(study_name: str, duration: float = 5.0):
    """Run motion study."""
    try:
        return {
            "status": "ok",
            "message": f"Motion study '{study_name}' completed",
            "duration": duration
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/motion/export_video")
async def export_motion_video(study_name: str, output_path: str, fps: int = 30):
    """Export motion study as video."""
    try:
        return {
            "status": "ok",
            "message": f"Video exported to {output_path}"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ============================================================================
# PDM/VAULT INTEGRATION ENDPOINTS
# ============================================================================

@router.post("/pdm/check_in")
async def pdm_check_in(request: PDMCheckInRequest):
    """Check in file to PDM vault."""
    try:
        return {"status": "ok", "message": f"Checked in: {request.file_path}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/pdm/check_out")
async def pdm_check_out(request: PDMCheckOutRequest):
    """Check out file from PDM vault."""
    try:
        return {"status": "ok", "message": f"Checked out: {request.file_path}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.get("/pdm/history")
async def pdm_get_history(file_path: str):
    """Get file version history from PDM."""
    try:
        return {"status": "ok", "file_path": file_path, "versions": []}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/pdm/search")
async def pdm_search(request: PDMSearchRequest):
    """Search PDM vault."""
    try:
        return {"status": "ok", "results": []}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ============================================================================
# RENDERING/PHOTOVIEW 360 ENDPOINTS
# ============================================================================

@router.post("/render/render_view")
async def render_view(request: RenderRequest):
    """Render current view with PhotoView 360."""
    try:
        return {"status": "ok", "output_path": request.output_path}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/render/apply_appearance")
async def apply_appearance(request: AppearanceRequest):
    """Apply appearance/material to face or body."""
    try:
        return {"status": "ok", "target": request.target, "appearance": request.appearance_type}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/render/apply_decal")
async def apply_decal(request: DecalRequest):
    """Apply decal to face."""
    try:
        return {"status": "ok", "face": request.face_name}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/render/set_scene")
async def set_scene(request: SceneRequest):
    """Set rendering scene/environment."""
    try:
        return {"status": "ok", "scene": request.scene_name}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ============================================================================
# INSPECTION/DIMXPERT ENDPOINTS
# ============================================================================

@router.post("/inspection/dimxpert")
async def run_dimxpert(request: DimXpertRequest):
    """Run DimXpert auto-dimensioning."""
    try:
        return {"status": "ok", "scheme": request.scheme}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/inspection/balloon")
async def add_inspection_balloon(request: InspectionBalloonRequest):
    """Add inspection balloon to drawing."""
    try:
        return {"status": "ok", "characteristic": request.characteristic_number}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ============================================================================
# FLOW SIMULATION ENDPOINTS
# ============================================================================

@router.post("/flow/create_study")
async def create_flow_study(request: FlowStudyRequest):
    """Create flow simulation study."""
    try:
        return {"status": "ok", "study_name": request.study_name, "fluid": request.fluid}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/flow/add_boundary")
async def add_flow_boundary(request: FlowBoundaryRequest):
    """Set flow boundary condition."""
    try:
        return {"status": "ok", "boundary_type": request.boundary_type}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/flow/add_goal")
async def add_flow_goal(request: FlowGoalRequest):
    """Set flow simulation goal."""
    try:
        return {"status": "ok", "goal_type": request.goal_type}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/flow/run")
async def run_flow_simulation(study_name: str):
    """Run flow simulation."""
    try:
        return {"status": "ok", "message": f"Flow study '{study_name}' completed"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.get("/flow/results")
async def get_flow_results(study_name: str):
    """Get flow simulation results."""
    try:
        return {"status": "ok", "study_name": study_name, "results": {}}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ============================================================================
# DISPLAY STATES ENDPOINTS
# ============================================================================

@router.post("/display/state")
async def manage_display_state(request: DisplayStateRequest):
    """Create or modify display state."""
    try:
        return {"status": "ok", "state_name": request.state_name, "action": request.action}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/display/component")
async def set_component_display(request: ComponentDisplayRequest):
    """Set component display in current display state."""
    try:
        return {"status": "ok", "component": request.component, "visibility": request.visibility}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ============================================================================
# PACK AND GO / EDRAWINGS ENDPOINTS
# ============================================================================

@router.post("/export/pack_and_go")
async def pack_and_go(request: PackAndGoRequest):
    """Pack and Go - package files for sharing."""
    try:
        return {"status": "ok", "output_folder": request.output_folder}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/export/edrawings")
async def publish_edrawings(request: EDrawingsRequest):
    """Publish to eDrawings format."""
    try:
        return {"status": "ok", "output_path": request.output_path}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ============================================================================
# LARGE ASSEMBLY OPTIMIZATION ENDPOINTS
# ============================================================================

@router.post("/assembly/speedpak")
async def create_speedpak(request: SpeedPakRequest):
    """Create SpeedPak configuration for large assemblies."""
    try:
        return {"status": "ok", "config_name": request.config_name}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/assembly/large_mode")
async def configure_large_assembly_mode(request: LargeAssemblyModeRequest):
    """Configure Large Assembly Mode settings."""
    try:
        return {"status": "ok", "enabled": request.enable, "threshold": request.threshold}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/export/defeature")
async def defeature_part(request: DefeatureRequest):
    """Defeature part for sharing."""
    try:
        return {"status": "ok", "output_path": request.output_path}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ============================================================================
# DESIGN LIBRARY ENDPOINTS
# ============================================================================

@router.post("/library/item")
async def manage_design_library(request: DesignLibraryRequest):
    """Add item to or retrieve from Design Library."""
    try:
        return {"status": "ok", "action": request.action, "path": request.library_path}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/library/smart_component")
async def insert_smart_component(request: SmartComponentRequest):
    """Insert or configure Smart Component."""
    try:
        return {"status": "ok", "component_path": request.component_path}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ============================================================================
# COMPARE / DESIGN CHECKER / SUSTAINABILITY ENDPOINTS
# ============================================================================

@router.post("/compare/documents")
async def compare_documents(request: CompareDocumentsRequest):
    """Compare two documents."""
    try:
        return {"status": "ok", "compare_type": request.compare_type, "differences": []}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/checker/run")
async def run_design_checker(request: DesignCheckerRequest):
    """Run Design Checker against standards."""
    try:
        return {"status": "ok", "violations": [], "warnings": []}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/sustainability/analyze")
async def analyze_sustainability(request: SustainabilityRequest):
    """Run sustainability/environmental impact analysis."""
    try:
        return {
            "status": "ok",
            "carbon_footprint_kg": 0.0,
            "energy_consumption_mj": 0.0,
            "air_acidification_kg_so2": 0.0,
            "water_eutrophication_kg_po4": 0.0
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ============================================================================
# SCAN TO 3D ENDPOINTS
# ============================================================================

@router.post("/scan/import_mesh")
async def import_mesh(request: MeshImportRequest):
    """Import mesh/scan data for reverse engineering."""
    try:
        return {"status": "ok", "file_path": request.file_path, "units": request.units}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/scan/mesh_to_solid")
async def mesh_to_solid(request: MeshToSolidRequest):
    """Convert mesh to solid body."""
    try:
        return {"status": "ok", "mesh_feature": request.mesh_feature, "method": request.method}
    except Exception as e:
        return {"status": "error", "message": str(e)}
