/**
 * Market Analysis Overview Page
 * Hub for all analysis timeframes
 */

"use client";

import Link from "next/link";
import { useState } from "react";
import type { CycleDay, BTMMLevel, SessionName } from "@/lib/trading/types";
import { CYCLE_DAY_INFO, LEVEL_INFO, SESSIONS } from "@/lib/trading/constants";

export default function AnalysisPage() {
  const [selectedPair, setSelectedPair] = useState("EUR/USD");

  // Mock data for current market state
  const marketState = {
    currentSession: "newyork" as SessionName,
    cycleDay: 2 as CycleDay,
    level: "II" as BTMMLevel,
    bias: "bullish" as "bullish" | "bearish" | "neutral",
    asianRangePips: 45,
    adrUsed: 65,
  };

  const analysisLinks = [
    {
      href: "/trading/analysis/live",
      title: "Live Session",
      description: "Real-time session analysis and key levels",
      icon: "⚡",
      badge: "Active",
    },
    {
      href: "/trading/analysis/daily",
      title: "Daily Bias",
      description: "Today's market bias and trading plan",
      icon: "📅",
      badge: null,
    },
    {
      href: "/trading/analysis/weekly",
      title: "Weekly Outlook",
      description: "Weekly cycle analysis and key events",
      icon: "📊",
      badge: null,
    },
    {
      href: "/trading/analysis/monthly",
      title: "Monthly Cycle",
      description: "Monthly trends and institutional positioning",
      icon: "📈",
      badge: null,
    },
  ];

  return (
    <div className="min-h-screen bg-vulcan-darker p-6">
      {/* Header */}
      <div className="mb-6">
        <Link href="/trading" className="text-vulcan-accent text-sm hover:underline mb-2 inline-block">
          &larr; Back to Trading
        </Link>
        <h1 className="text-2xl font-bold text-white">Market Analysis</h1>
        <p className="text-white/50">BTMM analysis across all timeframes</p>
      </div>

      {/* Current Market State */}
      <div className="glass rounded-xl p-6 mb-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-white">Current Market State</h2>
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

        <div className="grid grid-cols-6 gap-4">
          {/* Current Session */}
          <div className="p-4 bg-white/5 rounded-lg">
            <div className="text-xs text-white/40 uppercase tracking-wider mb-1">Session</div>
            <div className="flex items-center gap-2">
              <div
                className="w-2 h-2 rounded-full animate-pulse"
                style={{ backgroundColor: SESSIONS[marketState.currentSession].color }}
              />
              <span className="text-white font-medium capitalize">{marketState.currentSession}</span>
            </div>
          </div>

          {/* Cycle Day */}
          <div className="p-4 bg-white/5 rounded-lg">
            <div className="text-xs text-white/40 uppercase tracking-wider mb-1">Cycle Day</div>
            <span
              className={`px-2 py-1 rounded text-sm font-medium ${
                marketState.cycleDay === 1
                  ? "bg-yellow-500/20 text-yellow-400"
                  : marketState.cycleDay === 2
                  ? "bg-orange-500/20 text-orange-400"
                  : "bg-green-500/20 text-green-400"
              }`}
            >
              Day {marketState.cycleDay}
            </span>
          </div>

          {/* Level */}
          <div className="p-4 bg-white/5 rounded-lg">
            <div className="text-xs text-white/40 uppercase tracking-wider mb-1">Level</div>
            <span
              className="px-2 py-1 rounded text-sm font-medium"
              style={{
                backgroundColor: LEVEL_INFO[marketState.level].color + "33",
                color: LEVEL_INFO[marketState.level].color,
              }}
            >
              Level {marketState.level}
            </span>
          </div>

          {/* Bias */}
          <div className="p-4 bg-white/5 rounded-lg">
            <div className="text-xs text-white/40 uppercase tracking-wider mb-1">Daily Bias</div>
            <span
              className={`font-medium capitalize ${
                marketState.bias === "bullish"
                  ? "text-trading-bullish"
                  : marketState.bias === "bearish"
                  ? "text-trading-bearish"
                  : "text-white/60"
              }`}
            >
              {marketState.bias}
            </span>
          </div>

          {/* Asian Range */}
          <div className="p-4 bg-white/5 rounded-lg">
            <div className="text-xs text-white/40 uppercase tracking-wider mb-1">Asian Range</div>
            <span className="text-white font-mono">{marketState.asianRangePips} pips</span>
          </div>

          {/* ADR Used */}
          <div className="p-4 bg-white/5 rounded-lg">
            <div className="text-xs text-white/40 uppercase tracking-wider mb-1">ADR Used</div>
            <div className="flex items-center gap-2">
              <span className="text-white font-mono">{marketState.adrUsed}%</span>
              <div className="flex-1 h-1.5 bg-white/10 rounded-full overflow-hidden">
                <div
                  className={`h-full transition-all ${
                    marketState.adrUsed > 80 ? "bg-trading-bearish" : "bg-vulcan-accent"
                  }`}
                  style={{ width: `${marketState.adrUsed}%` }}
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Analysis Links */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        {analysisLinks.map((link) => (
          <Link
            key={link.href}
            href={link.href}
            className="glass rounded-xl p-6 hover:bg-white/5 transition-colors group"
          >
            <div className="flex items-start justify-between mb-4">
              <span className="text-3xl">{link.icon}</span>
              {link.badge && (
                <span className="px-2 py-1 bg-trading-bullish/20 text-trading-bullish text-xs font-medium rounded-full">
                  {link.badge}
                </span>
              )}
            </div>
            <h3 className="text-lg font-semibold text-white group-hover:text-vulcan-accent transition-colors">
              {link.title}
            </h3>
            <p className="text-sm text-white/50 mt-1">{link.description}</p>
          </Link>
        ))}
      </div>

      {/* Quick Reference */}
      <div className="grid grid-cols-3 gap-4">
        {/* Cycle Day Guide */}
        <div className="glass rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Cycle Day Guide</h3>
          <div className="space-y-3">
            {([1, 2, 3] as CycleDay[]).map((day) => (
              <div
                key={day}
                className={`p-3 rounded-lg ${
                  marketState.cycleDay === day ? "bg-white/10 border border-white/20" : "bg-white/5"
                }`}
              >
                <div className="font-medium text-white">{CYCLE_DAY_INFO[day].name}</div>
                <div className="text-xs text-white/40 mt-1">{CYCLE_DAY_INFO[day].strategy}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Level Guide */}
        <div className="glass rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Level Guide</h3>
          <div className="space-y-3">
            {(["I", "II", "III"] as BTMMLevel[]).map((level) => (
              <div
                key={level}
                className={`p-3 rounded-lg ${
                  marketState.level === level ? "bg-white/10 border border-white/20" : "bg-white/5"
                }`}
              >
                <div className="font-medium" style={{ color: LEVEL_INFO[level].color }}>
                  {LEVEL_INFO[level].name}
                </div>
                <div className="text-xs text-white/40 mt-1">{LEVEL_INFO[level].importance}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Session Times */}
        <div className="glass rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Session Times (EST)</h3>
          <div className="space-y-3">
            {(Object.entries(SESSIONS) as [SessionName, typeof SESSIONS[SessionName]][]).map(
              ([name, session]) => (
                <div
                  key={name}
                  className={`p-3 rounded-lg ${
                    marketState.currentSession === name
                      ? "bg-white/10 border border-white/20"
                      : "bg-white/5"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div
                        className="w-2 h-2 rounded-full"
                        style={{ backgroundColor: session.color }}
                      />
                      <span className="font-medium text-white capitalize">{name}</span>
                    </div>
                    <span className="text-xs text-white/40">
                      {session.start} - {session.end}
                    </span>
                  </div>
                </div>
              )
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
