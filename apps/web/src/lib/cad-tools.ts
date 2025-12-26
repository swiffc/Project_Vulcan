/**
 * CAD Tools for Claude Tool Calling
 *
 * These tools enable Claude to directly control SolidWorks via the Desktop Server.
 * Uses Anthropic's tool_use feature.
 */

import Anthropic from "@anthropic-ai/sdk";

// Desktop server URL
const DESKTOP_URL = process.env.DESKTOP_SERVER_URL || "http://localhost:8000";

/**
 * Tool definitions for Claude
 */
export const CAD_TOOLS: Anthropic.Tool[] = [
  // === Connection ===
  {
    name: "sw_connect",
    description: "Connect to a running SolidWorks instance. Call this first before any other SolidWorks operations.",
    input_schema: {
      type: "object" as const,
      properties: {},
      required: [],
    },
  },
  {
    name: "sw_status",
    description: "Check SolidWorks connection status and get info about the current document.",
    input_schema: {
      type: "object" as const,
      properties: {},
      required: [],
    },
  },
  {
    name: "sw_set_custom_property",
    description: "Set a custom property for a SolidWorks document (e.g., Description, PartNumber).",
    input_schema: {
      type: "object" as const,
      properties: {
        name: { type: "string", description: "Property name" },
        value: { type: "string", description: "Property value" },
      },
      required: ["name", "value"],
    },
  },

  // === Document Creation ===
  {
    name: "sw_new_part",
    description: "Create a new SolidWorks part document. Returns success when the new part is created.",
    input_schema: {
      type: "object" as const,
      properties: {},
      required: [],
    },
  },
  {
    name: "sw_new_assembly",
    description: "Create a new SolidWorks assembly document.",
    input_schema: {
      type: "object" as const,
      properties: {},
      required: [],
    },
  },
  {
    name: "sw_open",
    description: "Open an existing SolidWorks document (.sldprt, .sldasm, or .slddrw).",
    input_schema: {
      type: "object" as const,
      properties: {
        filepath: {
          type: "string",
          description: "Path to SolidWorks file to open",
        },
      },
      required: ["filepath"],
    },
  },
  {
    name: "sw_save",
    description: "Save the current document to a file.",
    input_schema: {
      type: "object" as const,
      properties: {
        filepath: {
          type: "string",
          description: "Full path to save the file, e.g., C:/Parts/flange.sldprt",
        },
      },
      required: ["filepath"],
    },
  },
  {
    name: "sw_export",
    description: "Export the current SolidWorks document to another format (STEP, IGES, STL, PDF, DWG, DXF).",
    input_schema: {
      type: "object" as const,
      properties: {
        filepath: {
          type: "string",
          description: "Path to save exported file",
        },
        format: {
          type: "string",
          enum: ["step", "iges", "stl", "pdf", "dwg", "dxf"],
          description: "Export format",
        },
      },
      required: ["filepath", "format"],
    },
  },

  // === Sketching ===
  {
    name: "sw_create_sketch",
    description: "Start a new sketch on a plane. Must close sketch before creating features.",
    input_schema: {
      type: "object" as const,
      properties: {
        plane: {
          type: "string",
          enum: ["Front", "Top", "Right"],
          description: "The reference plane for the sketch",
        },
      },
      required: ["plane"],
    },
  },
  {
    name: "sw_close_sketch",
    description: "Exit the current sketch. Must be called before applying features like extrude.",
    input_schema: {
      type: "object" as const,
      properties: {},
      required: [],
    },
  },
  {
    name: "sw_edit_sketch",
    description: "Open an existing sketch for editing by name. Returns sketch info including segments and dimensions.",
    input_schema: {
      type: "object" as const,
      properties: {
        sketch_name: {
          type: "string",
          description: "Name of the sketch to edit, e.g., 'Sketch1', 'Base-Sketch'",
        },
      },
      required: ["sketch_name"],
    },
  },
  {
    name: "sw_get_sketch_info",
    description: "Get detailed information about a sketch including all segments (lines, arcs, circles), dimensions, and constraints.",
    input_schema: {
      type: "object" as const,
      properties: {
        sketch_name: {
          type: "string",
          description: "Name of the sketch to inspect. If not provided, returns info for the active sketch.",
        },
      },
      required: [],
    },
  },
  {
    name: "sw_open_component",
    description: "Open a component from the current assembly for editing. Opens the part/sub-assembly in a separate window.",
    input_schema: {
      type: "object" as const,
      properties: {
        component_name: {
          type: "string",
          description: "Name of the component to open, e.g., 'InletFlange-1', 'Housing<1>'",
        },
      },
      required: ["component_name"],
    },
  },
  {
    name: "sw_draw_circle",
    description: "Draw a circle in the active sketch. Units are in meters.",
    input_schema: {
      type: "object" as const,
      properties: {
        x: {
          type: "number",
          description: "X coordinate of center (meters)",
        },
        y: {
          type: "number",
          description: "Y coordinate of center (meters)",
        },
        radius: {
          type: "number",
          description: "Radius of circle (meters). Example: 0.025 = 25mm",
        },
      },
      required: ["x", "y", "radius"],
    },
  },
  {
    name: "sw_draw_rectangle",
    description: "Draw a corner rectangle in the active sketch. Units are in meters.",
    input_schema: {
      type: "object" as const,
      properties: {
        x1: { type: "number", description: "First corner X (meters)" },
        y1: { type: "number", description: "First corner Y (meters)" },
        x2: { type: "number", description: "Opposite corner X (meters)" },
        y2: { type: "number", description: "Opposite corner Y (meters)" },
      },
      required: ["x1", "y1", "x2", "y2"],
    },
  },
  {
    name: "sw_draw_line",
    description: "Draw a line in the active sketch. Units are in meters.",
    input_schema: {
      type: "object" as const,
      properties: {
        x1: { type: "number", description: "Start X (meters)" },
        y1: { type: "number", description: "Start Y (meters)" },
        x2: { type: "number", description: "End X (meters)" },
        y2: { type: "number", description: "End Y (meters)" },
      },
      required: ["x1", "y1", "x2", "y2"],
    },
  },

  // === Features ===
  {
    name: "sw_extrude",
    description: "Extrude the current sketch to create a solid boss. Close the sketch first.",
    input_schema: {
      type: "object" as const,
      properties: {
        depth: {
          type: "number",
          description: "Extrusion depth (meters). Example: 0.010 = 10mm",
        },
        direction: {
          type: "number",
          enum: [0, 1],
          description: "0 = one direction, 1 = both directions (mid-plane)",
        },
      },
      required: ["depth"],
    },
  },
  {
    name: "sw_extrude_cut",
    description: "Extrude cut to remove material. Close the sketch first.",
    input_schema: {
      type: "object" as const,
      properties: {
        depth: {
          type: "number",
          description: "Cut depth (meters). Use 999 for 'Through All'",
        },
      },
      required: ["depth"],
    },
  },
  {
    name: "sw_revolve",
    description: "Revolve the current sketch around an axis to create a solid.",
    input_schema: {
      type: "object" as const,
      properties: {
        angle: {
          type: "number",
          description: "Revolve angle in degrees. 360 = full revolution.",
        },
      },
      required: ["angle"],
    },
  },
  {
    name: "sw_fillet",
    description: "Apply a fillet (rounded edge) to selected edges.",
    input_schema: {
      type: "object" as const,
      properties: {
        radius: {
          type: "number",
          description: "Fillet radius (meters). Example: 0.002 = 2mm",
        },
      },
      required: ["radius"],
    },
  },
  {
    name: "sw_chamfer",
    description: "Apply a chamfer (angled edge) to selected edges.",
    input_schema: {
      type: "object" as const,
      properties: {
        distance: {
          type: "number",
          description: "Chamfer distance (meters)",
        },
        angle: {
          type: "number",
          description: "Chamfer angle in degrees (default 45)",
        },
      },
      required: ["distance"],
    },
  },
  {
    name: "sw_loft",
    description: "Create a loft feature between multiple profiles.",
    input_schema: {
      type: "object" as const,
      properties: {
        profiles: {
          type: "array",
          items: { type: "string" },
          description: "List of sketch names or indices for profiles",
        },
        guide_curves: {
          type: "array",
          items: { type: "string" },
          description: "Optional guide curves",
        },
      },
      required: ["profiles"],
    },
  },
  {
    name: "sw_sweep",
    description: "Create a sweep feature along a path.",
    input_schema: {
      type: "object" as const,
      properties: {
        profile: {
          type: "string",
          description: "Profile sketch name",
        },
        path: {
          type: "string",
          description: "Path sketch name",
        },
      },
      required: ["profile", "path"],
    },
  },
  {
    name: "sw_shell",
    description: "Create a shell feature to hollow out a part.",
    input_schema: {
      type: "object" as const,
      properties: {
        thickness: {
          type: "number",
          description: "Shell thickness (meters)",
        },
        faces_to_remove: {
          type: "array",
          items: { type: "string" },
          description: "Optional list of face names to remove",
        },
      },
      required: ["thickness"],
    },
  },
  {
    name: "sw_mirror",
    description: "Mirror features or bodies across a plane.",
    input_schema: {
      type: "object" as const,
      properties: {
        plane: {
          type: "string",
          enum: ["Front", "Top", "Right"],
          description: "Mirror plane",
        },
        features: {
          type: "array",
          items: { type: "string" },
          description: "Optional list of feature names to mirror",
        },
      },
      required: ["plane"],
    },
  },
  {
    name: "sw_draw_spline",
    description: "Draw a spline curve in the active sketch.",
    input_schema: {
      type: "object" as const,
      properties: {
        points: {
          type: "array",
          items: {
            type: "object",
            properties: {
              x: { type: "number" },
              y: { type: "number" },
            },
            required: ["x", "y"],
          },
          description: "List of {x, y} points for the spline",
        },
      },
      required: ["points"],
    },
  },
  {
    name: "sw_draw_polygon",
    description: "Draw a polygon in the active sketch.",
    input_schema: {
      type: "object" as const,
      properties: {
        center_x: { type: "number", description: "Center X (meters)" },
        center_y: { type: "number", description: "Center Y (meters)" },
        radius: { type: "number", description: "Radius (meters)" },
        sides: { type: "number", description: "Number of sides" },
      },
      required: ["center_x", "center_y", "radius", "sides"],
    },
  },
  {
    name: "sw_draw_ellipse",
    description: "Draw an ellipse in the active sketch.",
    input_schema: {
      type: "object" as const,
      properties: {
        center_x: { type: "number", description: "Center X (meters)" },
        center_y: { type: "number", description: "Center Y (meters)" },
        radius_x: { type: "number", description: "X radius (meters)" },
        radius_y: { type: "number", description: "Y radius (meters)" },
      },
      required: ["center_x", "center_y", "radius_x", "radius_y"],
    },
  },
  {
    name: "sw_add_sketch_constraint",
    description: "Add a constraint between sketch entities.",
    input_schema: {
      type: "object" as const,
      properties: {
        constraint_type: {
          type: "string",
          enum: ["coincident", "parallel", "perpendicular", "tangent", "equal"],
          description: "Type of constraint",
        },
        entity1: {
          type: "string",
          description: "First entity name or index",
        },
        entity2: {
          type: "string",
          description: "Second entity name or index",
        },
      },
      required: ["constraint_type", "entity1", "entity2"],
    },
  },
  {
    name: "sw_add_sketch_dimension",
    description: "Add a dimension to a sketch entity.",
    input_schema: {
      type: "object" as const,
      properties: {
        entity: {
          type: "string",
          description: "Entity name or index",
        },
        value: {
          type: "number",
          description: "Dimension value (meters)",
        },
      },
      required: ["entity", "value"],
    },
  },

  // === Patterns ===
  {
    name: "sw_pattern_circular",
    description: "Create a circular pattern of the last feature around an axis.",
    input_schema: {
      type: "object" as const,
      properties: {
        count: {
          type: "number",
          description: "Number of instances in the pattern",
        },
        spacing: {
          type: "number",
          description: "Angular spacing in radians. Use 6.283 (2*PI) for full circle equally spaced.",
        },
      },
      required: ["count", "spacing"],
    },
  },
  {
    name: "sw_pattern_linear",
    description: "Create a linear pattern of the last feature.",
    input_schema: {
      type: "object" as const,
      properties: {
        count_x: { type: "number", description: "Count in X direction" },
        count_y: { type: "number", description: "Count in Y direction" },
        spacing_x: { type: "number", description: "Spacing in X (meters)" },
        spacing_y: { type: "number", description: "Spacing in Y (meters)" },
      },
      required: ["count_x", "spacing_x"],
    },
  },

  // === Selection ===
  {
    name: "sw_select_face",
    description: "Select a face by clicking at coordinates on the model.",
    input_schema: {
      type: "object" as const,
      properties: {
        x: { type: "number", description: "X coordinate (meters)" },
        y: { type: "number", description: "Y coordinate (meters)" },
        z: { type: "number", description: "Z coordinate (meters)" },
      },
      required: ["x", "y", "z"],
    },
  },
  {
    name: "sw_select_edge",
    description: "Select an edge at the given coordinates.",
    input_schema: {
      type: "object" as const,
      properties: {
        x: { type: "number", description: "X coordinate (meters)" },
        y: { type: "number", description: "Y coordinate (meters)" },
        z: { type: "number", description: "Z coordinate (meters)" },
      },
      required: ["x", "y", "z"],
    },
  },
  {
    name: "sw_clear_selection",
    description: "Clear all current selections.",
    input_schema: {
      type: "object" as const,
      properties: {},
      required: [],
    },
  },

  // === Assembly ===
  {
    name: "sw_insert_component",
    description: "Insert a component into the current assembly.",
    input_schema: {
      type: "object" as const,
      properties: {
        filepath: {
          type: "string",
          description: "Path to the part or assembly file to insert",
        },
        x: { type: "number", description: "X position (meters)" },
        y: { type: "number", description: "Y position (meters)" },
        z: { type: "number", description: "Z position (meters)" },
      },
      required: ["filepath"],
    },
  },
  {
    name: "sw_add_mate",
    description: "Add a mate constraint between two selected entities.",
    input_schema: {
      type: "object" as const,
      properties: {
        mate_type: {
          type: "string",
          enum: ["coincident", "concentric", "parallel", "perpendicular", "distance", "angle"],
          description: "Type of mate to add",
        },
        value: {
          type: "number",
          description: "Value for distance or angle mates (meters or degrees)",
        },
      },
      required: ["mate_type"],
    },
  },
  {
    name: "sw_get_bom",
    description: "Extract the Bill of Materials (BOM) from the current SolidWorks assembly. Returns a list of all parts with quantities, part numbers, and file paths.",
    input_schema: {
      type: "object" as const,
      properties: {},
      required: [],
    },
  },
  {
    name: "sw_get_bom_pdf",
    description: "Generate a PDF Bill of Materials for the current SolidWorks assembly.",
    input_schema: {
      type: "object" as const,
      properties: {},
      required: [],
    },
  },
  {
    name: "sw_get_spatial_positions",
    description: "Get 3D spatial positions and relationships of all components in the assembly. Returns X/Y/Z coordinates, distances between parts, and identifies adjacent/nearby components. Useful for analyzing seal-to-ring relationships, axial alignments, and component proximity.",
    input_schema: {
      type: "object" as const,
      properties: {},
      required: [],
    },
  },
  {
    name: "sw_analyze_assembly",
    description: "Run AI-powered design analysis on the current assembly. Analyzes each part's function, suggests proper naming, provides design recommendations, identifies potential issues, and learns from design patterns. Returns geometry, material, features, and mates data.",
    input_schema: {
      type: "object" as const,
      properties: {},
      required: [],
    },
  },
  {
    name: "sw_pattern_component",
    description: "Create a pattern of components in a SolidWorks assembly (linear, circular, or pattern-driven).",
    input_schema: {
      type: "object" as const,
      properties: {
        pattern_type: {
          type: "string",
          enum: ["linear", "circular", "pattern_driven"],
          description: "Pattern type",
        },
        component_name: { type: "string", description: "Component name to pattern" },
        direction1: {
          type: "object",
          description: "First direction: {x, y, z, count, spacing}",
        },
        direction2: {
          type: "object",
          description: "Second direction (optional)",
        },
        axis: {
          type: "object",
          description: "For circular: {x, y, z, count, angle}",
        },
        pattern_feature: {
          type: "string",
          description: "Pattern feature name (for pattern-driven)",
        },
      },
      required: ["pattern_type", "component_name"],
    },
  },
  {
    name: "sw_create_exploded_view",
    description: "Create an exploded view of a SolidWorks assembly.",
    input_schema: {
      type: "object" as const,
      properties: {
        view_name: { type: "string", description: "View name (optional)" },
        create_new: { type: "boolean", description: "Create new view" },
      },
      required: [],
    },
  },
  {
    name: "sw_move_component",
    description: "Move a component in a SolidWorks assembly.",
    input_schema: {
      type: "object" as const,
      properties: {
        component_name: { type: "string", description: "Component name" },
        x: { type: "number", description: "X position (meters)" },
        y: { type: "number", description: "Y position (meters)" },
        z: { type: "number", description: "Z position (meters)" },
      },
      required: ["component_name", "x", "y", "z"],
    },
  },
  {
    name: "sw_suppress_component",
    description: "Suppress or unsuppress a component in a SolidWorks assembly.",
    input_schema: {
      type: "object" as const,
      properties: {
        component_name: { type: "string", description: "Component name" },
        suppress: { type: "boolean", description: "True to suppress, false to unsuppress" },
      },
      required: ["component_name"],
    },
  },
  {
    name: "sw_set_component_visibility",
    description: "Set component visibility in a SolidWorks assembly.",
    input_schema: {
      type: "object" as const,
      properties: {
        component_name: { type: "string", description: "Component name" },
        visible: { type: "boolean", description: "True to show, false to hide" },
      },
      required: ["component_name"],
    },
  },
  {
    name: "sw_replace_component",
    description: "Replace a component with another file in a SolidWorks assembly.",
    input_schema: {
      type: "object" as const,
      properties: {
        component_name: { type: "string", description: "Component name to replace" },
        new_filepath: { type: "string", description: "Path to replacement file" },
      },
      required: ["component_name", "new_filepath"],
    },
  },
  {
    name: "sw_add_advanced_mate",
    description: "Add advanced mate types (gear, cam, width, slot, symmetric, path) in SolidWorks.",
    input_schema: {
      type: "object" as const,
      properties: {
        mate_type: {
          type: "string",
          enum: ["gear", "cam", "width", "slot", "symmetric", "path"],
          description: "Advanced mate type",
        },
        value: { type: "number", description: "Value (optional)" },
        ratio: { type: "number", description: "Gear ratio (for gear mate)" },
      },
      required: ["mate_type"],
    },
  },
  {
    name: "sw_add_assembly_feature",
    description: "Add assembly-level feature (cut, hole, fillet) in SolidWorks.",
    input_schema: {
      type: "object" as const,
      properties: {
        feature_type: {
          type: "string",
          enum: ["cut", "hole", "fillet"],
          description: "Feature type",
        },
        depth: { type: "number", description: "Depth for cut/hole (meters)" },
        radius: { type: "number", description: "Radius for fillet (meters)" },
        hole_type: {
          type: "string",
          enum: ["simple", "counterbore", "countersink"],
          description: "Hole type",
        },
      },
      required: ["feature_type"],
    },
  },
  {
    name: "sw_check_interference",
    description: "Check for interference between components in a SolidWorks assembly.",
    input_schema: {
      type: "object" as const,
      properties: {
        component1: { type: "string", description: "First component (optional)" },
        component2: { type: "string", description: "Second component (optional)" },
      },
      required: [],
    },
  },
  {
    name: "sw_draft",
    description: "Add a draft feature to selected faces in SolidWorks.",
    input_schema: {
      type: "object" as const,
      properties: {
        angle: { type: "number", description: "Draft angle in degrees" },
        faces: {
          type: "array",
          items: { type: "string" },
          description: "Face names or indices (optional)",
        },
      },
      required: ["angle"],
    },
  },
  {
    name: "sw_rib",
    description: "Create a rib feature in SolidWorks.",
    input_schema: {
      type: "object" as const,
      properties: {
        thickness: { type: "number", description: "Rib thickness (meters)" },
        direction: {
          type: "string",
          enum: ["one", "both"],
          description: "Direction",
        },
      },
      required: ["thickness"],
    },
  },
  {
    name: "sw_combine_bodies",
    description: "Combine bodies using boolean operations (add, subtract, intersect) in SolidWorks.",
    input_schema: {
      type: "object" as const,
      properties: {
        operation: {
          type: "string",
          enum: ["add", "subtract", "intersect"],
          description: "Boolean operation",
        },
        body_names: {
          type: "array",
          items: { type: "string" },
          description: "Body names to combine",
        },
      },
      required: ["operation", "body_names"],
    },
  },
  {
    name: "sw_split_body",
    description: "Split a body using a plane in SolidWorks.",
    input_schema: {
      type: "object" as const,
      properties: {
        plane: {
          type: "string",
          enum: ["Front", "Top", "Right"],
          description: "Plane name",
        },
      },
      required: ["plane"],
    },
  },
  {
    name: "sw_move_copy_body",
    description: "Move or copy a body in SolidWorks.",
    input_schema: {
      type: "object" as const,
      properties: {
        body_name: { type: "string", description: "Body name" },
        x: { type: "number", description: "X translation (meters)" },
        y: { type: "number", description: "Y translation (meters)" },
        z: { type: "number", description: "Z translation (meters)" },
        copy: { type: "boolean", description: "True to copy, false to move" },
      },
      required: ["body_name"],
    },
  },
  {
    name: "sw_set_material",
    description: "Assign material to a SolidWorks part.",
    input_schema: {
      type: "object" as const,
      properties: {
        material_name: {
          type: "string",
          description: "Material name (e.g., 'Steel', 'Aluminum')",
        },
      },
      required: ["material_name"],
    },
  },
  {
    name: "sw_get_mass_properties",
    description: "Get mass properties (mass, volume, surface area, center of mass) of a SolidWorks part.",
    input_schema: {
      type: "object" as const,
      properties: {},
      required: [],
    },
  },

  // === Inventor Basic Operations ===
  {
    name: "inv_connect",
    description: "Connect to a running Inventor instance. Call this first before any other Inventor operations.",
    input_schema: {
      type: "object" as const,
      properties: {},
      required: [],
    },
  },
  {
    name: "inv_status",
    description: "Check Inventor connection status and get info about the current document.",
    input_schema: {
      type: "object" as const,
      properties: {},
      required: [],
    },
  },
  {
    name: "inv_new_part",
    description: "Create a new Inventor part document. Returns success when the new part is created.",
    input_schema: {
      type: "object" as const,
      properties: {},
      required: [],
    },
  },
  {
    name: "inv_save",
    description: "Save the current Inventor document to a file.",
    input_schema: {
      type: "object" as const,
      properties: {
        filepath: {
          type: "string",
          description: "Full path to save the file, e.g., C:/Parts/flange.ipt",
        },
      },
      required: ["filepath"],
    },
  },

  // === Inventor Sketching ===
  {
    name: "inv_create_sketch",
    description: "Start a new sketch on a plane in Inventor. Units are in cm.",
    input_schema: {
      type: "object" as const,
      properties: {
        plane: {
          type: "string",
          enum: ["XY", "XZ", "YZ"],
          description: "The reference plane for the sketch",
        },
      },
      required: ["plane"],
    },
  },
  {
    name: "inv_draw_circle",
    description: "Draw a circle in the active Inventor sketch. Units are in cm.",
    input_schema: {
      type: "object" as const,
      properties: {
        x: {
          type: "number",
          description: "X coordinate of center (cm)",
        },
        y: {
          type: "number",
          description: "Y coordinate of center (cm)",
        },
        radius: {
          type: "number",
          description: "Radius of circle (cm). Example: 2.5 = 25mm",
        },
      },
      required: ["x", "y", "radius"],
    },
  },
  {
    name: "inv_draw_rectangle",
    description: "Draw a corner rectangle in the active Inventor sketch. Units are in cm.",
    input_schema: {
      type: "object" as const,
      properties: {
        x1: { type: "number", description: "First corner X (cm)" },
        y1: { type: "number", description: "First corner Y (cm)" },
        x2: { type: "number", description: "Opposite corner X (cm)" },
        y2: { type: "number", description: "Opposite corner Y (cm)" },
      },
      required: ["x1", "y1", "x2", "y2"],
    },
  },
  {
    name: "inv_draw_line",
    description: "Draw a line in the active Inventor sketch. Units are in cm.",
    input_schema: {
      type: "object" as const,
      properties: {
        x1: { type: "number", description: "Start X (cm)" },
        y1: { type: "number", description: "Start Y (cm)" },
        x2: { type: "number", description: "End X (cm)" },
        y2: { type: "number", description: "End Y (cm)" },
      },
      required: ["x1", "y1", "x2", "y2"],
    },
  },
  {
    name: "inv_draw_arc",
    description: "Draw an arc in the active Inventor sketch. Units are in cm.",
    input_schema: {
      type: "object" as const,
      properties: {
        center_x: { type: "number", description: "Center X (cm)" },
        center_y: { type: "number", description: "Center Y (cm)" },
        radius: { type: "number", description: "Radius (cm)" },
        start_angle: { type: "number", description: "Start angle in degrees" },
        end_angle: { type: "number", description: "End angle in degrees" },
      },
      required: ["center_x", "center_y", "radius", "start_angle", "end_angle"],
    },
  },

  // === Inventor Features ===
  {
    name: "inv_extrude",
    description: "Extrude the current Inventor sketch profile to create a solid. Units are in cm.",
    input_schema: {
      type: "object" as const,
      properties: {
        depth: {
          type: "number",
          description: "Extrusion depth (cm). Example: 1.0 = 10mm",
        },
        direction: {
          type: "string",
          enum: ["positive", "negative", "symmetric"],
          description: "Extrusion direction",
        },
      },
      required: ["depth"],
    },
  },
  {
    name: "inv_revolve",
    description: "Revolve the current Inventor sketch profile around an axis to create a solid.",
    input_schema: {
      type: "object" as const,
      properties: {
        angle: {
          type: "number",
          description: "Revolve angle in degrees. 360 = full revolution.",
        },
      },
      required: ["angle"],
    },
  },
  {
    name: "inv_fillet",
    description: "Apply a fillet (rounded edge) to selected edges in Inventor. Units are in cm.",
    input_schema: {
      type: "object" as const,
      properties: {
        radius: {
          type: "number",
          description: "Fillet radius (cm). Example: 0.2 = 2mm",
        },
      },
      required: ["radius"],
    },
  },
  {
    name: "inv_loft",
    description: "Create a loft feature between multiple profiles in Inventor.",
    input_schema: {
      type: "object" as const,
      properties: {
        profiles: {
          type: "array",
          items: { type: "string" },
          description: "List of sketch names or indices for profiles",
        },
        guide_curves: {
          type: "array",
          items: { type: "string" },
          description: "Optional guide curves",
        },
      },
      required: ["profiles"],
    },
  },
  {
    name: "inv_sweep",
    description: "Create a sweep feature along a path in Inventor.",
    input_schema: {
      type: "object" as const,
      properties: {
        profile: {
          type: "string",
          description: "Profile sketch name",
        },
        path: {
          type: "string",
          description: "Path sketch name",
        },
      },
      required: ["profile", "path"],
    },
  },
  {
    name: "inv_shell",
    description: "Create a shell feature to hollow out a part in Inventor.",
    input_schema: {
      type: "object" as const,
      properties: {
        thickness: {
          type: "number",
          description: "Shell thickness (cm)",
        },
        faces_to_remove: {
          type: "array",
          items: { type: "string" },
          description: "Optional list of face names to remove",
        },
      },
      required: ["thickness"],
    },
  },
  {
    name: "inv_mirror",
    description: "Mirror features or bodies across a plane in Inventor.",
    input_schema: {
      type: "object" as const,
      properties: {
        plane: {
          type: "string",
          enum: ["XY", "XZ", "YZ"],
          description: "Mirror plane",
        },
        features: {
          type: "array",
          items: { type: "string" },
          description: "Optional list of feature names to mirror",
        },
      },
      required: ["plane"],
    },
  },
  {
    name: "inv_draw_spline",
    description: "Draw a spline curve in the active Inventor sketch.",
    input_schema: {
      type: "object" as const,
      properties: {
        points: {
          type: "array",
          items: {
            type: "object",
            properties: {
              x: { type: "number" },
              y: { type: "number" },
            },
            required: ["x", "y"],
          },
          description: "List of {x, y} points for the spline (cm)",
        },
      },
      required: ["points"],
    },
  },
  {
    name: "inv_draw_polygon",
    description: "Draw a polygon in the active Inventor sketch.",
    input_schema: {
      type: "object" as const,
      properties: {
        center_x: { type: "number", description: "Center X (cm)" },
        center_y: { type: "number", description: "Center Y (cm)" },
        radius: { type: "number", description: "Radius (cm)" },
        sides: { type: "number", description: "Number of sides" },
      },
      required: ["center_x", "center_y", "radius", "sides"],
    },
  },
  {
    name: "inv_draw_ellipse",
    description: "Draw an ellipse in the active Inventor sketch.",
    input_schema: {
      type: "object" as const,
      properties: {
        center_x: { type: "number", description: "Center X (cm)" },
        center_y: { type: "number", description: "Center Y (cm)" },
        radius_x: { type: "number", description: "X radius (cm)" },
        radius_y: { type: "number", description: "Y radius (cm)" },
      },
      required: ["center_x", "center_y", "radius_x", "radius_y"],
    },
  },
  {
    name: "inv_add_sketch_constraint",
    description: "Add a constraint between sketch entities in Inventor.",
    input_schema: {
      type: "object" as const,
      properties: {
        constraint_type: {
          type: "string",
          enum: ["coincident", "parallel", "perpendicular", "tangent", "equal"],
          description: "Type of constraint",
        },
        entity1: {
          type: "string",
          description: "First entity name or index",
        },
        entity2: {
          type: "string",
          description: "Second entity name or index",
        },
      },
      required: ["constraint_type", "entity1", "entity2"],
    },
  },
  {
    name: "inv_add_sketch_dimension",
    description: "Add a dimension to a sketch entity in Inventor.",
    input_schema: {
      type: "object" as const,
      properties: {
        entity: {
          type: "string",
          description: "Entity name or index",
        },
        value: {
          type: "number",
          description: "Dimension value (cm)",
        },
      },
      required: ["entity", "value"],
    },
  },
  {
    name: "inv_open",
    description: "Open an existing Inventor document (.ipt, .iam, or .idw).",
    input_schema: {
      type: "object" as const,
      properties: {
        filepath: {
          type: "string",
          description: "Path to Inventor file to open",
        },
      },
      required: ["filepath"],
    },
  },
  {
    name: "inv_export",
    description: "Export the current Inventor document to another format (STEP, IGES, STL, PDF).",
    input_schema: {
      type: "object" as const,
      properties: {
        filepath: {
          type: "string",
          description: "Path to save exported file",
        },
        format: {
          type: "string",
          enum: ["step", "iges", "stl", "pdf"],
          description: "Export format",
        },
      },
      required: ["filepath", "format"],
    },
  },
  {
    name: "inv_chamfer",
    description: "Apply a chamfer (angled edge) to selected edges in Inventor. Units are in cm.",
    input_schema: {
      type: "object" as const,
      properties: {
        distance: { type: "number", description: "Chamfer distance (cm)" },
        angle: { type: "number", description: "Chamfer angle in degrees (default 45)" },
      },
      required: ["distance"],
    },
  },
  {
    name: "inv_pattern_circular",
    description: "Create a circular pattern of the last feature in Inventor.",
    input_schema: {
      type: "object" as const,
      properties: {
        count: { type: "number", description: "Number of instances" },
        spacing: { type: "number", description: "Angular spacing in degrees" },
      },
      required: ["count", "spacing"],
    },
  },
  {
    name: "inv_pattern_linear",
    description: "Create a linear pattern of the last feature in Inventor.",
    input_schema: {
      type: "object" as const,
      properties: {
        count_x: { type: "number", description: "Count in X direction" },
        count_y: { type: "number", description: "Count in Y direction" },
        spacing_x: { type: "number", description: "Spacing in X (cm)" },
        spacing_y: { type: "number", description: "Spacing in Y (cm)" },
      },
      required: ["count_x", "spacing_x"],
    },
  },
  {
    name: "inv_draft",
    description: "Add a draft feature to selected faces in Inventor.",
    input_schema: {
      type: "object" as const,
      properties: {
        angle: { type: "number", description: "Draft angle in degrees" },
        faces: { type: "array", items: { type: "string" }, description: "Optional face names" },
      },
      required: ["angle"],
    },
  },
  {
    name: "inv_rib",
    description: "Create a rib feature in Inventor.",
    input_schema: {
      type: "object" as const,
      properties: {
        thickness: { type: "number", description: "Rib thickness (cm)" },
        direction: { type: "string", enum: ["one", "both"], description: "Direction" },
      },
      required: ["thickness"],
    },
  },
  {
    name: "inv_combine_bodies",
    description: "Combine bodies using boolean operations in Inventor.",
    input_schema: {
      type: "object" as const,
      properties: {
        operation: { type: "string", enum: ["add", "subtract", "intersect"], description: "Boolean operation" },
        body_names: { type: "array", items: { type: "string" }, description: "Body names" },
      },
      required: ["operation", "body_names"],
    },
  },
  {
    name: "inv_split_body",
    description: "Split a body using a plane in Inventor.",
    input_schema: {
      type: "object" as const,
      properties: {
        plane: { type: "string", enum: ["XY", "XZ", "YZ"], description: "Plane name" },
      },
      required: ["plane"],
    },
  },
  {
    name: "inv_move_copy_body",
    description: "Move or copy a body in Inventor.",
    input_schema: {
      type: "object" as const,
      properties: {
        body_name: { type: "string", description: "Body name" },
        x: { type: "number", description: "X translation (cm)" },
        y: { type: "number", description: "Y translation (cm)" },
        z: { type: "number", description: "Z translation (cm)" },
        copy: { type: "boolean", description: "True to copy, false to move" },
      },
      required: ["body_name"],
    },
  },
  {
    name: "inv_set_material",
    description: "Assign material to an Inventor part.",
    input_schema: {
      type: "object" as const,
      properties: {
        material_name: { type: "string", description: "Material name" },
      },
      required: ["material_name"],
    },
  },
  {
    name: "inv_set_custom_property",
    description: "Set a custom property (iProperty) for an Inventor document.",
    input_schema: {
      type: "object" as const,
      properties: {
        name: { type: "string", description: "Property name" },
        value: { type: "string", description: "Property value" },
      },
      required: ["name", "value"],
    },
  },
  {
    name: "inv_get_mass_properties",
    description: "Get mass properties of an Inventor part.",
    input_schema: {
      type: "object" as const,
      properties: {},
      required: [],
    },
  },

  // === SolidWorks Drawings ===
  {
    name: "sw_new_drawing",
    description: "Create a new SolidWorks drawing document.",
    input_schema: {
      type: "object" as const,
      properties: {
        template_path: {
          type: "string",
          description: "Optional custom template path",
        },
      },
      required: [],
    },
  },
  {
    name: "sw_create_drawing_view",
    description: "Create a view in a SolidWorks drawing.",
    input_schema: {
      type: "object" as const,
      properties: {
        view_type: {
          type: "string",
          enum: ["front", "top", "isometric", "section", "detail"],
          description: "Type of view to create",
        },
        model_path: {
          type: "string",
          description: "Path to part/assembly file",
        },
        x: { type: "number", description: "X position" },
        y: { type: "number", description: "Y position" },
        scale: { type: "number", description: "View scale" },
      },
      required: ["view_type"],
    },
  },
  {
    name: "sw_add_drawing_dimension",
    description: "Add a dimension to a SolidWorks drawing view.",
    input_schema: {
      type: "object" as const,
      properties: {
        view_name: { type: "string", description: "View name" },
        entity1: { type: "string", description: "First entity" },
        entity2: { type: "string", description: "Second entity (optional)" },
        value: { type: "number", description: "Dimension value (optional)" },
      },
      required: ["view_name", "entity1"],
    },
  },
  {
    name: "sw_add_drawing_note",
    description: "Add a note/annotation to a SolidWorks drawing.",
    input_schema: {
      type: "object" as const,
      properties: {
        view_name: { type: "string", description: "View name" },
        text: { type: "string", description: "Note text" },
        x: { type: "number", description: "X position" },
        y: { type: "number", description: "Y position" },
      },
      required: ["text", "x", "y"],
    },
  },
  {
    name: "sw_add_bom",
    description: "Add a BOM table to a SolidWorks drawing.",
    input_schema: {
      type: "object" as const,
      properties: {
        assembly_path: {
          type: "string",
          description: "Path to assembly file",
        },
        x: { type: "number", description: "X position" },
        y: { type: "number", description: "Y position" },
      },
      required: ["assembly_path"],
    },
  },
  {
    name: "sw_edit_title_block",
    description: "Edit a title block field in a SolidWorks drawing.",
    input_schema: {
      type: "object" as const,
      properties: {
        field_name: { type: "string", description: "Title block field name" },
        value: { type: "string", description: "Field value" },
      },
      required: ["field_name", "value"],
    },
  },
  {
    name: "sw_add_revision_table",
    description: "Add a revision table to a SolidWorks drawing.",
    input_schema: {
      type: "object" as const,
      properties: {
        x: { type: "number", description: "X position" },
        y: { type: "number", description: "Y position" },
        num_rows: { type: "number", description: "Number of rows (default: 5)" },
      },
      required: [],
    },
  },
  {
    name: "sw_add_revision",
    description: "Add a revision entry to the revision table.",
    input_schema: {
      type: "object" as const,
      properties: {
        revision: { type: "string", description: "Revision identifier (e.g., 'A', 'B', '1')" },
        description: { type: "string", description: "Revision description" },
        date: { type: "string", description: "Revision date" },
      },
      required: ["revision"],
    },
  },
  {
    name: "sw_add_balloon",
    description: "Add a balloon/callout to a component in a SolidWorks drawing view.",
    input_schema: {
      type: "object" as const,
      properties: {
        view_name: { type: "string", description: "View name" },
        component_name: { type: "string", description: "Component name or number" },
        x: { type: "number", description: "X position" },
        y: { type: "number", description: "Y position" },
        balloon_style: {
          type: "string",
          enum: ["circular", "square", "triangle"],
          description: "Balloon style",
        },
      },
      required: ["view_name", "component_name", "x", "y"],
    },
  },
  {
    name: "sw_add_sheet",
    description: "Add a new sheet to a SolidWorks drawing.",
    input_schema: {
      type: "object" as const,
      properties: {
        sheet_name: { type: "string", description: "Sheet name (optional)" },
        sheet_size: {
          type: "string",
          enum: ["A", "B", "C", "D", "E"],
          description: "Sheet size",
        },
      },
      required: [],
    },
  },
  {
    name: "sw_set_view_properties",
    description: "Set properties of a drawing view (scale, display mode).",
    input_schema: {
      type: "object" as const,
      properties: {
        view_name: { type: "string", description: "View name" },
        scale: { type: "number", description: "View scale" },
        display_mode: {
          type: "string",
          enum: ["wireframe", "hidden", "shaded"],
          description: "Display mode",
        },
      },
      required: ["view_name"],
    },
  },
  {
    name: "sw_add_centerline",
    description: "Add a centerline to a SolidWorks drawing view.",
    input_schema: {
      type: "object" as const,
      properties: {
        view_name: { type: "string", description: "View name" },
        x1: { type: "number", description: "Start X" },
        y1: { type: "number", description: "Start Y" },
        x2: { type: "number", description: "End X" },
        y2: { type: "number", description: "End Y" },
      },
      required: ["view_name", "x1", "y1", "x2", "y2"],
    },
  },
  {
    name: "sw_add_center_mark",
    description: "Add a center mark to a hole in a SolidWorks drawing view.",
    input_schema: {
      type: "object" as const,
      properties: {
        view_name: { type: "string", description: "View name" },
        x: { type: "number", description: "X position" },
        y: { type: "number", description: "Y position" },
      },
      required: ["view_name", "x", "y"],
    },
  },
  {
    name: "sw_add_hatching",
    description: "Add hatching/pattern to a section view in SolidWorks drawing.",
    input_schema: {
      type: "object" as const,
      properties: {
        view_name: { type: "string", description: "View name" },
        pattern: { type: "string", description: "Hatch pattern (default: ansi31)" },
        scale: { type: "number", description: "Pattern scale" },
      },
      required: ["view_name"],
    },
  },
  {
    name: "sw_add_table",
    description: "Add a general table to a SolidWorks drawing.",
    input_schema: {
      type: "object" as const,
      properties: {
        num_rows: { type: "number", description: "Number of rows" },
        num_cols: { type: "number", description: "Number of columns" },
        x: { type: "number", description: "X position" },
        y: { type: "number", description: "Y position" },
        row_heights: {
          type: "array",
          items: { type: "number" },
          description: "Row heights array (optional)",
        },
        col_widths: {
          type: "array",
          items: { type: "number" },
          description: "Column widths array (optional)",
        },
      },
      required: ["num_rows", "num_cols", "x", "y"],
    },
  },
  {
    name: "sw_add_leader_line",
    description: "Add a leader line with optional text to a SolidWorks drawing.",
    input_schema: {
      type: "object" as const,
      properties: {
        view_name: { type: "string", description: "View name" },
        points: {
          type: "array",
          items: {
            type: "object",
            properties: {
              x: { type: "number" },
              y: { type: "number" },
            },
          },
          description: "Array of {x, y} points for leader line",
        },
        text: { type: "string", description: "Optional text annotation" },
      },
      required: ["view_name", "points"],
    },
  },

  // === Inventor Drawings ===
  {
    name: "inv_new_drawing",
    description: "Create a new Inventor drawing document.",
    input_schema: {
      type: "object" as const,
      properties: {
        template_path: {
          type: "string",
          description: "Optional custom template path",
        },
      },
      required: [],
    },
  },
  {
    name: "inv_create_drawing_view",
    description: "Create a view in an Inventor drawing.",
    input_schema: {
      type: "object" as const,
      properties: {
        view_type: {
          type: "string",
          enum: ["front", "top", "isometric", "section", "detail"],
          description: "Type of view to create",
        },
        model_path: {
          type: "string",
          description: "Path to part/assembly file",
        },
        x: { type: "number", description: "X position (cm)" },
        y: { type: "number", description: "Y position (cm)" },
        scale: { type: "number", description: "View scale" },
      },
      required: ["view_type"],
    },
  },
  {
    name: "inv_add_drawing_dimension",
    description: "Add a dimension to an Inventor drawing view.",
    input_schema: {
      type: "object" as const,
      properties: {
        view_name: { type: "string", description: "View name" },
        entity1: { type: "string", description: "First entity" },
        entity2: { type: "string", description: "Second entity (optional)" },
        value: { type: "number", description: "Dimension value (optional)" },
      },
      required: ["view_name", "entity1"],
    },
  },
  {
    name: "inv_add_drawing_note",
    description: "Add a note/annotation to an Inventor drawing.",
    input_schema: {
      type: "object" as const,
      properties: {
        view_name: { type: "string", description: "View name" },
        text: { type: "string", description: "Note text" },
        x: { type: "number", description: "X position (cm)" },
        y: { type: "number", description: "Y position (cm)" },
      },
      required: ["text", "x", "y"],
    },
  },
  {
    name: "inv_add_bom",
    description: "Add a BOM table to an Inventor drawing.",
    input_schema: {
      type: "object" as const,
      properties: {
        assembly_path: {
          type: "string",
          description: "Path to assembly file",
        },
        x: { type: "number", description: "X position (cm)" },
        y: { type: "number", description: "Y position (cm)" },
      },
      required: ["assembly_path"],
    },
  },
  {
    name: "inv_edit_title_block",
    description: "Edit a title block field in an Inventor drawing.",
    input_schema: {
      type: "object" as const,
      properties: {
        field_name: { type: "string", description: "Title block field name" },
        value: { type: "string", description: "Field value" },
      },
      required: ["field_name", "value"],
    },
  },
  {
    name: "inv_add_revision_table",
    description: "Add a revision table to an Inventor drawing.",
    input_schema: {
      type: "object" as const,
      properties: {
        x: { type: "number", description: "X position (cm)" },
        y: { type: "number", description: "Y position (cm)" },
        num_rows: { type: "number", description: "Number of rows (default: 5)" },
      },
      required: [],
    },
  },
  {
    name: "inv_add_revision",
    description: "Add a revision entry to the revision table.",
    input_schema: {
      type: "object" as const,
      properties: {
        revision: { type: "string", description: "Revision identifier (e.g., 'A', 'B', '1')" },
        description: { type: "string", description: "Revision description" },
        date: { type: "string", description: "Revision date" },
      },
      required: ["revision"],
    },
  },
  {
    name: "inv_add_balloon",
    description: "Add a balloon/callout to a component in an Inventor drawing view.",
    input_schema: {
      type: "object" as const,
      properties: {
        view_name: { type: "string", description: "View name" },
        component_name: { type: "string", description: "Component name or number" },
        x: { type: "number", description: "X position (cm)" },
        y: { type: "number", description: "Y position (cm)" },
        balloon_style: {
          type: "string",
          enum: ["circular", "square", "triangle"],
          description: "Balloon style",
        },
      },
      required: ["view_name", "component_name", "x", "y"],
    },
  },
  {
    name: "inv_add_sheet",
    description: "Add a new sheet to an Inventor drawing.",
    input_schema: {
      type: "object" as const,
      properties: {
        sheet_name: { type: "string", description: "Sheet name (optional)" },
        sheet_size: {
          type: "string",
          enum: ["A", "B", "C", "D", "E"],
          description: "Sheet size",
        },
      },
      required: [],
    },
  },
  {
    name: "inv_set_view_properties",
    description: "Set properties of a drawing view (scale, display mode).",
    input_schema: {
      type: "object" as const,
      properties: {
        view_name: { type: "string", description: "View name" },
        scale: { type: "number", description: "View scale" },
        display_mode: {
          type: "string",
          enum: ["wireframe", "hidden", "shaded"],
          description: "Display mode",
        },
      },
      required: ["view_name"],
    },
  },
  {
    name: "inv_add_centerline",
    description: "Add a centerline to an Inventor drawing view.",
    input_schema: {
      type: "object" as const,
      properties: {
        view_name: { type: "string", description: "View name" },
        x1: { type: "number", description: "Start X (cm)" },
        y1: { type: "number", description: "Start Y (cm)" },
        x2: { type: "number", description: "End X (cm)" },
        y2: { type: "number", description: "End Y (cm)" },
      },
      required: ["view_name", "x1", "y1", "x2", "y2"],
    },
  },
  {
    name: "inv_add_center_mark",
    description: "Add a center mark to a hole in an Inventor drawing view.",
    input_schema: {
      type: "object" as const,
      properties: {
        view_name: { type: "string", description: "View name" },
        x: { type: "number", description: "X position (cm)" },
        y: { type: "number", description: "Y position (cm)" },
      },
      required: ["view_name", "x", "y"],
    },
  },
  {
    name: "inv_add_hatching",
    description: "Add hatching/pattern to a section view in Inventor drawing.",
    input_schema: {
      type: "object" as const,
      properties: {
        view_name: { type: "string", description: "View name" },
        pattern: { type: "string", description: "Hatch pattern (default: ansi31)" },
        scale: { type: "number", description: "Pattern scale" },
      },
      required: ["view_name"],
    },
  },
  {
    name: "inv_add_table",
    description: "Add a general table to an Inventor drawing.",
    input_schema: {
      type: "object" as const,
      properties: {
        num_rows: { type: "number", description: "Number of rows" },
        num_cols: { type: "number", description: "Number of columns" },
        x: { type: "number", description: "X position (cm)" },
        y: { type: "number", description: "Y position (cm)" },
        row_heights: {
          type: "array",
          items: { type: "number" },
          description: "Row heights array (optional)",
        },
        col_widths: {
          type: "array",
          items: { type: "number" },
          description: "Column widths array (optional)",
        },
      },
      required: ["num_rows", "num_cols", "x", "y"],
    },
  },
  {
    name: "inv_add_leader_line",
    description: "Add a leader line with optional text to an Inventor drawing.",
    input_schema: {
      type: "object" as const,
      properties: {
        view_name: { type: "string", description: "View name" },
        points: {
          type: "array",
          items: {
            type: "object",
            properties: {
              x: { type: "number" },
              y: { type: "number" },
            },
          },
          description: "Array of {x, y} points for leader line",
        },
        text: { type: "string", description: "Optional text annotation" },
      },
      required: ["view_name", "points"],
    },
  },

  // === Inventor Assembly ===
  {
    name: "inv_new_assembly",
    description: "Create a new Inventor assembly document.",
    input_schema: {
      type: "object" as const,
      properties: {},
      required: [],
    },
  },
  {
    name: "inv_insert_component",
    description: "Insert a component into the current Inventor assembly.",
    input_schema: {
      type: "object" as const,
      properties: {
        filepath: {
          type: "string",
          description: "Path to the part or assembly file to insert",
        },
        x: { type: "number", description: "X position (cm)" },
        y: { type: "number", description: "Y position (cm)" },
        z: { type: "number", description: "Z position (cm)" },
      },
      required: ["filepath"],
    },
  },
  {
    name: "inv_add_joint",
    description: "Add a joint constraint between two components in an Inventor assembly.",
    input_schema: {
      type: "object" as const,
      properties: {
        joint_type: {
          type: "string",
          enum: ["rigid", "revolute", "slider", "cylindrical", "planar", "ball"],
          description: "Type of joint to add",
        },
        component1: {
          type: "string",
          description: "Name of first component",
        },
        component2: {
          type: "string",
          description: "Name of second component",
        },
        geometry1: {
          type: "string",
          description: "Face or edge name on component1",
        },
        geometry2: {
          type: "string",
          description: "Face or edge name on component2",
        },
      },
      required: ["joint_type", "component1", "component2", "geometry1", "geometry2"],
    },
  },
  {
    name: "inv_pattern_component",
    description: "Create a pattern of components in an Inventor assembly.",
    input_schema: {
      type: "object" as const,
      properties: {
        pattern_type: { type: "string", enum: ["linear", "circular"], description: "Pattern type" },
        component_name: { type: "string", description: "Component name" },
        direction1: { type: "object", description: "First direction info" },
        direction2: { type: "object", description: "Second direction info" },
        axis: { type: "object", description: "Rotation axis info" },
      },
      required: ["pattern_type", "component_name"],
    },
  },
  {
    name: "inv_create_exploded_view",
    description: "Create an exploded view of an Inventor assembly.",
    input_schema: {
      type: "object" as const,
      properties: {
        view_name: { type: "string", description: "View name" },
        create_new: { type: "boolean", description: "Create new view" },
      },
      required: [],
    },
  },
  {
    name: "inv_move_component",
    description: "Move a component in an Inventor assembly.",
    input_schema: {
      type: "object" as const,
      properties: {
        component_name: { type: "string", description: "Component name" },
        x: { type: "number", description: "X pos (cm)" },
        y: { type: "number", description: "Y pos (cm)" },
        z: { type: "number", description: "Z pos (cm)" },
      },
      required: ["component_name", "x", "y", "z"],
    },
  },
  {
    name: "inv_suppress_component",
    description: "Suppress or unsuppress a component in Inventor.",
    input_schema: {
      type: "object" as const,
      properties: {
        component_name: { type: "string", description: "Component name" },
        suppress: { type: "boolean", description: "True to suppress" },
      },
      required: ["component_name"],
    },
  },
  {
    name: "inv_set_component_visibility",
    description: "Set component visibility in Inventor.",
    input_schema: {
      type: "object" as const,
      properties: {
        component_name: { type: "string", description: "Component name" },
        visible: { type: "boolean", description: "True to show" },
      },
      required: ["component_name"],
    },
  },
  {
    name: "inv_replace_component",
    description: "Replace a component in Inventor.",
    input_schema: {
      type: "object" as const,
      properties: {
        component_name: { type: "string", description: "Component name" },
        new_filepath: { type: "string", description: "Path to replacement" },
      },
      required: ["component_name", "new_filepath"],
    },
  },
  {
    name: "inv_check_interference",
    description: "Check for interference in an Inventor assembly.",
    input_schema: {
      type: "object" as const,
      properties: {
        component1: { type: "string", description: "First component" },
        component2: { type: "string", description: "Second component" },
      },
      required: [],
    },
  },
  {
    name: "inv_zoom_fit",
    description: "Zoom to fit in Inventor.",
    input_schema: {
      type: "object" as const,
      properties: {},
      required: [],
    },
  },
  {
    name: "inv_set_view",
    description: "Set view orientation in Inventor.",
    input_schema: {
      type: "object" as const,
      properties: {
        view: { type: "string", enum: ["front", "back", "top", "bottom", "left", "right", "isometric"], description: "View name" },
      },
      required: ["view"],
    },
  },

  // === Inventor iMates ===
  {
    name: "inv_create_imates_for_assembly",
    description: "Create Insert, Mate, and Composite iMates for hole-to-hole alignment in an Inventor assembly. Automatically detects holes and creates appropriate iMates.",
    input_schema: {
      type: "object" as const,
      properties: {
        filepath: {
          type: "string",
          description: "Path to Inventor assembly file (.iam)",
        },
        part_ids: {
          type: "array",
          items: { type: "string" },
          description: "Optional: Specific part IDs to process. If not provided, processes all parts.",
        },
      },
      required: ["filepath"],
    },
  },
  {
    name: "inv_create_composite_imates",
    description: "Create Composite iMates for bolt patterns in an Inventor part. Groups multiple hole iMates into a single Composite iMate.",
    input_schema: {
      type: "object" as const,
      properties: {
        filepath: {
          type: "string",
          description: "Path to Inventor part file (.ipt)",
        },
        pattern_type: {
          type: "string",
          enum: ["auto", "circular", "rectangular"],
          description: "Pattern type to detect. 'auto' detects both circular and rectangular patterns.",
        },
      },
      required: ["filepath"],
    },
  },
  {
    name: "inv_verify_hole_alignment",
    description: "Verify hole alignment in an Inventor assembly by reading created iMates. Reports any mis-aligned holes within ±1/16\" tolerance.",
    input_schema: {
      type: "object" as const,
      properties: {
        filepath: {
          type: "string",
          description: "Path to Inventor assembly file (.iam)",
        },
        tolerance: {
          type: "number",
          description: "Tolerance in meters (default: 0.0015875 = 1/16\")",
        },
      },
      required: ["filepath"],
    },
  },

  // === SolidWorks Mate References ===
  {
    name: "sw_create_mate_refs_for_assembly",
    description: "Create Concentric + Coincident Mate References (SmartMates) for hole alignment in a SolidWorks assembly. Automatically detects holes and creates appropriate Mate References.",
    input_schema: {
      type: "object" as const,
      properties: {
        filepath: {
          type: "string",
          description: "Path to SolidWorks assembly file (.sldasm)",
        },
        part_ids: {
          type: "array",
          items: { type: "string" },
          description: "Optional: Specific part IDs to process. If not provided, processes all parts.",
        },
      },
      required: ["filepath"],
    },
  },
  {
    name: "sw_verify_hole_alignment",
    description: "Verify hole alignment in a SolidWorks assembly by reading created Mate References. Reports any mis-aligned holes within ±1/16\" tolerance.",
    input_schema: {
      type: "object" as const,
      properties: {
        filepath: {
          type: "string",
          description: "Path to SolidWorks assembly file (.sldasm)",
        },
        tolerance: {
          type: "number",
          description: "Tolerance in meters (default: 0.0015875 = 1/16\")",
        },
      },
      required: ["filepath"],
    },
  },

  // === Screenshot & Vision Tools ===
  {
    name: "sw_screenshot",
    description: "Take a screenshot of the current SolidWorks view.",
    input_schema: {
      type: "object" as const,
      properties: {},
      required: [],
    },
  },
  {
    name: "sw_screenshot_window",
    description: "Capture screenshot of only the SolidWorks window (not full screen).",
    input_schema: {
      type: "object" as const,
      properties: {
        window_title: {
          type: "string",
          description: "Window title to capture (default: 'SolidWorks')",
        },
      },
      required: [],
    },
  },
  {
    name: "sw_screenshot_viewport",
    description: "Capture screenshot of only the 3D viewport (excludes toolbars, feature tree).",
    input_schema: {
      type: "object" as const,
      properties: {},
      required: [],
    },
  },
  {
    name: "sw_screenshot_feature_tree",
    description: "Capture screenshot of the feature tree panel.",
    input_schema: {
      type: "object" as const,
      properties: {},
      required: [],
    },
  },
  {
    name: "sw_screenshot_property_manager",
    description: "Capture screenshot of the property manager panel.",
    input_schema: {
      type: "object" as const,
      properties: {},
      required: [],
    },
  },
  {
    name: "sw_capture_multi_view",
    description: "Capture multiple standard views (Front, Top, Right, Isometric) in one call.",
    input_schema: {
      type: "object" as const,
      properties: {
        views: {
          type: "array",
          items: { type: "string" },
          description: "List of views to capture: front, top, right, isometric, etc.",
        },
      },
      required: [],
    },
  },
  {
    name: "sw_extract_dimensions_screenshot",
    description: "Extract dimensions visible in screenshot using OCR and pattern matching.",
    input_schema: {
      type: "object" as const,
      properties: {
        image_base64: {
          type: "string",
          description: "Base64 encoded screenshot image",
        },
      },
      required: ["image_base64"],
    },
  },
  {
    name: "sw_detect_gdt_symbols",
    description: "Detect and identify GD&T symbols in drawing screenshot.",
    input_schema: {
      type: "object" as const,
      properties: {
        image_base64: {
          type: "string",
          description: "Base64 encoded screenshot image",
        },
      },
      required: ["image_base64"],
    },
  },
  {
    name: "sw_detect_annotations",
    description: "Detect and extract all annotations (notes, balloons, dimensions) from drawing screenshot.",
    input_schema: {
      type: "object" as const,
      properties: {
        image_base64: {
          type: "string",
          description: "Base64 encoded screenshot image",
        },
      },
      required: ["image_base64"],
    },
  },
  {
    name: "sw_extract_bom_screenshot",
    description: "Extract BOM table from drawing screenshot.",
    input_schema: {
      type: "object" as const,
      properties: {
        image_base64: {
          type: "string",
          description: "Base64 encoded screenshot image",
        },
      },
      required: ["image_base64"],
    },
  },
  {
    name: "sw_analyze_drawing_sheet",
    description: "Comprehensive analysis of entire drawing sheet (dimensions, GD&T, annotations, BOM).",
    input_schema: {
      type: "object" as const,
      properties: {
        image_base64: {
          type: "string",
          description: "Base64 encoded screenshot image",
        },
      },
      required: ["image_base64"],
    },
  },
  {
    name: "sw_compare_screenshots",
    description: "Compare two screenshots and highlight differences.",
    input_schema: {
      type: "object" as const,
      properties: {
        image1_base64: {
          type: "string",
          description: "First screenshot (base64)",
        },
        image2_base64: {
          type: "string",
          description: "Second screenshot (base64)",
        },
        threshold: {
          type: "number",
          description: "Similarity threshold (0.0-1.0, default: 0.95)",
        },
      },
      required: ["image1_base64", "image2_base64"],
    },
  },

  // === Batch Operations (High Performance) ===
  {
    name: "sw_batch_operations",
    description: "Execute multiple operations with deferred rebuild (MUCH FASTER - 3-5x speedup). Use this when making multiple changes to avoid rebuilds after each operation.",
    input_schema: {
      type: "object" as const,
      properties: {
        operations: {
          type: "array",
          items: {
            type: "object",
            properties: {
              operation: { type: "string", description: "Operation name (extrude, fillet, hole, etc.)" },
              params: { type: "object", description: "Operation parameters" },
            },
            required: ["operation", "params"],
          },
          description: "List of operations to execute",
        },
        rebuild_at_end: {
          type: "boolean",
          description: "Rebuild once at end (default: true)",
        },
        disable_graphics: {
          type: "boolean",
          description: "Disable graphics during operations for speed (default: true)",
        },
      },
      required: ["operations"],
    },
  },
  {
    name: "sw_batch_properties",
    description: "Update multiple custom properties in one call (MUCH FASTER - 5x speedup). Use this instead of multiple sw_set_custom_property calls.",
    input_schema: {
      type: "object" as const,
      properties: {
        properties: {
          type: "object",
          description: "Property name -> value mapping",
        },
      },
      required: ["properties"],
    },
  },
  {
    name: "sw_batch_dimensions",
    description: "Update multiple dimensions in one call (FASTER). Use this when modifying multiple dimensions.",
    input_schema: {
      type: "object" as const,
      properties: {
        dimensions: {
          type: "object",
          description: "Dimension name -> value mapping (e.g., {'D1@Sketch1': 0.05})",
        },
      },
      required: ["dimensions"],
    },
  },
  {
    name: "sw_zoom_fit",
    description: "Zoom to fit all geometry in the view.",
    input_schema: {
      type: "object" as const,
      properties: {},
      required: [],
    },
  },
  {
    name: "sw_set_view",
    description: "Set the view orientation.",
    input_schema: {
      type: "object" as const,
      properties: {
        view: {
          type: "string",
          enum: ["front", "back", "top", "bottom", "left", "right", "isometric", "trimetric"],
          description: "Standard view orientation",
        },
      },
      required: ["view"],
    },
  },
  // === Advanced Mechanical Toolsets ===
  {
    name: "sw_create_plane_offset",
    description: "Create a reference plane at an offset distance from an existing plane or face in SolidWorks.",
    input_schema: {
      type: "object" as const,
      properties: {
        base_name: { type: "string", description: "Name of the base plane or face" },
        distance: { type: "number", description: "Offset distance in meters" },
        flip: { type: "boolean", description: "Flip the offset direction" },
      },
      required: ["base_name", "distance"],
    },
  },
  {
    name: "sw_hole_wizard",
    description: "Create a standardized hole using the SolidWorks Hole Wizard.",
    input_schema: {
      type: "object" as const,
      properties: {
        type: { type: "number", description: "0=Counterbore, 1=Countersink, 2=Hole, 3=Tap" },
        standard: { type: "number", description: "1=Ansi Inch, 0=Ansi Metric" },
        size: { type: "string", description: "Size string, e.g. '#10', '1/4', 'M5'" },
        depth: { type: "number", description: "Hole depth in meters" },
        x: { type: "number", description: "X coordinate for location (meters)" },
        y: { type: "number", description: "Y coordinate for location (meters)" },
      },
      required: ["size"],
    },
  },
  {
    name: "sw_sheet_metal_base",
    description: "Convert a sketch to a sheet metal base flange in SolidWorks.",
    input_schema: {
      type: "object" as const,
      properties: {
        thickness: { type: "number", description: "Sheet thickness (meters)" },
        radius: { type: "number", description: "Bend radius (meters)" },
        depth: { type: "number", description: "Extrusion depth (meters)" },
      },
      required: ["thickness"],
    },
  },
  {
    name: "sw_sheet_metal_edge_flange",
    description: "Add an edge flange to a sheet metal part in SolidWorks.",
    input_schema: {
      type: "object" as const,
      properties: {
        edge_index: { type: "number", description: "Index of the edge to attach to" },
        angle: { type: "number", description: "Flange angle in degrees" },
        length: { type: "number", description: "Flange length (meters)" },
      },
      required: ["edge_index"],
    },
  },
  {
    name: "inv_create_work_plane_offset",
    description: "Create a work plane at an offset distance from an existing plane or face in Inventor.",
    input_schema: {
      type: "object" as const,
      properties: {
        base_name: { type: "string", description: "Name of the base plane or face" },
        distance: { type: "number", description: "Offset distance in centimeters" },
      },
      required: ["base_name", "distance"],
    },
  },
  {
    name: "inv_hole",
    description: "Create a hole feature in Inventor.",
    input_schema: {
      type: "object" as const,
      properties: {
        size: { type: "string", description: "Hole size, e.g. '0.5 cm'" },
        depth: { type: "number", description: "Depth in centimeters" },
        x: { type: "number", description: "X pos (cm)" },
        y: { type: "number", description: "Y pos (cm)" },
      },
      required: ["size"],
    },
  },
  {
    name: "inv_sheet_metal_face",
    description: "Create a sheet metal face from a sketch in Inventor.",
    input_schema: {
      type: "object" as const,
      properties: {
        sketch_name: { type: "string", description: "Name of the sketch" },
      },
      required: ["sketch_name"],
    },
  },
  {
    name: "inv_sheet_metal_flange",
    description: "Create a sheet metal flange on an edge in Inventor.",
    input_schema: {
      type: "object" as const,
      properties: {
        edge_index: { type: "number", description: "Edge index" },
        angle: { type: "number", description: "Angle in degrees" },
        distance: { type: "number", description: "Flange length in cm" },
      },
      required: ["edge_index"],
    },
  },
  {
    name: "sw_add_configuration",
    description: "Add a new configuration to a SolidWorks part or assembly.",
    input_schema: {
      type: "object" as const,
      properties: {
        name: { type: "string", description: "Configuration name" },
        description: { type: "string", description: "Optional description" },
      },
      required: ["name"],
    },
  },
  {
    name: "sw_add_structural_member",
    description: "Add a weldment structural member to a SolidWorks part.",
    input_schema: {
      type: "object" as const,
      properties: {
        standard: { type: "string", description: "Standard (e.g., 'ansi inch')" },
        type: { type: "string", description: "Type (e.g., 'pipe')" },
        size: { type: "string", description: "Size (e.g., '0.5 skip sch 40')" },
        path_segments: { type: "array", items: { type: "string" }, description: "Sketch segment names" },
      },
      required: ["path_segments"],
    },
  },

  // === Routing (Pipe, Tube, Electrical) ===
  {
    name: "sw_create_pipe_route",
    description: "Create a pipe route between two points in SolidWorks. Requires Routing add-in.",
    input_schema: {
      type: "object" as const,
      properties: {
        start_point: { type: "array", items: { type: "number" }, description: "Start point [x, y, z] in meters" },
        end_point: { type: "array", items: { type: "number" }, description: "End point [x, y, z] in meters" },
        pipe_standard: { type: "string", description: "Pipe standard: ANSI, ISO, DIN" },
        pipe_size: { type: "string", description: "Nominal pipe size e.g., '2 inch'" },
        schedule: { type: "string", description: "Pipe schedule e.g., '40'" },
        bend_radius: { type: "number", description: "Bend radius in meters (optional)" },
      },
      required: ["start_point", "end_point"],
    },
  },
  {
    name: "sw_insert_fitting",
    description: "Insert a routing fitting (elbow, tee, flange, valve) at a position.",
    input_schema: {
      type: "object" as const,
      properties: {
        fitting_type: { type: "string", enum: ["elbow", "tee", "reducer", "flange", "valve", "cap", "coupling"], description: "Type of fitting" },
        position: { type: "array", items: { type: "number" }, description: "Position [x, y, z] in meters" },
        size: { type: "string", description: "Fitting size e.g., '2 inch'" },
        angle: { type: "number", description: "Angle for elbows (degrees)" },
      },
      required: ["fitting_type", "position"],
    },
  },
  {
    name: "sw_create_electrical_route",
    description: "Create electrical cable/wire route between connectors.",
    input_schema: {
      type: "object" as const,
      properties: {
        start_connector: { type: "string", description: "Start connector component name" },
        end_connector: { type: "string", description: "End connector component name" },
        cable_type: { type: "string", description: "Cable/wire type e.g., '18 AWG'" },
        bundle_diameter: { type: "number", description: "Bundle diameter in meters (optional)" },
      },
      required: ["start_connector", "end_connector"],
    },
  },
  {
    name: "sw_flatten_route",
    description: "Flatten route for manufacturing documentation.",
    input_schema: {
      type: "object" as const,
      properties: {},
      required: [],
    },
  },
  {
    name: "sw_get_route_properties",
    description: "Get routing properties (lengths, bend data, fittings).",
    input_schema: {
      type: "object" as const,
      properties: {},
      required: [],
    },
  },

  // === Weldments ===
  {
    name: "sw_insert_structural_member",
    description: "Insert weldment structural member along sketch path segments.",
    input_schema: {
      type: "object" as const,
      properties: {
        standard: { type: "string", description: "Standard: ansi inch, iso, din, jis" },
        profile_type: { type: "string", description: "Type: c channel, angle, pipe, square tube, i beam" },
        size: { type: "string", description: "Profile size designation e.g., 'C3 x 4.1'" },
        path_segments: { type: "array", items: { type: "string" }, description: "Names of sketch segments to follow" },
        corner_treatment: { type: "string", description: "Corner: miter, butt, cope, end cap" },
        apply_corner: { type: "boolean", description: "Apply corner treatment" },
      },
      required: ["path_segments"],
    },
  },
  {
    name: "sw_add_weld_bead",
    description: "Add weld bead between two faces.",
    input_schema: {
      type: "object" as const,
      properties: {
        weld_type: { type: "string", enum: ["fillet", "groove", "plug", "slot", "spot"], description: "Type of weld" },
        face1: { type: "string", description: "First face to weld" },
        face2: { type: "string", description: "Second face to weld" },
        size: { type: "number", description: "Weld size in meters (e.g., leg size for fillet)" },
        intermittent: { type: "boolean", description: "Intermittent weld pattern" },
        length: { type: "number", description: "Weld segment length if intermittent" },
        pitch: { type: "number", description: "Pitch between segments if intermittent" },
      },
      required: ["weld_type", "face1", "face2"],
    },
  },
  {
    name: "sw_trim_extend_member",
    description: "Trim or extend a structural member to another member or face.",
    input_schema: {
      type: "object" as const,
      properties: {
        member_to_trim: { type: "string", description: "Name of member to trim/extend" },
        trim_to: { type: "string", description: "Name of member or face to trim to" },
        operation: { type: "string", enum: ["trim", "extend"], description: "Operation type" },
      },
      required: ["member_to_trim", "trim_to"],
    },
  },
  {
    name: "sw_add_gusset",
    description: "Add gusset plate to structural corner.",
    input_schema: {
      type: "object" as const,
      properties: {
        vertex_point: { type: "array", items: { type: "number" }, description: "Corner vertex [x, y, z]" },
        thickness: { type: "number", description: "Gusset thickness in meters" },
        d1: { type: "number", description: "Length along member 1 in meters" },
        d2: { type: "number", description: "Length along member 2 in meters" },
      },
      required: ["vertex_point"],
    },
  },
  {
    name: "sw_add_end_cap",
    description: "Add end cap to structural member.",
    input_schema: {
      type: "object" as const,
      properties: {
        member_name: { type: "string", description: "Structural member name" },
        end: { type: "string", enum: ["start", "end", "both"], description: "Which end(s) to cap" },
        thickness: { type: "number", description: "End cap thickness in meters" },
        offset: { type: "number", description: "Offset from end in meters" },
      },
      required: ["member_name"],
    },
  },
  {
    name: "sw_get_weldment_cut_list",
    description: "Get weldment cut list with lengths and quantities.",
    input_schema: {
      type: "object" as const,
      properties: {},
      required: [],
    },
  },

  // === Sheet Metal (Full) ===
  {
    name: "sw_base_flange",
    description: "Create sheet metal base flange from sketch.",
    input_schema: {
      type: "object" as const,
      properties: {
        thickness: { type: "number", description: "Sheet thickness in meters" },
        bend_radius: { type: "number", description: "Default bend radius in meters" },
        depth: { type: "number", description: "Flange depth in meters" },
        direction: { type: "number", description: "0=one direction, 1=mid-plane, 2=both" },
      },
      required: ["thickness"],
    },
  },
  {
    name: "sw_edge_flange",
    description: "Add edge flange to sheet metal edge.",
    input_schema: {
      type: "object" as const,
      properties: {
        edge_name: { type: "string", description: "Edge to add flange to" },
        length: { type: "number", description: "Flange length in meters" },
        angle: { type: "number", description: "Flange angle in degrees" },
        gap: { type: "number", description: "Gap from adjacent flange in meters" },
        flange_position: { type: "string", enum: ["material_inside", "material_outside", "bend_outside"], description: "Flange position" },
      },
      required: ["edge_name"],
    },
  },
  {
    name: "sw_hem",
    description: "Add hem to sheet metal edge.",
    input_schema: {
      type: "object" as const,
      properties: {
        edge_name: { type: "string", description: "Edge to add hem to" },
        hem_type: { type: "string", enum: ["closed", "open", "teardrop", "rolled"], description: "Hem type" },
        gap: { type: "number", description: "Gap for open hem in meters" },
        length: { type: "number", description: "Custom hem length" },
      },
      required: ["edge_name"],
    },
  },
  {
    name: "sw_jog",
    description: "Add jog (offset bend) to sheet metal.",
    input_schema: {
      type: "object" as const,
      properties: {
        edge_name: { type: "string", description: "Edge for jog" },
        offset: { type: "number", description: "Jog offset distance in meters" },
        fixed_face: { type: "string", enum: ["top", "bottom"], description: "Fixed face" },
      },
      required: ["edge_name"],
    },
  },
  {
    name: "sw_lofted_bend",
    description: "Create lofted bend between two open profiles.",
    input_schema: {
      type: "object" as const,
      properties: {
        profile1: { type: "string", description: "First profile sketch name" },
        profile2: { type: "string", description: "Second profile sketch name" },
        faceted: { type: "boolean", description: "Faceted approximation" },
        num_bends: { type: "number", description: "Number of bends for faceted" },
      },
      required: ["profile1", "profile2"],
    },
  },
  {
    name: "sw_flat_pattern",
    description: "Generate or export flat pattern.",
    input_schema: {
      type: "object" as const,
      properties: {
        export: { type: "boolean", description: "Export to DXF/DWG" },
        export_path: { type: "string", description: "Export file path" },
        include_bend_lines: { type: "boolean", description: "Include bend lines in export" },
      },
      required: [],
    },
  },
  {
    name: "sw_corner_relief",
    description: "Add corner relief to sheet metal.",
    input_schema: {
      type: "object" as const,
      properties: {
        relief_type: { type: "string", enum: ["rectangular", "circular", "tear"], description: "Relief type" },
        relief_ratio: { type: "number", description: "Relief size ratio" },
      },
      required: [],
    },
  },
  {
    name: "sw_get_bend_table",
    description: "Get sheet metal bend table (K-factor, bend allowance).",
    input_schema: {
      type: "object" as const,
      properties: {},
      required: [],
    },
  },

  // === Drawing Tools (Full) ===
  {
    name: "sw_section_view",
    description: "Create section view in drawing.",
    input_schema: {
      type: "object" as const,
      properties: {
        parent_view: { type: "string", description: "Parent view name" },
        section_line_start: { type: "array", items: { type: "number" }, description: "Section line start [x, y]" },
        section_line_end: { type: "array", items: { type: "number" }, description: "Section line end [x, y]" },
        label: { type: "string", description: "Section label (A-A, B-B, etc.)" },
        scale: { type: "number", description: "View scale" },
        position: { type: "array", items: { type: "number" }, description: "View position on sheet [x, y]" },
      },
      required: ["parent_view", "section_line_start", "section_line_end", "position"],
    },
  },
  {
    name: "sw_detail_view",
    description: "Create detail view in drawing.",
    input_schema: {
      type: "object" as const,
      properties: {
        parent_view: { type: "string", description: "Parent view name" },
        center: { type: "array", items: { type: "number" }, description: "Detail center [x, y]" },
        radius: { type: "number", description: "Detail circle radius in meters" },
        scale: { type: "number", description: "Detail view scale" },
        label: { type: "string", description: "Detail label" },
        position: { type: "array", items: { type: "number" }, description: "View position on sheet [x, y]" },
      },
      required: ["parent_view", "center", "position"],
    },
  },
  {
    name: "sw_auxiliary_view",
    description: "Create auxiliary (projected) view.",
    input_schema: {
      type: "object" as const,
      properties: {
        parent_view: { type: "string", description: "Parent view name" },
        edge_name: { type: "string", description: "Hinge edge for projection" },
        position: { type: "array", items: { type: "number" }, description: "View position on sheet [x, y]" },
      },
      required: ["parent_view", "edge_name", "position"],
    },
  },
  {
    name: "sw_add_gdt",
    description: "Add GD&T (Geometric Dimensioning & Tolerancing) symbol.",
    input_schema: {
      type: "object" as const,
      properties: {
        feature_name: { type: "string", description: "Feature to attach GD&T" },
        symbol_type: { type: "string", enum: ["position", "flatness", "perpendicularity", "parallelism", "concentricity", "circularity", "cylindricity", "profile_surface", "profile_line", "runout", "total_runout", "angularity", "symmetry"], description: "GD&T symbol type" },
        tolerance: { type: "number", description: "Tolerance value in meters" },
        datum_refs: { type: "array", items: { type: "string" }, description: "Datum references [A, B, C]" },
        material_condition: { type: "string", enum: ["MMC", "LMC", "RFS"], description: "Material condition modifier" },
      },
      required: ["feature_name", "symbol_type", "tolerance"],
    },
  },
  {
    name: "sw_add_datum",
    description: "Add datum feature symbol.",
    input_schema: {
      type: "object" as const,
      properties: {
        edge_or_face: { type: "string", description: "Edge or face name" },
        label: { type: "string", description: "Datum label (A, B, C...)" },
      },
      required: ["edge_or_face", "label"],
    },
  },
  {
    name: "sw_add_surface_finish",
    description: "Add surface finish symbol.",
    input_schema: {
      type: "object" as const,
      properties: {
        face_name: { type: "string", description: "Face to apply symbol" },
        roughness_ra: { type: "number", description: "Surface roughness Ra in micrometers" },
        machining_required: { type: "boolean", description: "Machining required" },
        process: { type: "string", description: "Manufacturing process" },
      },
      required: ["face_name", "roughness_ra"],
    },
  },
  {
    name: "sw_add_weld_symbol",
    description: "Add welding symbol to drawing.",
    input_schema: {
      type: "object" as const,
      properties: {
        joint_edge: { type: "string", description: "Joint edge name" },
        weld_type: { type: "string", enum: ["fillet", "groove_v", "groove_u", "groove_j", "plug", "spot", "seam"], description: "Weld type" },
        size: { type: "number", description: "Weld size in meters" },
        arrow_side: { type: "boolean", description: "Weld on arrow side" },
        other_side: { type: "boolean", description: "Weld on other side" },
        all_around: { type: "boolean", description: "Weld all around" },
        field_weld: { type: "boolean", description: "Field weld" },
        tail_note: { type: "string", description: "Tail specification (e.g., A2.4)" },
      },
      required: ["joint_edge", "weld_type"],
    },
  },
  {
    name: "sw_auto_balloon",
    description: "Auto-balloon all components in view.",
    input_schema: {
      type: "object" as const,
      properties: {
        view_name: { type: "string", description: "View to balloon" },
        balloon_style: { type: "string", enum: ["circular", "triangle", "hexagon", "diamond"], description: "Balloon style" },
        leader_style: { type: "string", enum: ["straight", "bent"], description: "Leader style" },
        attach_to: { type: "string", enum: ["face", "edge"], description: "Attachment point" },
      },
      required: ["view_name"],
    },
  },
  {
    name: "sw_hole_table",
    description: "Insert hole table for a view.",
    input_schema: {
      type: "object" as const,
      properties: {
        view_name: { type: "string", description: "View containing holes" },
        origin: { type: "array", items: { type: "number" }, description: "Table origin [x, y]" },
        datum_origin: { type: "array", items: { type: "number" }, description: "Hole position datum [x, y]" },
      },
      required: ["view_name", "origin"],
    },
  },
  {
    name: "sw_bend_table",
    description: "Insert bend table for sheet metal drawing.",
    input_schema: {
      type: "object" as const,
      properties: {
        view_name: { type: "string", description: "Flat pattern view name" },
        table_position: { type: "array", items: { type: "number" }, description: "Table position [x, y]" },
      },
      required: ["view_name", "table_position"],
    },
  },
  {
    name: "sw_ordinate_dimensions",
    description: "Add ordinate dimension set.",
    input_schema: {
      type: "object" as const,
      properties: {
        view_name: { type: "string", description: "View name" },
        edges: { type: "array", items: { type: "string" }, description: "List of edge names to dimension" },
        origin_edge: { type: "string", description: "Origin edge (zero reference)" },
        direction: { type: "string", enum: ["horizontal", "vertical"], description: "Dimension direction" },
      },
      required: ["view_name", "edges", "origin_edge"],
    },
  },

  // === Simulation/FEA ===
  {
    name: "sw_create_simulation_study",
    description: "Create a simulation study.",
    input_schema: {
      type: "object" as const,
      properties: {
        study_name: { type: "string", description: "Study name" },
        study_type: { type: "string", enum: ["static", "frequency", "buckling", "thermal", "fatigue", "drop_test"], description: "Study type" },
      },
      required: ["study_name"],
    },
  },
  {
    name: "sw_add_fixture",
    description: "Apply fixture/restraint to simulation.",
    input_schema: {
      type: "object" as const,
      properties: {
        face_names: { type: "array", items: { type: "string" }, description: "Faces to fix" },
        fixture_type: { type: "string", enum: ["fixed", "roller", "hinge", "fixed_hinge", "symmetry"], description: "Fixture type" },
      },
      required: ["face_names"],
    },
  },
  {
    name: "sw_add_load",
    description: "Apply load to simulation.",
    input_schema: {
      type: "object" as const,
      properties: {
        face_names: { type: "array", items: { type: "string" }, description: "Faces to apply load" },
        load_type: { type: "string", enum: ["force", "pressure", "torque", "gravity", "centrifugal", "bearing"], description: "Load type" },
        value: { type: "number", description: "Load value (N, Pa, Nm, etc.)" },
        direction: { type: "array", items: { type: "number" }, description: "Direction vector [x, y, z]" },
      },
      required: ["face_names", "load_type", "value"],
    },
  },
  {
    name: "sw_create_mesh",
    description: "Configure and create mesh.",
    input_schema: {
      type: "object" as const,
      properties: {
        mesh_quality: { type: "string", enum: ["draft", "standard", "fine"], description: "Mesh quality" },
        element_size: { type: "number", description: "Element size in meters" },
      },
      required: [],
    },
  },
  {
    name: "sw_run_simulation",
    description: "Run simulation analysis.",
    input_schema: {
      type: "object" as const,
      properties: {
        study_name: { type: "string", description: "Study to run" },
      },
      required: ["study_name"],
    },
  },
  {
    name: "sw_get_simulation_results",
    description: "Get simulation results (stress, displacement, FOS).",
    input_schema: {
      type: "object" as const,
      properties: {
        study_name: { type: "string", description: "Study name" },
      },
      required: ["study_name"],
    },
  },

  // === Design Tables & Equations ===
  {
    name: "sw_add_equation",
    description: "Add or modify equation in SolidWorks.",
    input_schema: {
      type: "object" as const,
      properties: {
        equation: { type: "string", description: "Equation string, e.g., 'D1@Sketch1 = D2@Sketch2 * 2'" },
      },
      required: ["equation"],
    },
  },
  {
    name: "sw_add_global_variable",
    description: "Add global variable.",
    input_schema: {
      type: "object" as const,
      properties: {
        name: { type: "string", description: "Variable name" },
        value: { type: "number", description: "Variable value" },
        unit: { type: "string", description: "Unit (mm, in, deg, etc.)" },
      },
      required: ["name", "value"],
    },
  },
  {
    name: "sw_list_equations",
    description: "List all equations and global variables.",
    input_schema: {
      type: "object" as const,
      properties: {},
      required: [],
    },
  },
  {
    name: "sw_insert_design_table",
    description: "Insert or update design table.",
    input_schema: {
      type: "object" as const,
      properties: {
        excel_path: { type: "string", description: "Path to Excel file (optional, auto-create if empty)" },
        edit_mode: { type: "string", enum: ["auto", "manual"], description: "Edit mode" },
      },
      required: [],
    },
  },

  // === Toolbox ===
  {
    name: "sw_insert_toolbox_part",
    description: "Insert Toolbox standard part (bolt, nut, washer, pin, etc.).",
    input_schema: {
      type: "object" as const,
      properties: {
        standard: { type: "string", enum: ["ANSI Inch", "ANSI Metric", "ISO", "DIN", "JIS", "BSI", "GB"], description: "Standard" },
        category: { type: "string", description: "Category: Bolts and Screws, Nuts, Washers, Pins, etc." },
        part_type: { type: "string", description: "Part type: Hex Bolt, Socket Head Cap Screw, etc." },
        size: { type: "string", description: "Size designation: 1/4-20, M6x1.0, etc." },
        length: { type: "number", description: "Length for fasteners in meters" },
      },
      required: ["category", "part_type", "size"],
    },
  },
  {
    name: "sw_smart_fasteners",
    description: "Auto-insert smart fasteners for all holes.",
    input_schema: {
      type: "object" as const,
      properties: {
        hole_series: { type: "boolean", description: "Include hole series" },
        add_washers: { type: "boolean", description: "Add washers" },
        add_nuts: { type: "boolean", description: "Add nuts where applicable" },
      },
      required: [],
    },
  },
  {
    name: "sw_list_toolbox_standards",
    description: "List available Toolbox standards and categories.",
    input_schema: {
      type: "object" as const,
      properties: {},
      required: [],
    },
  },

  // === Surface Modeling ===
  {
    name: "sw_extruded_surface",
    description: "Create extruded surface.",
    input_schema: {
      type: "object" as const,
      properties: {
        profile: { type: "string", description: "Profile sketch name" },
        depth: { type: "number", description: "Extrusion depth in meters" },
        direction: { type: "number", description: "0=one direction, 1=both" },
      },
      required: ["profile"],
    },
  },
  {
    name: "sw_lofted_surface",
    description: "Create lofted surface.",
    input_schema: {
      type: "object" as const,
      properties: {
        profiles: { type: "array", items: { type: "string" }, description: "List of profile sketch names" },
        guide_curves: { type: "array", items: { type: "string" }, description: "Guide curve sketches (optional)" },
      },
      required: ["profiles"],
    },
  },
  {
    name: "sw_filled_surface",
    description: "Create filled (patch) surface.",
    input_schema: {
      type: "object" as const,
      properties: {
        boundary_edges: { type: "array", items: { type: "string" }, description: "Boundary edge names" },
        constraint_type: { type: "string", enum: ["contact", "tangent", "curvature"], description: "Constraint type" },
      },
      required: ["boundary_edges"],
    },
  },
  {
    name: "sw_offset_surface",
    description: "Create offset surface.",
    input_schema: {
      type: "object" as const,
      properties: {
        surface_face: { type: "string", description: "Face to offset" },
        distance: { type: "number", description: "Offset distance in meters" },
      },
      required: ["surface_face", "distance"],
    },
  },
  {
    name: "sw_trim_surface",
    description: "Trim surface with another surface or sketch.",
    input_schema: {
      type: "object" as const,
      properties: {
        surface_to_trim: { type: "string", description: "Surface face to trim" },
        trim_tool: { type: "string", description: "Trimming surface or sketch" },
        keep_inside: { type: "boolean", description: "Keep inside of trim boundary" },
      },
      required: ["surface_to_trim", "trim_tool"],
    },
  },
  {
    name: "sw_knit_surfaces",
    description: "Knit surfaces together.",
    input_schema: {
      type: "object" as const,
      properties: {
        surfaces: { type: "array", items: { type: "string" }, description: "Surface face names to knit" },
        create_solid: { type: "boolean", description: "Create solid if closed volume" },
        merge_entities: { type: "boolean", description: "Merge faces" },
      },
      required: ["surfaces"],
    },
  },

  // === Mold Tools ===
  {
    name: "sw_parting_line",
    description: "Create parting line for mold.",
    input_schema: {
      type: "object" as const,
      properties: {
        pull_direction: { type: "array", items: { type: "number" }, description: "Pull direction [x, y, z]" },
        draft_angle: { type: "number", description: "Minimum draft angle in degrees" },
      },
      required: [],
    },
  },
  {
    name: "sw_parting_surface",
    description: "Create parting surface.",
    input_schema: {
      type: "object" as const,
      properties: {
        parting_line_feature: { type: "string", description: "Parting line feature name" },
        surface_type: { type: "string", enum: ["perpendicular", "parallel", "ruled"], description: "Surface type" },
        distance: { type: "number", description: "Surface extension distance in meters" },
      },
      required: ["parting_line_feature"],
    },
  },
  {
    name: "sw_core_cavity",
    description: "Split core and cavity.",
    input_schema: {
      type: "object" as const,
      properties: {
        parting_surface: { type: "string", description: "Parting surface feature name" },
        core_block: { type: "string", description: "Core block body name" },
        cavity_block: { type: "string", description: "Cavity block body name" },
      },
      required: ["parting_surface", "core_block", "cavity_block"],
    },
  },
  {
    name: "sw_draft_analysis",
    description: "Analyze draft for moldability.",
    input_schema: {
      type: "object" as const,
      properties: {
        pull_direction: { type: "string", description: "Pull direction as comma-separated values '0,0,1'" },
        draft_angle: { type: "number", description: "Minimum draft angle in degrees" },
      },
      required: [],
    },
  },

  // === Costing ===
  {
    name: "sw_run_costing",
    description: "Run costing analysis.",
    input_schema: {
      type: "object" as const,
      properties: {
        template: { type: "string", enum: ["machining", "sheet_metal", "casting", "3d_printing", "weldment"], description: "Costing template" },
        material_cost_per_kg: { type: "number", description: "Material cost per kg" },
        labor_rate: { type: "number", description: "Labor rate per hour" },
      },
      required: [],
    },
  },
  {
    name: "sw_get_costing_operations",
    description: "Get manufacturing operations for costing.",
    input_schema: {
      type: "object" as const,
      properties: {},
      required: [],
    },
  },

  // === Motion Studies ===
  {
    name: "sw_create_motion_study",
    description: "Create motion study.",
    input_schema: {
      type: "object" as const,
      properties: {
        study_name: { type: "string", description: "Motion study name" },
        study_type: { type: "string", enum: ["animation", "basic_motion", "motion_analysis"], description: "Study type" },
      },
      required: [],
    },
  },
  {
    name: "sw_add_motor",
    description: "Add motor to motion study.",
    input_schema: {
      type: "object" as const,
      properties: {
        component: { type: "string", description: "Component to apply motor to" },
        motor_type: { type: "string", enum: ["rotary", "linear"], description: "Motor type" },
        rpm: { type: "number", description: "RPM for rotary or mm/s for linear" },
      },
      required: ["component"],
    },
  },
  {
    name: "sw_run_motion_study",
    description: "Run motion study.",
    input_schema: {
      type: "object" as const,
      properties: {
        study_name: { type: "string", description: "Study name" },
        duration: { type: "number", description: "Duration in seconds" },
      },
      required: ["study_name"],
    },
  },
  {
    name: "sw_export_motion_video",
    description: "Export motion study as video.",
    input_schema: {
      type: "object" as const,
      properties: {
        study_name: { type: "string", description: "Study name" },
        output_path: { type: "string", description: "Output video path" },
        fps: { type: "number", description: "Frames per second" },
      },
      required: ["study_name", "output_path"],
    },
  },
];

