/**
 * Trading Module - Main Page
 * Unified tabbed interface with all trading functionality
 * TradingView-inspired layout with BTMM strategy integration
 */

"use client";

import { useState } from "react";
import { TradingHeader } from "@/components/trading/header";
import { LeftPanel, RightPanel } from "@/components/trading/layout";
import { TradingViewEmbed } from "@/components/trading/TradingViewEmbed";
import { Sidebar } from "@/components/layout/Sidebar";
import type { CycleDay } from "@/lib/trading/types";

// Tab Content Components
import { DashboardTab } from "@/components/trading/tabs/DashboardTab";
import { JournalTab } from "@/components/trading/tabs/JournalTab";
import { AnalysisTab } from "@/components/trading/tabs/AnalysisTab";
import { PerformanceTab } from "@/components/trading/tabs/PerformanceTab";
import { ToolsTab } from "@/components/trading/tabs/ToolsTab";
import { SettingsTab } from "@/components/trading/tabs/SettingsTab";

type TabId = "dashboard" | "journal" | "analysis" | "performance" | "tools" | "settings";

const TABS: { id: TabId; label: string; icon: string }[] = [
  { id: "dashboard", label: "Dashboard", icon: "📊" },
  { id: "journal", label: "Journal", icon: "📓" },
  { id: "analysis", label: "Analysis", icon: "📈" },
  { id: "performance", label: "Performance", icon: "🎯" },
  { id: "tools", label: "Tools", icon: "🔧" },
  { id: "settings", label: "Settings", icon: "⚙️" },
];

