/**
 * Performance Tab Component
 * Trading statistics, metrics, and performance charts
 */

"use client";

import { useState } from "react";

type TimeRange = "week" | "month" | "quarter" | "year" | "all";

export function PerformanceTab() {
  const [timeRange, setTimeRange] = useState<TimeRange>("month");

  // Mock performance data
  const stats = {
    totalTrades: 47,
    winRate: 68,
    profitFactor: 2.1,
    avgWin: 85,
    avgLoss: 35,
    totalPnL: 2450,
    bestTrade: 250,
    worstTrade: -120,
    maxDrawdown: 8.5,
    currentStreak: 3,
    avgRMultiple: 1.8,
  };

  const setupStats = [
    { type: "Type 1a", trades: 15, winRate: 73, avgPnL: 65 },
    { type: "Type 2a", trades: 12, winRate: 58, avgPnL: 42 },
    { type: "Type 3a", trades: 8, winRate: 75, avgPnL: 88 },
    { type: "Type 4a", trades: 12, winRate: 67, avgPnL: 55 },
  ];

  const sessionStats = [
    { session: "Asian", trades: 8, winRate: 50, avgPnL: 25 },
    { session: "London", trades: 22, winRate: 72, avgPnL: 78 },
    { session: "New York", trades: 17, winRate: 70, avgPnL: 62 },
  ];

  return (
    <div className="h-full overflow-auto p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-bold text-white">Performance</h2>
          <p className="text-white/50 text-sm">Trading statistics and analytics</p>
        </div>

        <div className="flex gap-2">
          {(["week", "month", "quarter", "year", "all"] as TimeRange[]).map((range) => (
            <button
              key={range}
              onClick={() => setTimeRange(range)}
              className={`px-3 py-1.5 text-sm font-medium rounded-lg transition-all capitalize ${
                timeRange === range ? "bg-vulcan-accent text-white" : "bg-white/5 text-white/50 hover:bg-white/10"
              }`}
            >
              {range}
            </button>
          ))}
        </div>
      </div>

      {/* Main Stats Grid */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <StatCard label="Total Trades" value={stats.totalTrades} />
        <StatCard label="Win Rate" value={`${stats.winRate}%`} color={stats.winRate >= 50 ? "#3fb950" : "#f85149"} />
        <StatCard label="Profit Factor" value={stats.profitFactor.toFixed(1)} color={stats.profitFactor >= 1 ? "#3fb950" : "#f85149"} />
        <StatCard label="Total P/L" value={`$${stats.totalPnL}`} color={stats.totalPnL >= 0 ? "#3fb950" : "#f85149"} />
      </div>

      {/* Secondary Stats */}
      <div className="grid grid-cols-6 gap-4 mb-6">
        <MiniStatCard label="Avg Win" value={`${stats.avgWin} pips`} color="#3fb950" />
        <MiniStatCard label="Avg Loss" value={`${stats.avgLoss} pips`} color="#f85149" />
        <MiniStatCard label="Best Trade" value={`$${stats.bestTrade}`} color="#3fb950" />
        <MiniStatCard label="Worst Trade" value={`$${stats.worstTrade}`} color="#f85149" />
        <MiniStatCard label="Max DD" value={`${stats.maxDrawdown}%`} color="#f85149" />
        <MiniStatCard label="Avg R" value={`${stats.avgRMultiple.toFixed(1)}R`} color="#58a6ff" />
      </div>

      <div className="grid grid-cols-2 gap-6">
        {/* Setup Performance */}
        <div className="glass rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Performance by Setup</h3>
          <div className="space-y-3">
            {setupStats.map((setup) => (
              <div key={setup.type} className="p-3 bg-white/5 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-white font-medium">{setup.type}</span>
                  <span className="text-xs text-white/40">{setup.trades} trades</span>
                </div>
                <div className="flex items-center gap-4">
                  <div className="flex-1">
                    <div className="flex justify-between text-xs mb-1">
                      <span className="text-white/40">Win Rate</span>
                      <span className={setup.winRate >= 50 ? "text-trading-bullish" : "text-trading-bearish"}>
                        {setup.winRate}%
                      </span>
                    </div>
                    <div className="h-1.5 bg-white/10 rounded-full overflow-hidden">
                      <div
                        className={`h-full ${setup.winRate >= 50 ? "bg-trading-bullish" : "bg-trading-bearish"}`}
                        style={{ width: `${setup.winRate}%` }}
                      />
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-xs text-white/40">Avg P/L</div>
                    <div className={`font-mono ${setup.avgPnL >= 0 ? "text-trading-bullish" : "text-trading-bearish"}`}>
                      {setup.avgPnL >= 0 ? "+" : ""}{setup.avgPnL}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Session Performance */}
        <div className="glass rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Performance by Session</h3>
          <div className="space-y-3">
            {sessionStats.map((session) => (
              <div key={session.session} className="p-3 bg-white/5 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-white font-medium">{session.session}</span>
                  <span className="text-xs text-white/40">{session.trades} trades</span>
                </div>
                <div className="flex items-center gap-4">
                  <div className="flex-1">
                    <div className="flex justify-between text-xs mb-1">
                      <span className="text-white/40">Win Rate</span>
                      <span className={session.winRate >= 50 ? "text-trading-bullish" : "text-trading-bearish"}>
                        {session.winRate}%
                      </span>
                    </div>
                    <div className="h-1.5 bg-white/10 rounded-full overflow-hidden">
                      <div
                        className={`h-full ${session.winRate >= 50 ? "bg-trading-bullish" : "bg-trading-bearish"}`}
                        style={{ width: `${session.winRate}%` }}
                      />
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-xs text-white/40">Avg P/L</div>
                    <div className={`font-mono ${session.avgPnL >= 0 ? "text-trading-bullish" : "text-trading-bearish"}`}>
                      {session.avgPnL >= 0 ? "+" : ""}{session.avgPnL}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Equity Curve Placeholder */}
        <div className="col-span-2 glass rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Equity Curve</h3>
          <div className="h-48 bg-white/5 rounded-lg flex items-center justify-center">
            <div className="text-center text-white/40">
              <div className="text-4xl mb-2">📈</div>
              <div>Equity chart visualization coming soon</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({ label, value, color }: { label: string; value: string | number; color?: string }) {
  return (
    <div className="glass rounded-xl p-4">
      <div className="text-xs text-white/40 uppercase tracking-wider mb-1">{label}</div>
      <div className="text-2xl font-bold" style={{ color: color || "white" }}>
        {value}
      </div>
    </div>
  );
}

function MiniStatCard({ label, value, color }: { label: string; value: string; color: string }) {
  return (
    <div className="p-3 bg-white/5 rounded-lg text-center">
      <div className="text-xs text-white/40 mb-1">{label}</div>
      <div className="font-mono font-medium" style={{ color }}>
        {value}
      </div>
    </div>
  );
}
