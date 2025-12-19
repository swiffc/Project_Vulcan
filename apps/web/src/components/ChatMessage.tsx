"use client";

import ReactMarkdown from "react-markdown";
import { Message } from "@/lib/types";

interface ChatMessageProps {
  message: Message;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === "user";
  const isStreaming = message.status === "streaming";
  const isError = message.status === "error";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[85%] rounded-2xl px-4 py-3 ${
          isUser
            ? "bg-vulcan-accent text-white"
            : "glass-dark"
        } ${isError ? "border border-vulcan-error/50" : ""}`}
      >
        {/* Role indicator */}
        {!isUser && (
          <div className="flex items-center gap-2 mb-2 text-xs text-white/50">
            <span className="w-5 h-5 rounded-full bg-gradient-to-br from-vulcan-accent to-purple-600 flex items-center justify-center text-[10px]">
              V
            </span>
            <span>Vulcan</span>
            {isStreaming && (
              <span className="flex items-center gap-1">
                <span className="w-1.5 h-1.5 bg-vulcan-accent rounded-full animate-pulse" />
                <span>thinking...</span>
              </span>
            )}
          </div>
        )}

        {/* Message content with markdown */}
        <div
          className={`markdown-content ${
            isStreaming ? "streaming-cursor" : ""
          }`}
        >
          <ReactMarkdown
            components={{
              // Custom rendering for status emojis
              p: ({ children }) => {
                const text = String(children);
                // Highlight status markers
                if (text.includes("✅") || text.includes("📊") || text.includes("📈") || text.includes("🛑")) {
                  return <p className="font-medium">{children}</p>;
                }
                return <p>{children}</p>;
              },
              // Code blocks with syntax highlighting style
              code: ({ className, children, ...props }) => {
                const isInline = !className;
                if (isInline) {
                  return (
                    <code className="bg-black/30 px-1.5 py-0.5 rounded text-sm font-mono text-vulcan-accent">
                      {children}
                    </code>
                  );
                }
                return (
                  <code className={className} {...props}>
                    {children}
                  </code>
                );
              },
              // Tables with glass styling
              table: ({ children }) => (
                <div className="overflow-x-auto my-2">
                  <table className="w-full border-collapse">{children}</table>
                </div>
              ),
              th: ({ children }) => (
                <th className="border border-white/10 px-3 py-2 text-left bg-white/5 font-semibold">
                  {children}
                </th>
              ),
              td: ({ children }) => (
                <td className="border border-white/10 px-3 py-2">{children}</td>
              ),
            }}
          >
            {message.content}
          </ReactMarkdown>
        </div>

        {/* Screenshot attachment */}
        {message.screenshot && (
          <div className="mt-3 rounded-lg overflow-hidden border border-white/10">
            <img
              src={`data:image/png;base64,${message.screenshot}`}
              alt="Screenshot"
              className="w-full"
            />
          </div>
        )}

        {/* Timestamp */}
        <div className="mt-2 text-xs text-white/30">
          {message.timestamp.toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          })}
        </div>
      </div>
    </div>
  );
}
