/**
 * Analysis Tab Component
 * Market analysis with session, daily, weekly views
 */

"use client";

import { useState, useEffect } from "react";
import type { CycleDay, BTMMLevel, SessionName } from "@/lib/trading/types";
import { SESSIONS, CYCLE_DAY_INFO, LEVEL_INFO } from "@/lib/trading/constants";

interface AnalysisTabProps {
  selectedPair: string;
  cycleDay: CycleDay;
}

type AnalysisView = "live" | "daily" | "weekly" | "monthly";

export function AnalysisTab({ selectedPair, cycleDay }: AnalysisTabProps) {
  const [view, setView] = useState<AnalysisView>("live");
  const [currentTime, setCurrentTime] = useState(new Date());

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

  const currentSession = getCurrentSession();

  return (
    <div className="h-full overflow-auto p-6">
      {/* Header with View Switcher */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-bold text-white">Market Analysis</h2>
          <p className="text-white/50 text-sm">BTMM analysis for {selectedPair}</p>
        </div>

        <div className="flex gap-2">
          {(["live", "daily", "weekly", "monthly"] as AnalysisView[]).map((v) => (
            <button
              key={v}
              onClick={() => setView(v)}
              className={`px-4 py-2 text-sm font-medium rounded-lg transition-all capitalize ${
                view === v ? "bg-vulcan-accent text-white" : "bg-white/5 text-white/50 hover:bg-white/10"
              }`}
            >
              {v}
            </button>
          ))}
        </div>
      </div>

      {/* View Content */}
      {view === "live" && <LiveView currentSession={currentSession} currentTime={currentTime} />}
      {view === "daily" && <DailyView cycleDay={cycleDay} />}
      {view === "weekly" && <WeeklyView />}
      {view === "monthly" && <MonthlyView />}
    </div>
  );
}

/* Live Session View */
function LiveView({ currentSession, currentTime }: { currentSession: SessionName; currentTime: Date }) {
  return (
    <div className="grid grid-cols-3 gap-6">
      {/* Session Status */}
      <div className="col-span-2 glass rounded-xl p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-white">Session Status</h3>
          <div className="text-2xl font-mono text-white">
            {currentTime.toLocaleTimeString("en-US", { timeZone: "America/New_York", hour12: false })}
          </div>
        </div>

        <div className="space-y-3">
          {(Object.entries(SESSIONS) as [SessionName, typeof SESSIONS[SessionName]][]).map(([name, session]) => {
            const isActive = currentSession === name;
            return (
              <div key={name} className="flex items-center gap-4">
                <div className={`w-20 text-sm font-medium capitalize ${isActive ? "text-white" : "text-white/40"}`}>
                  {name}
                </div>
                <div className="flex-1 h-3 bg-white/10 rounded-full overflow-hidden">
                  <div
                    className={`h-full transition-all ${isActive ? "animate-pulse" : ""}`}
                    style={{
                      width: isActive ? "60%" : "100%",
                      backgroundColor: isActive ? session.color : session.color + "30",
                    }}
                  />
                </div>
                <div className="text-xs text-white/40 w-28 text-right">
                  {session.start} - {session.end}
                </div>
                {isActive && (
                  <span className="px-2 py-0.5 bg-trading-bullish/20 text-trading-bullish text-xs rounded">Active</span>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Key Levels */}
      <div className="glass rounded-xl p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Key Levels</h3>
        <div className="space-y-3">
          <LevelRow label="Asian High" value="1.0985" color="#a371f7" />
          <LevelRow label="Asian Low" value="1.0945" color="#a371f7" />
          <LevelRow label="Previous High" value="1.1010" color="#f85149" />
          <LevelRow label="Previous Low" value="1.0920" color="#3fb950" />
          <LevelRow label="Weekly Open" value="1.0960" color="#58a6ff" />
        </div>
      </div>
    </div>
  );
}

/* Daily Bias View */
function DailyView({ cycleDay }: { cycleDay: CycleDay }) {
  const [bias, setBias] = useState<"bullish" | "bearish" | "neutral">("bullish");
  const [level, setLevel] = useState<BTMMLevel>("II");

  return (
    <div className="grid grid-cols-2 gap-6">
      {/* Bias Selection */}
      <div className="glass rounded-xl p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Daily Bias</h3>
        <div className="grid grid-cols-3 gap-3">
          {(["bullish", "bearish", "neutral"] as const).map((b) => (
            <button
              key={b}
              onClick={() => setBias(b)}
              className={`p-4 rounded-lg transition-all capitalize ${
                bias === b
                  ? b === "bullish"
                    ? "bg-trading-bullish/20 border border-trading-bullish text-trading-bullish"
                    : b === "bearish"
                    ? "bg-trading-bearish/20 border border-trading-bearish text-trading-bearish"
                    : "bg-white/20 border border-white/40 text-white"
                  : "bg-white/5 text-white/50 hover:bg-white/10"
              }`}
            >
              {b === "bullish" ? "📈" : b === "bearish" ? "📉" : "➡️"}
              <div className="mt-2 font-medium">{b}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Cycle Day Info */}
      <div className="glass rounded-xl p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Cycle Day</h3>
        <div className="space-y-2">
          {([1, 2, 3] as CycleDay[]).map((day) => (
            <div
              key={day}
              className={`p-3 rounded-lg ${
                cycleDay === day ? "bg-white/10 border border-white/20" : "bg-white/5"
              }`}
            >
              <div className="font-medium text-white">{CYCLE_DAY_INFO[day].name}</div>
              <div className="text-xs text-white/40 mt-1">{CYCLE_DAY_INFO[day].strategy}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Notes */}
      <div className="col-span-2 glass rounded-xl p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Trading Plan</h3>
        <textarea
          className="w-full h-32 trading-input resize-none"
          placeholder="What's your trading plan for today?..."
        />
      </div>
    </div>
  );
}

/* Weekly View */
function WeeklyView() {
  const weekDays = [
    { day: "Monday", cycleDay: 1, bias: "neutral" },
    { day: "Tuesday", cycleDay: 2, bias: "bullish" },
    { day: "Wednesday", cycleDay: 3, bias: "bullish" },
    { day: "Thursday", cycleDay: 1, bias: "neutral" },
    { day: "Friday", cycleDay: 2, bias: "bearish" },
  ];

  return (
    <div className="glass rounded-xl p-6">
      <h3 className="text-lg font-semibold text-white mb-4">Weekly Plan</h3>
      <div className="space-y-3">
        {weekDays.map((day) => (
          <div key={day.day} className="flex items-center gap-4 p-3 bg-white/5 rounded-lg">
            <div className="w-24 font-medium text-white">{day.day}</div>
            <span
              className={`px-2 py-0.5 rounded text-xs ${
                day.cycleDay === 1
                  ? "bg-yellow-500/20 text-yellow-400"
                  : day.cycleDay === 2
                  ? "bg-orange-500/20 text-orange-400"
                  : "bg-green-500/20 text-green-400"
              }`}
            >
              Day {day.cycleDay}
            </span>
            <span
              className={`px-2 py-0.5 rounded text-xs capitalize ${
                day.bias === "bullish"
                  ? "bg-trading-bullish/20 text-trading-bullish"
                  : day.bias === "bearish"
                  ? "bg-trading-bearish/20 text-trading-bearish"
                  : "bg-white/20 text-white/60"
              }`}
            >
              {day.bias}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

/* Monthly View */
function MonthlyView() {
  return (
    <div className="grid grid-cols-2 gap-6">
      <div className="glass rounded-xl p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Monthly Stats</h3>
        <div className="space-y-3">
          <StatRow label="Monthly Open" value="1.0520" />
          <StatRow label="Monthly High" value="1.1015" />
          <StatRow label="Monthly Low" value="1.0450" />
          <StatRow label="Current" value="1.0972" />
          <StatRow label="Change" value="+4.3%" color="#3fb950" />
        </div>
      </div>

      <div className="glass rounded-xl p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Monthly Notes</h3>
        <textarea
          className="w-full h-40 trading-input resize-none"
          placeholder="Major themes, institutional positioning..."
        />
      </div>
    </div>
  );
}

function LevelRow({ label, value, color }: { label: string; value: string; color: string }) {
  return (
    <div className="flex justify-between items-center py-2 border-b border-white/5 last:border-0">
      <span className="text-white/40 text-sm">{label}</span>
      <span className="font-mono font-medium" style={{ color }}>
        {value}
      </span>
    </div>
  );
}

function StatRow({ label, value, color }: { label: string; value: string; color?: string }) {
  return (
    <div className="flex justify-between items-center py-2 border-b border-white/5 last:border-0">
      <span className="text-white/40 text-sm">{label}</span>
      <span className="font-mono font-medium" style={{ color: color || "white" }}>
        {value}
      </span>
    </div>
  );
}