export default function TradingPage() {
  // Tab state
  const [activeTab, setActiveTab] = useState<TabId>("dashboard");

  // Shared state for dashboard
  const [selectedPair, setSelectedPair] = useState("EUR/USD");
  const [isAdvancedMode, setIsAdvancedMode] = useState(false);
  const [isLeftPanelCollapsed, setIsLeftPanelCollapsed] = useState(false);
  const [isRightPanelCollapsed, setIsRightPanelCollapsed] = useState(false);
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [cycleDay, setCycleDay] = useState<CycleDay>(1);
  const [selectedTimeframe, setSelectedTimeframe] = useState("1H");

  // Render active tab content
  const renderTabContent = () => {
    switch (activeTab) {
      case "dashboard":
        return (
          <DashboardView
            selectedPair={selectedPair}
            setSelectedPair={setSelectedPair}
            isAdvancedMode={isAdvancedMode}
            setIsAdvancedMode={setIsAdvancedMode}
            isLeftPanelCollapsed={isLeftPanelCollapsed}
            setIsLeftPanelCollapsed={setIsLeftPanelCollapsed}
            isRightPanelCollapsed={isRightPanelCollapsed}
            setIsRightPanelCollapsed={setIsRightPanelCollapsed}
            cycleDay={cycleDay}
            setCycleDay={setCycleDay}
            selectedTimeframe={selectedTimeframe}
            setSelectedTimeframe={setSelectedTimeframe}
            isChatOpen={isChatOpen}
            setIsChatOpen={setIsChatOpen}
          />
        );
      case "journal":
        return <JournalTab />;
      case "analysis":
        return <AnalysisTab selectedPair={selectedPair} cycleDay={cycleDay} />;
      case "performance":
        return <PerformanceTab />;
      case "tools":
        return <ToolsTab />;
      case "settings":
        return <SettingsTab />;
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-vulcan-darker flex flex-col">
      {/* Top Navigation Bar */}
      <header className="h-12 bg-vulcan-darker border-b border-white/10 flex items-center justify-between px-4">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-vulcan-accent to-purple-600 flex items-center justify-center">
            <span className="text-white text-sm font-bold">V</span>
          </div>
          <span className="text-lg font-semibold text-white">Trading</span>
        </div>

        {/* Main Tabs */}
        <nav className="flex items-center gap-1">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg transition-all ${
                activeTab === tab.id
                  ? "bg-vulcan-accent text-white"
                  : "text-white/50 hover:text-white hover:bg-white/5"
              }`}
            >
              <span>{tab.icon}</span>
              <span>{tab.label}</span>
            </button>
          ))}
        </nav>

        {/* Right Actions */}
        <div className="flex items-center gap-3">
          {/* AI Chat Toggle */}
          <button
            onClick={() => setIsChatOpen(!isChatOpen)}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-lg transition-all ${
              isChatOpen
                ? "bg-vulcan-accent text-white"
                : "bg-white/5 text-white/60 hover:bg-white/10 hover:text-white"
            }`}
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
              />
            </svg>
            <span className="text-sm font-medium">AI Chat</span>
          </button>

          {/* Current Pair Display */}
          <div className="px-3 py-1.5 bg-white/5 rounded-lg text-sm">
            <span className="text-white/40">Pair: </span>
            <span className="text-white font-medium">{selectedPair}</span>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <div className="flex-1 overflow-hidden relative">
        {renderTabContent()}

        {/* Floating AI Chat Sidebar */}
        {isChatOpen && (
          <div className="fixed right-0 top-12 bottom-0 w-96 z-50 shadow-2xl border-l border-white/10 bg-vulcan-darker">
            {/* Chat Header */}
            <div className="flex items-center justify-between px-4 py-3 border-b border-white/10 bg-vulcan-darker">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-vulcan-accent to-purple-600 flex items-center justify-center">
                  <span className="text-white text-sm font-bold">V</span>
                </div>
                <div>
                  <div className="text-sm font-medium text-white">Vulcan AI</div>
                  <div className="text-xs text-white/40">Trading Assistant</div>
                </div>
              </div>
              <button
                onClick={() => setIsChatOpen(false)}
                className="p-2 rounded-lg hover:bg-white/5 text-white/50 hover:text-white transition-colors"
              >
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* Chat Content */}
            <div className="h-[calc(100%-56px)]">
              <Sidebar agentContext="trading" />
            </div>
          </div>
        )}

        {/* Floating Chat Button (when chat is closed) */}
        {!isChatOpen && (
          <button
            onClick={() => setIsChatOpen(true)}
            className="fixed bottom-6 right-6 w-14 h-14 rounded-full bg-gradient-to-br from-vulcan-accent to-purple-600 text-white shadow-lg shadow-vulcan-accent/30 flex items-center justify-center hover:scale-105 transition-transform z-50"
            title="Open AI Chat"
          >
            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
              />
            </svg>
          </button>
        )}
      </div>
    </div>
  );
}

/* Dashboard View - Chart with Panels */
interface DashboardViewProps {
  selectedPair: string;
  setSelectedPair: (pair: string) => void;
  isAdvancedMode: boolean;
  setIsAdvancedMode: (mode: boolean) => void;
  isLeftPanelCollapsed: boolean;
  setIsLeftPanelCollapsed: (collapsed: boolean) => void;
  isRightPanelCollapsed: boolean;
  setIsRightPanelCollapsed: (collapsed: boolean) => void;
  cycleDay: CycleDay;
  setCycleDay: (day: CycleDay) => void;
  selectedTimeframe: string;
  setSelectedTimeframe: (tf: string) => void;
  isChatOpen: boolean;
  setIsChatOpen: (open: boolean) => void;
}

function DashboardView({
  selectedPair,
  setSelectedPair,
  isAdvancedMode,
  setIsAdvancedMode,
  isLeftPanelCollapsed,
  setIsLeftPanelCollapsed,
  isRightPanelCollapsed,
  setIsRightPanelCollapsed,
  cycleDay,
  setCycleDay,
  selectedTimeframe,
  setSelectedTimeframe,
}: DashboardViewProps) {
  return (
    <div className="trading-layout h-full">
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
            <TradingViewEmbed symbol={selectedPair.replace("/", "")} theme="dark" height="100%" />
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
    <span className={`px-2 py-1 text-xs font-medium rounded border ${colors[day]}`}>{labels[day]}</span>
  );
}
