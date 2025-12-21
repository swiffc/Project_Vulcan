/**
 * CAD Strategy Recipes
 *
 * Pre-built patterns for common CAD operations.
 * Used by the chatbot to understand how to build common parts.
 */

export interface RecipeStep {
  tool: string;
  description: string;
  params: Record<string, unknown>;
}

export interface CADRecipe {
  name: string;
  description: string;
  category: "part" | "assembly" | "feature";
  requiredInputs: string[];
  steps: RecipeStep[];
}

/**
 * Common part recipes
 */
export const PART_RECIPES: CADRecipe[] = [
  // === BASIC SHAPES ===
  {
    name: "cylinder",
    description: "Simple cylinder with specified diameter and height",
    category: "part",
    requiredInputs: ["diameter", "height"],
    steps: [
      { tool: "sw_connect", description: "Connect to SolidWorks", params: {} },
      { tool: "sw_new_part", description: "Create new part", params: {} },
      { tool: "sw_create_sketch", description: "Start sketch on Front plane", params: { plane: "Front" } },
      { tool: "sw_draw_circle", description: "Draw circle at origin", params: { x: 0, y: 0, radius: "${diameter/2}" } },
      { tool: "sw_close_sketch", description: "Exit sketch", params: {} },
      { tool: "sw_extrude", description: "Extrude to height", params: { depth: "${height}" } },
      { tool: "sw_zoom_fit", description: "Zoom to fit", params: {} },
      { tool: "sw_set_view", description: "Set isometric view", params: { view: "isometric" } },
    ],
  },

  {
    name: "rectangular_block",
    description: "Rectangular block with width, depth, and height",
    category: "part",
    requiredInputs: ["width", "depth", "height"],
    steps: [
      { tool: "sw_connect", description: "Connect to SolidWorks", params: {} },
      { tool: "sw_new_part", description: "Create new part", params: {} },
      { tool: "sw_create_sketch", description: "Start sketch on Top plane", params: { plane: "Top" } },
      { tool: "sw_draw_rectangle", description: "Draw centered rectangle", params: { x1: "${-width/2}", y1: "${-depth/2}", x2: "${width/2}", y2: "${depth/2}" } },
      { tool: "sw_close_sketch", description: "Exit sketch", params: {} },
      { tool: "sw_extrude", description: "Extrude to height", params: { depth: "${height}" } },
      { tool: "sw_zoom_fit", description: "Zoom to fit", params: {} },
      { tool: "sw_set_view", description: "Set isometric view", params: { view: "isometric" } },
    ],
  },

  // === COMMON PARTS ===
  {
    name: "flange",
    description: "Circular flange with center hole and bolt pattern",
    category: "part",
    requiredInputs: ["outer_diameter", "thickness", "center_hole_diameter", "bolt_circle_diameter", "bolt_hole_diameter", "bolt_count"],
    steps: [
      { tool: "sw_connect", description: "Connect to SolidWorks", params: {} },
      { tool: "sw_new_part", description: "Create new part", params: {} },
      // Base disc
      { tool: "sw_create_sketch", description: "Sketch outer circle on Front", params: { plane: "Front" } },
      { tool: "sw_draw_circle", description: "Draw outer diameter", params: { x: 0, y: 0, radius: "${outer_diameter/2}" } },
      { tool: "sw_close_sketch", description: "Exit sketch", params: {} },
      { tool: "sw_extrude", description: "Extrude thickness", params: { depth: "${thickness}" } },
      // Center hole
      { tool: "sw_create_sketch", description: "Sketch center hole", params: { plane: "Front" } },
      { tool: "sw_draw_circle", description: "Draw center hole", params: { x: 0, y: 0, radius: "${center_hole_diameter/2}" } },
      { tool: "sw_close_sketch", description: "Exit sketch", params: {} },
      { tool: "sw_extrude_cut", description: "Cut through all", params: { depth: 999 } },
      // Bolt holes
      { tool: "sw_create_sketch", description: "Sketch first bolt hole", params: { plane: "Front" } },
      { tool: "sw_draw_circle", description: "Draw bolt hole on bolt circle", params: { x: "${bolt_circle_diameter/2}", y: 0, radius: "${bolt_hole_diameter/2}" } },
      { tool: "sw_close_sketch", description: "Exit sketch", params: {} },
      { tool: "sw_extrude_cut", description: "Cut through", params: { depth: 999 } },
      { tool: "sw_pattern_circular", description: "Pattern bolt holes", params: { count: "${bolt_count}", spacing: 6.283185 } },
      { tool: "sw_zoom_fit", description: "Zoom to fit", params: {} },
      { tool: "sw_set_view", description: "Set isometric view", params: { view: "isometric" } },
    ],
  },

  {
    name: "shaft",
    description: "Simple shaft with optional keyway",
    category: "part",
    requiredInputs: ["diameter", "length"],
    steps: [
      { tool: "sw_connect", description: "Connect to SolidWorks", params: {} },
      { tool: "sw_new_part", description: "Create new part", params: {} },
      { tool: "sw_create_sketch", description: "Sketch circle on Front", params: { plane: "Front" } },
      { tool: "sw_draw_circle", description: "Draw shaft diameter", params: { x: 0, y: 0, radius: "${diameter/2}" } },
      { tool: "sw_close_sketch", description: "Exit sketch", params: {} },
      { tool: "sw_extrude", description: "Extrude length", params: { depth: "${length}" } },
      { tool: "sw_zoom_fit", description: "Zoom to fit", params: {} },
      { tool: "sw_set_view", description: "Set isometric view", params: { view: "isometric" } },
    ],
  },

  {
    name: "l_bracket",
    description: "L-shaped bracket with specified dimensions",
    category: "part",
    requiredInputs: ["vertical_leg", "horizontal_leg", "thickness", "width"],
    steps: [
      { tool: "sw_connect", description: "Connect to SolidWorks", params: {} },
      { tool: "sw_new_part", description: "Create new part", params: {} },
      { tool: "sw_create_sketch", description: "Sketch L-profile on Front", params: { plane: "Front" } },
      // Draw L-shape using lines
      { tool: "sw_draw_line", description: "Bottom horizontal", params: { x1: 0, y1: 0, x2: "${horizontal_leg}", y2: 0 } },
      { tool: "sw_draw_line", description: "Right vertical up", params: { x1: "${horizontal_leg}", y1: 0, x2: "${horizontal_leg}", y2: "${thickness}" } },
      { tool: "sw_draw_line", description: "Inner horizontal", params: { x1: "${horizontal_leg}", y1: "${thickness}", x2: "${thickness}", y2: "${thickness}" } },
      { tool: "sw_draw_line", description: "Inner vertical", params: { x1: "${thickness}", y1: "${thickness}", x2: "${thickness}", y2: "${vertical_leg}" } },
      { tool: "sw_draw_line", description: "Top horizontal", params: { x1: "${thickness}", y1: "${vertical_leg}", x2: 0, y2: "${vertical_leg}" } },
      { tool: "sw_draw_line", description: "Left vertical down", params: { x1: 0, y1: "${vertical_leg}", x2: 0, y2: 0 } },
      { tool: "sw_close_sketch", description: "Exit sketch", params: {} },
      { tool: "sw_extrude", description: "Extrude width", params: { depth: "${width}" } },
      { tool: "sw_zoom_fit", description: "Zoom to fit", params: {} },
      { tool: "sw_set_view", description: "Set isometric view", params: { view: "isometric" } },
    ],
  },

  {
    name: "washer",
    description: "Simple washer with inner and outer diameter",
    category: "part",
    requiredInputs: ["inner_diameter", "outer_diameter", "thickness"],
    steps: [
      { tool: "sw_connect", description: "Connect to SolidWorks", params: {} },
      { tool: "sw_new_part", description: "Create new part", params: {} },
      { tool: "sw_create_sketch", description: "Sketch outer circle", params: { plane: "Front" } },
      { tool: "sw_draw_circle", description: "Draw outer diameter", params: { x: 0, y: 0, radius: "${outer_diameter/2}" } },
      { tool: "sw_close_sketch", description: "Exit sketch", params: {} },
      { tool: "sw_extrude", description: "Extrude thickness", params: { depth: "${thickness}" } },
      { tool: "sw_create_sketch", description: "Sketch inner hole", params: { plane: "Front" } },
      { tool: "sw_draw_circle", description: "Draw inner diameter", params: { x: 0, y: 0, radius: "${inner_diameter/2}" } },
      { tool: "sw_close_sketch", description: "Exit sketch", params: {} },
      { tool: "sw_extrude_cut", description: "Cut through", params: { depth: 999 } },
      { tool: "sw_zoom_fit", description: "Zoom to fit", params: {} },
      { tool: "sw_set_view", description: "Set isometric view", params: { view: "isometric" } },
    ],
  },

  {
    name: "tube",
    description: "Hollow tube/pipe with inner and outer diameter",
    category: "part",
    requiredInputs: ["outer_diameter", "wall_thickness", "length"],
    steps: [
      { tool: "sw_connect", description: "Connect to SolidWorks", params: {} },
      { tool: "sw_new_part", description: "Create new part", params: {} },
      { tool: "sw_create_sketch", description: "Sketch outer circle", params: { plane: "Front" } },
      { tool: "sw_draw_circle", description: "Draw outer diameter", params: { x: 0, y: 0, radius: "${outer_diameter/2}" } },
      { tool: "sw_close_sketch", description: "Exit sketch", params: {} },
      { tool: "sw_extrude", description: "Extrude length", params: { depth: "${length}" } },
      { tool: "sw_create_sketch", description: "Sketch inner hole", params: { plane: "Front" } },
      { tool: "sw_draw_circle", description: "Draw inner diameter", params: { x: 0, y: 0, radius: "${(outer_diameter/2) - wall_thickness}" } },
      { tool: "sw_close_sketch", description: "Exit sketch", params: {} },
      { tool: "sw_extrude_cut", description: "Cut through", params: { depth: 999 } },
      { tool: "sw_zoom_fit", description: "Zoom to fit", params: {} },
      { tool: "sw_set_view", description: "Set isometric view", params: { view: "isometric" } },
    ],
  },

  {
    name: "plate_with_holes",
    description: "Rectangular plate with a grid of holes",
    category: "part",
    requiredInputs: ["length", "width", "thickness", "hole_diameter", "holes_x", "holes_y", "hole_spacing"],
    steps: [
      { tool: "sw_connect", description: "Connect to SolidWorks", params: {} },
      { tool: "sw_new_part", description: "Create new part", params: {} },
      { tool: "sw_create_sketch", description: "Sketch plate on Top", params: { plane: "Top" } },
      { tool: "sw_draw_rectangle", description: "Draw plate outline", params: { x1: 0, y1: 0, x2: "${length}", y2: "${width}" } },
      { tool: "sw_close_sketch", description: "Exit sketch", params: {} },
      { tool: "sw_extrude", description: "Extrude thickness", params: { depth: "${thickness}" } },
      { tool: "sw_create_sketch", description: "Sketch first hole", params: { plane: "Top" } },
      { tool: "sw_draw_circle", description: "Draw hole", params: { x: "${hole_spacing}", y: "${hole_spacing}", radius: "${hole_diameter/2}" } },
      { tool: "sw_close_sketch", description: "Exit sketch", params: {} },
      { tool: "sw_extrude_cut", description: "Cut through", params: { depth: 999 } },
      { tool: "sw_pattern_linear", description: "Pattern holes", params: { count_x: "${holes_x}", count_y: "${holes_y}", spacing_x: "${hole_spacing}", spacing_y: "${hole_spacing}" } },
      { tool: "sw_zoom_fit", description: "Zoom to fit", params: {} },
      { tool: "sw_set_view", description: "Set isometric view", params: { view: "isometric" } },
    ],
  },
];

