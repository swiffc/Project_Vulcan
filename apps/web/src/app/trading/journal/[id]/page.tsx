/**
 * Trade Detail/Edit Page
 * View and edit existing trade entries
 */

"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import type { Trade, TradeResult } from "@/lib/trading/types";
import {
  SETUP_LABELS,
  SETUP_DESCRIPTIONS,
  CYCLE_DAY_INFO,
  LEVEL_INFO,
  TRADING_COLORS,
} from "@/lib/trading/constants";

// Mock data - replace with API call
const mockTrade: Trade = {
  id: "1",
  pair: "EUR/USD",
  direction: "long",
  entryPrice: 1.095,
  exitPrice: 1.102,
  stopLoss: 1.092,
  takeProfit1: 1.102,
  positionSize: 0.1,
  riskPercent: 1,
  setupType: "1a",
  cycleDay: 3,
  level: "I",
  asianRange: "small",
  asianRangePips: 35,
  strikeZone: "+25-50",
  mmBehavior: "stop_hunt_low",
  mwPattern: true,
  mwPatternType: "W",
  candlestickPattern: "morning_star",
  emaAlignment: true,
  tdiSignal: "sharkfin",
  sessionConfirmation: true,
  levelConfirmation: true,
  adrConfirmation: true,
  entryScreenshot: "/screenshots/entry-1.png",
  preTradeNotes: "Strong bullish divergence on TDI. W pattern forming at Level I. Asian range was small, room for expansion.",
  duringTradeNotes: "Price pulled back slightly after entry but EMAs held. Added to position at the water EMA.",
  postTradeNotes: "Trade hit TP1 exactly. Could have held for TP2 but followed the plan.",
  lessonsLearned: "Trust the setup. The pullback was scary but the confluence was strong.",
  entryTime: "2025-12-19T08:30:00Z",
  exitTime: "2025-12-19T14:45:00Z",
  createdAt: "2025-12-19T08:30:00Z",
  updatedAt: "2025-12-19T14:45:00Z",
  result: "win",
  pnlPips: 70,
  pnlDollars: 700,
  rMultiple: 2.3,
  entrySession: "london",
};

