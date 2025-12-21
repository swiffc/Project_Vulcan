"use client";

import { useState } from "react";
import { Card, CardHeader, CardContent } from "../ui/Card";
import { Button } from "../ui/Button";
import { Badge } from "../ui/Badge";
import { TradingViewChart } from "./TradingViewChart";
import { TradingViewEmbed } from "./TradingViewEmbed";

interface PairAnalysis {
  pair: string;
  symbol: string; // TradingView symbol format
  bias: "bullish" | "bearish" | "neutral";
  setup: string;
  timeframe: string;
  confidence: number;
  notes: string;
}

const pairAnalysis: PairAnalysis[] = [
  {
    pair: "GBP/USD",
    symbol: "FX:GBPUSD",
    bias: "bearish",
    setup: "Q2 Manipulation",
    timeframe: "4H",
    confidence: 85,
    notes: "HTF bearish, waiting for Asian high sweep",
  },
  {
    pair: "EUR/USD",
    symbol: "FX:EURUSD",
    bias: "bullish",
    setup: "OTE in Discount",
    timeframe: "1H",
    confidence: 72,
    notes: "Daily FVG filled, looking for London reversal",
  },
  {
    pair: "XAU/USD",
    symbol: "OANDA:XAUUSD",
    bias: "neutral",
    setup: "Consolidation",
    timeframe: "4H",
    confidence: 45,
    notes: "Range-bound, wait for breakout",
  },
  {
    pair: "USD/JPY",
    symbol: "FX:USDJPY",
    bias: "bullish",
    setup: "Breaker Block",
    timeframe: "1H",
    confidence: 78,
    notes: "Clean bullish structure, targeting previous highs",
  },
  {
    pair: "BTC/USD",
    symbol: "BITSTAMP:BTCUSD",
    bias: "bullish",
    setup: "Weekly FVG",
    timeframe: "Daily",
    confidence: 68,
    notes: "Holding weekly support, momentum building",
  },
];

// Interval mapping
const intervals: { [key: string]: string } = {
  "1M": "1",
  "5M": "5",
  "15M": "15",
  "1H": "60",
  "4H": "240",
  "Daily": "D",
  "Weekly": "W",
};

const biasColors = {
  bullish: "text-green-400",
  bearish: "text-red-400",
  neutral: "text-amber-400",
};

type ChartMode = "widget" | "account";

