/**
 * Left Panel Component
 * Collapsible panel with watchlist, cycle day, and session info
 */

"use client";

import { useState } from "react";
import type { CycleDay, BTMMLevel, SessionName } from "@/lib/trading/types";
import { CYCLE_DAY_INFO, LEVEL_INFO, TRADING_PAIRS } from "@/lib/trading/constants";

interface LeftPanelProps {
  isCollapsed: boolean;
  onToggleCollapse: () => void;
  selectedPair: string;
  onPairSelect: (pair: string) => void;
  cycleDay: CycleDay;
  onCycleDayChange: (day: CycleDay) => void;
}

export function LeftPanel({
  isCollapsed,
  onToggleCollapse,
  selectedPair,
  onPairSelect,
  cycleDay,
  onCycleDayChange,
}: LeftPanelProps) {
  const [activeTab, setActiveTab] = useState<"watchlist" | "analysis" | "notes">("watchlist");

  return (
    <aside
      className={`trading-left-panel flex flex-col border-r border-white/10 bg-vulcan-darker/50 transition-all duration-300 ${
        isCollapsed ? "w-12" : "w-72"
      }`}
    >
      {/* Collapse Toggle */}
      <button
        onClick={onToggleCollapse}
        className="flex items-center justify-center h-10 border-b border-white/10 hover:bg-white/5 transition-colors"
      >
        <svg
          className={`w-4 h-4 text-white/50 transition-transform ${isCollapsed ? "rotate-180" : ""}`}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
        </svg>
      </button>

      {!isCollapsed && (
        <>
          {/* Cycle Day Selector */}
          <div className="p-3 border-b border-white/10">
            <div className="text-xs text-white/40 uppercase tracking-wider mb-2">3-Day Cycle</div>
            <div className="flex gap-1">
              {([1, 2, 3] as CycleDay[]).map((day) => (
                <button
                  key={day}
                  onClick={() => onCycleDayChange(day)}
                  className={`flex-1 py-2 rounded-lg text-sm font-medium transition-all ${
                    cycleDay === day
                      ? day === 1
                        ? "bg-yellow-500/20 text-yellow-400 border border-yellow-500/30"
                        : day === 2
                        ? "bg-orange-500/20 text-orange-400 border border-orange-500/30"
                        : "bg-green-500/20 text-green-400 border border-green-500/30"
                      : "bg-white/5 text-white/50 hover:bg-white/10"
                  }`}
                  title={CYCLE_DAY_INFO[day].description}
                >
                  D{day}
                </button>
              ))}
            </div>
            <div className="mt-2 text-xs text-white/40">
              {CYCLE_DAY_INFO[cycleDay].name}
            </div>
          </div>

          {/* Level Quick Select */}
          <div className="p-3 border-b border-white/10">
            <div className="text-xs text-white/40 uppercase tracking-wider mb-2">Level Focus</div>
            <div className="flex gap-1">
              {(["I", "II", "III"] as BTMMLevel[]).map((level) => (
                <button
                  key={level}
                  className="flex-1 py-1.5 rounded-lg text-xs font-medium bg-white/5 text-white/50 hover:bg-white/10 transition-all"
                  style={{ borderLeft: `3px solid ${LEVEL_INFO[level].color}` }}
                  title={LEVEL_INFO[level].description}
                >
                  {level}
                </button>
              ))}
            </div>
          </div>

          {/* Tabs */}
          <div className="flex border-b border-white/10">
            {(["watchlist", "analysis", "notes"] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`flex-1 py-2 text-xs font-medium uppercase tracking-wider transition-all ${
                  activeTab === tab
                    ? "text-vulcan-accent border-b-2 border-vulcan-accent"
                    : "text-white/40 hover:text-white/60"
                }`}
              >
                {tab}
              </button>
            ))}
          </div>

          {/* Tab Content */}
          <div className="flex-1 overflow-y-auto">
            {activeTab === "watchlist" && (
              <WatchlistTab selectedPair={selectedPair} onPairSelect={onPairSelect} />
            )}
            {activeTab === "analysis" && <AnalysisTab cycleDay={cycleDay} />}
            {activeTab === "notes" && <NotesTab />}
          </div>
        </>
      )}

      {/* Collapsed View - Icon Only */}
      {isCollapsed && (
        <div className="flex flex-col items-center gap-3 py-4">
          <button
            className="w-8 h-8 rounded-lg bg-white/5 hover:bg-white/10 flex items-center justify-center text-white/50 hover:text-white transition-all"
            title="Watchlist"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 10h16M4 14h16M4 18h16" />
            </svg>
          </button>
          <button
            className="w-8 h-8 rounded-lg bg-white/5 hover:bg-white/10 flex items-center justify-center text-white/50 hover:text-white transition-all"
            title="Analysis"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </button>
          <button
            className="w-8 h-8 rounded-lg bg-white/5 hover:bg-white/10 flex items-center justify-center text-white/50 hover:text-white transition-all"
            title="Notes"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
          </button>
        </div>
      )}
    </aside>
  );
}

