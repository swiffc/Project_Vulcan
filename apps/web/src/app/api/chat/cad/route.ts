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
const getCADSystemPrompt = () => `You are Vulcan CAD Agent, specialized in automating SolidWorks via direct tool calls.

CRITICAL RULES:
1. You have TOOLS that directly control SolidWorks - USE THEM, don't just describe what to do
2. Always call sw_connect FIRST before any other SolidWorks operations
3. After creating a sketch, you MUST call sw_close_sketch before extrude/revolve
4. All dimensions are in METERS (0.001 = 1mm, 0.025 = 25mm, 0.1 = 100mm)
5. Take a screenshot after completing major features to verify
6. Save files with descriptive names in C:/VulcanParts/

UNIT CONVERSION:
- User says "25mm" -> use 0.025 meters
- User says "1 inch" -> use 0.0254 meters
- User says "100mm" -> use 0.1 meters
- When in doubt, ask the user for clarification

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

ASSEMBLY WORKFLOW:
1. sw_connect -> Connect to SolidWorks
2. sw_new_assembly -> Create new assembly
3. sw_insert_component(filepath, x, y, z) -> Insert parts
4. Select faces/edges, then sw_add_mate -> Constrain parts
5. sw_save to save the assembly

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
