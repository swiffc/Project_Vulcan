/**
 * Claude API Client
 *
 * Thin wrapper around Anthropic SDK with streaming support.
 * Falls back to Ollama if Claude is unavailable.
 */

import Anthropic from "@anthropic-ai/sdk";

const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY || "",
});

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface StreamCallbacks {
  onToken: (token: string) => void;
  onComplete: (fullResponse: string) => void;
  onError: (error: Error) => void;
}

/**
 * Stream a chat response from Claude
 */
export async function streamChat(
  messages: ChatMessage[],
  systemPrompt: string,
  callbacks: StreamCallbacks
): Promise<void> {
  try {
    const stream = await anthropic.messages.stream({
      model: "claude-sonnet-4-20250514",
      max_tokens: 4096,
      system: systemPrompt,
      messages: messages.map((m) => ({
        role: m.role,
        content: m.content,
      })),
    });

    let fullResponse = "";

    for await (const event of stream) {
      if (
        event.type === "content_block_delta" &&
        event.delta.type === "text_delta"
      ) {
        const token = event.delta.text;
        fullResponse += token;
        callbacks.onToken(token);
      }
    }

    callbacks.onComplete(fullResponse);
  } catch (error) {
    console.error("Claude API error:", error);

    // Try Ollama fallback
    try {
      await streamOllama(messages, systemPrompt, callbacks);
    } catch (ollamaError) {
      callbacks.onError(error as Error);
    }
  }
}

/**
 * Ollama fallback for local LLM
 */
async function streamOllama(
  messages: ChatMessage[],
  systemPrompt: string,
  callbacks: StreamCallbacks
): Promise<void> {
  const ollamaUrl = process.env.OLLAMA_URL || "http://localhost:11434";

  const response = await fetch(`${ollamaUrl}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      model: "llama3.2",
      messages: [
        { role: "system", content: systemPrompt },
        ...messages.map((m) => ({ role: m.role, content: m.content })),
      ],
      stream: true,
    }),
  });

  if (!response.ok) {
    throw new Error("Ollama request failed");
  }

  const reader = response.body?.getReader();
  const decoder = new TextDecoder();
  let fullResponse = "";

  if (reader) {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value, { stream: true });
      const lines = chunk.split("\n").filter((l) => l.trim());

      for (const line of lines) {
        try {
          const data = JSON.parse(line);
          if (data.message?.content) {
            const token = data.message.content;
            fullResponse += token;
            callbacks.onToken(token);
          }
        } catch {
          // Skip invalid JSON
        }
      }
    }
  }

  callbacks.onComplete(fullResponse);
}

/**
 * Non-streaming chat (for simple queries)
 */
export async function chat(
  messages: ChatMessage[],
  systemPrompt: string
): Promise<string> {
  try {
    const response = await anthropic.messages.create({
      model: "claude-sonnet-4-20250514",
      max_tokens: 4096,
      system: systemPrompt,
      messages: messages.map((m) => ({
        role: m.role,
        content: m.content,
      })),
    });

    const content = response.content[0];
    if (content.type === "text") {
      return content.text;
    }
    return "";
  } catch (error) {
    console.error("Claude API error:", error);
    throw error;
  }
}
