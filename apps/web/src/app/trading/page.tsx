/**
 * Trading Module - Main Page
 * TradingView-inspired layout with BTMM strategy integration
 * Phase 14 Redesign - Week 1 Foundation
 */

"use client";

import { useState } from "react";
import { TradingHeader } from "@/components/trading/header";
import { LeftPanel } from "@/components/trading/layout";
import { TradingViewEmbed } from "@/components/trading/TradingViewEmbed";
import { Sidebar } from "@/components/layout/Sidebar";
import type { CycleDay } from "@/lib/trading/types";

export default function TradingPage() {
  // State management
  const [selectedPair, setSelectedPair] = useState("EUR/USD");
  const [isAdvancedMode, setIsAdvancedMode] = useState(false);
  const [isLeftPanelCollapsed, setIsLeftPanelCollapsed] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [cycleDay, setCycleDay] = useState<CycleDay>(1);

  return (
    <div className="trading-layout">
      {/* Header */}
      <TradingHeader
        selectedPair={selectedPair}
        onPairChange={setSelectedPair}
        isAdvancedMode={isAdvancedMode}
        onModeToggle={() => setIsAdvancedMode(!isAdvancedMode)}
      />

      {/* Left Panel */}
      <LeftPanel
        isCollapsed={isLeftPanelCollapsed}
        onToggleCollapse={() => setIsLeftPanelCollapsed(!isLeftPanelCollapsed)}
        selectedPair={selectedPair}
        onPairSelect={setSelectedPair}
        cycleDay={cycleDay}
        onCycleDayChange={setCycleDay}
      />

      {/* Main Content Area */}
      <main className="trading-main flex flex-col bg-vulcan-darker/30 overflow-hidden">
        {/* Chart Area */}
        <div className="flex-1 p-2">
          <div className="h-full w-full rounded-lg overflow-hidden border border-white/10">
            <TradingViewEmbed
              symbol={selectedPair.replace("/", "")}
              theme="dark"
              height="100%"
            />
          </div>
        </div>

        {/* Bottom Bar - Quick Actions */}
        <div className="h-14 border-t border-white/10 flex items-center justify-between px-4 bg-vulcan-darker/50">
          <div className="flex items-center gap-4">
            {/* Timeframe Selector */}
            <div className="flex items-center gap-1">
              {["1m", "5m", "15m", "1H", "4H", "1D"].map((tf) => (
                <button
                  key={tf}
                  className={`px-2.5 py-1 text-xs font-medium rounded transition-all ${
                    tf === "1H"
                      ? "bg-vulcan-accent text-white"
                      : "text-white/50 hover:text-white hover:bg-white/5"
                  }`}
                >
                  {tf}
                </button>
              ))}
            </div>

            {/* Cycle Day Badge */}
            <CycleDayBadge day={cycleDay} />

            {/* Mode Indicator */}
            <span className={`text-xs font-medium ${isAdvancedMode ? "text-vulcan-accent" : "text-white/40"}`}>
              {isAdvancedMode ? "Advanced" : "Basic"}
            </span>
          </div>

          {/* Trade Actions */}
          <div className="flex items-center gap-3">
            {/* Chat Toggle */}
            <button
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              className="p-2 rounded-lg hover:bg-white/5 text-white/50 hover:text-white transition-all"
              title="Open AI Assistant"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
            </button>

            {/* Trade Buttons */}
            <button className="trading-btn-sell text-white text-sm">
              SELL
            </button>
            <button className="trading-btn-buy text-white text-sm">
              BUY
            </button>
          </div>
        </div>
      </main>

      {/* Right Sidebar - AI Chat (conditionally rendered) */}
      {isSidebarOpen && (
        <aside className="trading-right-panel w-80 border-l border-white/10">
          <Sidebar agentContext="trading" />
        </aside>
      )}
    </div>
  );
}

function CycleDayBadge({ day }: { day: CycleDay }) {
  const colors = {
    1: "bg-yellow-500/20 text-yellow-400 border-yellow-500/30",
    2: "bg-orange-500/20 text-orange-400 border-orange-500/30",
    3: "bg-green-500/20 text-green-400 border-green-500/30",
  };

  const labels = {
    1: "D1 Accum",
    2: "D2 Manip",
    3: "D3 Dist",
  };

  return (
    <span className={`px-2 py-1 text-xs font-medium rounded border ${colors[day]}`}>
      {labels[day]}
    </span>
  );
}
