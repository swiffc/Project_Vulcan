/**
 * Trading Module - Main Page
 * TradingView-inspired layout with BTMM strategy integration
 * Phase 14 Redesign - Week 2 Trade Entry
 */

"use client";

import { useState } from "react";
import { TradingHeader } from "@/components/trading/header";
import { LeftPanel, RightPanel } from "@/components/trading/layout";
import { TradingViewEmbed } from "@/components/trading/TradingViewEmbed";
import type { CycleDay } from "@/lib/trading/types";

export default function TradingPage() {
  // State management
  const [selectedPair, setSelectedPair] = useState("EUR/USD");
  const [isAdvancedMode, setIsAdvancedMode] = useState(false);
  const [isLeftPanelCollapsed, setIsLeftPanelCollapsed] = useState(false);
  const [isRightPanelCollapsed, setIsRightPanelCollapsed] = useState(false);
  const [cycleDay, setCycleDay] = useState<CycleDay>(1);
  const [selectedTimeframe, setSelectedTimeframe] = useState("1H");

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
        <div className="h-12 border-t border-white/10 flex items-center justify-between px-4 bg-vulcan-darker/50">
          <div className="flex items-center gap-4">
            {/* Timeframe Selector */}
            <div className="flex items-center gap-1">
              {["1m", "5m", "15m", "1H", "4H", "1D"].map((tf) => (
                <button
                  key={tf}
                  onClick={() => setSelectedTimeframe(tf)}
                  className={`px-2.5 py-1 text-xs font-medium rounded transition-all ${
                    selectedTimeframe === tf
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

          {/* Quick Info */}
          <div className="flex items-center gap-4 text-xs">
            <div className="text-white/40">
              <span className="text-white/60">Pair: </span>
              <span className="text-white font-medium">{selectedPair}</span>
            </div>
            <div className="text-white/40">
              <span className="text-white/60">TF: </span>
              <span className="text-white font-medium">{selectedTimeframe}</span>
            </div>
          </div>
        </div>
      </main>

      {/* Right Panel - Trade Entry */}
      <RightPanel
        isCollapsed={isRightPanelCollapsed}
        onToggleCollapse={() => setIsRightPanelCollapsed(!isRightPanelCollapsed)}
        selectedPair={selectedPair}
        cycleDay={cycleDay}
      />
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
