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

  // === Utilities ===
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
    sw_zoom_fit: { method: "POST", endpoint: "/com/solidworks/zoom_fit" },
    sw_set_view: { method: "POST", endpoint: "/com/solidworks/set_view" },
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
    // Inventor Assembly
    inv_new_assembly: { method: "POST", endpoint: "/com/inventor/new_assembly" },
    inv_insert_component: { method: "POST", endpoint: "/com/inventor/insert_component" },
    inv_add_joint: { method: "POST", endpoint: "/com/inventor/add_joint" },
  };

  const mapping = endpointMap[toolName];
  if (!mapping) {
    return { success: false, error: `Unknown tool: ${toolName}` };
  }

  try {
    const url = `${DESKTOP_URL}${mapping.endpoint}`;
    const options: RequestInit = {
      method: mapping.method,
      headers: { "Content-Type": "application/json" },
    };

    if (mapping.method === "POST" && Object.keys(toolInput).length > 0) {
      options.body = JSON.stringify(toolInput);
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
