/**
 * Right Panel Component
 * Trade entry form with position sizing, checklist, and quick actions
 */

"use client";

import { useState } from "react";
import type { TradeDirection, SetupType, BTMMLevel, CycleDay } from "@/lib/trading/types";
import { SETUP_LABELS, TRADING_PAIRS, DEFAULT_CHECKLIST } from "@/lib/trading/constants";
import { PositionSizeCalculator } from "../calculators/PositionSizeCalculator";
import { PreTradeChecklist } from "../entry/PreTradeChecklist";

interface RightPanelProps {
  isCollapsed: boolean;
  onToggleCollapse: () => void;
  selectedPair: string;
  cycleDay: CycleDay;
}

type PanelTab = "entry" | "calculator" | "checklist";

export function RightPanel({
  isCollapsed,
  onToggleCollapse,
  selectedPair,
  cycleDay,
}: RightPanelProps) {
  const [activeTab, setActiveTab] = useState<PanelTab>("entry");
  const [direction, setDirection] = useState<TradeDirection>("long");
  const [setupType, setSetupType] = useState<SetupType>("1a");
  const [level, setLevel] = useState<BTMMLevel>("I");
  const [entryPrice, setEntryPrice] = useState("");
  const [stopLoss, setStopLoss] = useState("");
  const [takeProfit, setTakeProfit] = useState("");
  const [riskPercent, setRiskPercent] = useState("1");

  const currentPair = TRADING_PAIRS.find((p) => p.symbol === selectedPair);
  const pipValue = currentPair?.pipValue || 0.0001;

  // Calculate pips
  const calculatePips = (price1: string, price2: string): number => {
    const p1 = parseFloat(price1);
    const p2 = parseFloat(price2);
    if (isNaN(p1) || isNaN(p2)) return 0;
    return Math.abs(p1 - p2) / pipValue;
  };

  const slPips = calculatePips(entryPrice, stopLoss);
  const tpPips = calculatePips(entryPrice, takeProfit);
  const rrRatio = slPips > 0 ? (tpPips / slPips).toFixed(2) : "0.00";

  return (
    <aside
      className={`trading-right-panel flex flex-col border-l border-white/10 bg-vulcan-darker/50 transition-all duration-300 ${
        isCollapsed ? "w-12" : "w-80"
      }`}
    >
      {/* Collapse Toggle */}
      <button
        onClick={onToggleCollapse}
        className="flex items-center justify-center h-10 border-b border-white/10 hover:bg-white/5 transition-colors"
      >
        <svg
          className={`w-4 h-4 text-white/50 transition-transform ${isCollapsed ? "" : "rotate-180"}`}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 5l7 7-7 7M5 5l7 7-7 7" />
        </svg>
      </button>

      {!isCollapsed && (
        <>
          {/* Tabs */}
          <div className="flex border-b border-white/10">
            {(["entry", "calculator", "checklist"] as PanelTab[]).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`flex-1 py-2.5 text-xs font-medium uppercase tracking-wider transition-all ${
                  activeTab === tab
                    ? "text-vulcan-accent border-b-2 border-vulcan-accent bg-vulcan-accent/5"
                    : "text-white/40 hover:text-white/60"
                }`}
              >
                {tab === "entry" && "Trade"}
                {tab === "calculator" && "Calc"}
                {tab === "checklist" && "Check"}
              </button>
            ))}
          </div>

          {/* Tab Content */}
          <div className="flex-1 overflow-y-auto">
            {activeTab === "entry" && (
              <TradeEntryForm
                direction={direction}
                setDirection={setDirection}
                setupType={setupType}
                setSetupType={setSetupType}
                level={level}
                setLevel={setLevel}
                entryPrice={entryPrice}
                setEntryPrice={setEntryPrice}
                stopLoss={stopLoss}
                setStopLoss={setStopLoss}
                takeProfit={takeProfit}
                setTakeProfit={setTakeProfit}
                riskPercent={riskPercent}
                setRiskPercent={setRiskPercent}
                cycleDay={cycleDay}
                slPips={slPips}
                tpPips={tpPips}
                rrRatio={rrRatio}
                selectedPair={selectedPair}
              />
            )}
            {activeTab === "calculator" && (
              <PositionSizeCalculator
                selectedPair={selectedPair}
                riskPercent={parseFloat(riskPercent) || 1}
              />
            )}
            {activeTab === "checklist" && <PreTradeChecklist />}
          </div>
        </>
      )}

      {/* Collapsed View */}
      {isCollapsed && (
        <div className="flex flex-col items-center gap-3 py-4">
          <button
            onClick={() => { onToggleCollapse(); setActiveTab("entry"); }}
            className="w-8 h-8 rounded-lg bg-white/5 hover:bg-white/10 flex items-center justify-center text-white/50 hover:text-white transition-all"
            title="Trade Entry"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
          </button>
          <button
            onClick={() => { onToggleCollapse(); setActiveTab("calculator"); }}
            className="w-8 h-8 rounded-lg bg-white/5 hover:bg-white/10 flex items-center justify-center text-white/50 hover:text-white transition-all"
            title="Calculator"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
            </svg>
          </button>
          <button
            onClick={() => { onToggleCollapse(); setActiveTab("checklist"); }}
            className="w-8 h-8 rounded-lg bg-white/5 hover:bg-white/10 flex items-center justify-center text-white/50 hover:text-white transition-all"
            title="Checklist"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </button>
        </div>
      )}
    </aside>
  );
}

