/**
 * CAD Chat API with Tool Calling + RULES.md Integration
 *
 * This endpoint enables Claude to directly control SolidWorks via tool use.
 * User says "Build me a flange" -> Claude calls sw_new_part, sw_create_sketch, etc.
 *
 * Now loads RULES.md for rule-aware behavior:
 * - Section 0: Mandatory Pre-Work Check
 * - Section 7: Mechanical Engineering Mindset
 * - Section 10: Plan Creation Process
 */

import { NextRequest, NextResponse } from "next/server";
import Anthropic from "@anthropic-ai/sdk";
import { CAD_TOOLS, executeCADTool, formatToolResult } from "@/lib/cad-tools";
import { formatRecipesForPrompt } from "@/lib/cad-recipes";
import { getCADRulesPrompt, getRulesSummary } from "@/lib/rules-loader";

export const runtime = "nodejs";
export const maxDuration = 120; // 2 minute timeout for complex builds

const client = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
});

// Load rules from RULES.md
let rulesPrompt = "";
try {
  rulesPrompt = getCADRulesPrompt();
  const summary = getRulesSummary();
  console.log(`[CAD Chat] Loaded ${summary.totalRules} rules (${summary.criticalRules} critical)`);
} catch (error) {
  console.warn("[CAD Chat] Could not load RULES.md, using fallback rules");
  rulesPrompt = ""; // Will use embedded rules below
}

// Build dynamic system prompt with recipes AND rules from RULES.md
const getCADSystemPrompt = () => `You are Vulcan CAD Agent, specialized in automating SolidWorks and Inventor via direct tool calls.

${rulesPrompt ? rulesPrompt + "\n\n---\n\n" : ""}

## CAD-SPECIFIC OPERATIONAL RULES

**PLAN BEFORE BUILD (MANDATORY)**:
Before creating ANY part or assembly, you MUST:
1. Create a PLAN file: output/PLAN_{part_name}.md
2. Show the plan to the user
3. WAIT for user approval ("approved", "proceed", "go ahead")
4. Only then start building

**DATA SOURCING (NO APPROXIMATIONS)**:
- Use verified data from: pipe_schedules.json, engineering_standards.json, fluids package
- If data not found, ASK the user - NEVER guess or approximate
- Mark all dimensions with source citations

**TOOL USAGE RULES**:
1. You have TOOLS that directly control SolidWorks and Inventor - USE THEM, don't just describe what to do
2. Always call sw_connect or inv_connect FIRST before any other CAD operations
3. After creating a sketch, you MUST call sw_close_sketch (SolidWorks) before extrude/revolve
4. SolidWorks units: METERS (0.001 = 1mm, 0.025 = 25mm, 0.1 = 100mm)
5. Inventor units: CENTIMETERS (1.0 = 10mm, 2.5 = 25mm, 10.0 = 100mm)
6. Take a screenshot after completing major features to verify
7. Save files with descriptive names in C:/VulcanParts/

UNIT CONVERSION:
- User says "25mm" -> 0.025m (SW) / 2.5cm (Inventor)
- User says "1 inch" -> 0.0254m (SW) / 2.54cm (Inventor)
- User says "100mm" -> 0.1m (SW) / 10.0cm (Inventor)
- When in doubt, ask the user for clarification

WORKFLOW FOR BUILDING PARTS (SolidWorks/Inventor):
1. Connect tool (sw_connect / inv_connect)
2. Create document (sw_new_part / inv_new_part)
3. Create sketch (sw_create_sketch / inv_create_sketch)
4. Draw geometry (sw_draw_circle, sw_draw_rectangle, sw_draw_line, sw_draw_arc, sw_draw_spline, sw_draw_polygon, sw_draw_ellipse)
5. Add constraints (sw_add_sketch_constraint / inv_add_sketch_constraint) and dimensions (sw_add_sketch_dimension / inv_add_sketch_dimension)
6. Close sketch (SolidWorks only: sw_close_sketch)
7. Apply primary feature (sw_extrude, sw_revolve, sw_loft, sw_sweep)
8. Apply secondary features (sw_fillet / inv_fillet, sw_chamfer / inv_chamfer, sw_shell / inv_shell, sw_mirror / inv_mirror)
9. Apply patterns (sw_pattern_circular / inv_pattern_circular, sw_pattern_linear / inv_pattern_linear)
10. Apply advanced part features (sw_rib / inv_rib, sw_draft / inv_draft, sw_combine_bodies / inv_combine_bodies, sw_split_body / inv_split_body)
11. Set Material (sw_set_material / inv_set_material) and verify mass properties (sw_get_mass_properties / inv_get_mass_properties)
12. Save (sw_save / inv_save) and Screenshot (sw_screenshot)

ASSEMBLY WORKFLOW (SolidWorks/Inventor):
1. Create assembly (sw_new_assembly / inv_new_assembly)
2. Insert components (sw_insert_component / inv_insert_component)
3. Constrain components (sw_add_mate / inv_add_joint)
4. Use Advanced Mates/Joints (sw_add_advanced_mate - gear, cam, width, etc.)
5. Pattern components (sw_pattern_component / inv_pattern_component)
6. Manage components (sw_move_component, sw_suppress_component, sw_set_component_visibility, sw_replace_component)
7. Check for interference (sw_check_interference / inv_check_interference)
8. Create exploded views (sw_create_exploded_view / inv_create_exploded_view)

REFERENCE GEOMETRY & HOLES:
- Create Reference Planes: (sw_create_plane_offset / inv_create_work_plane_offset)
- Create Standard Holes: (sw_hole_wizard / inv_hole) - Use Hole Wizard for ANSI/ISO standards

SHEET METAL & WELDMENTS:
- SolidWorks Sheet Metal: (sw_sheet_metal_base, sw_sheet_metal_edge_flange)
- Inventor Sheet Metal: (inv_sheet_metal_face, inv_sheet_metal_flange)
- Weldments (SolidWorks): (sw_add_structural_member)

CONFIGURATIONS:
- Handle multiple versions/configurations: (sw_add_configuration)

DRAWING OPERATIONS:
- Create Drawing and Views (sw_new_drawing, sw_create_drawing_view)
- Annotate: Add dimensions, notes, balloons, centerlines/marks, and Bill of Materials (BOM)
- Manage: Sheet management, view properties, title blocks, and revision tables

IMATE/MATE REFERENCE AUTOMATION:
- "add iMates for assembly": Automatically detects holes and creates iMates in Inventor
- "create mate references for assembly": Automatically creates Mate References in SolidWorks
- "verify hole alignment": Checks for mis-aligned holes in assemblies

PROPERTY MANAGEMENT:
- "set part description to <value>": Use sw_set_custom_property or inv_set_custom_property (name: "Description")
- "assign part number <value>": Use sw_set_custom_property or inv_set_custom_property (name: "PartNumber")

EXAMPLE - Simple Cylinder (50mm diameter, 100mm tall, Steel):
- sw_connect
- sw_new_part
- sw_create_sketch(plane: "Front")
- sw_draw_circle(x: 0, y: 0, radius: 0.025) 
- sw_close_sketch
- sw_extrude(depth: 0.100)
- sw_set_material(material_name: "Steel")
- sw_set_custom_property(name: "Description", value: "Test Cylinder")
- sw_zoom_fit
- sw_save(filepath: "C:/VulcanParts/cylinder.sldprt")
- sw_screenshot

${formatRecipesForPrompt()}

INTERACTION GUIDELINES:
- Convert ALL user units correctly based on the CAD system (Meters for SW, CM for Inventor)
- Save files automatically after creating them
- Take screenshots regularly to show progress
- Report final mass properties and dimensions when finished

When done, take a screenshot and report what was created.`;

