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
const getCADSystemPrompt = () => `You are Vulcan CAD Agent - an expert mechanical design assistant with REAL COM API access to SolidWorks and Inventor.

${rulesPrompt ? rulesPrompt + "\n\n---\n\n" : ""}

## CORE CAPABILITIES & EXPERTISE

You have DIRECT access to CAD systems and can execute over 200+ operations including:
- **Vision Analysis**: You can SEE what's on the SolidWorks screen and automatically analyze parts, assemblies, and drawings
- **Part Modeling**: Sketching, Extrudes, Revolves, Lofts, Sweeps, Fillets, Chamfers, Holes
- **Assembly**: Mates/Constraints, Patterns, Interference Detection, Exploded Views
- **Drawings**: Views, Dimensions, Annotations, BOM generation
- **Advanced**: Sheet Metal, Weldments, Surfacing, Multi-Body Parts
- **Analysis**: Mass Properties, Hole Validation (ASME Y14.5), Design Recommendations
- **Validation**: 130+ ACHE validators, GD&T checks, Material specs, Welding standards

## ENGINEERING KNOWLEDGE BASE
- **Standards**: ASME (Y14.5, B16.5, B16.9, B31.3), AWS D1.1, AISC, ASTM, ISO
- **Materials**: ASTM A36 (steel), 316SS (stainless), 6061-T6 (aluminum)
- **Pipe & Fittings**: ANSI/ASME B16 series, pipe schedules (10, 40, 80, 160, XXS)
- **Fasteners**: ANSI/ASME B18 bolts, nuts, washers
- **Heat Exchangers**: ACHE (Air-Cooled Heat Exchanger) design principles

## MANDATORY WORKFLOW: PLAN-BUILD-VERIFY

**STEP 1 - PLAN** (BEFORE building anything):
1. Clarify requirements (dimensions, material, standards)
2. Check engineering database for standard components
3. Create PLAN file: output/PLAN_{part_name}.md
4. Show plan to user
5. WAIT for explicit approval ("approved", "proceed", "go ahead")

**STEP 2 - BUILD** (After approval):
1. Connection is auto-handled, but you can call sw_connect / inv_connect if needed
2. Create document: sw_new_part / inv_new_part
3. Create sketch: sw_create_sketch / inv_create_sketch (plane: Front/Top/Right)
4. Draw geometry with EXACT units
5. Add constraints (horizontal, vertical, coincident, perpendicular, etc.)
6. Close sketch (SW only: sw_close_sketch)
7. Apply features (extrude, revolve, fillet, chamfer)
8. Set material: sw_set_material / inv_set_material
9. Verify: sw_get_mass_properties / inv_get_mass_properties
10. Save: sw_save / inv_save
11. Screenshot: sw_screenshot

**STEP 3 - VERIFY**:
- Check mass properties (realistic weight for material?)
- Take screenshot (does it match intent?)
- Run validation if applicable (sw_validate_part)

## CRITICAL RULES

⚠️ **NEVER OUTPUT FAKE CODE**: Don't write Python/code blocks pretending to execute - USE THE TOOLS
⚠️ **UNIT CONVERSION IS CRITICAL**:
  - SolidWorks: METERS (0.001m = 1mm, 0.025m = 25mm, 0.1m = 100mm)
  - Inventor: CENTIMETERS (1cm = 10mm, 2.5cm = 25mm, 10cm = 100mm)
⚠️ **DATA ACCURACY**: Use verified standards data - NEVER approximate pipe sizes, bolt dimensions, material properties
⚠️ **CLOSE SKETCHES**: SolidWorks requires sw_close_sketch BEFORE extrude/revolve
⚠️ **HUMAN APPROVAL**: Wait for approval before starting build operations
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
- **AUTOMATIC VISION**: When SolidWorks is open, you automatically see and analyze what's on screen
- **PROACTIVE INFORMATION**: If you see a part/assembly/drawing on screen, proactively provide information about it:
  * Part type and geometry
  * Dimensions and features visible
  * Material properties (if visible)
  * Design recommendations
  * Standards compliance notes
  * Assembly relationships (if applicable)

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

    // Convert to Anthropic format, sanitizing to only keep simple text messages
    // This prevents the "unexpected tool_use_id found in tool_result blocks" error
    // when conversation history contains corrupted tool_use/tool_result from previous requests
    const anthropicMessages: Anthropic.MessageParam[] = messages
      .filter((m) => {
        // Only keep messages with string content (not arrays/objects from tool calling)
        return typeof m.content === "string" && m.content.trim().length > 0;
      })
      .map((m) => ({
        role: m.role,
        content: m.content,
      }));

    // Validate we still have messages after sanitization
    if (anthropicMessages.length === 0) {
      return NextResponse.json(
        { error: "No valid messages after sanitization" },
        { status: 400 }
      );
    }

    // AUTO-CONNECT: Check SolidWorks status and connect if needed
    const desktopUrl = process.env.DESKTOP_SERVER_URL || "http://localhost:8000";
    let swStatus: any = null;
    let screenshotContext = "";
    
    try {
      swStatus = await fetch(`${desktopUrl}/com/solidworks/status`)
        .then(r => r.json())
        .catch(() => ({ connected: false }));

      if (!swStatus?.connected) {
        console.log("[CAD Chat] Auto-connecting to SolidWorks...");
        const connectResult = await executeCADTool("sw_connect", {});
        if (connectResult.success) {
          console.log("[CAD Chat] ✅ Auto-connected to SolidWorks");
          // Re-fetch status after connection
          swStatus = await fetch(`${desktopUrl}/com/solidworks/status`)
            .then(r => r.json())
            .catch(() => ({ connected: false }));
        } else {
          console.warn("[CAD Chat] ⚠️ Auto-connect failed, but continuing (agent will handle connection)");
        }
      } else {
        console.log("[CAD Chat] SolidWorks already connected");
      }

      // AUTO-SCREENSHOT & VISION ANALYSIS: Capture and analyze what's on screen
      if (swStatus?.connected && swStatus?.has_document) {
        console.log("[CAD Chat] 📸 Capturing SolidWorks screen for analysis...");
        try {
          const screenshotResult = await executeCADTool("sw_screenshot", {});
          
          if (screenshotResult.success && screenshotResult.result?.image) {
            console.log("[CAD Chat] 🔍 Analyzing screenshot with vision...");
            
            // Use Claude Vision API to analyze the screenshot
            const visionResponse = await client.messages.create({
              model: "claude-sonnet-4-20250514",
              max_tokens: 1024,
              messages: [
                {
                  role: "user",
                  content: [
                    {
                      type: "image",
                      source: {
                        type: "base64",
                        media_type: "image/png",
                        data: screenshotResult.result.image.replace(/^data:image\/\w+;base64,/, ""),
                      },
                    },
                    {
                      type: "text",
                      text: `Analyze this SolidWorks screen. Provide a detailed description of:
