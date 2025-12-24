import { NextRequest } from "next/server";
import { orchestrate, augmentSystemPrompt } from "@/lib/orchestrator";
import { streamChat, ChatMessage } from "@/lib/claude-client";

export const runtime = "nodejs";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    // Filter out messages with empty content (can happen from failed streaming)
    const messages: ChatMessage[] = (body.messages || []).filter(
      (m: ChatMessage) => m.content && m.content.trim().length > 0
    );

    if (messages.length === 0) {
      return new Response(JSON.stringify({ error: "No messages provided" }), {
        status: 400,
        headers: { "Content-Type": "application/json" },
      });
    }

    // Get the last user message for routing
    const lastUserMessage = messages.filter((m) => m.role === "user").pop();
    if (!lastUserMessage) {
      return new Response(JSON.stringify({ error: "No user message found" }), {
        status: 400,
        headers: { "Content-Type": "application/json" },
      });
    }

    // Route to appropriate agent
    const { agent, systemPrompt, requiresDesktop } = orchestrate(
      lastUserMessage.content
    );

    console.log(`[Orchestrator] Routing to ${agent.name}`);

    // For CAD context, fetch current SolidWorks/Inventor status AND relevant data
    let cadContext = "";
    if (agent.id === "cad" || body.agentContext === "cad") {
      try {
        const desktopUrl = process.env.DESKTOP_SERVER_URL || "http://localhost:8000";
        const msg = lastUserMessage.content.toLowerCase();

        // Always fetch basic status
        const [swStatus, invStatus] = await Promise.all([
          fetch(`${desktopUrl}/com/solidworks/status`).then(r => r.json()).catch(() => null),
          fetch(`${desktopUrl}/com/inventor/status`).then(r => r.json()).catch(() => null),
        ]);

        if (swStatus?.connected && swStatus?.has_document) {
          cadContext += `\n\n[CURRENT CAD CONTEXT]\nSolidWorks ${swStatus.version} is running.\nActive document: ${swStatus.document_name}\n`;

          // Pre-fetch data based on user query
          const fetchPromises: Promise<any>[] = [];

          // If user asks about parts, count, BOM, assembly
          if (msg.match(/\b(part|count|how many|bom|bill|assembly|component|total)\b/)) {
            fetchPromises.push(
              fetch(`${desktopUrl}/com/solidworks/get_bom`)
                .then(r => r.json())
                .then(data => {
                  if (data.bom) {
                    cadContext += `\n[BOM DATA - ALREADY FETCHED]\nTotal unique parts: ${data.total_unique_parts}\nParts:\n`;
                    data.bom.slice(0, 20).forEach((item: any) => {
                      cadContext += `- ${item.part_number} (qty: ${item.qty})\n`;
                    });
                    if (data.bom.length > 20) {
                      cadContext += `... and ${data.bom.length - 20} more parts\n`;
                    }
                  }
                })
                .catch(() => null)
            );
          }

          // If user asks about properties
          if (msg.match(/\b(propert|custom|metadata|info)\b/)) {
            fetchPromises.push(
              fetch(`${desktopUrl}/com/solidworks/get_custom_properties`)
                .then(r => r.json())
                .then(data => {
                  if (data.properties) {
                    cadContext += `\n[PROPERTIES DATA - ALREADY FETCHED]\n`;
                    Object.entries(data.properties).forEach(([key, val]) => {
                      cadContext += `- ${key}: ${val}\n`;
                    });
                  }
                })
                .catch(() => null)
            );
          }

          // If user asks about holes or validation
          if (msg.match(/\b(hole|validat|check|error|standard)\b/)) {
            fetchPromises.push(
              fetch(`${desktopUrl}/com/solidworks/validate_holes`)
                .then(r => r.json())
                .then(data => {
                  cadContext += `\n[HOLE VALIDATION - ALREADY FETCHED]\nTotal holes found: ${data.total_holes}\n`;
                  if (data.validation?.warnings?.length > 0) {
                    cadContext += `Warnings: ${data.validation.warnings.length}\n`;
                    data.validation.warnings.forEach((w: any) => {
                      cadContext += `- ${w.message}\n`;
                    });
                  }
                  if (data.validation?.errors?.length > 0) {
                    cadContext += `Errors: ${data.validation.errors.length}\n`;
                  }
                })
                .catch(() => null)
            );
          }

          // If user asks about spatial positions, relationships, seals, or analysis
          if (msg.match(/\b(position|spatial|where|location|relationship|seal|ring|adjacent|nearby|distance)\b/)) {
            fetchPromises.push(
              fetch(`${desktopUrl}/com/solidworks/get_spatial_positions`)
                .then(r => r.json())
                .then(data => {
                  if (data.components) {
                    cadContext += `\n[SPATIAL POSITIONS - ALREADY FETCHED]\nTotal components: ${data.total_components}\n`;
                    cadContext += `\nComponent positions (X, Y, Z in mm):\n`;
                    data.components.slice(0, 15).forEach((c: any) => {
                      cadContext += `- ${c.name}: (${c.position.x}, ${c.position.y}, ${c.position.z}) [${c.part_type}]\n`;
                    });
                    if (data.type_groups) {
                      cadContext += `\nType groups:\n`;
                      Object.entries(data.type_groups).forEach(([type, parts]: [string, any]) => {
                        cadContext += `- ${type}: ${parts.length} parts\n`;
                      });
                    }
                    if (data.seal_ring_pairs?.length > 0) {
                      cadContext += `\nSeal-Ring pairs:\n`;
                      data.seal_ring_pairs.forEach((pair: any) => {
                        cadContext += `- ${pair.component1} <-> ${pair.component2}: ${pair.distance_mm}mm\n`;
                      });
                    }
                  }
                })
                .catch(() => null)
            );
          }

          // If user asks about analysis, recommendations, or design review
          if (msg.match(/\b(analy|recommend|design|review|purpose|function|suggest|insight)\b/)) {
            fetchPromises.push(
              fetch(`${desktopUrl}/com/solidworks/analysis/analyze`)
                .then(r => r.json())
                .then(data => {
                  if (data.part_analyses) {
                    cadContext += `\n[DESIGN ANALYSIS - ALREADY FETCHED]\nParts analyzed: ${data.total_parts_analyzed}\n`;
                    cadContext += `\nAssembly category: ${data.assembly_insights?.assembly_category}\n`;
                    cadContext += `Complexity score: ${data.assembly_insights?.complexity_score}/10\n`;
                    cadContext += `\nPart analyses:\n`;
                    data.part_analyses.slice(0, 10).forEach((p: any) => {
                      cadContext += `\n${p.part_number}:\n`;
                      cadContext += `  Type: ${p.part_type} (${Math.round(p.confidence * 100)}% confidence)\n`;
                      cadContext += `  Suggested name: ${p.suggested_name || 'N/A'}\n`;
                      cadContext += `  Purpose: ${p.purpose?.substring(0, 100)}...\n`;
                      if (p.geometry?.mass_kg) cadContext += `  Mass: ${p.geometry.mass_kg}kg\n`;
                      if (p.material?.name) cadContext += `  Material: ${p.material.name}\n`;
                      if (p.recommendations?.length > 0) {
                        cadContext += `  Recommendations: ${p.recommendations[0]}\n`;
                      }
                    });
                    if (data.assembly_insights?.recommendations) {
                      cadContext += `\nAssembly recommendations:\n`;
                      data.assembly_insights.recommendations.slice(0, 5).forEach((r: string) => {
                        cadContext += `- ${r}\n`;
                      });
                    }
                  }
                })
                .catch(() => null)
            );
          }

          // If user asks to edit a sketch
          const sketchMatch = msg.match(/edit\s+(?:the\s+)?(?:sketch\s+)?["']?(\w+(?:\s+\w+)?)["']?/i) ||
                              msg.match(/sketch\s*(\d+|base|profile)/i);
          if (sketchMatch || msg.match(/\b(edit sketch|sketch info|sketch geometry|dimensions|constraints)\b/)) {
            const sketchName = sketchMatch?.[1] || "Sketch1";
            fetchPromises.push(
              fetch(`${desktopUrl}/com/solidworks/edit_sketch`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ sketch_name: sketchName }),
              })
                .then(r => r.json())
                .then(data => {
                  if (data.status === "editing") {
                    cadContext += `\n[SKETCH EDITING - ALREADY OPENED]\nSketch: ${data.sketch_name}\nStatus: In edit mode\n`;
                    if (data.segments?.length > 0) {
                      cadContext += `\nSketch Segments:\n`;
                      data.segments.forEach((seg: any, i: number) => {
                        cadContext += `- ${i+1}. ${seg.type}${seg.is_construction ? ' (construction)' : ''}\n`;
                      });
                    }
                  }
                })
                .catch(() => null)
            );
          }

          // If user asks to open a component
          const componentMatch = msg.match(/open\s+(?:the\s+)?(?:component\s+)?["']?([A-Za-z0-9_-]+(?:<\d+>)?)/i) ||
                                 msg.match(/open\s+(?:the\s+)?([A-Za-z]+flange|housing|bracket|plate|frame)/i);
          if (componentMatch) {
            const componentName = componentMatch[1];
            fetchPromises.push(
              fetch(`${desktopUrl}/com/solidworks/open_component`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ component_name: componentName }),
              })
                .then(r => r.json())
                .then(data => {
                  if (data.status === "ok") {
                    cadContext += `\n[COMPONENT OPENED - ALREADY ACTIVE]\nComponent: ${data.component_name}\nFile: ${data.filepath}\nType: ${data.document_type}\n`;
                    cadContext += `\nThe component is now open and ready for inspection. You can analyze its features.`;
                  }
                })
                .catch(() => null)
            );
          }

          // Wait for all data fetches
          await Promise.all(fetchPromises);

          cadContext += `\n\n⚠️ CRITICAL: You have REAL DATA above. DO NOT output Python code or fake function calls. Analyze the data directly.`;
        } else if (swStatus?.connected) {
          cadContext += `\n\n[CURRENT CAD CONTEXT]\nSolidWorks ${swStatus.version} is running but no document is open.`;
        }

        if (invStatus?.connected && invStatus?.has_document) {
          cadContext += `\nInventor is running. Active document: ${invStatus.document_name}`;
        }
      } catch (e) {
        console.log("Could not fetch CAD status:", e);
      }
    }

    // Augment with RAG Context
    const augmentedPrompt = await augmentSystemPrompt(systemPrompt + cadContext, lastUserMessage.content);

    // Create SSE stream
    const encoder = new TextEncoder();
    const stream = new ReadableStream({
      async start(controller) {
        // Send agent info
        controller.enqueue(
          encoder.encode(
            `data: ${JSON.stringify({ agent: agent.id, agentName: agent.name })}\n\n`
          )
        );

        await streamChat(messages, augmentedPrompt, {
          onToken: (token) => {
            controller.enqueue(
              encoder.encode(`data: ${JSON.stringify({ content: token })}\n\n`)
            );
          },
          onComplete: async (fullResponse) => {
            // If desktop action was required, we could trigger it here
            // and send screenshot back
            if (requiresDesktop) {
              try {
                // Attempt to take screenshot
                const screenshotResponse = await fetch(
                  `${process.env.DESKTOP_SERVER_URL || "http://localhost:8000"}/screen/screenshot`,
                  { method: "POST" }
                );
                if (screenshotResponse.ok) {
                  const data = await screenshotResponse.json();
                  if (data.image) {
                    controller.enqueue(
                      encoder.encode(
                        `data: ${JSON.stringify({ screenshot: data.image })}\n\n`
                      )
                    );
                  }
                }
              } catch (e) {
                console.log("Desktop server not available for screenshot");
              }
            }

            controller.enqueue(encoder.encode("data: [DONE]\n\n"));
            controller.close();
          },
          onError: (error) => {
            controller.enqueue(
              encoder.encode(
                `data: ${JSON.stringify({ error: error.message })}\n\n`
              )
            );
            controller.close();
          },
        });
      },
    });

    return new Response(stream, {
      headers: {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        Connection: "keep-alive",
      },
    });
  } catch (error) {
    console.error("Chat API error:", error);
    return new Response(
      JSON.stringify({ error: "Internal server error" }),
      {
        status: 500,
        headers: { "Content-Type": "application/json" },
      }
    );
  }
}