/**
 * Feature recipes for adding to existing parts
 */
export const FEATURE_RECIPES: CADRecipe[] = [
  {
    name: "add_center_hole",
    description: "Add a center hole to an existing circular part",
    category: "feature",
    requiredInputs: ["hole_diameter"],
    steps: [
      { tool: "sw_create_sketch", description: "Sketch hole on Front", params: { plane: "Front" } },
      { tool: "sw_draw_circle", description: "Draw hole", params: { x: 0, y: 0, radius: "${hole_diameter/2}" } },
      { tool: "sw_close_sketch", description: "Exit sketch", params: {} },
      { tool: "sw_extrude_cut", description: "Cut through", params: { depth: 999 } },
    ],
  },

  {
    name: "add_bolt_pattern",
    description: "Add a circular bolt pattern",
    category: "feature",
    requiredInputs: ["bolt_circle_diameter", "hole_diameter", "bolt_count"],
    steps: [
      { tool: "sw_create_sketch", description: "Sketch first hole", params: { plane: "Front" } },
      { tool: "sw_draw_circle", description: "Draw hole on bolt circle", params: { x: "${bolt_circle_diameter/2}", y: 0, radius: "${hole_diameter/2}" } },
      { tool: "sw_close_sketch", description: "Exit sketch", params: {} },
      { tool: "sw_extrude_cut", description: "Cut through", params: { depth: 999 } },
      { tool: "sw_pattern_circular", description: "Pattern holes", params: { count: "${bolt_count}", spacing: 6.283185 } },
    ],
  },

  {
    name: "add_keyway",
    description: "Add a keyway slot to a shaft",
    category: "feature",
    requiredInputs: ["key_width", "key_depth", "key_length"],
    steps: [
      { tool: "sw_create_sketch", description: "Sketch keyway on Right plane", params: { plane: "Right" } },
      { tool: "sw_draw_rectangle", description: "Draw keyway profile", params: { x1: "${-key_width/2}", y1: 0, x2: "${key_width/2}", y2: "${key_depth}" } },
      { tool: "sw_close_sketch", description: "Exit sketch", params: {} },
      { tool: "sw_extrude_cut", description: "Cut keyway length", params: { depth: "${key_length}" } },
    ],
  },

  {
    name: "add_chamfer_edges",
    description: "Add chamfers to all edges",
    category: "feature",
    requiredInputs: ["chamfer_distance"],
    steps: [
      { tool: "sw_chamfer", description: "Apply chamfer", params: { distance: "${chamfer_distance}", angle: 45 } },
    ],
  },

  {
    name: "add_fillet_edges",
    description: "Add fillets to all edges",
    category: "feature",
    requiredInputs: ["fillet_radius"],
    steps: [
      { tool: "sw_fillet", description: "Apply fillet", params: { radius: "${fillet_radius}" } },
    ],
  },
];