export default function TradeDetailPage() {
  const params = useParams();
  const router = useRouter();
  const [trade, setTrade] = useState<Trade | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [activeTab, setActiveTab] = useState<"details" | "analysis" | "review">("details");

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchTrade() {
      if (!params.id) return;
      
      try {
        setLoading(true);
        const response = await fetch(`/api/trading/journal/${params.id}`);
        if (!response.ok) {
          if (response.status === 404) throw new Error("Trade not found");
          throw new Error("Failed to fetch trade");
        }
        const data = await response.json();
        
        // Map Prisma DB snake_case fields back to frontend camelCase expectations
        const mappedTrade: Trade = {
          ...data,
          pair: data.symbol,
          entryPrice: data.entry_price,
          exitPrice: data.exit_price,
          positionSize: data.quantity,
          riskPercent: data.risk_percent || 1,
          setupType: data.setup,
          entryTime: data.created_at,
          exitTime: data.updated_at,
          stopLoss: data.stop,
          takeProfit1: data.target,
        };
        
        setTrade(mappedTrade);
      } catch (err: any) {
        console.error(err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    fetchTrade();
  }, [params.id]);

  if (loading) {
    return (
      <div className="min-h-screen bg-vulcan-darker flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-vulcan-accent"></div>
          <div className="text-white/50">Loading trade details...</div>
        </div>
      </div>
    );
  }

  if (error || !trade) {
    return (
      <div className="min-h-screen bg-vulcan-darker flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-400 mb-4 font-bold">🛑 {error || "Trade not found"}</div>
          <Link href="/trading/journal" className="text-vulcan-accent hover:underline">
            Return to Journal
          </Link>
        </div>
      </div>
    );
  }

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString("en-US", {
      weekday: "short",
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const tabs = [
    { id: "details", label: "Trade Details" },
    { id: "analysis", label: "BTMM Analysis" },
    { id: "review", label: "Post-Trade Review" },
  ] as const;

  return (
    <div className="min-h-screen bg-vulcan-darker p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <Link href="/trading/journal" className="text-vulcan-accent text-sm hover:underline mb-2 inline-block">
            &larr; Back to Journal
          </Link>
          <div className="flex items-center gap-4">
            <h1 className="text-2xl font-bold text-white">{trade.pair}</h1>
            <span
              className={`px-3 py-1 rounded-full text-sm font-bold ${
                trade.direction === "long"
                  ? "bg-trading-bullish/20 text-trading-bullish"
                  : "bg-trading-bearish/20 text-trading-bearish"
              }`}
            >
              {trade.direction.toUpperCase()}
            </span>
            <ResultBadge result={trade.result} />
          </div>
          <p className="text-white/50">{formatDate(trade.entryTime)}</p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setIsEditing(!isEditing)}
            className="px-4 py-2 bg-white/5 text-white/70 rounded-lg hover:bg-white/10 transition-colors"
          >
            {isEditing ? "Cancel" : "Edit"}
          </button>
          <button
            onClick={() => router.push("/trading/journal")}
            className="px-4 py-2 bg-vulcan-accent text-white rounded-lg hover:bg-vulcan-accent/80 transition-colors"
          >
            Close Trade
          </button>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-5 gap-4 mb-6">
        <StatCard label="P/L (Pips)" value={`${trade.pnlPips! >= 0 ? "+" : ""}${trade.pnlPips}`} positive={trade.pnlPips! >= 0} />
        <StatCard label="P/L ($)" value={`${trade.pnlDollars! >= 0 ? "+" : ""}$${trade.pnlDollars}`} positive={trade.pnlDollars! >= 0} />
        <StatCard label="R Multiple" value={`${trade.rMultiple! >= 0 ? "+" : ""}${trade.rMultiple?.toFixed(1)}R`} positive={trade.rMultiple! >= 0} />
        <StatCard label="Risk %" value={`${trade.riskPercent}%`} />
        <StatCard label="Duration" value={calculateDuration(trade.entryTime, trade.exitTime!)} />
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
      {activeTab === "details" && <DetailsTab trade={trade} />}
      {activeTab === "analysis" && <AnalysisTab trade={trade} />}
      {activeTab === "review" && <ReviewTab trade={trade} />}
    </div>
  );
}

function StatCard({ label, value, positive }: { label: string; value: string; positive?: boolean }) {
  return (
    <div className="glass rounded-xl p-4">
      <div className="text-xs text-white/40 uppercase tracking-wider mb-1">{label}</div>
      <div
        className={`text-xl font-bold font-mono ${
          positive === undefined ? "text-white" : positive ? "text-trading-bullish" : "text-trading-bearish"
        }`}
      >
        {value}
      </div>
    </div>
  );
}

function ResultBadge({ result }: { result?: TradeResult }) {
  if (!result) return null;

  const styles = {
    win: "bg-trading-bullish/20 text-trading-bullish",
    loss: "bg-trading-bearish/20 text-trading-bearish",
    breakeven: "bg-yellow-500/20 text-yellow-400",
  };

  return (
    <span className={`px-3 py-1 rounded-full text-sm font-bold ${styles[result]}`}>
      {result.toUpperCase()}
    </span>
  );
}

function calculateDuration(start: string, end: string): string {
  const diff = new Date(end).getTime() - new Date(start).getTime();
  const hours = Math.floor(diff / (1000 * 60 * 60));
  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
  return `${hours}h ${minutes}m`;
}

/* Details Tab */
function DetailsTab({ trade }: { trade: Trade }) {
  return (
    <div className="grid grid-cols-2 gap-6">
      {/* Left - Entry Info */}
      <div className="glass rounded-xl p-6">
        <h2 className="text-lg font-semibold text-white mb-4">Entry Information</h2>
        <div className="space-y-4">
          <DetailRow label="Entry Price" value={trade.entryPrice.toString()} mono />
          <DetailRow label="Stop Loss" value={trade.stopLoss.toString()} mono />
          <DetailRow label="Take Profit 1" value={trade.takeProfit1.toString()} mono />
          {trade.takeProfit2 && <DetailRow label="Take Profit 2" value={trade.takeProfit2.toString()} mono />}
          <DetailRow label="Position Size" value={`${trade.positionSize} lots`} />
          <DetailRow label="Entry Session" value={trade.entrySession} capitalize />
        </div>
      </div>

      {/* Right - Exit Info */}
      <div className="glass rounded-xl p-6">
        <h2 className="text-lg font-semibold text-white mb-4">Exit Information</h2>
        <div className="space-y-4">
          <DetailRow label="Exit Price" value={trade.exitPrice?.toString() || "Open"} mono />
          <DetailRow label="Exit Time" value={trade.exitTime ? new Date(trade.exitTime).toLocaleString() : "Open"} />
          <DetailRow label="Result" value={trade.result?.toUpperCase() || "Pending"} />
          <DetailRow label="P/L Pips" value={`${trade.pnlPips! >= 0 ? "+" : ""}${trade.pnlPips}`} />
          <DetailRow label="P/L Dollars" value={`$${trade.pnlDollars}`} />
          <DetailRow label="R Multiple" value={`${trade.rMultiple?.toFixed(2)}R`} />
        </div>
      </div>

      {/* Screenshot */}
      {trade.entryScreenshot && (
        <div className="col-span-2 glass rounded-xl p-6">
          <h2 className="text-lg font-semibold text-white mb-4">Entry Screenshot</h2>
          <div className="aspect-video bg-white/5 rounded-lg flex items-center justify-center">
            <span className="text-white/40">Screenshot would appear here</span>
          </div>
        </div>
      )}
    </div>
  );
}

/* Analysis Tab */
function AnalysisTab({ trade }: { trade: Trade }) {
  return (
    <div className="grid grid-cols-2 gap-6">
      {/* Left - Setup Info */}
      <div className="glass rounded-xl p-6">
        <h2 className="text-lg font-semibold text-white mb-4">Setup Classification</h2>
        <div className="space-y-4">
          <div>
            <div className="text-xs text-white/40 uppercase tracking-wider mb-1">Setup Type</div>
            <div className="text-white font-medium">{SETUP_LABELS[trade.setupType]}</div>
            <div className="text-xs text-white/40 mt-1">{SETUP_DESCRIPTIONS[trade.setupType]}</div>
          </div>

          <div>
            <div className="text-xs text-white/40 uppercase tracking-wider mb-1">Cycle Day</div>
            <div className="flex items-center gap-2">
              <span
                className={`px-2 py-1 rounded text-sm font-medium ${
                  trade.cycleDay === 1
                    ? "bg-yellow-500/20 text-yellow-400"
                    : trade.cycleDay === 2
                    ? "bg-orange-500/20 text-orange-400"
                    : "bg-green-500/20 text-green-400"
                }`}
              >
                Day {trade.cycleDay}
              </span>
              <span className="text-white/60">{CYCLE_DAY_INFO[trade.cycleDay].name.split(" - ")[1]}</span>
            </div>
          </div>

          <div>
            <div className="text-xs text-white/40 uppercase tracking-wider mb-1">BTMM Level</div>
            <div className="flex items-center gap-2">
              <span
                className="px-2 py-1 rounded text-sm font-medium"
                style={{
                  backgroundColor: LEVEL_INFO[trade.level].color + "33",
                  color: LEVEL_INFO[trade.level].color,
                }}
              >
                Level {trade.level}
              </span>
              <span className="text-white/60">{LEVEL_INFO[trade.level].name.split(" - ")[1]}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Right - Confirmations */}
      <div className="glass rounded-xl p-6">
        <h2 className="text-lg font-semibold text-white mb-4">Trade Confirmations</h2>
        <div className="space-y-3">
          <ConfirmationItem label="M/W Pattern" checked={trade.mwPattern} value={trade.mwPatternType} />
          <ConfirmationItem label="EMA Alignment" checked={trade.emaAlignment} />
          <ConfirmationItem label="TDI Signal" checked={trade.tdiSignal !== "none"} value={trade.tdiSignal} />
          <ConfirmationItem label="Candlestick Pattern" checked={trade.candlestickPattern !== "none"} value={trade.candlestickPattern} />
          <ConfirmationItem label="Session Confirmation" checked={trade.sessionConfirmation} />
          <ConfirmationItem label="Level Confirmation" checked={trade.levelConfirmation} />
          <ConfirmationItem label="ADR Confirmation" checked={trade.adrConfirmation} />
        </div>
      </div>

      {/* Market Context */}
      <div className="col-span-2 glass rounded-xl p-6">
        <h2 className="text-lg font-semibold text-white mb-4">Market Context</h2>
        <div className="grid grid-cols-4 gap-4">
          <DetailRow label="Asian Range" value={trade.asianRange} capitalize />
          <DetailRow label="Asian Pips" value={trade.asianRangePips?.toString() || "N/A"} />
          <DetailRow label="Strike Zone" value={trade.strikeZone} />
          <DetailRow label="MM Behavior" value={trade.mmBehavior.replace(/_/g, " ")} capitalize />
        </div>
      </div>
    </div>
  );
}

/* Review Tab */
function ReviewTab({ trade }: { trade: Trade }) {
  return (
    <div className="space-y-6">
      {/* Notes Grid */}
      <div className="grid grid-cols-2 gap-6">
        {/* Pre-Trade Notes */}
        <div className="glass rounded-xl p-6">
          <h2 className="text-lg font-semibold text-white mb-4">Pre-Trade Analysis</h2>
          <p className="text-white/70 whitespace-pre-wrap">
            {trade.preTradeNotes || "No pre-trade notes recorded."}
          </p>
        </div>

        {/* During Trade Notes */}
        <div className="glass rounded-xl p-6">
          <h2 className="text-lg font-semibold text-white mb-4">During Trade Notes</h2>
          <p className="text-white/70 whitespace-pre-wrap">
            {trade.duringTradeNotes || "No notes recorded during the trade."}
          </p>
        </div>
      </div>

      {/* Post Trade Review */}
      <div className="glass rounded-xl p-6">
        <h2 className="text-lg font-semibold text-white mb-4">Post-Trade Review</h2>
        <p className="text-white/70 whitespace-pre-wrap">
          {trade.postTradeNotes || "No post-trade review recorded."}
        </p>
      </div>

      {/* Lessons Learned */}
      <div className="glass rounded-xl p-6 border border-vulcan-accent/30">
        <h2 className="text-lg font-semibold text-vulcan-accent mb-4">Lessons Learned</h2>
        <p className="text-white/70 whitespace-pre-wrap">
          {trade.lessonsLearned || "No lessons recorded yet."}
        </p>
      </div>

      {/* Trade Score (Future Feature) */}
      <div className="glass rounded-xl p-6">
        <h2 className="text-lg font-semibold text-white mb-4">Trade Score</h2>
        <div className="flex items-center gap-8">
          <div className="text-center">
            <div className="text-4xl font-bold text-vulcan-accent">8.5</div>
            <div className="text-xs text-white/40 mt-1">Overall Score</div>
          </div>
          <div className="flex-1 space-y-2">
            <ScoreBar label="Setup Quality" score={9} />
            <ScoreBar label="Entry Timing" score={8} />
            <ScoreBar label="Risk Management" score={9} />
            <ScoreBar label="Trade Execution" score={8} />
          </div>
        </div>
      </div>
    </div>
  );
}

function DetailRow({ label, value, mono, capitalize }: { label: string; value: string; mono?: boolean; capitalize?: boolean }) {
  return (
    <div className="flex justify-between items-center py-2 border-b border-white/5 last:border-0">
      <span className="text-white/40 text-sm">{label}</span>
      <span className={`text-white font-medium ${mono ? "font-mono" : ""} ${capitalize ? "capitalize" : ""}`}>
        {value}
      </span>
    </div>
  );
}

function ConfirmationItem({ label, checked, value }: { label: string; checked: boolean; value?: string }) {
  return (
    <div className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
      <span className="text-white/70">{label}</span>
      <div className="flex items-center gap-2">
        {value && value !== "none" && (
          <span className="text-xs text-white/40 capitalize">{value.replace(/_/g, " ")}</span>
        )}
        <span
          className={`w-5 h-5 rounded-full flex items-center justify-center ${
            checked ? "bg-trading-bullish/20 text-trading-bullish" : "bg-white/10 text-white/30"
          }`}
        >
          {checked ? "✓" : "✗"}
        </span>
      </div>
    </div>
  );
}

function ScoreBar({ label, score }: { label: string; score: number }) {
  return (
    <div className="flex items-center gap-3">
      <span className="text-xs text-white/40 w-32">{label}</span>
      <div className="flex-1 h-2 bg-white/10 rounded-full overflow-hidden">
        <div
          className="h-full bg-gradient-to-r from-vulcan-accent to-purple-500"
          style={{ width: `${score * 10}%` }}
        />
      </div>
      <span className="text-xs text-white font-mono w-6">{score}</span>
    </div>
  );
}
