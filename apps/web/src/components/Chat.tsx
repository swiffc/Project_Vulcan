"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { Message, MessageRole } from "@/lib/types";
import { ChatMessage } from "./ChatMessage";
import { ChatInput } from "./ChatInput";

const MAX_RETRIES = 3;
const RETRY_DELAY = 1000;

const DEFAULT_WELCOME =
  "Welcome to **Project Vulcan**. I'm your AI operating system for CAD automation and paper trading.\n\n" +
  "**Quick commands:**\n" +
  "- `Build flange` - Create CAD parts via SolidWorks/Inventor\n" +
  "- `Scan GBP/USD` - Analyze trading setups\n" +
  "- `Weekly review` - Generate performance summary\n\n" +
  "How can I help you today?";

// Quick command suggestions based on context
const QUICK_COMMANDS = {
  trading: [
    { label: "Scan EUR/USD", command: "Scan EUR/USD for ICT setups" },
    { label: "Weekly Review", command: "Generate my weekly trading review" },
    { label: "Risk Check", command: "Check my open positions and risk" },
    { label: "Session Times", command: "What are the key session times today?" },
  ],
  cad: [
    { label: "New Part", command: "Create a new part from template" },
    { label: "ECN Status", command: "Show pending ECN revisions" },
    { label: "Export STEP", command: "Export current assembly to STEP" },
    { label: "Check GD&T", command: "Validate GD&T on current drawing" },
  ],
  general: [
    { label: "System Status", command: "Show system status" },
    { label: "Cost Report", command: "Show today's API cost report" },
    { label: "Help", command: "What can you do?" },
    { label: "Dashboard", command: "Show me the dashboard metrics" },
  ],
};

interface ChatProps {
  agentContext?: "trading" | "cad" | "general";
  welcomeMessage?: string;
}

export function Chat({ agentContext, welcomeMessage }: ChatProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      role: "assistant",
      content: welcomeMessage || DEFAULT_WELCOME,
      timestamp: new Date(),
      status: "complete",
    },
  ]);
  const [isStreaming, setIsStreaming] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const streamWithRetry = useCallback(
    async (
      messagePayload: { role: string; content: string }[],
      assistantMessageId: string,
      retryCount = 0
    ): Promise<boolean> => {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 60000);

        const response = await fetch("/api/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ messages: messagePayload, agentContext }),
          signal: controller.signal,
        });

        clearTimeout(timeoutId);

        if (!response.ok) throw new Error(`HTTP ${response.status}`);

        const reader = response.body?.getReader();
        const decoder = new TextDecoder();
        let fullContent = "";

        if (reader) {
          while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value, { stream: true });
            const lines = chunk.split("\n");

            for (const line of lines) {
              if (line.startsWith("data: ")) {
                const data = line.slice(6);
                if (data === "[DONE]") continue;

                try {
                  const parsed = JSON.parse(data);
                  if (parsed.content) {
                    fullContent += parsed.content;
                    setMessages((prev) =>
                      prev.map((m) =>
                        m.id === assistantMessageId
                          ? { ...m, content: fullContent }
                          : m
                      )
                    );
                  }
                  if (parsed.screenshot) {
                    setMessages((prev) =>
                      prev.map((m) =>
                        m.id === assistantMessageId
                          ? { ...m, screenshot: parsed.screenshot }
                          : m
                      )
                    );
                  }
                } catch {
                  // Skip invalid JSON
                }
              }
            }
          }
        }

        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantMessageId ? { ...m, status: "complete" } : m
          )
        );
        return true;
      } catch (error) {
        console.error(`Stream attempt ${retryCount + 1} failed:`, error);

        if (retryCount < MAX_RETRIES) {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantMessageId
                ? { ...m, content: `Reconnecting... (attempt ${retryCount + 2}/${MAX_RETRIES + 1})` }
                : m
            )
          );
          await new Promise((r) => setTimeout(r, RETRY_DELAY * (retryCount + 1)));
          return streamWithRetry(messagePayload, assistantMessageId, retryCount + 1);
        }
        return false;
      }
    },
    []
  );

  const handleSendMessage = async (content: string) => {
    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: "user",
      content,
      timestamp: new Date(),
      status: "complete",
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsStreaming(true);

    const assistantMessageId = `assistant-${Date.now()}`;
    const assistantMessage: Message = {
      id: assistantMessageId,
      role: "assistant",
      content: "",
      timestamp: new Date(),
      status: "streaming",
    };

    setMessages((prev) => [...prev, assistantMessage]);

    const messagePayload = [...messages, userMessage].map((m) => ({
      role: m.role,
      content: m.content,
    }));

    const success = await streamWithRetry(messagePayload, assistantMessageId);

    if (!success) {
      setMessages((prev) =>
        prev.map((m) =>
          m.id === assistantMessageId
            ? {
                ...m,
                content: "Connection failed after multiple attempts. Please check your network and try again.",
                status: "error",
              }
            : m
        )
      );
    }

    setIsStreaming(false);
  };

  const context = agentContext || "general";
  const quickCommands = QUICK_COMMANDS[context];
  const showQuickCommands = messages.length <= 2 && !isStreaming;

  return (
    <div className="flex flex-col flex-1 gap-4">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-4 pb-4">
        {messages.map((message) => (
          <ChatMessage key={message.id} message={message} />
        ))}

        {/* Typing indicator */}
        {isStreaming && (
          <div className="flex justify-start">
            <div className="glass-dark rounded-2xl px-4 py-3">
              <div className="flex items-center gap-2">
                <div className="flex gap-1">
                  <span className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                  <span className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                  <span className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
                </div>
                <span className="text-xs text-white/40">Vulcan is thinking...</span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Quick Commands */}
      {showQuickCommands && (
        <div className="flex flex-wrap gap-2 px-2">
          {quickCommands.map((cmd) => (
            <button
              key={cmd.label}
              onClick={() => handleSendMessage(cmd.command)}
              className="px-3 py-1.5 rounded-full text-xs font-medium glass hover-lift
                         text-white/70 hover:text-white border border-white/10
                         hover:border-indigo-400/50 transition-all"
            >
              {cmd.label}
            </button>
          ))}
        </div>
      )}

      {/* Input */}
      <ChatInput onSend={handleSendMessage} disabled={isStreaming} />

      {/* Model indicator */}
      <div className="flex items-center justify-center gap-2 text-xs text-white/30">
        <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
        <span>Cost-optimized routing active</span>
        <span className="text-white/20">|</span>
        <span>Haiku for simple, Sonnet for complex</span>
      </div>
    </div>
  );
}
