/**
 * Weekly Outlook Page
 * Weekly cycle analysis and key events
 */

"use client";

import { useState } from "react";
import Link from "next/link";
import type { CycleDay } from "@/lib/trading/types";

export default function WeeklyAnalysisPage() {
  const [selectedPair, setSelectedPair] = useState("EUR/USD");

  const weekDays = [
    { day: "Monday", date: "Dec 16", cycleDay: 1 as CycleDay, bias: "neutral", notes: "Week starts, establishing range" },
    { day: "Tuesday", date: "Dec 17", cycleDay: 2 as CycleDay, bias: "bullish", notes: "Expected manipulation before move" },
    { day: "Wednesday", date: "Dec 18", cycleDay: 3 as CycleDay, bias: "bullish", notes: "Distribution day - trend continuation" },
    { day: "Thursday", date: "Dec 19", cycleDay: 1 as CycleDay, bias: "neutral", notes: "New cycle begins" },
    { day: "Friday", date: "Dec 20", cycleDay: 2 as CycleDay, bias: "bearish", notes: "Week close - possible reversal" },
  ];

  const events = [
    { time: "Mon 8:30", event: "Empire State Mfg", impact: "medium" },
    { time: "Tue 8:30", event: "Retail Sales", impact: "high" },
    { time: "Wed 14:00", event: "FOMC Statement", impact: "high" },
    { time: "Thu 8:30", event: "Jobless Claims", impact: "medium" },
    { time: "Fri 8:30", event: "PCE Price Index", impact: "high" },
  ];

  return (
    <div className="min-h-screen bg-vulcan-darker p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <Link href="/trading/analysis" className="text-vulcan-accent text-sm hover:underline mb-2 inline-block">
            &larr; Back to Analysis
          </Link>
          <h1 className="text-2xl font-bold text-white">Weekly Outlook</h1>
          <p className="text-white/50">Week of December 16-20, 2025</p>
        </div>

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

      <div className="grid grid-cols-3 gap-6">
        {/* Left - Weekly Calendar */}
        <div className="col-span-2">
          <div className="glass rounded-xl p-6">
            <h2 className="text-lg font-semibold text-white mb-4">Weekly Trading Plan</h2>
            <div className="space-y-3">
              {weekDays.map((day, index) => {
                const isToday = day.date === "Dec 20"; // Mock current day
                return (
                  <div
                    key={day.day}
                    className={`p-4 rounded-lg transition-all ${
                      isToday
                        ? "bg-vulcan-accent/20 border border-vulcan-accent/50"
                        : "bg-white/5 hover:bg-white/10"
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        <div className="text-center w-16">
                          <div className="text-xs text-white/40">{day.day.slice(0, 3)}</div>
                          <div className="text-lg font-bold text-white">{day.date.split(" ")[1]}</div>
                        </div>
                        <div>
                          <div className="flex items-center gap-2">
                            <span
                              className={`px-2 py-0.5 rounded text-xs font-medium ${
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
                              className={`px-2 py-0.5 rounded text-xs font-medium capitalize ${
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
                          <div className="text-sm text-white/50 mt-1">{day.notes}</div>
                        </div>
                      </div>
                      {isToday && (
                        <span className="px-2 py-1 bg-vulcan-accent text-white text-xs font-medium rounded">
                          Today
                        </span>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Weekly Levels */}
          <div className="glass rounded-xl p-6 mt-6">
            <h2 className="text-lg font-semibold text-white mb-4">Weekly Key Levels</h2>
            <div className="grid grid-cols-4 gap-4">
              <LevelCard label="Weekly Open" value="1.0960" color="#58a6ff" />
              <LevelCard label="Weekly High" value="1.1015" color="#f85149" />
              <LevelCard label="Weekly Low" value="1.0890" color="#3fb950" />
              <LevelCard label="Prev Week Close" value="1.0958" color="#a371f7" />
            </div>
          </div>
        </div>

        {/* Right - Events & Notes */}
        <div className="space-y-6">
          {/* Economic Events */}
          <div className="glass rounded-xl p-6">
            <h3 className="text-sm font-semibold text-white/60 uppercase tracking-wider mb-4">
              Economic Events (EST)
            </h3>
            <div className="space-y-2">
              {events.map((event, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-3 bg-white/5 rounded-lg"
                >
                  <div>
                    <div className="text-xs text-white/40">{event.time}</div>
                    <div className="text-sm text-white">{event.event}</div>
                  </div>
                  <span
                    className={`px-2 py-0.5 rounded text-xs font-medium ${
                      event.impact === "high"
                        ? "bg-trading-bearish/20 text-trading-bearish"
                        : "bg-yellow-500/20 text-yellow-400"
                    }`}
                  >
                    {event.impact.toUpperCase()}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Weekly Outlook Notes */}
          <div className="glass rounded-xl p-6">
            <h3 className="text-sm font-semibold text-white/60 uppercase tracking-wider mb-4">
              Weekly Notes
            </h3>
            <textarea
              className="w-full h-40 trading-input resize-none"
              placeholder="Your weekly market outlook...

- Key themes
- Expected moves
- Pairs to focus on"
            />
          </div>

          {/* Week Stats */}
          <div className="glass rounded-xl p-6">
            <h3 className="text-sm font-semibold text-white/60 uppercase tracking-wider mb-4">
              This Week's Stats
            </h3>
            <div className="space-y-3">
              <StatRow label="Trades Taken" value="5" />
              <StatRow label="Win Rate" value="80%" color="#3fb950" />
              <StatRow label="Total P/L" value="+145 pips" color="#3fb950" />
              <StatRow label="Avg R:R" value="1:2.3" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function LevelCard({
  label,
  value,
  color,
}: {
  label: string;
  value: string;
  color: string;
}) {
  return (
    <div className="p-4 bg-white/5 rounded-lg text-center">
      <div className="text-xs text-white/40 mb-1">{label}</div>
      <div className="text-lg font-mono font-bold" style={{ color }}>
        {value}
      </div>
    </div>
  );
}

function StatRow({
  label,
  value,
  color,
}: {
  label: string;
  value: string;
  color?: string;
}) {
  return (
    <div className="flex justify-between items-center py-2 border-b border-white/5 last:border-0">
      <span className="text-white/40 text-sm">{label}</span>
      <span className="font-medium" style={{ color: color || "white" }}>
        {value}
      </span>
    </div>
  );
}