/**
 * Assembly recipes
 */
export const ASSEMBLY_RECIPES: CADRecipe[] = [
  {
    name: "simple_assembly",
    description: "Create a simple assembly with two mated parts",
    category: "assembly",
    requiredInputs: ["part1_path", "part2_path"],
    steps: [
      { tool: "sw_connect", description: "Connect to SolidWorks", params: {} },
      { tool: "sw_new_assembly", description: "Create new assembly", params: {} },
      { tool: "sw_insert_component", description: "Insert first part at origin", params: { filepath: "${part1_path}", x: 0, y: 0, z: 0 } },
      { tool: "sw_insert_component", description: "Insert second part offset", params: { filepath: "${part2_path}", x: 0.1, y: 0, z: 0 } },
      { tool: "sw_zoom_fit", description: "Zoom to fit", params: {} },
      { tool: "sw_set_view", description: "Set isometric view", params: { view: "isometric" } },
    ],
  },
];

/**
 * Get all recipes
 */
export function getAllRecipes(): CADRecipe[] {
  return [...PART_RECIPES, ...FEATURE_RECIPES, ...ASSEMBLY_RECIPES];
}

/**
 * Find a recipe by name
 */
export function findRecipe(name: string): CADRecipe | undefined {
  return getAllRecipes().find((r) => r.name.toLowerCase() === name.toLowerCase());
}

