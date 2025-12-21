"use client";

import { useState } from "react";
import { Card, CardHeader, CardContent } from "../ui/Card";
import { Button } from "../ui/Button";
import { Badge } from "../ui/Badge";
import { TradingViewChart } from "./TradingViewChart";

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

export function MarketAnalysis() {
  const [selectedPair, setSelectedPair] = useState<PairAnalysis>(pairAnalysis[0]);
  const [selectedInterval, setSelectedInterval] = useState("1H");

  return (
    <div className="space-y-4 mt-4">
      {/* TradingView Chart - Now Real! */}
      <Card>
        <CardHeader
          title={`${selectedPair.pair} Chart`}
          subtitle="TradingView Live Data"
          action={
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
          }
        />
        <CardContent className="h-[450px] p-0">
          <TradingViewChart
            symbol={selectedPair.symbol}
            interval={intervals[selectedInterval]}
            theme="dark"
            autosize={true}
          />
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
