"use client";

import { useState } from "react";
import { Card, CardHeader, CardContent } from "../ui/Card";
import { Button } from "../ui/Button";
import { Badge } from "../ui/Badge";

interface PairAnalysis {
  pair: string;
  bias: "bullish" | "bearish" | "neutral";
  setup: string;
  timeframe: string;
  confidence: number;
  notes: string;
}

const mockAnalysis: PairAnalysis[] = [
  {
    pair: "GBP/USD",
    bias: "bearish",
    setup: "Q2 Manipulation",
    timeframe: "4H",
    confidence: 85,
    notes: "HTF bearish, waiting for Asian high sweep",
  },
  {
    pair: "EUR/USD",
    bias: "bullish",
    setup: "OTE in Discount",
    timeframe: "1H",
    confidence: 72,
    notes: "Daily FVG filled, looking for London reversal",
  },
  {
    pair: "XAU/USD",
    bias: "neutral",
    setup: "Consolidation",
    timeframe: "4H",
    confidence: 45,
    notes: "Range-bound, wait for breakout",
  },
];

const biasColors = {
  bullish: "text-green-400",
  bearish: "text-red-400",
  neutral: "text-amber-400",
};

export function MarketAnalysis() {
  const [selectedPair, setSelectedPair] = useState<string | null>(null);

  return (
    <div className="space-y-4 mt-4">
      {/* TradingView Chart Embed */}
      <Card>
        <CardHeader
          title="Chart"
          subtitle="TradingView Integration"
          action={
            <div className="flex gap-2">
              <Button variant="ghost" size="sm">1H</Button>
              <Button variant="ghost" size="sm">4H</Button>
              <Button variant="primary" size="sm">Daily</Button>
            </div>
          }
        />
        <CardContent className="h-[400px] flex items-center justify-center bg-gradient-to-br from-white/5 to-transparent rounded-lg">
          <div className="text-center">
            <div className="w-16 h-16 mx-auto mb-4 rounded-xl bg-white/10 flex items-center justify-center">
              <svg className="w-8 h-8 text-white/50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
            </div>
            <p className="text-white/50 mb-2">TradingView Chart Widget</p>
            <p className="text-xs text-white/30">Connect your TradingView account to display live charts</p>
            <Button variant="outline" size="sm" className="mt-4">
              Connect TradingView
            </Button>
          </div>
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
              {mockAnalysis.map((analysis) => (
                <div
                  key={analysis.pair}
                  className={`py-3 flex items-center justify-between hover:bg-white/5 -mx-4 px-4 cursor-pointer transition-colors ${
                    selectedPair === analysis.pair ? "bg-white/10" : ""
                  }`}
                  onClick={() => setSelectedPair(analysis.pair)}
                >
                  <div className="flex items-center gap-4">
                    <div className="w-12">
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
          <CardHeader title="Setup Details" subtitle={selectedPair || "Select a pair"} />
          <CardContent>
            {selectedPair ? (
              <div className="space-y-4">
                {(() => {
                  const analysis = mockAnalysis.find((a) => a.pair === selectedPair);
                  if (!analysis) return null;
                  return (
                    <>
                      <div>
                        <label className="text-xs text-white/40 uppercase tracking-wider">Bias</label>
                        <p className={`font-medium ${biasColors[analysis.bias]}`}>
                          {analysis.bias.charAt(0).toUpperCase() + analysis.bias.slice(1)}
                        </p>
                      </div>
                      <div>
                        <label className="text-xs text-white/40 uppercase tracking-wider">Setup Type</label>
                        <p className="text-white">{analysis.setup}</p>
                      </div>
                      <div>
                        <label className="text-xs text-white/40 uppercase tracking-wider">Timeframe</label>
                        <p className="text-white">{analysis.timeframe}</p>
                      </div>
                      <div>
                        <label className="text-xs text-white/40 uppercase tracking-wider">Notes</label>
                        <p className="text-white/70 text-sm">{analysis.notes}</p>
                      </div>
                      <div className="pt-4 space-y-2">
                        <Button variant="primary" className="w-full">Log Trade Entry</Button>
                        <Button variant="outline" className="w-full">Add to Watchlist</Button>
                      </div>
                    </>
                  );
                })()}
              </div>
            ) : (
              <div className="text-center py-8 text-white/40">
                <svg className="w-12 h-12 mx-auto mb-2 opacity-50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
                <p>Click a pair to view details</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
