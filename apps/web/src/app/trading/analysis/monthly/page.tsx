/**
 * Monthly Cycle Analysis Page
 * Monthly trends and institutional positioning
 */

"use client";

import { useState } from "react";
import Link from "next/link";

export default function MonthlyAnalysisPage() {
  const [selectedPair, setSelectedPair] = useState("EUR/USD");
  const [selectedMonth, setSelectedMonth] = useState("December 2025");

  const monthlyData = {
    open: 1.0520,
    high: 1.1015,
    low: 1.0450,
    currentPrice: 1.0972,
    range: 565,
    direction: "bullish" as "bullish" | "bearish",
    percentChange: 4.3,
  };

  const weeklyBreakdown = [
    { week: "Week 1", high: 1.0580, low: 1.0450, close: 1.0565, bias: "bearish" },
    { week: "Week 2", high: 1.0720, low: 1.0520, close: 1.0695, bias: "bullish" },
    { week: "Week 3", high: 1.0950, low: 1.0680, close: 1.0920, bias: "bullish" },
    { week: "Week 4", high: 1.1015, low: 1.0890, close: 1.0972, bias: "bullish" },
  ];

  const institutionalData = [
    { category: "Commercial Hedgers", net: -45000, change: "+5,200" },
    { category: "Non-Commercial (Specs)", net: 32000, change: "-3,800" },
    { category: "Small Traders", net: 13000, change: "-1,400" },
  ];

  return (
    <div className="min-h-screen bg-vulcan-darker p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <Link href="/trading/analysis" className="text-vulcan-accent text-sm hover:underline mb-2 inline-block">
            &larr; Back to Analysis
          </Link>
          <h1 className="text-2xl font-bold text-white">Monthly Cycle</h1>
          <p className="text-white/50">{selectedMonth}</p>
        </div>

        <div className="flex items-center gap-3">
          <select
            value={selectedMonth}
            onChange={(e) => setSelectedMonth(e.target.value)}
            className="trading-input"
          >
            <option value="December 2025">December 2025</option>
            <option value="November 2025">November 2025</option>
            <option value="October 2025">October 2025</option>
          </select>
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

      {/* Monthly Overview */}
      <div className="glass rounded-xl p-6 mb-6">
        <div className="grid grid-cols-6 gap-4">
          <StatCard label="Monthly Open" value={monthlyData.open.toFixed(4)} />
          <StatCard label="Monthly High" value={monthlyData.high.toFixed(4)} color="#f85149" />
          <StatCard label="Monthly Low" value={monthlyData.low.toFixed(4)} color="#3fb950" />
          <StatCard label="Current" value={monthlyData.currentPrice.toFixed(4)} color="#58a6ff" />
          <StatCard label="Range" value={`${monthlyData.range} pips`} />
          <StatCard
            label="Change"
            value={`${monthlyData.percentChange > 0 ? "+" : ""}${monthlyData.percentChange}%`}
            color={monthlyData.percentChange > 0 ? "#3fb950" : "#f85149"}
          />
        </div>
      </div>

      <div className="grid grid-cols-3 gap-6">
        {/* Left - Weekly Breakdown */}
        <div className="col-span-2 space-y-6">
          {/* Monthly Candle Visualization */}
          <div className="glass rounded-xl p-6">
            <h2 className="text-lg font-semibold text-white mb-4">Monthly Price Structure</h2>
            <div className="h-48 bg-white/5 rounded-lg p-4 relative">
              {/* Simplified candle visualization */}
              <div className="absolute left-1/2 top-0 bottom-0 w-24 -translate-x-1/2 flex flex-col">
                {/* High wick */}
                <div className="flex-none h-[10%] flex justify-center">
                  <div className="w-0.5 h-full bg-trading-bullish" />
                </div>
                {/* Body */}
                <div className="flex-1 bg-trading-bullish/30 border-2 border-trading-bullish rounded relative">
                  {/* Labels */}
                  <div className="absolute -left-24 top-0 text-xs text-trading-bearish font-mono">
                    H: {monthlyData.high.toFixed(4)}
                  </div>
                  <div className="absolute -right-24 top-[30%] text-xs text-white font-mono">
                    O: {monthlyData.open.toFixed(4)}
                  </div>
                  <div className="absolute -right-24 bottom-0 text-xs text-vulcan-accent font-mono">
                    C: {monthlyData.currentPrice.toFixed(4)}
                  </div>
                  <div className="absolute -left-24 bottom-0 text-xs text-trading-bullish font-mono">
                    L: {monthlyData.low.toFixed(4)}
                  </div>
                </div>
                {/* Low wick */}
                <div className="flex-none h-[15%] flex justify-center">
                  <div className="w-0.5 h-full bg-trading-bullish" />
                </div>
              </div>

              {/* Range indicator */}
              <div className="absolute right-4 top-1/2 -translate-y-1/2 text-center">
                <div className="text-2xl font-bold text-white">{monthlyData.range}</div>
                <div className="text-xs text-white/40">pips range</div>
              </div>
            </div>
          </div>

          {/* Weekly Breakdown */}
          <div className="glass rounded-xl p-6">
            <h2 className="text-lg font-semibold text-white mb-4">Weekly Breakdown</h2>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-white/10">
                    <th className="text-left p-3 text-xs text-white/40 uppercase">Week</th>
                    <th className="text-right p-3 text-xs text-white/40 uppercase">High</th>
                    <th className="text-right p-3 text-xs text-white/40 uppercase">Low</th>
                    <th className="text-right p-3 text-xs text-white/40 uppercase">Close</th>
                    <th className="text-center p-3 text-xs text-white/40 uppercase">Bias</th>
                  </tr>
                </thead>
                <tbody>
                  {weeklyBreakdown.map((week, index) => (
                    <tr key={week.week} className="border-b border-white/5">
                      <td className="p-3 text-white font-medium">{week.week}</td>
                      <td className="p-3 text-right font-mono text-trading-bearish">{week.high.toFixed(4)}</td>
                      <td className="p-3 text-right font-mono text-trading-bullish">{week.low.toFixed(4)}</td>
                      <td className="p-3 text-right font-mono text-white">{week.close.toFixed(4)}</td>
                      <td className="p-3 text-center">
                        <span
                          className={`px-2 py-0.5 rounded text-xs font-medium capitalize ${
                            week.bias === "bullish"
                              ? "bg-trading-bullish/20 text-trading-bullish"
                              : "bg-trading-bearish/20 text-trading-bearish"
                          }`}
                        >
                          {week.bias}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Right - COT & Analysis */}
        <div className="space-y-6">
          {/* Monthly Trend */}
          <div className="glass rounded-xl p-6">
            <h3 className="text-sm font-semibold text-white/60 uppercase tracking-wider mb-4">
              Monthly Trend
            </h3>
            <div className="text-center py-4">
              <div className="text-4xl mb-2">
                {monthlyData.direction === "bullish" ? "📈" : "📉"}
              </div>
              <div
                className={`text-2xl font-bold capitalize ${
                  monthlyData.direction === "bullish" ? "text-trading-bullish" : "text-trading-bearish"
                }`}
              >
                {monthlyData.direction}
              </div>
              <div className="text-sm text-white/40 mt-1">Strong uptrend since October</div>
            </div>
          </div>

          {/* COT Data (Simplified) */}
          <div className="glass rounded-xl p-6">
            <h3 className="text-sm font-semibold text-white/60 uppercase tracking-wider mb-4">
              COT Positioning
            </h3>
            <div className="space-y-3">
              {institutionalData.map((item) => (
                <div key={item.category} className="p-3 bg-white/5 rounded-lg">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm text-white">{item.category}</span>
                    <span className="text-xs text-white/40">{item.change}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 h-2 bg-white/10 rounded-full overflow-hidden">
                      <div
                        className={`h-full ${item.net > 0 ? "bg-trading-bullish" : "bg-trading-bearish"}`}
                        style={{ width: `${Math.abs(item.net) / 1000}%` }}
                      />
                    </div>
                    <span
                      className={`text-sm font-mono ${
                        item.net > 0 ? "text-trading-bullish" : "text-trading-bearish"
                      }`}
                    >
                      {item.net > 0 ? "+" : ""}
                      {(item.net / 1000).toFixed(0)}K
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Monthly Notes */}
          <div className="glass rounded-xl p-6">
            <h3 className="text-sm font-semibold text-white/60 uppercase tracking-wider mb-4">
              Monthly Notes
            </h3>
            <textarea
              className="w-full h-32 trading-input resize-none"
              placeholder="Major themes, key levels, institutional moves..."
            />
          </div>

          {/* Historical Comparison */}
          <div className="glass rounded-xl p-6">
            <h3 className="text-sm font-semibold text-white/60 uppercase tracking-wider mb-4">
              December Historical
            </h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-white/40">Avg Range:</span>
                <span className="text-white">520 pips</span>
              </div>
              <div className="flex justify-between">
                <span className="text-white/40">Typical Bias:</span>
                <span className="text-trading-bullish">Bullish (68%)</span>
              </div>
              <div className="flex justify-between">
                <span className="text-white/40">Best Week:</span>
                <span className="text-white">Week 2-3</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({
  label,
  value,
  color,
}: {
  label: string;
  value: string;
  color?: string;
}) {
  return (
    <div className="p-4 bg-white/5 rounded-lg text-center">
      <div className="text-xs text-white/40 uppercase tracking-wider mb-1">{label}</div>
      <div className="text-lg font-mono font-bold" style={{ color: color || "white" }}>
        {value}
      </div>
    </div>
  );
}