/**
 * Execute a CAD tool by calling the Desktop Server
 */
export async function executeCADTool(
  toolName: string,
  toolInput: Record<string, unknown>
): Promise<{ success: boolean; result?: unknown; error?: string }> {

  // Map tool names to Desktop Server endpoints
  const endpointMap: Record<string, { method: string; endpoint: string }> = {
    sw_connect: { method: "POST", endpoint: "/com/solidworks/connect" },
    sw_status: { method: "GET", endpoint: "/com/solidworks/status" },
    sw_new_part: { method: "POST", endpoint: "/com/solidworks/new_part" },
    sw_new_assembly: { method: "POST", endpoint: "/com/solidworks/new_assembly" },
    sw_open: { method: "POST", endpoint: "/com/solidworks/open" },
    sw_save: { method: "POST", endpoint: "/com/solidworks/save" },
    sw_export: { method: "POST", endpoint: "/com/solidworks/export" },
    sw_create_sketch: { method: "POST", endpoint: "/com/solidworks/create_sketch" },
    sw_close_sketch: { method: "POST", endpoint: "/com/solidworks/close_sketch" },
    sw_edit_sketch: { method: "POST", endpoint: "/com/solidworks/edit_sketch" },
    sw_get_sketch_info: { method: "GET", endpoint: "/com/solidworks/get_sketch_info" },
    sw_open_component: { method: "POST", endpoint: "/com/solidworks/open_component" },
    sw_draw_circle: { method: "POST", endpoint: "/com/solidworks/draw_circle" },
    sw_draw_rectangle: { method: "POST", endpoint: "/com/solidworks/draw_rectangle" },
    sw_draw_line: { method: "POST", endpoint: "/com/solidworks/draw_line" },
    sw_extrude: { method: "POST", endpoint: "/com/solidworks/extrude" },
    sw_extrude_cut: { method: "POST", endpoint: "/com/solidworks/extrude_cut" },
    sw_revolve: { method: "POST", endpoint: "/com/solidworks/revolve" },
    sw_fillet: { method: "POST", endpoint: "/com/solidworks/fillet" },
    sw_chamfer: { method: "POST", endpoint: "/com/solidworks/chamfer" },
    sw_pattern_circular: { method: "POST", endpoint: "/com/solidworks/pattern_circular" },
    sw_pattern_linear: { method: "POST", endpoint: "/com/solidworks/pattern_linear" },
    sw_select_face: { method: "POST", endpoint: "/com/solidworks/select_face" },
    sw_select_edge: { method: "POST", endpoint: "/com/solidworks/select_edge" },
    sw_clear_selection: { method: "POST", endpoint: "/com/solidworks/clear_selection" },
    sw_insert_component: { method: "POST", endpoint: "/com/solidworks/insert_component" },
    sw_add_mate: { method: "POST", endpoint: "/com/solidworks/add_mate" },
    sw_screenshot: { method: "POST", endpoint: "/screen/screenshot" },
    sw_screenshot_window: { method: "POST", endpoint: "/screen/window/SolidWorks" },
    sw_screenshot_viewport: { method: "POST", endpoint: "/com/solidworks/screenshot_viewport" },
    sw_screenshot_feature_tree: { method: "POST", endpoint: "/com/solidworks/screenshot_feature_tree" },
    sw_screenshot_property_manager: { method: "POST", endpoint: "/com/solidworks/screenshot_property_manager" },
    sw_capture_multi_view: { method: "POST", endpoint: "/cad/vision/multi-view" },
    sw_extract_dimensions_screenshot: { method: "POST", endpoint: "/cad/vision/extract-dimensions" },
    sw_detect_gdt_symbols: { method: "POST", endpoint: "/cad/vision/detect-gdt-symbols" },
    sw_detect_annotations: { method: "POST", endpoint: "/cad/vision/detect-annotations" },
    sw_extract_bom_screenshot: { method: "POST", endpoint: "/cad/vision/extract-bom" },
    sw_analyze_drawing_sheet: { method: "POST", endpoint: "/cad/vision/analyze-drawing-sheet" },
    sw_compare_screenshots: { method: "POST", endpoint: "/screen/compare" },
    sw_batch_operations: { method: "POST", endpoint: "/com/solidworks/batch/execute" },
    sw_batch_properties: { method: "POST", endpoint: "/com/solidworks/batch/properties" },
    sw_batch_dimensions: { method: "POST", endpoint: "/com/solidworks/batch/dimensions" },
    sw_zoom_fit: { method: "POST", endpoint: "/com/solidworks/zoom_fit" },
    sw_set_view: { method: "POST", endpoint: "/com/solidworks/set_view" },
    // SolidWorks Advanced Features
    sw_loft: { method: "POST", endpoint: "/com/solidworks/loft" },
    sw_sweep: { method: "POST", endpoint: "/com/solidworks/sweep" },
    sw_shell: { method: "POST", endpoint: "/com/solidworks/shell" },
    sw_mirror: { method: "POST", endpoint: "/com/solidworks/mirror" },
    // SolidWorks Advanced Sketching
    sw_draw_spline: { method: "POST", endpoint: "/com/solidworks/draw_spline" },
    sw_draw_polygon: { method: "POST", endpoint: "/com/solidworks/draw_polygon" },
    sw_draw_ellipse: { method: "POST", endpoint: "/com/solidworks/draw_ellipse" },
    sw_add_sketch_constraint: { method: "POST", endpoint: "/com/solidworks/add_sketch_constraint" },
    sw_add_sketch_dimension: { method: "POST", endpoint: "/com/solidworks/add_sketch_dimension" },
    // SolidWorks Drawings
    sw_new_drawing: { method: "POST", endpoint: "/com/solidworks/drawings/new_drawing" },
    sw_create_drawing_view: { method: "POST", endpoint: "/com/solidworks/drawings/create_view" },
    sw_add_drawing_dimension: { method: "POST", endpoint: "/com/solidworks/drawings/add_dimension" },
    sw_add_drawing_note: { method: "POST", endpoint: "/com/solidworks/drawings/add_note" },
    sw_add_bom: { method: "POST", endpoint: "/com/solidworks/drawings/add_bom" },
    sw_get_bom: { method: "GET", endpoint: "/com/solidworks/get_bom" },
    sw_get_bom_pdf: { method: "GET", endpoint: "/com/solidworks/get_bom_pdf" },
    sw_get_spatial_positions: { method: "GET", endpoint: "/com/solidworks/get_spatial_positions" },
    sw_analyze_assembly: { method: "GET", endpoint: "/com/solidworks/analysis/analyze" },
    sw_edit_title_block: { method: "POST", endpoint: "/com/solidworks/drawings/edit_title_block" },
    sw_add_revision_table: { method: "POST", endpoint: "/com/solidworks/drawings/add_revision_table" },
    sw_add_revision: { method: "POST", endpoint: "/com/solidworks/drawings/add_revision" },
    sw_add_balloon: { method: "POST", endpoint: "/com/solidworks/drawings/add_balloon" },
    sw_add_sheet: { method: "POST", endpoint: "/com/solidworks/drawings/add_sheet" },
    sw_set_view_properties: { method: "POST", endpoint: "/com/solidworks/drawings/set_view_properties" },
    sw_add_centerline: { method: "POST", endpoint: "/com/solidworks/drawings/add_centerline" },
    sw_add_center_mark: { method: "POST", endpoint: "/com/solidworks/drawings/add_center_mark" },
    sw_add_hatching: { method: "POST", endpoint: "/com/solidworks/drawings/add_hatching" },
    sw_add_table: { method: "POST", endpoint: "/com/solidworks/drawings/add_table" },
    sw_add_leader_line: { method: "POST", endpoint: "/com/solidworks/drawings/add_leader_line" },
    // Inventor iMates
    inv_create_imates_for_assembly: { method: "POST", endpoint: "/com/inventor/imates/create_imates" },
    inv_create_composite_imates: { method: "POST", endpoint: "/com/inventor/imates/create_composite_imates" },
    inv_verify_hole_alignment: { method: "POST", endpoint: "/com/inventor/imates/verify_alignment" },
    // SolidWorks Mate References
    sw_create_mate_refs_for_assembly: { method: "POST", endpoint: "/com/solidworks/mate_references/create_mate_refs" },
    sw_verify_hole_alignment: { method: "POST", endpoint: "/com/solidworks/mate_references/verify_alignment" },
    // Inventor Basic Operations
    inv_connect: { method: "POST", endpoint: "/com/inventor/connect" },
    inv_status: { method: "GET", endpoint: "/com/inventor/status" },
    inv_new_part: { method: "POST", endpoint: "/com/inventor/new_part" },
    inv_save: { method: "POST", endpoint: "/com/inventor/save" },
    // Inventor Sketching
    inv_create_sketch: { method: "POST", endpoint: "/com/inventor/create_sketch" },
    inv_draw_circle: { method: "POST", endpoint: "/com/inventor/draw_circle" },
    inv_draw_rectangle: { method: "POST", endpoint: "/com/inventor/draw_rectangle" },
    inv_draw_line: { method: "POST", endpoint: "/com/inventor/draw_line" },
    inv_draw_arc: { method: "POST", endpoint: "/com/inventor/draw_arc" },
    // Inventor Features
    inv_extrude: { method: "POST", endpoint: "/com/inventor/extrude" },
    inv_revolve: { method: "POST", endpoint: "/com/inventor/revolve" },
    inv_fillet: { method: "POST", endpoint: "/com/inventor/fillet" },
    // Inventor File Operations
    inv_open: { method: "POST", endpoint: "/com/inventor/open" },
    inv_export: { method: "POST", endpoint: "/com/inventor/export" },
    // Inventor Advanced Features
    inv_loft: { method: "POST", endpoint: "/com/inventor/loft" },
    inv_sweep: { method: "POST", endpoint: "/com/inventor/sweep" },
    inv_shell: { method: "POST", endpoint: "/com/inventor/shell" },
    inv_mirror: { method: "POST", endpoint: "/com/inventor/mirror" },
    // Inventor Advanced Sketching
    inv_draw_spline: { method: "POST", endpoint: "/com/inventor/draw_spline" },
    inv_draw_polygon: { method: "POST", endpoint: "/com/inventor/draw_polygon" },
    inv_draw_ellipse: { method: "POST", endpoint: "/com/inventor/draw_ellipse" },
    inv_add_sketch_constraint: { method: "POST", endpoint: "/com/inventor/add_sketch_constraint" },
    inv_add_sketch_dimension: { method: "POST", endpoint: "/com/inventor/add_sketch_dimension" },
    // Inventor Drawings
    inv_new_drawing: { method: "POST", endpoint: "/com/inventor/drawings/new_drawing" },
    inv_create_drawing_view: { method: "POST", endpoint: "/com/inventor/drawings/create_view" },
    inv_add_drawing_dimension: { method: "POST", endpoint: "/com/inventor/drawings/add_dimension" },
    inv_add_drawing_note: { method: "POST", endpoint: "/com/inventor/drawings/add_note" },
    inv_add_bom: { method: "POST", endpoint: "/com/inventor/drawings/add_bom" },
    inv_edit_title_block: { method: "POST", endpoint: "/com/inventor/drawings/edit_title_block" },
    inv_add_revision_table: { method: "POST", endpoint: "/com/inventor/drawings/add_revision_table" },
    inv_add_revision: { method: "POST", endpoint: "/com/inventor/drawings/add_revision" },
    inv_add_balloon: { method: "POST", endpoint: "/com/inventor/drawings/add_balloon" },
    inv_add_sheet: { method: "POST", endpoint: "/com/inventor/drawings/add_sheet" },
    inv_set_view_properties: { method: "POST", endpoint: "/com/inventor/drawings/set_view_properties" },
    inv_add_centerline: { method: "POST", endpoint: "/com/inventor/drawings/add_centerline" },
    inv_add_center_mark: { method: "POST", endpoint: "/com/inventor/drawings/add_center_mark" },
    inv_add_hatching: { method: "POST", endpoint: "/com/inventor/drawings/add_hatching" },
    inv_add_table: { method: "POST", endpoint: "/com/inventor/drawings/add_table" },
    inv_add_leader_line: { method: "POST", endpoint: "/com/inventor/drawings/add_leader_line" },
    // Inventor Assembly
    inv_new_assembly: { method: "POST", endpoint: "/com/inventor/new_assembly" },
    inv_insert_component: { method: "POST", endpoint: "/com/inventor/insert_component" },
    inv_add_joint: { method: "POST", endpoint: "/com/inventor/add_joint" },
    inv_pattern_component: { method: "POST", endpoint: "/com/inventor/pattern_component" },
    inv_create_exploded_view: { method: "POST", endpoint: "/com/inventor/create_exploded_view" },
    inv_move_component: { method: "POST", endpoint: "/com/inventor/move_component" },
    inv_suppress_component: { method: "POST", endpoint: "/com/inventor/suppress_component" },
    inv_set_component_visibility: { method: "POST", endpoint: "/com/inventor/set_component_visibility" },
    inv_replace_component: { method: "POST", endpoint: "/com/inventor/replace_component" },
    inv_check_interference: { method: "POST", endpoint: "/com/inventor/check_interference" },
    inv_zoom_fit: { method: "POST", endpoint: "/com/inventor/zoom_fit" },
    inv_set_view: { method: "POST", endpoint: "/com/inventor/set_view" },
    inv_chamfer: { method: "POST", endpoint: "/com/inventor/chamfer" },
    inv_pattern_circular: { method: "POST", endpoint: "/com/inventor/pattern_circular" },
    inv_pattern_linear: { method: "POST", endpoint: "/com/inventor/pattern_linear" },
    inv_draft: { method: "POST", endpoint: "/com/inventor/draft" },
    inv_rib: { method: "POST", endpoint: "/com/inventor/rib" },
    inv_combine_bodies: { method: "POST", endpoint: "/com/inventor/combine_bodies" },
    inv_split_body: { method: "POST", endpoint: "/com/inventor/split_body" },
    inv_move_copy_body: { method: "POST", endpoint: "/com/inventor/move_copy_body" },
    inv_set_material: { method: "POST", endpoint: "/com/inventor/set_material" },
    inv_get_mass_properties: { method: "POST", endpoint: "/com/inventor/get_mass_properties" },
    sw_set_custom_property: { method: "POST", endpoint: "/com/solidworks/set_custom_property" },
    inv_set_custom_property: { method: "POST", endpoint: "/com/inventor/set_custom_property" },
    // Advanced Tools
    sw_create_plane_offset: { method: "POST", endpoint: "/com/solidworks/create_plane_offset" },
    sw_hole_wizard: { method: "POST", endpoint: "/com/solidworks/hole_wizard" },
    sw_sheet_metal_base: { method: "POST", endpoint: "/com/solidworks/sheet_metal_base" },
    sw_sheet_metal_edge_flange: { method: "POST", endpoint: "/com/solidworks/sheet_metal_edge_flange" },
    inv_create_work_plane_offset: { method: "POST", endpoint: "/com/inventor/create_work_plane_offset" },
    inv_hole: { method: "POST", endpoint: "/com/inventor/hole" },
    inv_sheet_metal_face: { method: "POST", endpoint: "/com/inventor/sheet_metal_face" },
    inv_sheet_metal_flange: { method: "POST", endpoint: "/com/inventor/sheet_metal_flange" },
    sw_add_configuration: { method: "POST", endpoint: "/com/solidworks/add_configuration" },
    sw_add_structural_member: { method: "POST", endpoint: "/com/solidworks/add_structural_member" },
  };

  const mapping = endpointMap[toolName];
  if (!mapping) {
    return { success: false, error: `Unknown tool: ${toolName}` };
  }

  try {
    // Handle path parameters (e.g., /screen/window/{window_title})
    let url = `${DESKTOP_URL}${mapping.endpoint}`;
    if (mapping.endpoint.includes("{window_title}")) {
      const windowTitle = (toolInput.window_title as string) || "SolidWorks";
      url = url.replace("{window_title}", windowTitle);
    }
    
    const options: RequestInit = {
      method: mapping.method,
      headers: { "Content-Type": "application/json" },
    };

    if (mapping.method === "POST" && Object.keys(toolInput).length > 0) {
      // Don't include path parameters in body
      const bodyInput = { ...toolInput };
      delete bodyInput.window_title;
      if (Object.keys(bodyInput).length > 0) {
        options.body = JSON.stringify(bodyInput);
      }
    }

    console.log(`[CAD Tool] Executing ${toolName} -> ${url}`);
    const response = await fetch(url, options);

    if (!response.ok) {
      const errorText = await response.text();
      return { success: false, error: `HTTP ${response.status}: ${errorText}` };
    }

    const result = await response.json();
    return { success: true, result };

  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    console.error(`[CAD Tool] Error executing ${toolName}:`, errorMessage);
    return { success: false, error: errorMessage };
  }
}

/**
 * Format tool result for Claude
 */
export function formatToolResult(
  toolName: string,
  result: { success: boolean; result?: unknown; error?: string }
): string {
  if (result.success) {
    return JSON.stringify({
      status: "success",
      tool: toolName,
      data: result.result,
    });
  } else {
    return JSON.stringify({
      status: "error",
      tool: toolName,
      error: result.error,
    });
  }
}