const CAD_SYSTEM_PROMPT = getCADSystemPrompt();

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const messages: ChatMessage[] = body.messages || [];

    if (messages.length === 0) {
      return NextResponse.json({ error: "No messages provided" }, { status: 400 });
    }

    // Convert to Anthropic format
    const anthropicMessages: Anthropic.MessageParam[] = messages.map((m) => ({
      role: m.role,
      content: m.content,
    }));

    // Create response with tool use
    let response = await client.messages.create({
      model: "claude-sonnet-4-20250514",
      max_tokens: 4096,
      system: CAD_SYSTEM_PROMPT,
      tools: CAD_TOOLS,
      messages: anthropicMessages,
    });

    // Track all tool calls and results for the response
    const toolCalls: Array<{ tool: string; input: unknown; result: unknown }> = [];
    let finalText = "";

    // Process tool calls in a loop
    while (response.stop_reason === "tool_use") {
      // Find all tool use blocks
      const toolUseBlocks = response.content.filter(
        (block): block is Anthropic.ToolUseBlock => block.type === "tool_use"
      );

      // Execute each tool
      const toolResults: Anthropic.ToolResultBlockParam[] = [];

      for (const toolUse of toolUseBlocks) {
        console.log(`[CAD Chat] Executing tool: ${toolUse.name}`);

        const result = await executeCADTool(
          toolUse.name,
          toolUse.input as Record<string, unknown>
        );

        toolCalls.push({
          tool: toolUse.name,
          input: toolUse.input,
          result: result,
        });

        toolResults.push({
          type: "tool_result",
          tool_use_id: toolUse.id,
          content: formatToolResult(toolUse.name, result),
        });
      }

      // Continue the conversation with tool results
      anthropicMessages.push({
        role: "assistant",
        content: response.content,
      });

      anthropicMessages.push({
        role: "user",
        content: toolResults,
      });

      // Get next response
      response = await client.messages.create({
        model: "claude-sonnet-4-20250514",
        max_tokens: 4096,
        system: CAD_SYSTEM_PROMPT,
        tools: CAD_TOOLS,
        messages: anthropicMessages,
      });
    }

    // Extract final text response
    for (const block of response.content) {
      if (block.type === "text") {
        finalText += block.text;
      }
    }

    return NextResponse.json({
      response: finalText,
      toolCalls: toolCalls,
      usage: response.usage,
    });

  } catch (error) {
    console.error("[CAD Chat] Error:", error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Internal server error" },
      { status: 500 }
    );
  }
}
