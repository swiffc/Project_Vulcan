/**
 * Live Session Analysis Page
 * Real-time session monitoring and key levels
 */

"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import type { SessionName } from "@/lib/trading/types";
import { SESSIONS, KILL_ZONES, TRUE_OPENS } from "@/lib/trading/constants";

export default function LiveAnalysisPage() {
  const [currentTime, setCurrentTime] = useState(new Date());
  const [selectedPair, setSelectedPair] = useState("EUR/USD");

  useEffect(() => {
    const interval = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(interval);
  }, []);

  const getCurrentSession = (): SessionName => {
    const hour = currentTime.getHours();
    if (hour >= 19 || hour < 2) return "asian";
    if (hour >= 2 && hour < 8) return "london";
    if (hour >= 8 && hour < 17) return "newyork";
    return "gap";
  };

  const isInKillZone = (): { active: boolean; zone: string | null } => {
    const hour = currentTime.getHours();
    if (hour >= 2 && hour < 5) return { active: true, zone: "London Kill Zone" };
    if (hour >= 8 && hour < 11) return { active: true, zone: "NY Kill Zone" };
    if (hour >= 0 && hour < 1) return { active: true, zone: "Asian Close" };
    return { active: false, zone: null };
  };

  const currentSession = getCurrentSession();
  const killZone = isInKillZone();

  // Mock price levels
  const levels = {
    asianHigh: 1.0985,
    asianLow: 1.0945,
    previousHigh: 1.1010,
    previousLow: 1.0920,
    weeklyOpen: 1.0960,
    currentPrice: 1.0972,
  };

  return (
    <div className="min-h-screen bg-vulcan-darker p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <Link href="/trading/analysis" className="text-vulcan-accent text-sm hover:underline mb-2 inline-block">
            &larr; Back to Analysis
          </Link>
          <h1 className="text-2xl font-bold text-white">Live Session Analysis</h1>
          <p className="text-white/50">Real-time market monitoring</p>
        </div>

        <div className="flex items-center gap-4">
          <select
            value={selectedPair}
            onChange={(e) => setSelectedPair(e.target.value)}
            className="trading-input"
          >
            <option value="EUR/USD">EUR/USD</option>
            <option value="GBP/USD">GBP/USD</option>
            <option value="USD/JPY">USD/JPY</option>
          </select>
        </div>
      </div>

      {/* Session Status Bar */}
      <div className="glass rounded-xl p-4 mb-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-6">
            {/* Current Session */}
            <div className="flex items-center gap-3">
              <div
                className="w-3 h-3 rounded-full animate-pulse"
                style={{ backgroundColor: SESSIONS[currentSession].color }}
              />
              <div>
                <div className="text-xs text-white/40">Current Session</div>
                <div className="text-lg font-semibold text-white capitalize">{currentSession}</div>
              </div>
            </div>

            {/* Kill Zone Status */}
            {killZone.active && (
              <div className="px-4 py-2 bg-trading-bullish/20 border border-trading-bullish/30 rounded-lg">
                <div className="text-xs text-trading-bullish/70">Active Kill Zone</div>
                <div className="text-sm font-semibold text-trading-bullish">{killZone.zone}</div>
              </div>
            )}
          </div>

          {/* Time Display */}
          <div className="text-right">
            <div className="text-xs text-white/40">EST Time</div>
            <div className="text-2xl font-mono text-white">
              {currentTime.toLocaleTimeString("en-US", { timeZone: "America/New_York", hour12: false })}
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-6">
        {/* Left - Key Levels */}
        <div className="col-span-2">
          <div className="glass rounded-xl p-6">
            <h2 className="text-lg font-semibold text-white mb-4">Key Price Levels</h2>

            {/* Price Ladder Visualization */}
            <div className="relative h-80 bg-white/5 rounded-lg p-4">
              {/* Level Markers */}
              <LevelMarker level={levels.previousHigh} label="Previous High" color="#f85149" position={15} />
              <LevelMarker level={levels.asianHigh} label="Asian High" color="#a371f7" position={30} />
              <LevelMarker level={levels.weeklyOpen} label="Weekly Open" color="#58a6ff" position={50} />
              <LevelMarker level={levels.asianLow} label="Asian Low" color="#a371f7" position={70} />
              <LevelMarker level={levels.previousLow} label="Previous Low" color="#3fb950" position={85} />

              {/* Current Price */}
              <div
                className="absolute left-0 right-0 flex items-center gap-2"
                style={{ top: "45%" }}
              >
                <div className="flex-1 h-0.5 bg-vulcan-accent" />
                <div className="px-3 py-1.5 bg-vulcan-accent text-white text-sm font-mono font-bold rounded">
                  {levels.currentPrice.toFixed(4)}
                </div>
                <div className="flex-1 h-0.5 bg-vulcan-accent" />
              </div>
            </div>
          </div>

          {/* Session Progress */}
          <div className="glass rounded-xl p-6 mt-6">
            <h2 className="text-lg font-semibold text-white mb-4">Session Progress</h2>
            <div className="space-y-4">
              {(Object.entries(SESSIONS) as [SessionName, typeof SESSIONS[SessionName]][]).map(
                ([name, session]) => {
                  const isActive = currentSession === name;
                  return (
                    <div key={name} className="flex items-center gap-4">
                      <div
                        className={`w-24 text-sm font-medium capitalize ${
                          isActive ? "text-white" : "text-white/40"
                        }`}
                      >
                        {name}
                      </div>
                      <div className="flex-1 h-2 bg-white/10 rounded-full overflow-hidden">
                        <div
                          className={`h-full transition-all duration-1000 ${
                            isActive ? "animate-pulse" : ""
                          }`}
                          style={{
                            width: isActive ? "60%" : "100%",
                            backgroundColor: isActive ? session.color : session.color + "40",
                          }}
                        />
                      </div>
                      <div className="text-xs text-white/40 w-24 text-right">
                        {session.start} - {session.end}
                      </div>
                    </div>
                  );
                }
              )}
            </div>
          </div>
        </div>

        {/* Right - Live Stats */}
        <div className="space-y-6">
          {/* Range Stats */}
          <div className="glass rounded-xl p-6">
            <h3 className="text-sm font-semibold text-white/60 uppercase tracking-wider mb-4">Range Stats</h3>
            <div className="space-y-3">
              <StatRow label="Asian Range" value="40 pips" />
              <StatRow label="London Range" value="65 pips" />
              <StatRow label="NY Range" value="45 pips" />
              <StatRow label="Today's ADR" value="78 pips" />
              <StatRow label="ADR % Used" value="72%" />
            </div>
          </div>

          {/* MM Activity */}
          <div className="glass rounded-xl p-6">
            <h3 className="text-sm font-semibold text-white/60 uppercase tracking-wider mb-4">MM Activity</h3>
            <div className="space-y-3">
              <div className="p-3 bg-orange-500/10 border border-orange-500/20 rounded-lg">
                <div className="text-xs text-orange-400/70">Detected Pattern</div>
                <div className="text-sm font-medium text-orange-400">Stop Hunt Below Asian Low</div>
              </div>
              <div className="p-3 bg-white/5 rounded-lg">
                <div className="text-xs text-white/40">Last Trap</div>
                <div className="text-sm text-white">08:15 EST - Bear Trap at 1.0948</div>
              </div>
            </div>
          </div>

          {/* Quick Notes */}
          <div className="glass rounded-xl p-6">
            <h3 className="text-sm font-semibold text-white/60 uppercase tracking-wider mb-4">Session Notes</h3>
            <textarea
              className="w-full h-32 trading-input resize-none"
              placeholder="Add notes about current session..."
            />
          </div>
        </div>
      </div>
    </div>
  );
}

function LevelMarker({
  level,
  label,
  color,
  position,
}: {
  level: number;
  label: string;
  color: string;
  position: number;
}) {
  return (
    <div
      className="absolute left-0 right-0 flex items-center gap-2"
      style={{ top: `${position}%` }}
    >
      <div className="flex-1 h-px" style={{ backgroundColor: color + "60" }} />
      <div
        className="px-2 py-1 text-xs font-mono rounded"
        style={{ backgroundColor: color + "20", color }}
      >
        {level.toFixed(4)}
      </div>
      <div className="text-xs" style={{ color: color + "80" }}>
        {label}
      </div>
      <div className="flex-1 h-px" style={{ backgroundColor: color + "60" }} />
    </div>
  );
}

function StatRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between items-center py-2 border-b border-white/5 last:border-0">
      <span className="text-white/40 text-sm">{label}</span>
      <span className="text-white font-mono font-medium">{value}</span>
    </div>
  );
}
