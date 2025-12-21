/**
 * New Trade Entry Page
 * Full trade entry form with BTMM-specific fields
 */

"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import type {
  Trade,
  TradeDirection,
  SetupType,
  CycleDay,
  BTMMLevel,
  AsianRangeStatus,
  StrikeZone,
  MMBehavior,
  CandlestickPattern,
  TDISignal,
  SessionName,
  ChecklistItem,
} from "@/lib/trading/types";
import {
  TRADING_PAIRS,
  SETUP_LABELS,
  SETUP_DESCRIPTIONS,
  DEFAULT_CHECKLIST,
  CYCLE_DAY_INFO,
  LEVEL_INFO,
  TRADING_COLORS,
} from "@/lib/trading/constants";

type TradeFormData = Omit<Trade, "id" | "createdAt" | "updatedAt">;

export default function NewTradePage() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<"entry" | "btmm" | "checklist" | "notes">("entry");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [checklist, setChecklist] = useState<ChecklistItem[]>(DEFAULT_CHECKLIST);

  const [formData, setFormData] = useState<Partial<TradeFormData>>({
    pair: "EUR/USD",
    direction: "long",
    setupType: "1a",
    cycleDay: 1,
    level: "I",
    asianRange: "small",
    strikeZone: "none",
    mmBehavior: "none",
    candlestickPattern: "none",
    tdiSignal: "none",
    mwPattern: false,
    emaAlignment: false,
    sessionConfirmation: false,
    levelConfirmation: false,
    adrConfirmation: false,
    riskPercent: 1,
    entrySession: "london",
    entryTime: new Date().toISOString(),
  });

  const updateField = <K extends keyof TradeFormData>(field: K, value: TradeFormData[K]) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const toggleChecklistItem = (id: string) => {
    setChecklist((prev) =>
      prev.map((item) =>
        item.id === id ? { ...item, checked: !item.checked } : item
      )
    );
  };

  const requiredCheckedCount = checklist.filter((item) => item.required && item.checked).length;
  const requiredTotalCount = checklist.filter((item) => item.required).length;
  const isChecklistComplete = requiredCheckedCount === requiredTotalCount;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!isChecklistComplete) {
      alert("Please complete all required checklist items before submitting.");
      return;
    }

    setIsSubmitting(true);
    try {
      // TODO: Save trade to API/database
      console.log("Trade data:", formData);
      router.push("/trading/journal");
    } catch (error) {
      console.error("Error saving trade:", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const tabs = [
    { id: "entry", label: "Entry Details" },
    { id: "btmm", label: "BTMM Setup" },
    { id: "checklist", label: "Checklist" },
    { id: "notes", label: "Notes" },
  ] as const;

  return (
    <div className="min-h-screen bg-vulcan-darker p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <Link href="/trading/journal" className="text-vulcan-accent text-sm hover:underline mb-2 inline-block">
            &larr; Back to Journal
          </Link>
          <h1 className="text-2xl font-bold text-white">New Trade Entry</h1>
          <p className="text-white/50">Log your trade with BTMM analysis</p>
        </div>

        <div className="flex items-center gap-4">
          {/* Checklist Progress */}
          <div className="text-right">
            <div className="text-xs text-white/40 mb-1">Checklist</div>
            <div className={`text-sm font-medium ${isChecklistComplete ? "text-trading-bullish" : "text-trading-bearish"}`}>
              {requiredCheckedCount}/{requiredTotalCount} Required
            </div>
          </div>

          <button
            onClick={handleSubmit}
            disabled={isSubmitting || !isChecklistComplete}
            className={`px-6 py-2 rounded-lg font-medium transition-all ${
              isChecklistComplete
                ? "bg-vulcan-accent text-white hover:bg-vulcan-accent/80"
                : "bg-white/10 text-white/30 cursor-not-allowed"
            }`}
          >
            {isSubmitting ? "Saving..." : "Save Trade"}
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-6">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2 text-sm font-medium rounded-lg transition-all ${
              activeTab === tab.id
                ? "bg-vulcan-accent text-white"
                : "bg-white/5 text-white/50 hover:bg-white/10 hover:text-white"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <form onSubmit={handleSubmit}>
        {activeTab === "entry" && (
          <EntryDetailsTab formData={formData} updateField={updateField} />
        )}
        {activeTab === "btmm" && (
          <BTMMSetupTab formData={formData} updateField={updateField} />
        )}
        {activeTab === "checklist" && (
          <ChecklistTab checklist={checklist} onToggle={toggleChecklistItem} />
        )}
        {activeTab === "notes" && (
          <NotesTab formData={formData} updateField={updateField} />
        )}
      </form>
    </div>
  );
}

/* Entry Details Tab */
function EntryDetailsTab({
  formData,
  updateField,
}: {
  formData: Partial<TradeFormData>;
  updateField: <K extends keyof TradeFormData>(field: K, value: TradeFormData[K]) => void;
}) {
  return (
    <div className="grid grid-cols-2 gap-6">
      {/* Left Column */}
      <div className="glass rounded-xl p-6 space-y-4">
        <h2 className="text-lg font-semibold text-white mb-4">Trade Information</h2>

        {/* Pair Selection */}
        <div>
          <label className="block text-xs text-white/40 uppercase tracking-wider mb-2">Currency Pair</label>
          <select
            value={formData.pair || "EUR/USD"}
            onChange={(e) => updateField("pair", e.target.value)}
            className="trading-input w-full"
          >
            {TRADING_PAIRS.map((pair) => (
              <option key={pair.symbol} value={pair.symbol}>
                {pair.symbol} - {pair.displayName}
              </option>
            ))}
          </select>
        </div>

        {/* Direction */}
        <div>
          <label className="block text-xs text-white/40 uppercase tracking-wider mb-2">Direction</label>
          <div className="grid grid-cols-2 gap-2">
            <button
              type="button"
              onClick={() => updateField("direction", "long")}
              className={`py-3 rounded-lg font-medium transition-all ${
                formData.direction === "long"
                  ? "bg-trading-bullish text-white"
                  : "bg-white/5 text-white/50 hover:bg-white/10"
              }`}
            >
              LONG
            </button>
            <button
              type="button"
              onClick={() => updateField("direction", "short")}
              className={`py-3 rounded-lg font-medium transition-all ${
                formData.direction === "short"
                  ? "bg-trading-bearish text-white"
                  : "bg-white/5 text-white/50 hover:bg-white/10"
              }`}
            >
              SHORT
            </button>
          </div>
        </div>

        {/* Session */}
        <div>
          <label className="block text-xs text-white/40 uppercase tracking-wider mb-2">Entry Session</label>
          <div className="grid grid-cols-4 gap-2">
            {(["asian", "london", "newyork", "gap"] as SessionName[]).map((session) => (
              <button
                type="button"
                key={session}
                onClick={() => updateField("entrySession", session)}
                className={`py-2 text-xs font-medium rounded-lg transition-all capitalize ${
                  formData.entrySession === session
                    ? "bg-vulcan-accent text-white"
                    : "bg-white/5 text-white/50 hover:bg-white/10"
                }`}
              >
                {session}
              </button>
            ))}
          </div>
        </div>

        {/* Entry Time */}
        <div>
          <label className="block text-xs text-white/40 uppercase tracking-wider mb-2">Entry Time</label>
          <input
            type="datetime-local"
            value={formData.entryTime?.slice(0, 16) || ""}
            onChange={(e) => updateField("entryTime", new Date(e.target.value).toISOString())}
            className="trading-input w-full"
          />
        </div>
      </div>

      {/* Right Column */}
      <div className="glass rounded-xl p-6 space-y-4">
        <h2 className="text-lg font-semibold text-white mb-4">Price Levels</h2>

        {/* Entry Price */}
        <div>
          <label className="block text-xs text-white/40 uppercase tracking-wider mb-2">Entry Price</label>
          <input
            type="number"
            step="0.00001"
            value={formData.entryPrice || ""}
            onChange={(e) => updateField("entryPrice", parseFloat(e.target.value))}
            className="trading-input w-full font-mono"
            placeholder="1.09500"
          />
        </div>

        {/* Stop Loss */}
        <div>
          <label className="block text-xs text-white/40 uppercase tracking-wider mb-2">Stop Loss</label>
          <input
            type="number"
            step="0.00001"
            value={formData.stopLoss || ""}
            onChange={(e) => updateField("stopLoss", parseFloat(e.target.value))}
            className="trading-input w-full font-mono"
            placeholder="1.09200"
          />
        </div>

        {/* Take Profit 1 */}
        <div>
          <label className="block text-xs text-white/40 uppercase tracking-wider mb-2">Take Profit 1</label>
          <input
            type="number"
            step="0.00001"
            value={formData.takeProfit1 || ""}
            onChange={(e) => updateField("takeProfit1", parseFloat(e.target.value))}
            className="trading-input w-full font-mono"
            placeholder="1.10000"
          />
        </div>

        {/* Take Profit 2 (Optional) */}
        <div>
          <label className="block text-xs text-white/40 uppercase tracking-wider mb-2">Take Profit 2 (Optional)</label>
          <input
            type="number"
            step="0.00001"
            value={formData.takeProfit2 || ""}
            onChange={(e) => updateField("takeProfit2", parseFloat(e.target.value))}
            className="trading-input w-full font-mono"
            placeholder="1.10500"
          />
        </div>

        {/* Position Size & Risk */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-xs text-white/40 uppercase tracking-wider mb-2">Position Size (Lots)</label>
            <input
              type="number"
              step="0.01"
              value={formData.positionSize || ""}
              onChange={(e) => updateField("positionSize", parseFloat(e.target.value))}
              className="trading-input w-full font-mono"
              placeholder="0.10"
            />
          </div>
          <div>
            <label className="block text-xs text-white/40 uppercase tracking-wider mb-2">Risk %</label>
            <input
              type="number"
              step="0.1"
              value={formData.riskPercent || 1}
              onChange={(e) => updateField("riskPercent", parseFloat(e.target.value))}
              className="trading-input w-full font-mono"
              placeholder="1.0"
            />
          </div>
        </div>
      </div>
    </div>
  );
}

/* BTMM Setup Tab */
function BTMMSetupTab({
  formData,
  updateField,
}: {
  formData: Partial<TradeFormData>;
  updateField: <K extends keyof TradeFormData>(field: K, value: TradeFormData[K]) => void;
}) {
  return (
    <div className="grid grid-cols-2 gap-6">
      {/* Left Column - Setup Type & Cycle */}
      <div className="glass rounded-xl p-6 space-y-4">
        <h2 className="text-lg font-semibold text-white mb-4">Setup Classification</h2>

        {/* Setup Type */}
        <div>
          <label className="block text-xs text-white/40 uppercase tracking-wider mb-2">Setup Type</label>
          <select
            value={formData.setupType || "1a"}
            onChange={(e) => updateField("setupType", e.target.value as SetupType)}
            className="trading-input w-full"
          >
            {Object.entries(SETUP_LABELS).map(([type, label]) => (
              <option key={type} value={type}>
                {label}
              </option>
            ))}
          </select>
          {formData.setupType && (
            <p className="mt-2 text-xs text-white/40">
              {SETUP_DESCRIPTIONS[formData.setupType]}
            </p>
          )}
        </div>

        {/* Cycle Day */}
        <div>
          <label className="block text-xs text-white/40 uppercase tracking-wider mb-2">Cycle Day</label>
          <div className="grid grid-cols-3 gap-2">
            {([1, 2, 3] as CycleDay[]).map((day) => (
              <button
                type="button"
                key={day}
                onClick={() => updateField("cycleDay", day)}
                className={`py-3 rounded-lg font-medium transition-all ${
                  formData.cycleDay === day
                    ? day === 1
                      ? "bg-yellow-500/20 text-yellow-400 border border-yellow-500/30"
                      : day === 2
                      ? "bg-orange-500/20 text-orange-400 border border-orange-500/30"
                      : "bg-green-500/20 text-green-400 border border-green-500/30"
                    : "bg-white/5 text-white/50 hover:bg-white/10 border border-transparent"
                }`}
              >
                Day {day}
              </button>
            ))}
          </div>
          {formData.cycleDay && (
            <div className="mt-2 p-3 bg-white/5 rounded-lg">
              <div className="text-sm font-medium text-white">{CYCLE_DAY_INFO[formData.cycleDay].name}</div>
              <div className="text-xs text-white/40 mt-1">{CYCLE_DAY_INFO[formData.cycleDay].description}</div>
            </div>
          )}
        </div>

        {/* Level */}
        <div>
          <label className="block text-xs text-white/40 uppercase tracking-wider mb-2">BTMM Level</label>
          <div className="grid grid-cols-3 gap-2">
            {(["I", "II", "III"] as BTMMLevel[]).map((level) => (
              <button
                type="button"
                key={level}
                onClick={() => updateField("level", level)}
                className={`py-3 rounded-lg font-medium transition-all ${
                  formData.level === level
                    ? `text-white`
                    : "bg-white/5 text-white/50 hover:bg-white/10"
                }`}
                style={{
                  backgroundColor:
                    formData.level === level
                      ? LEVEL_INFO[level].color + "33"
                      : undefined,
                  borderColor:
                    formData.level === level
                      ? LEVEL_INFO[level].color
                      : "transparent",
                  borderWidth: "1px",
                }}
              >
                Level {level}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Right Column - Market Context */}
      <div className="glass rounded-xl p-6 space-y-4">
        <h2 className="text-lg font-semibold text-white mb-4">Market Context</h2>

        {/* Asian Range */}
        <div>
          <label className="block text-xs text-white/40 uppercase tracking-wider mb-2">Asian Range</label>
          <div className="grid grid-cols-2 gap-2">
            {(["small", "large"] as AsianRangeStatus[]).map((size) => (
              <button
                type="button"
                key={size}
                onClick={() => updateField("asianRange", size)}
                className={`py-2 rounded-lg text-sm font-medium transition-all capitalize ${
                  formData.asianRange === size
                    ? "bg-vulcan-accent text-white"
                    : "bg-white/5 text-white/50 hover:bg-white/10"
                }`}
              >
                {size} (&lt;50 / &gt;50 pips)
              </button>
            ))}
          </div>
        </div>

        {/* MM Behavior */}
        <div>
          <label className="block text-xs text-white/40 uppercase tracking-wider mb-2">MM Behavior</label>
          <select
            value={formData.mmBehavior || "none"}
            onChange={(e) => updateField("mmBehavior", e.target.value as MMBehavior)}
            className="trading-input w-full"
          >
            <option value="none">None</option>
            <option value="trap_up">Trap Up</option>
            <option value="trap_down">Trap Down</option>
            <option value="stop_hunt_high">Stop Hunt High</option>
            <option value="stop_hunt_low">Stop Hunt Low</option>
          </select>
        </div>

        {/* Confirmations */}
        <div className="space-y-2">
          <label className="block text-xs text-white/40 uppercase tracking-wider mb-2">Confirmations</label>

          <label className="flex items-center gap-3 p-3 bg-white/5 rounded-lg cursor-pointer hover:bg-white/10 transition-colors">
            <input
              type="checkbox"
              checked={formData.mwPattern || false}
              onChange={(e) => updateField("mwPattern", e.target.checked)}
              className="w-4 h-4 rounded border-white/20 bg-white/5 text-vulcan-accent focus:ring-vulcan-accent"
            />
            <span className="text-sm text-white">M/W Pattern Visible</span>
          </label>

          <label className="flex items-center gap-3 p-3 bg-white/5 rounded-lg cursor-pointer hover:bg-white/10 transition-colors">
            <input
              type="checkbox"
              checked={formData.emaAlignment || false}
              onChange={(e) => updateField("emaAlignment", e.target.checked)}
              className="w-4 h-4 rounded border-white/20 bg-white/5 text-vulcan-accent focus:ring-vulcan-accent"
            />
            <span className="text-sm text-white">EMA Alignment</span>
          </label>

          <label className="flex items-center gap-3 p-3 bg-white/5 rounded-lg cursor-pointer hover:bg-white/10 transition-colors">
            <input
              type="checkbox"
              checked={formData.sessionConfirmation || false}
              onChange={(e) => updateField("sessionConfirmation", e.target.checked)}
              className="w-4 h-4 rounded border-white/20 bg-white/5 text-vulcan-accent focus:ring-vulcan-accent"
            />
            <span className="text-sm text-white">Session Confirmation</span>
          </label>
        </div>

        {/* TDI Signal */}
        <div>
          <label className="block text-xs text-white/40 uppercase tracking-wider mb-2">TDI Signal</label>
          <select
            value={formData.tdiSignal || "none"}
            onChange={(e) => updateField("tdiSignal", e.target.value as TDISignal)}
            className="trading-input w-full"
          >
            <option value="none">None</option>
            <option value="sharkfin">Sharkfin</option>
            <option value="blood_in_water">Blood in Water</option>
            <option value="cross_above">Cross Above</option>
            <option value="cross_below">Cross Below</option>
          </select>
        </div>

        {/* Candlestick Pattern */}
        <div>
          <label className="block text-xs text-white/40 uppercase tracking-wider mb-2">Candlestick Pattern</label>
          <select
            value={formData.candlestickPattern || "none"}
            onChange={(e) => updateField("candlestickPattern", e.target.value as CandlestickPattern)}
            className="trading-input w-full"
          >
            <option value="none">None</option>
            <option value="morning_star">Morning Star</option>
            <option value="evening_star">Evening Star</option>
            <option value="hammer">Hammer</option>
            <option value="inverted_hammer">Inverted Hammer</option>
            <option value="engulfing_bullish">Bullish Engulfing</option>
            <option value="engulfing_bearish">Bearish Engulfing</option>
            <option value="doji">Doji</option>
            <option value="shooting_star">Shooting Star</option>
          </select>
        </div>
      </div>
    </div>
  );
}

/* Checklist Tab */
function ChecklistTab({
  checklist,
  onToggle,
}: {
  checklist: ChecklistItem[];
  onToggle: (id: string) => void;
}) {
  const requiredItems = checklist.filter((item) => item.required);
  const optionalItems = checklist.filter((item) => !item.required);
  const requiredComplete = requiredItems.every((item) => item.checked);

  return (
    <div className="glass rounded-xl p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-semibold text-white">Pre-Trade Checklist</h2>
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
          <span>{checklist.filter((i) => i.checked).length}/{checklist.length}</span>
        </div>
        <div className="h-2 bg-white/10 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-vulcan-accent to-purple-500 transition-all"
            style={{
              width: `${(checklist.filter((i) => i.checked).length / checklist.length) * 100}%`,
            }}
          />
        </div>
      </div>

      {/* Required Items */}
      <div className="mb-6">
        <h3 className="text-sm font-medium text-white/60 mb-3">Required</h3>
        <div className="space-y-2">
          {requiredItems.map((item) => (
            <label
              key={item.id}
              className={`flex items-start gap-3 p-4 rounded-lg cursor-pointer transition-all ${
                item.checked
                  ? "bg-trading-bullish/10 border border-trading-bullish/30"
                  : "bg-white/5 border border-transparent hover:bg-white/10"
              }`}
            >
              <input
                type="checkbox"
                checked={item.checked}
                onChange={() => onToggle(item.id)}
                className="mt-0.5 w-5 h-5 rounded border-white/20 bg-white/5 text-vulcan-accent focus:ring-vulcan-accent"
              />
              <div className="flex-1">
                <div className="font-medium text-white">{item.label}</div>
                {item.description && (
                  <div className="text-xs text-white/40 mt-1">{item.description}</div>
                )}
              </div>
            </label>
          ))}
        </div>
      </div>

      {/* Optional Items */}
      <div>
        <h3 className="text-sm font-medium text-white/60 mb-3">Optional</h3>
        <div className="space-y-2">
          {optionalItems.map((item) => (
            <label
              key={item.id}
              className={`flex items-start gap-3 p-4 rounded-lg cursor-pointer transition-all ${
                item.checked
                  ? "bg-vulcan-accent/10 border border-vulcan-accent/30"
                  : "bg-white/5 border border-transparent hover:bg-white/10"
              }`}
            >
              <input
                type="checkbox"
                checked={item.checked}
                onChange={() => onToggle(item.id)}
                className="mt-0.5 w-5 h-5 rounded border-white/20 bg-white/5 text-vulcan-accent focus:ring-vulcan-accent"
              />
              <div className="flex-1">
                <div className="font-medium text-white">{item.label}</div>
                {item.description && (
                  <div className="text-xs text-white/40 mt-1">{item.description}</div>
                )}
              </div>
            </label>
          ))}
        </div>
      </div>
    </div>
  );
}

/* Notes Tab */
function NotesTab({
  formData,
  updateField,
}: {
  formData: Partial<TradeFormData>;
  updateField: <K extends keyof TradeFormData>(field: K, value: TradeFormData[K]) => void;
}) {
  return (
    <div className="grid grid-cols-2 gap-6">
      {/* Left Column */}
      <div className="glass rounded-xl p-6 space-y-4">
        <h2 className="text-lg font-semibold text-white mb-4">Trade Notes</h2>

        {/* Pre-Trade Notes */}
        <div>
          <label className="block text-xs text-white/40 uppercase tracking-wider mb-2">Pre-Trade Analysis</label>
          <textarea
            value={formData.preTradeNotes || ""}
            onChange={(e) => updateField("preTradeNotes", e.target.value)}
            className="trading-input w-full h-32 resize-none"
            placeholder="What is your analysis? Why are you taking this trade?"
          />
        </div>

        {/* During Trade Notes */}
        <div>
          <label className="block text-xs text-white/40 uppercase tracking-wider mb-2">During Trade (Optional)</label>
          <textarea
            value={formData.duringTradeNotes || ""}
            onChange={(e) => updateField("duringTradeNotes", e.target.value)}
            className="trading-input w-full h-24 resize-none"
            placeholder="Any observations while the trade is running..."
          />
        </div>
      </div>

      {/* Right Column */}
      <div className="glass rounded-xl p-6 space-y-4">
        <h2 className="text-lg font-semibold text-white mb-4">Screenshots</h2>

        {/* Entry Screenshot */}
        <div>
          <label className="block text-xs text-white/40 uppercase tracking-wider mb-2">Entry Screenshot</label>
          <div className="border-2 border-dashed border-white/20 rounded-lg p-8 text-center hover:border-vulcan-accent/50 transition-colors cursor-pointer">
            <svg className="w-8 h-8 mx-auto text-white/30 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <div className="text-sm text-white/40">Click to upload or drag & drop</div>
            <div className="text-xs text-white/20 mt-1">PNG, JPG up to 5MB</div>
          </div>
        </div>

        {/* Analysis Screenshot */}
        <div>
          <label className="block text-xs text-white/40 uppercase tracking-wider mb-2">Analysis Screenshot (Optional)</label>
          <div className="border-2 border-dashed border-white/20 rounded-lg p-6 text-center hover:border-vulcan-accent/50 transition-colors cursor-pointer">
            <svg className="w-6 h-6 mx-auto text-white/30 mb-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <div className="text-xs text-white/40">Upload higher TF analysis</div>
          </div>
        </div>
      </div>
    </div>
  );
}
