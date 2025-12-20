"use client";

import { useState } from "react";
import { Card, CardHeader, CardContent } from "../ui/Card";
import { Button } from "../ui/Button";
import { Badge } from "../ui/Badge";

interface WatchlistItem {
  pair: string;
  bias: "bullish" | "bearish" | "neutral";
  htfBias: string;
  notes: string;
  alerts: number;
  lastUpdated: Date;
}

const mockWatchlist: WatchlistItem[] = [
  {
    pair: "GBP/USD",
    bias: "bearish",
    htfBias: "Weekly bearish, daily in discount",
    notes: "Wait for Asian high sweep, sell into London",
    alerts: 2,
    lastUpdated: new Date(Date.now() - 1000 * 60 * 30),
  },
  {
    pair: "EUR/USD",
    bias: "bullish",
    htfBias: "Monthly bullish, weekly OTE",
    notes: "Looking for NY session reversal",
    alerts: 1,
    lastUpdated: new Date(Date.now() - 1000 * 60 * 60),
  },
  {
    pair: "XAU/USD",
    bias: "neutral",
    htfBias: "Consolidation range 2000-2050",
    notes: "Wait for breakout direction",
    alerts: 0,
    lastUpdated: new Date(Date.now() - 1000 * 60 * 60 * 3),
  },
  {
    pair: "US30",
    bias: "bullish",
    htfBias: "Daily bullish, 4H pullback",
    notes: "Buy dip into 4H FVG",
    alerts: 1,
    lastUpdated: new Date(Date.now() - 1000 * 60 * 45),
  },
  {
    pair: "NAS100",
    bias: "bullish",
    htfBias: "Weekly bullish, strong momentum",
    notes: "Look for continuation after consolidation",
    alerts: 0,
    lastUpdated: new Date(Date.now() - 1000 * 60 * 60 * 2),
  },
  {
    pair: "USD/JPY",
    bias: "bearish",
    htfBias: "BOJ intervention zone",
    notes: "Be cautious, potential reversal",
    alerts: 3,
    lastUpdated: new Date(Date.now() - 1000 * 60 * 15),
  },
];

const biasColors = {
  bullish: "border-green-500/50 bg-green-500/10",
  bearish: "border-red-500/50 bg-red-500/10",
  neutral: "border-amber-500/50 bg-amber-500/10",
};

const biasTextColors = {
  bullish: "text-green-400",
  bearish: "text-red-400",
  neutral: "text-amber-400",
};

const biasIcons = {
  bullish: (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
    </svg>
  ),
  bearish: (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" />
    </svg>
  ),
  neutral: (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 12H4" />
    </svg>
  ),
};

export function Watchlist() {
  const [watchlist] = useState<WatchlistItem[]>(mockWatchlist);
  const [selectedPair, setSelectedPair] = useState<string | null>(null);

  return (
    <div className="space-y-4 mt-4">
      {/* Header Actions */}
      <div className="flex justify-between items-center">
        <div className="flex gap-2">
          <Button variant={selectedPair === null ? "primary" : "ghost"} size="sm" onClick={() => setSelectedPair(null)}>
            All ({watchlist.length})
          </Button>
          <Button variant="ghost" size="sm">
            Bullish ({watchlist.filter((w) => w.bias === "bullish").length})
          </Button>
          <Button variant="ghost" size="sm">
            Bearish ({watchlist.filter((w) => w.bias === "bearish").length})
          </Button>
        </div>
        <Button variant="primary" size="sm">
          <svg className="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          Add Pair
        </Button>
      </div>

      {/* Watchlist Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {watchlist.map((item) => (
          <Card
            key={item.pair}
            className={`cursor-pointer transition-all hover:scale-[1.02] ${
              selectedPair === item.pair ? "ring-2 ring-vulcan-accent" : ""
            } ${biasColors[item.bias]}`}
            onClick={() => setSelectedPair(item.pair === selectedPair ? null : item.pair)}
          >
            <CardContent className="p-4">
              {/* Header */}
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <div className={biasTextColors[item.bias]}>
                    {biasIcons[item.bias]}
                  </div>
                  <span className="font-mono font-bold text-lg text-white">{item.pair}</span>
                </div>
                {item.alerts > 0 && (
                  <Badge variant="warning" size="sm">
                    {item.alerts} alert{item.alerts > 1 ? "s" : ""}
                  </Badge>
                )}
              </div>

              {/* Bias */}
              <div className="mb-3">
                <Badge
                  variant={item.bias === "bullish" ? "success" : item.bias === "bearish" ? "error" : "warning"}
                >
                  {item.bias.toUpperCase()}
                </Badge>
              </div>

              {/* HTF Analysis */}
              <div className="mb-2">
                <p className="text-xs text-white/40 uppercase tracking-wider mb-1">HTF Analysis</p>
                <p className="text-sm text-white/70">{item.htfBias}</p>
              </div>

              {/* Notes */}
              <div>
                <p className="text-xs text-white/40 uppercase tracking-wider mb-1">Notes</p>
                <p className="text-sm text-white/50">{item.notes}</p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Price Alerts Section */}
      <Card>
        <CardHeader
          title="Price Alerts"
          subtitle="Active notifications"
          action={
            <Button variant="outline" size="sm">
              <svg className="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
              </svg>
              Manage Alerts
            </Button>
          }
        />
        <CardContent>
          <div className="space-y-2">
            {[
              { pair: "GBP/USD", condition: "Price crosses above", level: "1.2700", active: true },
              { pair: "GBP/USD", condition: "Price crosses below", level: "1.2600", active: true },
              { pair: "EUR/USD", condition: "Price reaches", level: "1.0900", active: true },
              { pair: "USD/JPY", condition: "Price crosses above", level: "155.00", active: true },
              { pair: "USD/JPY", condition: "Price crosses below", level: "152.00", active: true },
              { pair: "USD/JPY", condition: "Price reaches", level: "150.00", active: true },
              { pair: "US30", condition: "Price crosses above", level: "40000", active: true },
            ].map((alert, i) => (
              <div
                key={i}
                className="flex items-center justify-between py-2 px-3 rounded-lg bg-white/5 hover:bg-white/10 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <span className="font-mono text-sm text-white">{alert.pair}</span>
                  <span className="text-white/50 text-sm">{alert.condition}</span>
                  <span className="font-mono text-vulcan-accent">{alert.level}</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className={`w-2 h-2 rounded-full ${alert.active ? "bg-green-500" : "bg-white/30"}`} />
                  <button className="text-white/30 hover:text-red-400 transition-colors">
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
