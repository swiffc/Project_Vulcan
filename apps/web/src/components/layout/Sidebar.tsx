"use client";

import { useState, useEffect } from "react";
import { Chat } from "../Chat";
import { Button } from "../ui/Button";

interface SidebarProps {
  agentContext: "trading" | "cad" | "general";
  defaultCollapsed?: boolean;
}

const contextConfig = {
  trading: {
    title: "Trading Assistant",
    subtitle: "ICT/BTMM Analysis",
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
      </svg>
    ),
    welcomeMessage: "I'm your trading assistant. I can help with:\n\n- **Market Analysis** (ICT/BTMM setups)\n- **Pair Scanning** (GBP/USD, EUR/USD, etc.)\n- **Trade Journaling**\n- **Performance Review**\n\nWhat would you like to analyze?",
  },
  cad: {
    title: "CAD Assistant",
    subtitle: "SolidWorks/Inventor",
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
      </svg>
    ),
    welcomeMessage: "I'm your CAD assistant. I can help with:\n\n- **PDF to Part** (dimension extraction)\n- **SolidWorks/Inventor** automation\n- **ECN Tracking**\n- **Export to Drive**\n\nUpload a drawing or describe what you need.",
  },
  general: {
    title: "Vulcan Assistant",
    subtitle: "General Help",
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
      </svg>
    ),
    welcomeMessage: "Welcome to Project Vulcan. How can I help you today?",
  },
};

export function Sidebar({ agentContext, defaultCollapsed = false }: SidebarProps) {
  const [isCollapsed, setIsCollapsed] = useState(defaultCollapsed);
  const config = contextConfig[agentContext];

  // Persist collapse state
  useEffect(() => {
    const saved = localStorage.getItem(`sidebar-${agentContext}-collapsed`);
    if (saved !== null) {
      setIsCollapsed(saved === "true");
    }
  }, [agentContext]);

  const toggleCollapse = () => {
    const newState = !isCollapsed;
    setIsCollapsed(newState);
    localStorage.setItem(`sidebar-${agentContext}-collapsed`, String(newState));
  };

  return (
    <div
      className={`flex flex-col h-full transition-all duration-300 ${
        isCollapsed ? "w-16" : "w-[400px]"
      }`}
    >
      {/* Header */}
      <div className="glass border-b border-white/10 p-3 flex items-center justify-between">
        {!isCollapsed && (
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-vulcan-accent/20 flex items-center justify-center text-vulcan-accent">
              {config.icon}
            </div>
            <div>
              <h3 className="text-sm font-semibold text-white">{config.title}</h3>
              <p className="text-xs text-white/40">{config.subtitle}</p>
            </div>
          </div>
        )}

        <Button
          variant="ghost"
          size="sm"
          onClick={toggleCollapse}
          className={isCollapsed ? "mx-auto" : ""}
        >
          <svg
            className={`w-5 h-5 transition-transform ${isCollapsed ? "rotate-180" : ""}`}
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M11 19l-7-7 7-7m8 14l-7-7 7-7"
            />
          </svg>
        </Button>
      </div>

      {/* Chat Content */}
      {!isCollapsed && (
        <div className="flex-1 flex flex-col min-h-0 p-3">
          <Chat agentContext={agentContext} welcomeMessage={config.welcomeMessage} />
        </div>
      )}

      {/* Collapsed State - Icon Only */}
      {isCollapsed && (
        <div className="flex-1 flex flex-col items-center py-4 gap-4">
          <button
            onClick={toggleCollapse}
            className="w-10 h-10 rounded-xl bg-vulcan-accent/20 flex items-center justify-center text-vulcan-accent hover:bg-vulcan-accent/30 transition-colors"
            title={`Open ${config.title}`}
          >
            {config.icon}
          </button>
        </div>
      )}
    </div>
  );
}
