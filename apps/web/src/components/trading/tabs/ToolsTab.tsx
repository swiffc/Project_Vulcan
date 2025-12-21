/**
 * Tools Tab Component
 * Trading calculators and utilities
 */

"use client";

import { useState } from "react";
import { DEFAULT_CHECKLIST } from "@/lib/trading/constants";
import type { ChecklistItem } from "@/lib/trading/types";

type ToolView = "calculator" | "checklist" | "adr";

export function ToolsTab() {
  const [view, setView] = useState<ToolView>("calculator");

  return (
    <div className="h-full overflow-auto p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-bold text-white">Trading Tools</h2>
          <p className="text-white/50 text-sm">Calculators and utilities</p>
        </div>

        <div className="flex gap-2">
          {(["calculator", "checklist", "adr"] as ToolView[]).map((v) => (
            <button
              key={v}
              onClick={() => setView(v)}
              className={`px-4 py-2 text-sm font-medium rounded-lg transition-all capitalize ${
                view === v ? "bg-vulcan-accent text-white" : "bg-white/5 text-white/50 hover:bg-white/10"
              }`}
            >
              {v === "adr" ? "ADR" : v}
            </button>
          ))}
        </div>
      </div>

      {/* Tool Content */}
      {view === "calculator" && <PositionSizeCalculator />}
      {view === "checklist" && <PreTradeChecklist />}
      {view === "adr" && <ADRCalculator />}
    </div>
  );
}

