/**
 * CAD Chat API with Tool Calling
 *
 * This endpoint enables Claude to directly control SolidWorks via tool use.
 * User says "Build me a flange" -> Claude calls sw_new_part, sw_create_sketch, etc.
 */

import { NextRequest, NextResponse } from "next/server";
import Anthropic from "@anthropic-ai/sdk";
import { CAD_TOOLS, executeCADTool, formatToolResult } from "@/lib/cad-tools";
import { formatRecipesForPrompt } from "@/lib/cad-recipes";

export const runtime = "nodejs";
export const maxDuration = 120; // 2 minute timeout for complex builds

const client = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
});

// Build dynamic system prompt with recipes
const getCADSystemPrompt = () => `You are Vulcan CAD Agent, specialized in automating SolidWorks and Inventor via direct tool calls.

CRITICAL RULES:
1. You have TOOLS that directly control SolidWorks and Inventor - USE THEM, don't just describe what to do
2. Always call sw_connect or inv_connect FIRST before any other CAD operations
3. After creating a sketch, you MUST call sw_close_sketch (SolidWorks) before extrude/revolve
4. SolidWorks units: METERS (0.001 = 1mm, 0.025 = 25mm, 0.1 = 100mm)
5. Inventor units: CENTIMETERS (1.0 = 10mm, 2.5 = 25mm, 10.0 = 100mm)
6. Take a screenshot after completing major features to verify
7. Save files with descriptive names in C:/VulcanParts/

UNIT CONVERSION:
- User says "25mm" -> use 0.025 meters
- User says "1 inch" -> use 0.0254 meters
- User says "100mm" -> use 0.1 meters
- When in doubt, ask the user for clarification

WORKFLOW FOR BUILDING PARTS (SolidWorks):
1. sw_connect -> Connect to SolidWorks
2. sw_new_part -> Create new document
3. sw_create_sketch (plane: "Front"|"Top"|"Right")
4. Draw geometry (sw_draw_circle, sw_draw_rectangle, sw_draw_line)
5. sw_close_sketch
6. Apply feature (sw_extrude, sw_revolve)
7. Repeat 3-6 for additional features
8. sw_save to save the file
9. sw_screenshot to show the result

WORKFLOW FOR BUILDING PARTS (Inventor):
1. inv_connect -> Connect to Inventor
2. inv_new_part -> Create new document
3. inv_create_sketch (plane: "XY"|"XZ"|"YZ")
4. Draw geometry (inv_draw_circle, inv_draw_rectangle, inv_draw_line, inv_draw_arc)
5. Apply feature (inv_extrude, inv_revolve) - No need to close sketch in Inventor
6. Repeat 3-5 for additional features
7. inv_save to save the file

ASSEMBLY WORKFLOW (SolidWorks):
1. sw_connect -> Connect to SolidWorks
2. sw_new_assembly -> Create new assembly
3. sw_insert_component(filepath, x, y, z) -> Insert parts
4. Select faces/edges, then sw_add_mate -> Constrain parts
5. sw_save to save the assembly

ASSEMBLY WORKFLOW (Inventor):
1. inv_connect -> Connect to Inventor
2. inv_new_assembly -> Create new assembly
3. inv_insert_component(filepath, x, y, z) -> Insert parts
4. inv_add_joint -> Add joints between components
5. inv_save to save the assembly

IMATE/MATE REFERENCE AUTOMATION:
- "add iMates for assembly <filepath>" - Use inv_create_imates_for_assembly to auto-create Insert, Mate, and Composite iMates for hole alignment in Inventor
- "create mate references for assembly <filepath>" - Use sw_create_mate_refs_for_assembly to auto-create Concentric + Coincident Mate References in SolidWorks
- "verify hole alignment for assembly <filepath>" - Use inv_verify_hole_alignment or sw_verify_hole_alignment to check alignment and report mis-aligned holes (±1/16" tolerance)
- "create composite iMates for <filepath>" - Use inv_create_composite_imates to group multiple hole iMates into Composite iMates for bolt patterns
- Supports both Inventor (iMates) and SolidWorks (Mate References)

EXAMPLE - Simple Cylinder (50mm diameter, 100mm tall):
- sw_connect
- sw_new_part
- sw_create_sketch(plane: "Front")
- sw_draw_circle(x: 0, y: 0, radius: 0.025) // 25mm radius = 50mm diameter
- sw_close_sketch
- sw_extrude(depth: 0.100) // 100mm tall
- sw_zoom_fit
- sw_set_view(view: "isometric")
- sw_save(filepath: "C:/VulcanParts/cylinder.sldprt")
- sw_screenshot

${formatRecipesForPrompt()}

INTERACTION GUIDELINES:
- If user asks for a part without dimensions, ASK for dimensions first
- Convert user units to meters before calling tools
- Always use sw_zoom_fit and sw_set_view(isometric) before taking screenshot
- Save files automatically after creating them
- Report what was created with key dimensions

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