interface TradeEntryFormProps {
  direction: TradeDirection;
  setDirection: (d: TradeDirection) => void;
  setupType: SetupType;
  setSetupType: (s: SetupType) => void;
  level: BTMMLevel;
  setLevel: (l: BTMMLevel) => void;
  entryPrice: string;
  setEntryPrice: (p: string) => void;
  stopLoss: string;
  setStopLoss: (p: string) => void;
  takeProfit: string;
  setTakeProfit: (p: string) => void;
  riskPercent: string;
  setRiskPercent: (r: string) => void;
  cycleDay: CycleDay;
  slPips: number;
  tpPips: number;
  rrRatio: string;
  selectedPair: string;
}

function TradeEntryForm({
  direction,
  setDirection,
  setupType,
  setSetupType,
  level,
  setLevel,
  entryPrice,
  setEntryPrice,
  stopLoss,
  setStopLoss,
  takeProfit,
  setTakeProfit,
  riskPercent,
  setRiskPercent,
  cycleDay,
  slPips,
  tpPips,
  rrRatio,
  selectedPair,
}: TradeEntryFormProps) {
  return (
    <div className="p-3 space-y-4">
      {/* Direction Toggle */}
      <div>
        <label className="text-xs text-white/40 uppercase tracking-wider mb-2 block">Direction</label>
        <div className="flex gap-2">
          <button
            onClick={() => setDirection("long")}
            className={`flex-1 py-2.5 rounded-lg font-medium text-sm transition-all ${
              direction === "long"
                ? "bg-trading-bullish text-white shadow-lg shadow-trading-bullish/30"
                : "bg-white/5 text-white/50 hover:bg-white/10"
            }`}
          >
            LONG
          </button>
          <button
            onClick={() => setDirection("short")}
            className={`flex-1 py-2.5 rounded-lg font-medium text-sm transition-all ${
              direction === "short"
                ? "bg-trading-bearish text-white shadow-lg shadow-trading-bearish/30"
                : "bg-white/5 text-white/50 hover:bg-white/10"
            }`}
          >
            SHORT
          </button>
        </div>
      </div>

      {/* Setup Type */}
      <div>
        <label className="text-xs text-white/40 uppercase tracking-wider mb-2 block">Setup Type</label>
        <select
          value={setupType}
          onChange={(e) => setSetupType(e.target.value as SetupType)}
          className="trading-select"
        >
          {Object.entries(SETUP_LABELS).map(([key, label]) => (
            <option key={key} value={key}>{label}</option>
          ))}
        </select>
      </div>

      {/* Level & Cycle */}
      <div className="grid grid-cols-2 gap-2">
        <div>
          <label className="text-xs text-white/40 uppercase tracking-wider mb-2 block">Level</label>
          <div className="flex gap-1">
            {(["I", "II", "III"] as BTMMLevel[]).map((l) => (
              <button
                key={l}
                onClick={() => setLevel(l)}
                className={`flex-1 py-1.5 rounded text-xs font-medium transition-all ${
                  level === l
                    ? "bg-vulcan-accent text-white"
                    : "bg-white/5 text-white/50 hover:bg-white/10"
                }`}
              >
                {l}
              </button>
            ))}
          </div>
        </div>
        <div>
          <label className="text-xs text-white/40 uppercase tracking-wider mb-2 block">Cycle</label>
          <div className="flex items-center justify-center py-1.5 rounded bg-white/5 text-sm font-medium">
            <span className={cycleDay === 1 ? "text-yellow-400" : cycleDay === 2 ? "text-orange-400" : "text-green-400"}>
              Day {cycleDay}
            </span>
          </div>
        </div>
      </div>

      {/* Price Inputs */}
      <div className="space-y-2">
        <div>
          <label className="text-xs text-white/40 uppercase tracking-wider mb-1 block">Entry Price</label>
          <input
            type="text"
            value={entryPrice}
            onChange={(e) => setEntryPrice(e.target.value)}
            placeholder="1.0950"
            className="trading-input"
          />
        </div>
        <div className="grid grid-cols-2 gap-2">
          <div>
            <label className="text-xs text-white/40 uppercase tracking-wider mb-1 block">
              Stop Loss <span className="text-trading-bearish">({slPips.toFixed(1)} pips)</span>
            </label>
            <input
              type="text"
              value={stopLoss}
              onChange={(e) => setStopLoss(e.target.value)}
              placeholder="1.0920"
              className="trading-input"
            />
          </div>
          <div>
            <label className="text-xs text-white/40 uppercase tracking-wider mb-1 block">
              Take Profit <span className="text-trading-bullish">({tpPips.toFixed(1)} pips)</span>
            </label>
            <input
              type="text"
              value={takeProfit}
              onChange={(e) => setTakeProfit(e.target.value)}
              placeholder="1.1010"
              className="trading-input"
            />
          </div>
        </div>
      </div>

      {/* Risk */}
      <div>
        <label className="text-xs text-white/40 uppercase tracking-wider mb-2 block">Risk %</label>
        <div className="flex gap-1">
          {["0.5", "1", "2", "3"].map((r) => (
            <button
              key={r}
              onClick={() => setRiskPercent(r)}
              className={`flex-1 py-1.5 rounded text-xs font-medium transition-all ${
                riskPercent === r
                  ? "bg-vulcan-accent text-white"
                  : "bg-white/5 text-white/50 hover:bg-white/10"
              }`}
            >
              {r}%
            </button>
          ))}
        </div>
      </div>

      {/* R:R Display */}
      <div className="p-3 rounded-lg bg-white/5 border border-white/10">
        <div className="flex justify-between items-center">
          <span className="text-xs text-white/40">Risk/Reward</span>
          <span className={`text-lg font-bold ${parseFloat(rrRatio) >= 2 ? "text-trading-bullish" : parseFloat(rrRatio) >= 1 ? "text-yellow-400" : "text-trading-bearish"}`}>
            1:{rrRatio}
          </span>
        </div>
      </div>

      {/* Submit */}
      <button
        className={`w-full py-3 rounded-lg font-bold text-white transition-all ${
          direction === "long"
            ? "bg-gradient-to-r from-trading-bullish to-emerald-600 hover:shadow-lg hover:shadow-trading-bullish/30"
            : "bg-gradient-to-r from-trading-bearish to-red-600 hover:shadow-lg hover:shadow-trading-bearish/30"
        }`}
      >
        {direction === "long" ? "OPEN LONG" : "OPEN SHORT"} {selectedPair}
      </button>
    </div>
  );
}
