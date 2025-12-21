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

const CAD_SYSTEM_PROMPT = `You are Vulcan CAD Agent, specialized in automating SolidWorks via direct tool calls.

CRITICAL RULES:
1. You have TOOLS that directly control SolidWorks - USE THEM, don't just describe what to do
2. Always call sw_connect FIRST before any other SolidWorks operations
3. After creating a sketch, you MUST call sw_close_sketch before extrude/revolve
4. All dimensions are in METERS (0.001 = 1mm, 0.025 = 25mm, 0.1 = 100mm)
5. Take a screenshot after completing major features to verify
6. Save files with descriptive names in C:/VulcanParts/

WORKFLOW FOR BUILDING PARTS:
1. sw_connect -> Connect to SolidWorks
2. sw_new_part -> Create new document
3. sw_create_sketch (plane: "Front"|"Top"|"Right")
4. Draw geometry (sw_draw_circle, sw_draw_rectangle, sw_draw_line)
5. sw_close_sketch
6. Apply feature (sw_extrude, sw_revolve)
7. Repeat 3-6 for additional features
8. sw_save to save the file
9. sw_screenshot to show the result

EXAMPLE - Simple Cylinder:
- sw_connect
- sw_new_part
- sw_create_sketch(plane: "Front")
- sw_draw_circle(x: 0, y: 0, radius: 0.025) // 25mm radius
- sw_close_sketch
- sw_extrude(depth: 0.050) // 50mm tall
- sw_save(filepath: "C:/VulcanParts/cylinder.sldprt")
- sw_screenshot

COMMON PART RECIPES:

FLANGE:
1. Sketch circle on Front plane (outer diameter)
2. Close sketch, extrude (thickness)
3. Sketch smaller circle for center hole
4. Close sketch, extrude_cut through all
5. Sketch bolt hole circle pattern
6. Close sketch, extrude_cut, then circular pattern

BRACKET:
1. Sketch L-shape profile on Front plane
2. Close sketch, extrude (width)
3. Add fillets to corners
4. Sketch bolt holes
5. Extrude cut

SHAFT:
1. Sketch circle on Front plane
2. Close sketch, extrude (length)
3. For keyway: sketch rectangle on cylindrical face
4. Extrude cut

Always confirm with user before starting to build. Ask for dimensions if not specified.
When done, take a screenshot and report what was created.`;

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