/* Position Size Calculator */
function PositionSizeCalculator() {
  const [accountBalance, setAccountBalance] = useState(10000);
  const [riskPercent, setRiskPercent] = useState(1);
  const [stopLossPips, setStopLossPips] = useState(30);
  const [pipValue, setPipValue] = useState(10); // $10 per pip for standard lot

  const riskAmount = accountBalance * (riskPercent / 100);
  const positionSizeLots = stopLossPips > 0 ? riskAmount / (stopLossPips * pipValue) : 0;
  const positionSizeUnits = positionSizeLots * 100000;

  return (
    <div className="grid grid-cols-2 gap-6">
      {/* Inputs */}
      <div className="glass rounded-xl p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Position Size Calculator</h3>
        <div className="space-y-4">
          <div>
            <label className="block text-xs text-white/40 uppercase tracking-wider mb-2">Account Balance ($)</label>
            <input
              type="number"
              value={accountBalance}
              onChange={(e) => setAccountBalance(parseFloat(e.target.value) || 0)}
              className="trading-input w-full font-mono"
            />
          </div>
          <div>
            <label className="block text-xs text-white/40 uppercase tracking-wider mb-2">Risk Per Trade (%)</label>
            <input
              type="number"
              step="0.1"
              value={riskPercent}
              onChange={(e) => setRiskPercent(parseFloat(e.target.value) || 0)}
              className="trading-input w-full font-mono"
            />
          </div>
          <div>
            <label className="block text-xs text-white/40 uppercase tracking-wider mb-2">Stop Loss (Pips)</label>
            <input
              type="number"
              value={stopLossPips}
              onChange={(e) => setStopLossPips(parseFloat(e.target.value) || 0)}
              className="trading-input w-full font-mono"
            />
          </div>
          <div>
            <label className="block text-xs text-white/40 uppercase tracking-wider mb-2">Pip Value ($)</label>
            <input
              type="number"
              step="0.1"
              value={pipValue}
              onChange={(e) => setPipValue(parseFloat(e.target.value) || 0)}
              className="trading-input w-full font-mono"
            />
          </div>
        </div>
      </div>

      {/* Results */}
      <div className="glass rounded-xl p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Results</h3>
        <div className="space-y-4">
          <ResultRow label="Risk Amount" value={`$${riskAmount.toFixed(2)}`} color="#f85149" />
          <ResultRow label="Position Size" value={`${positionSizeLots.toFixed(2)} lots`} color="#3fb950" />
          <ResultRow label="Mini Lots" value={`${(positionSizeLots * 10).toFixed(1)} mini`} />
          <ResultRow label="Micro Lots" value={`${(positionSizeLots * 100).toFixed(0)} micro`} />
          <ResultRow label="Units" value={positionSizeUnits.toLocaleString()} />

          {/* Quick Reference */}
          <div className="mt-6 p-4 bg-vulcan-accent/10 border border-vulcan-accent/30 rounded-lg">
            <div className="text-sm text-vulcan-accent mb-2">Quick Reference</div>
            <div className="text-xs text-white/60 space-y-1">
              <div>1 Standard Lot = 100,000 units</div>
              <div>1 Mini Lot = 10,000 units</div>
              <div>1 Micro Lot = 1,000 units</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

/* Pre-Trade Checklist */
function PreTradeChecklist() {
  const [checklist, setChecklist] = useState<ChecklistItem[]>(DEFAULT_CHECKLIST);

  const toggleItem = (id: string) => {
    setChecklist((prev) => prev.map((item) => (item.id === id ? { ...item, checked: !item.checked } : item)));
  };

  const requiredItems = checklist.filter((item) => item.required);
  const optionalItems = checklist.filter((item) => !item.required);
  const requiredComplete = requiredItems.every((item) => item.checked);
  const checkedCount = checklist.filter((item) => item.checked).length;

  return (
    <div className="glass rounded-xl p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-white">Pre-Trade Checklist</h3>
        <div className={`px-3 py-1 rounded-full text-sm font-medium ${
          requiredComplete
            ? "bg-trading-bullish/20 text-trading-bullish"
            : "bg-trading-bearish/20 text-trading-bearish"
        }`}>
          {requiredComplete ? "Ready to Trade" : "Complete Required Items"}
        </div>
      </div>

      {/* Progress Bar */}
      <div className="mb-6">
        <div className="flex justify-between text-xs text-white/40 mb-2">
          <span>Progress</span>
          <span>{checkedCount}/{checklist.length}</span>
        </div>
        <div className="h-2 bg-white/10 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-vulcan-accent to-purple-500 transition-all"
            style={{ width: `${(checkedCount / checklist.length) * 100}%` }}
          />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-6">
        {/* Required Items */}
        <div>
          <h4 className="text-sm font-medium text-white/60 mb-3">Required</h4>
          <div className="space-y-2">
            {requiredItems.map((item) => (
              <ChecklistItemRow key={item.id} item={item} onToggle={() => toggleItem(item.id)} />
            ))}
          </div>
        </div>

        {/* Optional Items */}
        <div>
          <h4 className="text-sm font-medium text-white/60 mb-3">Optional</h4>
          <div className="space-y-2">
            {optionalItems.map((item) => (
              <ChecklistItemRow key={item.id} item={item} onToggle={() => toggleItem(item.id)} />
            ))}
          </div>
        </div>
      </div>

      {/* Reset Button */}
      <div className="mt-6 flex justify-end">
        <button
          onClick={() => setChecklist(DEFAULT_CHECKLIST)}
          className="px-4 py-2 bg-white/5 text-white/70 rounded-lg hover:bg-white/10 transition-colors text-sm"
        >
          Reset Checklist
        </button>
      </div>
    </div>
  );
}

function ChecklistItemRow({ item, onToggle }: { item: ChecklistItem; onToggle: () => void }) {
  return (
    <label
      className={`flex items-start gap-3 p-3 rounded-lg cursor-pointer transition-all ${
        item.checked
          ? "bg-trading-bullish/10 border border-trading-bullish/30"
          : "bg-white/5 border border-transparent hover:bg-white/10"
      }`}
    >
      <input
        type="checkbox"
        checked={item.checked}
        onChange={onToggle}
        className="mt-0.5 w-4 h-4 rounded border-white/20 bg-white/5 text-vulcan-accent focus:ring-vulcan-accent"
      />
      <div className="flex-1">
        <div className="text-sm font-medium text-white">{item.label}</div>
        {item.description && <div className="text-xs text-white/40 mt-1">{item.description}</div>}
      </div>
    </label>
  );
}

/* ADR Calculator */
function ADRCalculator() {
  const [pair, setPair] = useState("EUR/USD");
  const [todayHigh, setTodayHigh] = useState(1.0985);
  const [todayLow, setTodayLow] = useState(1.0920);

  // Mock ADR data
  const adrData = {
    "EUR/USD": { avg: 80, current: 65 },
    "GBP/USD": { avg: 110, current: 95 },
    "USD/JPY": { avg: 70, current: 55 },
  };

  const selectedADR = adrData[pair as keyof typeof adrData] || { avg: 0, current: 0 };
  const todayRange = Math.round((todayHigh - todayLow) * 10000);
  const remaining = selectedADR.avg - todayRange;
  const percentUsed = Math.min(100, Math.round((todayRange / selectedADR.avg) * 100));

  return (
    <div className="grid grid-cols-2 gap-6">
      <div className="glass rounded-xl p-6">
        <h3 className="text-lg font-semibold text-white mb-4">ADR Calculator</h3>
        <div className="space-y-4">
          <div>
            <label className="block text-xs text-white/40 uppercase tracking-wider mb-2">Currency Pair</label>
            <select
              value={pair}
              onChange={(e) => setPair(e.target.value)}
              className="trading-input w-full"
            >
              <option value="EUR/USD">EUR/USD</option>
              <option value="GBP/USD">GBP/USD</option>
              <option value="USD/JPY">USD/JPY</option>
            </select>
          </div>
          <div>
            <label className="block text-xs text-white/40 uppercase tracking-wider mb-2">Today's High</label>
            <input
              type="number"
              step="0.0001"
              value={todayHigh}
              onChange={(e) => setTodayHigh(parseFloat(e.target.value) || 0)}
              className="trading-input w-full font-mono"
            />
          </div>
          <div>
            <label className="block text-xs text-white/40 uppercase tracking-wider mb-2">Today's Low</label>
            <input
              type="number"
              step="0.0001"
              value={todayLow}
              onChange={(e) => setTodayLow(parseFloat(e.target.value) || 0)}
              className="trading-input w-full font-mono"
            />
          </div>
        </div>
      </div>

      <div className="glass rounded-xl p-6">
        <h3 className="text-lg font-semibold text-white mb-4">ADR Analysis</h3>
        <div className="space-y-4">
          <ResultRow label="Average Daily Range" value={`${selectedADR.avg} pips`} />
          <ResultRow label="Today's Range" value={`${todayRange} pips`} />
          <ResultRow
            label="Remaining"
            value={`${remaining > 0 ? remaining : 0} pips`}
            color={remaining > 0 ? "#3fb950" : "#f85149"}
          />

          {/* ADR Progress */}
          <div className="mt-4">
            <div className="flex justify-between text-xs text-white/40 mb-2">
              <span>ADR Used</span>
              <span>{percentUsed}%</span>
            </div>
            <div className="h-3 bg-white/10 rounded-full overflow-hidden">
              <div
                className={`h-full transition-all ${
                  percentUsed > 80 ? "bg-trading-bearish" : percentUsed > 60 ? "bg-yellow-500" : "bg-trading-bullish"
                }`}
                style={{ width: `${percentUsed}%` }}
              />
            </div>
          </div>

          {/* Trading Recommendation */}
          <div className={`mt-4 p-4 rounded-lg ${
            remaining > 20 ? "bg-trading-bullish/10 border border-trading-bullish/30" : "bg-trading-bearish/10 border border-trading-bearish/30"
          }`}>
            <div className={`text-sm font-medium ${remaining > 20 ? "text-trading-bullish" : "text-trading-bearish"}`}>
              {remaining > 20 ? "Room for Trade" : "ADR Nearly Exhausted"}
            </div>
            <div className="text-xs text-white/60 mt-1">
              {remaining > 20
                ? `Approximately ${remaining} pips remaining in today's range`
                : "Consider waiting for next session or reducing position size"}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function ResultRow({ label, value, color }: { label: string; value: string; color?: string }) {
  return (
    <div className="flex justify-between items-center py-2 border-b border-white/5 last:border-0">
      <span className="text-white/40 text-sm">{label}</span>
      <span className="font-mono font-medium" style={{ color: color || "white" }}>
        {value}
      </span>
    </div>
  );
}