function WatchlistTab({
  selectedPair,
  onPairSelect,
}: {
  selectedPair: string;
  onPairSelect: (pair: string) => void;
}) {
  const watchlistPairs = TRADING_PAIRS.filter((p) =>
    ["EUR/USD", "GBP/USD", "USD/JPY", "EUR/JPY", "GBP/JPY", "AUD/USD"].includes(p.symbol)
  );

  return (
    <div className="p-2">
      {watchlistPairs.map((pair) => (
        <button
          key={pair.symbol}
          onClick={() => onPairSelect(pair.symbol)}
          className={`w-full flex items-center justify-between px-3 py-2 rounded-lg transition-all ${
            selectedPair === pair.symbol
              ? "bg-vulcan-accent/20 border border-vulcan-accent/30"
              : "hover:bg-white/5"
          }`}
        >
          <div className="flex items-center gap-2">
            <div
              className={`w-2 h-2 rounded-full ${
                Math.random() > 0.5 ? "bg-trading-bullish" : "bg-trading-bearish"
              }`}
            />
            <span className="text-sm font-medium text-white">{pair.symbol}</span>
          </div>
          <span className="text-xs text-white/40">ADR: {pair.typicalADR}</span>
        </button>
      ))}

      {/* Add Pair Button */}
      <button className="w-full mt-2 py-2 border border-dashed border-white/20 rounded-lg text-white/40 text-sm hover:border-white/40 hover:text-white/60 transition-all">
        + Add Pair
      </button>
    </div>
  );
}

function AnalysisTab({ cycleDay }: { cycleDay: CycleDay }) {
  const info = CYCLE_DAY_INFO[cycleDay];

  return (
    <div className="p-3 space-y-4">
      {/* Cycle Day Info */}
      <div className="glass rounded-lg p-3">
        <div className="text-sm font-medium text-white mb-1">{info.name}</div>
        <div className="text-xs text-white/50 mb-2">{info.description}</div>
        <div className="text-xs text-white/40">
          <span className="text-white/60">Typical:</span> {info.typical}
        </div>
        <div className="text-xs text-trading-bullish mt-1">
          <span className="text-white/60">Strategy:</span> {info.strategy}
        </div>
      </div>

      {/* Quick Checklist */}
      <div>
        <div className="text-xs text-white/40 uppercase tracking-wider mb-2">Quick Check</div>
        <div className="space-y-1.5">
          {["Session Active", "Kill Zone", "Level Identified", "TDI Aligned"].map((item) => (
            <div key={item} className="flex items-center gap-2 text-sm text-white/60">
              <div className="w-4 h-4 rounded border border-white/20" />
              {item}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function NotesTab() {
  return (
    <div className="p-3">
      <textarea
        className="w-full h-48 p-3 bg-white/5 border border-white/10 rounded-lg text-sm text-white placeholder-white/30 resize-none focus:outline-none focus:border-vulcan-accent"
        placeholder="Trading notes for today..."
      />
      <div className="flex justify-end mt-2">
        <button className="px-3 py-1.5 text-xs font-medium bg-vulcan-accent text-white rounded-lg hover:bg-vulcan-accent/80 transition-colors">
          Save Notes
        </button>
      </div>
    </div>
  );
}
