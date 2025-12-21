/**
 * Daily Bias Analysis Page
 * Today's market bias and trading plan
 */

"use client";

import { useState } from "react";
import Link from "next/link";
import type { CycleDay, BTMMLevel } from "@/lib/trading/types";
import { CYCLE_DAY_INFO, LEVEL_INFO, TRADING_PAIRS } from "@/lib/trading/constants";

export default function DailyAnalysisPage() {
  const [selectedPair, setSelectedPair] = useState("EUR/USD");
  const [bias, setBias] = useState<"bullish" | "bearish" | "neutral">("bullish");
  const [cycleDay, setCycleDay] = useState<CycleDay>(2);
  const [level, setLevel] = useState<BTMMLevel>("II");
  const [notes, setNotes] = useState("");

  const today = new Date().toLocaleDateString("en-US", {
    weekday: "long",
    month: "long",
    day: "numeric",
    year: "numeric",
  });

  return (
    <div className="min-h-screen bg-vulcan-darker p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <Link href="/trading/analysis" className="text-vulcan-accent text-sm hover:underline mb-2 inline-block">
            &larr; Back to Analysis
          </Link>
          <h1 className="text-2xl font-bold text-white">Daily Bias</h1>
          <p className="text-white/50">{today}</p>
        </div>

        <select
          value={selectedPair}
          onChange={(e) => setSelectedPair(e.target.value)}
          className="trading-input"
        >
          {TRADING_PAIRS.slice(0, 10).map((pair) => (
            <option key={pair.symbol} value={pair.symbol}>
              {pair.symbol}
            </option>
          ))}
        </select>
      </div>

      <div className="grid grid-cols-3 gap-6">
        {/* Left Column - Bias Setting */}
        <div className="col-span-2 space-y-6">
          {/* Bias Selection */}
          <div className="glass rounded-xl p-6">
            <h2 className="text-lg font-semibold text-white mb-4">Market Bias</h2>
            <div className="grid grid-cols-3 gap-4">
              {(["bullish", "bearish", "neutral"] as const).map((b) => (
                <button
                  key={b}
                  onClick={() => setBias(b)}
                  className={`p-4 rounded-xl transition-all ${
                    bias === b
                      ? b === "bullish"
                        ? "bg-trading-bullish/20 border-2 border-trading-bullish text-trading-bullish"
                        : b === "bearish"
                        ? "bg-trading-bearish/20 border-2 border-trading-bearish text-trading-bearish"
                        : "bg-white/20 border-2 border-white/40 text-white"
                      : "bg-white/5 border-2 border-transparent text-white/50 hover:bg-white/10"
                  }`}
                >
                  <div className="text-3xl mb-2">
                    {b === "bullish" ? "📈" : b === "bearish" ? "📉" : "➡️"}
                  </div>
                  <div className="text-lg font-semibold capitalize">{b}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Cycle Day & Level */}
          <div className="grid grid-cols-2 gap-6">
            {/* Cycle Day */}
            <div className="glass rounded-xl p-6">
              <h2 className="text-lg font-semibold text-white mb-4">Cycle Day</h2>
              <div className="space-y-2">
                {([1, 2, 3] as CycleDay[]).map((day) => (
                  <button
                    key={day}
                    onClick={() => setCycleDay(day)}
                    className={`w-full p-4 rounded-lg text-left transition-all ${
                      cycleDay === day
                        ? day === 1
                          ? "bg-yellow-500/20 border border-yellow-500/50"
                          : day === 2
                          ? "bg-orange-500/20 border border-orange-500/50"
                          : "bg-green-500/20 border border-green-500/50"
                        : "bg-white/5 border border-transparent hover:bg-white/10"
                    }`}
                  >
                    <div className="font-medium text-white">{CYCLE_DAY_INFO[day].name}</div>
                    <div className="text-xs text-white/40 mt-1">{CYCLE_DAY_INFO[day].strategy}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Level */}
            <div className="glass rounded-xl p-6">
              <h2 className="text-lg font-semibold text-white mb-4">BTMM Level</h2>
              <div className="space-y-2">
                {(["I", "II", "III"] as BTMMLevel[]).map((l) => (
                  <button
                    key={l}
                    onClick={() => setLevel(l)}
                    className={`w-full p-4 rounded-lg text-left transition-all ${
                      level === l
                        ? "border"
                        : "bg-white/5 border border-transparent hover:bg-white/10"
                    }`}
                    style={{
                      backgroundColor: level === l ? LEVEL_INFO[l].color + "20" : undefined,
                      borderColor: level === l ? LEVEL_INFO[l].color : undefined,
                    }}
                  >
                    <div className="font-medium" style={{ color: LEVEL_INFO[l].color }}>
                      {LEVEL_INFO[l].name}
                    </div>
                    <div className="text-xs text-white/40 mt-1">{LEVEL_INFO[l].description}</div>
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Key Levels */}
          <div className="glass rounded-xl p-6">
            <h2 className="text-lg font-semibold text-white mb-4">Key Levels</h2>
            <div className="grid grid-cols-3 gap-4">
              <LevelInput label="Asian High" defaultValue="1.0985" />
              <LevelInput label="Asian Low" defaultValue="1.0945" />
              <LevelInput label="Previous Day High" defaultValue="1.1010" />
              <LevelInput label="Previous Day Low" defaultValue="1.0920" />
              <LevelInput label="Weekly Open" defaultValue="1.0960" />
              <LevelInput label="Monthly Open" defaultValue="1.0890" />
            </div>
          </div>
        </div>

        {/* Right Column - Notes & Plan */}
        <div className="space-y-6">
          {/* Daily Summary */}
          <div className="glass rounded-xl p-6">
            <h3 className="text-sm font-semibold text-white/60 uppercase tracking-wider mb-4">Today's Summary</h3>
            <div className="space-y-3">
              <SummaryRow label="Pair" value={selectedPair} />
              <SummaryRow
                label="Bias"
                value={bias}
                color={
                  bias === "bullish"
                    ? "#3fb950"
                    : bias === "bearish"
                    ? "#f85149"
                    : "#6e7681"
                }
              />
              <SummaryRow label="Cycle" value={`Day ${cycleDay}`} />
              <SummaryRow label="Level" value={`Level ${level}`} />
            </div>
          </div>

          {/* Trading Plan */}
          <div className="glass rounded-xl p-6">
            <h3 className="text-sm font-semibold text-white/60 uppercase tracking-wider mb-4">Trading Plan</h3>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              className="w-full h-48 trading-input resize-none"
              placeholder="What's your trading plan for today?

- Entry criteria
- Key levels to watch
- Risk management
- Exit strategy"
            />
          </div>

          {/* Save Button */}
          <button className="w-full py-3 bg-vulcan-accent text-white font-medium rounded-lg hover:bg-vulcan-accent/80 transition-colors">
            Save Daily Bias
          </button>

          {/* Previous Days */}
          <div className="glass rounded-xl p-6">
            <h3 className="text-sm font-semibold text-white/60 uppercase tracking-wider mb-4">Recent Days</h3>
            <div className="space-y-2">
              <RecentDayRow date="Dec 19" bias="bullish" result="win" />
              <RecentDayRow date="Dec 18" bias="bearish" result="loss" />
              <RecentDayRow date="Dec 17" bias="bullish" result="win" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function LevelInput({ label, defaultValue }: { label: string; defaultValue: string }) {
  return (
    <div>
      <label className="block text-xs text-white/40 uppercase tracking-wider mb-2">{label}</label>
      <input
        type="text"
        defaultValue={defaultValue}
        className="trading-input w-full font-mono"
      />
    </div>
  );
}

function SummaryRow({ label, value, color }: { label: string; value: string; color?: string }) {
  return (
    <div className="flex justify-between items-center py-2 border-b border-white/5 last:border-0">
      <span className="text-white/40 text-sm">{label}</span>
      <span className="font-medium capitalize" style={{ color: color || "white" }}>
        {value}
      </span>
    </div>
  );
}

function RecentDayRow({
  date,
  bias,
  result,
}: {
  date: string;
  bias: "bullish" | "bearish";
  result: "win" | "loss";
}) {
  return (
    <div className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
      <span className="text-white/60 text-sm">{date}</span>
      <div className="flex items-center gap-2">
        <span
          className={`text-xs capitalize ${
            bias === "bullish" ? "text-trading-bullish" : "text-trading-bearish"
          }`}
        >
          {bias}
        </span>
        <span
          className={`px-2 py-0.5 rounded text-xs font-medium ${
            result === "win"
              ? "bg-trading-bullish/20 text-trading-bullish"
              : "bg-trading-bearish/20 text-trading-bearish"
          }`}
        >
          {result.toUpperCase()}
        </span>
      </div>
    </div>
  );
}