export function MarketAnalysis() {
  const [selectedPair, setSelectedPair] = useState<PairAnalysis>(pairAnalysis[0]);
  const [selectedInterval, setSelectedInterval] = useState("1H");
  const [chartMode, setChartMode] = useState<ChartMode>("widget");

  return (
    <div className="space-y-4 mt-4">
      {/* TradingView Chart */}
      <Card>
        <CardHeader
          title={`${selectedPair.pair} Chart`}
          subtitle={chartMode === "account" ? "Your TradingView Account" : "TradingView Public Widget"}
          action={
            <div className="flex items-center gap-3">
              {/* Mode Toggle */}
              <div className="flex rounded-lg bg-white/5 p-0.5">
                <button
                  onClick={() => setChartMode("widget")}
                  className={`px-3 py-1 text-xs rounded-md transition-all ${
                    chartMode === "widget"
                      ? "bg-indigo-500 text-white"
                      : "text-white/50 hover:text-white"
                  }`}
                >
                  Widget
                </button>
                <button
                  onClick={() => setChartMode("account")}
                  className={`px-3 py-1 text-xs rounded-md transition-all ${
                    chartMode === "account"
                      ? "bg-indigo-500 text-white"
                      : "text-white/50 hover:text-white"
                  }`}
                >
                  My Account
                </button>
              </div>

              <div className="h-6 w-px bg-white/10" />

              {/* Timeframe buttons - only for widget mode */}
              {chartMode === "widget" && (
                <>
                  <div className="flex gap-1">
                    {["15M", "1H", "4H", "Daily"].map((tf) => (
                      <Button
                        key={tf}
                        variant={selectedInterval === tf ? "primary" : "ghost"}
                        size="sm"
                        onClick={() => setSelectedInterval(tf)}
                      >
                        {tf}
                      </Button>
                    ))}
                  </div>
                  <div className="h-6 w-px bg-white/10" />
                </>
              )}

              <Button
                variant="secondary"
                size="sm"
                onClick={() => {
                  const tvInterval = intervals[selectedInterval];
                  const url = `https://www.tradingview.com/chart/?symbol=${selectedPair.symbol}&interval=${tvInterval}`;
                  window.open(url, '_blank', 'noopener,noreferrer');
                }}
                className="flex items-center gap-1.5"
              >
                <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
                  <polyline points="15 3 21 3 21 9" />
                  <line x1="10" y1="14" x2="21" y2="3" />
                </svg>
                Open in TradingView
              </Button>
            </div>
          }
        />
        <CardContent className="h-[500px] p-0">
          {chartMode === "widget" ? (
            <TradingViewChart
              symbol={selectedPair.symbol}
              interval={intervals[selectedInterval]}
              theme="dark"
              autosize={true}
            />
          ) : (
            <TradingViewEmbed
              symbol={selectedPair.symbol}
              interval={intervals[selectedInterval]}
            />
          )}
        </CardContent>
      </Card>

      {/* Pair Scanner */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <Card className="lg:col-span-2">
          <CardHeader
            title="Pair Scanner"
            subtitle="ICT/BTMM Setup Detection"
            action={
              <Button variant="primary" size="sm">
                <svg className="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                Scan All
              </Button>
            }
          />
          <CardContent>
            <div className="divide-y divide-white/5">
              {pairAnalysis.map((analysis) => (
                <div
                  key={analysis.pair}
                  className={`py-3 flex items-center justify-between hover:bg-white/5 -mx-4 px-4 cursor-pointer transition-colors ${
                    selectedPair.pair === analysis.pair ? "bg-indigo-500/20 border-l-2 border-indigo-400" : ""
                  }`}
                  onClick={() => setSelectedPair(analysis)}
                >
                  <div className="flex items-center gap-4">
                    <div className="w-16">
                      <span className="font-mono font-bold text-white">{analysis.pair.split("/")[0]}</span>
                      <span className="text-white/40">/{analysis.pair.split("/")[1]}</span>
                    </div>
                    <Badge variant={analysis.bias === "bullish" ? "success" : analysis.bias === "bearish" ? "error" : "warning"}>
                      {analysis.bias.toUpperCase()}
                    </Badge>
                    <span className="text-sm text-white/70">{analysis.setup}</span>
                  </div>
                  <div className="flex items-center gap-4">
                    <span className="text-xs text-white/40">{analysis.timeframe}</span>
                    <div className="flex items-center gap-2">
                      <div className="w-16 h-1.5 bg-white/10 rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full ${
                            analysis.confidence >= 70
                              ? "bg-green-500"
                              : analysis.confidence >= 50
                              ? "bg-amber-500"
                              : "bg-red-500"
                          }`}
                          style={{ width: `${analysis.confidence}%` }}
                        />
                      </div>
                      <span className="text-xs text-white/50">{analysis.confidence}%</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Setup Details */}
        <Card>
          <CardHeader title="Setup Details" subtitle={selectedPair.pair} />
          <CardContent>
            <div className="space-y-4">
              <div>
                <label className="text-xs text-white/40 uppercase tracking-wider">Bias</label>
                <p className={`font-medium ${biasColors[selectedPair.bias]}`}>
                  {selectedPair.bias.charAt(0).toUpperCase() + selectedPair.bias.slice(1)}
                </p>
              </div>
              <div>
                <label className="text-xs text-white/40 uppercase tracking-wider">Setup Type</label>
                <p className="text-white">{selectedPair.setup}</p>
              </div>
              <div>
                <label className="text-xs text-white/40 uppercase tracking-wider">Timeframe</label>
                <p className="text-white">{selectedPair.timeframe}</p>
              </div>
              <div>
                <label className="text-xs text-white/40 uppercase tracking-wider">Notes</label>
                <p className="text-white/70 text-sm">{selectedPair.notes}</p>
              </div>
              <div className="pt-4 space-y-2">
                <Button variant="primary" className="w-full">Log Trade Entry</Button>
                <Button variant="secondary" className="w-full">Add to Watchlist</Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