1. What type of document is open (Part, Assembly, or Drawing)?
2. What geometry/features are visible in the viewport?
3. What parts/components are shown (if assembly)?
4. Any dimensions, annotations, or drawing elements visible?
5. Overall design intent and key characteristics.

Be specific about dimensions, geometry types, materials (if visible), and any notable design features.`,
                    },
                  ],
                },
              ],
            });

            const visionAnalysis = visionResponse.content
              .filter((block: any) => block.type === "text")
              .map((block: any) => block.text)
              .join("\n");

            screenshotContext = `\n\n[VISUAL ANALYSIS OF CURRENT SOLIDWORKS SCREEN]\n${visionAnalysis}\n\nActive Document: ${swStatus.document_name || "Unknown"}\nDocument Type: ${swStatus.document_type || "Unknown"}\n`;
            
            console.log("[CAD Chat] ✅ Vision analysis complete");
          }
        } catch (error) {
          console.warn("[CAD Chat] Could not capture/analyze screenshot:", error);
          // Continue without screenshot context
        }
      }
    } catch (error) {
      console.warn("[CAD Chat] Could not check/connect to SolidWorks:", error);
      // Continue anyway - agent can handle connection
    }

    // Add screenshot context to the first user message if available
    if (screenshotContext && anthropicMessages.length > 0) {
      const firstUserMessage = anthropicMessages.find(m => m.role === "user");
      if (firstUserMessage && typeof firstUserMessage.content === "string") {
        firstUserMessage.content = screenshotContext + firstUserMessage.content;
      }
    }

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
