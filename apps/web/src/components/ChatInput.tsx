"use client";

import { useState, useRef, useEffect } from "react";

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

export function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [input, setInput] = useState("");
  const [isListening, setIsListening] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(
        textareaRef.current.scrollHeight,
        200
      )}px`;
    }
  }, [input]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !disabled) {
      onSend(input.trim());
      setInput("");
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  // Voice input (Web Speech API)
  const toggleVoiceInput = () => {
    if (!("webkitSpeechRecognition" in window || "SpeechRecognition" in window)) {
      alert("Voice input not supported in this browser");
      return;
    }

    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    const recognition = new SpeechRecognition();

    if (isListening) {
      recognition.stop();
      setIsListening(false);
      return;
    }

    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = "en-US";

    recognition.onstart = () => setIsListening(true);
    recognition.onend = () => setIsListening(false);
    recognition.onerror = () => setIsListening(false);

    recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      setInput((prev) => prev + transcript);
    };

    recognition.start();
  };

  return (
    <form onSubmit={handleSubmit} className="relative">
      <div className="glass rounded-2xl p-2 flex items-end gap-2">
        {/* Voice input button */}
        <button
          type="button"
          onClick={toggleVoiceInput}
          className={`p-2 rounded-xl transition-colors ${
            isListening
              ? "bg-vulcan-error text-white"
              : "hover:bg-white/10 text-white/50 hover:text-white"
          }`}
          title="Voice input"
        >
          <svg
            className="w-5 h-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
            />
          </svg>
        </button>

        {/* Text input */}
        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={
            disabled ? "Waiting for response..." : "Message Vulcan..."
          }
          disabled={disabled}
          rows={1}
          className="flex-1 bg-transparent border-none outline-none resize-none text-white placeholder:text-white/30 py-2 px-2 max-h-[200px]"
        />

        {/* Send button */}
        <button
          type="submit"
          disabled={disabled || !input.trim()}
          className={`p-2 rounded-xl transition-all ${
            input.trim() && !disabled
              ? "bg-vulcan-accent text-white hover:bg-vulcan-accent/80"
              : "bg-white/5 text-white/30"
          }`}
        >
          <svg
            className="w-5 h-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
            />
          </svg>
        </button>
      </div>

      {isListening && (
        <div className="absolute -top-8 left-1/2 -translate-x-1/2 bg-vulcan-error/90 text-white text-xs px-3 py-1 rounded-full flex items-center gap-2">
          <span className="w-2 h-2 bg-white rounded-full animate-pulse" />
          Listening...
        </div>
      )}
    </form>
  );
}
