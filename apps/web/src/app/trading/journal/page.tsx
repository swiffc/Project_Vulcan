/**
 * Trade Journal Page
 * List of all trades with filtering and search
 */

"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import type { Trade, TradeResult, SetupType } from "@/lib/trading/types";
import { SETUP_LABELS, TRADING_COLORS } from "@/lib/trading/constants";

export default function JournalPage() {
  const [filter, setFilter] = useState<"all" | TradeResult>("all");
  const [searchPair, setSearchPair] = useState("");
  const [trades, setTrades] = useState<Partial<Trade>[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchTrades();
  }, []);

  const fetchTrades = async () => {
    try {
      const response = await fetch("/api/trading/journal");
      if (!response.ok) {
        throw new Error("Failed to fetch trades");
      }
      const data = await response.json();
      setTrades(data);
    } catch (err) {
      console.error("Error fetching trades:", err);
      setError("Failed to load trades. Please ensure the database is running.");
    } finally {
      setLoading(false);
    }
  };

  const filteredTrades = trades.filter((trade) => {
    const matchesFilter = filter === "all" || trade.result === filter;
    const matchesSearch = !searchPair || trade.pair?.toLowerCase().includes(searchPair.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  const stats = {
    total: trades.length,
    wins: trades.filter((t) => t.result === "win").length,
    losses: trades.filter((t) => t.result === "loss").length,
    winRate: trades.length > 0
      ? ((trades.filter((t) => t.result === "win").length / trades.length) * 100).toFixed(1)
      : "0",
  };

  return (
    <div className="min-h-screen bg-vulcan-darker p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <Link href="/trading" className="text-vulcan-accent text-sm hover:underline mb-2 inline-block">
            ← Back to Trading
          </Link>
          <h1 className="text-2xl font-bold text-white">Trade Journal</h1>
          <p className="text-white/50">Review and analyze your trades</p>
        </div>
        <Link
          href="/trading/journal/new"
          className="px-4 py-2 bg-vulcan-accent text-white rounded-lg hover:bg-vulcan-accent/80 transition-colors font-medium"
        >
          + New Trade
        </Link>
      </div>

      {/* Stats Bar */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <StatCard label="Total Trades" value={stats.total} />
        <StatCard label="Wins" value={stats.wins} color="text-trading-bullish" />
        <StatCard label="Losses" value={stats.losses} color="text-trading-bearish" />
        <StatCard label="Win Rate" value={`${stats.winRate}%`} color={parseFloat(stats.winRate) >= 50 ? "text-trading-bullish" : "text-trading-bearish"} />
      </div>

      {/* Filters */}
      <div className="flex items-center gap-4 mb-6">
        <div className="flex gap-2">
          {(["all", "win", "loss", "breakeven"] as const).map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-3 py-1.5 text-sm font-medium rounded-lg transition-all ${
                filter === f
                  ? "bg-vulcan-accent text-white"
                  : "bg-white/5 text-white/50 hover:bg-white/10"
              }`}
            >
              {f.charAt(0).toUpperCase() + f.slice(1)}
            </button>
          ))}
        </div>
        <input
          type="text"
          value={searchPair}
          onChange={(e) => setSearchPair(e.target.value)}
          placeholder="Search pair..."
          className="trading-input w-48"
        />
      </div>

      {/* Trades Table */}
      <div className="glass rounded-xl overflow-hidden">
        {loading && (
          <div className="p-8 text-center text-white/40">
            Loading trades...
          </div>
        )}

        {error && (
          <div className="p-8 text-center text-trading-bearish">
            {error}
          </div>
        )}

        {!loading && !error && (
          <>
            <table className="w-full">
              <thead>
                <tr className="border-b border-white/10">
                  <th className="text-left p-4 text-xs text-white/40 uppercase tracking-wider">Date</th>
                  <th className="text-left p-4 text-xs text-white/40 uppercase tracking-wider">Pair</th>
                  <th className="text-left p-4 text-xs text-white/40 uppercase tracking-wider">Direction</th>
                  <th className="text-left p-4 text-xs text-white/40 uppercase tracking-wider">Setup</th>
                  <th className="text-left p-4 text-xs text-white/40 uppercase tracking-wider">Entry</th>
                  <th className="text-left p-4 text-xs text-white/40 uppercase tracking-wider">Result</th>
                  <th className="text-right p-4 text-xs text-white/40 uppercase tracking-wider">P/L</th>
                  <th className="text-right p-4 text-xs text-white/40 uppercase tracking-wider">R</th>
                </tr>
              </thead>
              <tbody>
                {filteredTrades.map((trade) => (
                  <TradeRow key={trade.id} trade={trade as Trade} />
                ))}
              </tbody>
            </table>

            {filteredTrades.length === 0 && !loading && (
              <div className="p-8 text-center text-white/40">
                No trades found matching your filters.
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

function StatCard({ label, value, color = "text-white" }: { label: string; value: string | number; color?: string }) {
  return (
    <div className="glass rounded-xl p-4">
      <div className="text-xs text-white/40 uppercase tracking-wider mb-1">{label}</div>
      <div className={`text-2xl font-bold ${color}`}>{value}</div>
    </div>
  );
}

function TradeRow({ trade }: { trade: Trade }) {
  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  return (
    <tr className="border-b border-white/5 hover:bg-white/5 transition-colors">
      <td className="p-4 text-sm text-white/70">{formatDate(trade.entryTime)}</td>
      <td className="p-4">
        <span className="font-medium text-white">{trade.pair}</span>
      </td>
      <td className="p-4">
        <span
          className={`px-2 py-1 rounded text-xs font-medium ${
            trade.direction === "long"
              ? "bg-trading-bullish/20 text-trading-bullish"
              : "bg-trading-bearish/20 text-trading-bearish"
          }`}
        >
          {trade.direction.toUpperCase()}
        </span>
      </td>
      <td className="p-4 text-sm text-white/70">{SETUP_LABELS[trade.setupType]}</td>
      <td className="p-4 text-sm text-white font-mono">{trade.entryPrice}</td>
      <td className="p-4">
        <span
          className={`px-2 py-1 rounded text-xs font-bold ${
            trade.result === "win"
              ? "bg-trading-bullish/20 text-trading-bullish"
              : trade.result === "loss"
              ? "bg-trading-bearish/20 text-trading-bearish"
              : "bg-yellow-500/20 text-yellow-400"
          }`}
        >
          {trade.result?.toUpperCase()}
        </span>
      </td>
      <td className="p-4 text-right">
        <span
          className={`font-mono font-medium ${
            (trade.pnlPips || 0) >= 0 ? "text-trading-bullish" : "text-trading-bearish"
          }`}
        >
          {(trade.pnlPips || 0) >= 0 ? "+" : ""}
          {trade.pnlPips} pips
        </span>
      </td>
      <td className="p-4 text-right">
        <span
          className={`font-mono font-bold ${
            (trade.rMultiple || 0) >= 0 ? "text-trading-bullish" : "text-trading-bearish"
          }`}
        >
          {(trade.rMultiple || 0) >= 0 ? "+" : ""}
          {trade.rMultiple?.toFixed(1)}R
        </span>
      </td>
    </tr>
  );
}