/**
 * Get recipes by category
 */
export function getRecipesByCategory(category: "part" | "assembly" | "feature"): CADRecipe[] {
  return getAllRecipes().filter((r) => r.category === category);
}

/**
 * Format recipes for the system prompt
 */
export function formatRecipesForPrompt(): string {
  let prompt = "AVAILABLE PART RECIPES:\n\n";

  for (const recipe of PART_RECIPES) {
    prompt += `${recipe.name.toUpperCase()}:\n`;
    prompt += `  Description: ${recipe.description}\n`;
    prompt += `  Required inputs: ${recipe.requiredInputs.join(", ")}\n`;
    prompt += `  Steps: ${recipe.steps.map((s) => s.tool).join(" -> ")}\n\n`;
  }

  prompt += "\nFEATURE RECIPES (add to existing parts):\n\n";
  for (const recipe of FEATURE_RECIPES) {
    prompt += `${recipe.name.toUpperCase()}:\n`;
    prompt += `  Description: ${recipe.description}\n`;
    prompt += `  Required inputs: ${recipe.requiredInputs.join(", ")}\n\n`;
  }

  return prompt;
}

/**
 * Convert dimension string to meters
 * Handles common unit suffixes
 */
export function parseToMeters(value: string | number): number {
  if (typeof value === "number") return value;

  const num = parseFloat(value);
  const lower = value.toLowerCase();

  if (lower.includes("mm")) return num / 1000;
  if (lower.includes("cm")) return num / 100;
  if (lower.includes("in") || lower.includes("inch")) return num * 0.0254;
  if (lower.includes("ft") || lower.includes("feet") || lower.includes("foot")) return num * 0.3048;

  // Assume meters if no unit
  return num;
}
