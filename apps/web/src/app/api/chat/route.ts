import { NextRequest } from "next/server";
import { orchestrate } from "@/lib/orchestrator";
import { streamChat, ChatMessage } from "@/lib/claude-client";

export const runtime = "nodejs";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const messages: ChatMessage[] = body.messages || [];

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

        await streamChat(messages, systemPrompt, {
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
