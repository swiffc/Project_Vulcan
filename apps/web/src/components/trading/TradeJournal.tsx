"use client";

import { useState } from "react";
import { Card, CardHeader, CardContent } from "../ui/Card";
import { Button } from "../ui/Button";
import { Badge } from "../ui/Badge";
import { TableHeader, TableBody, TableRow, TableHead, TableCell } from "../ui/Table";
import { formatDistanceToNow } from "date-fns";

interface Trade {
  id: string;
  pair: string;
  direction: "long" | "short";
  entry: number;
  exit: number | null;
  stopLoss: number;
  takeProfit: number;
  rMultiple: number | null;
  status: "open" | "win" | "loss" | "breakeven";
  setup: string;
  notes: string;
  timestamp: Date;
  screenshot?: string;
}

const mockTrades: Trade[] = [
  {
    id: "1",
    pair: "GBP/USD",
    direction: "short",
    entry: 1.2650,
    exit: 1.2580,
    stopLoss: 1.2690,
    takeProfit: 1.2550,
    rMultiple: 1.75,
    status: "win",
    setup: "Q2 Manipulation",
    notes: "Asian high swept, sold into London killzone",
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2),
  },
  {
    id: "2",
    pair: "EUR/USD",
    direction: "long",
    entry: 1.0875,
    exit: 1.0840,
    stopLoss: 1.0840,
    takeProfit: 1.0950,
    rMultiple: -1,
    status: "loss",
    setup: "OTE Retracement",
    notes: "Entered too early, should have waited for displacement",
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 24),
  },
  {
    id: "3",
    pair: "XAU/USD",
    direction: "long",
    entry: 2015.50,
    exit: null,
    stopLoss: 2008.00,
    takeProfit: 2035.00,
    rMultiple: null,
    status: "open",
    setup: "FVG Fill",
    notes: "4H FVG filled, looking for continuation",
    timestamp: new Date(Date.now() - 1000 * 60 * 30),
  },
];

export function TradeJournal() {
  const [showForm, setShowForm] = useState(false);
  const [trades] = useState<Trade[]>(mockTrades);

  return (
    <div className="space-y-4 mt-4">
      {/* Entry Form */}
      {showForm && (
        <Card>
          <CardHeader
            title="Log New Trade"
            action={
              <Button variant="ghost" size="sm" onClick={() => setShowForm(false)}>
                Cancel
              </Button>
            }
          />
          <CardContent>
            <form className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <label className="block text-xs text-white/50 mb-1">Pair</label>
                <select className="w-full px-3 py-2 rounded-lg bg-white/10 border border-white/10 text-white focus:outline-none focus:border-vulcan-accent">
                  <option value="GBP/USD">GBP/USD</option>
                  <option value="EUR/USD">EUR/USD</option>
                  <option value="XAU/USD">XAU/USD</option>
                  <option value="US30">US30</option>
                  <option value="NAS100">NAS100</option>
                </select>
              </div>
              <div>
                <label className="block text-xs text-white/50 mb-1">Direction</label>
                <select className="w-full px-3 py-2 rounded-lg bg-white/10 border border-white/10 text-white focus:outline-none focus:border-vulcan-accent">
                  <option value="long">Long</option>
                  <option value="short">Short</option>
                </select>
              </div>
              <div>
                <label className="block text-xs text-white/50 mb-1">Entry Price</label>
                <input
                  type="number"
                  step="0.00001"
                  className="w-full px-3 py-2 rounded-lg bg-white/10 border border-white/10 text-white focus:outline-none focus:border-vulcan-accent"
                  placeholder="1.26500"
                />
              </div>
              <div>
                <label className="block text-xs text-white/50 mb-1">Stop Loss</label>
                <input
                  type="number"
                  step="0.00001"
                  className="w-full px-3 py-2 rounded-lg bg-white/10 border border-white/10 text-white focus:outline-none focus:border-vulcan-accent"
                  placeholder="1.26900"
                />
              </div>
              <div>
                <label className="block text-xs text-white/50 mb-1">Take Profit</label>
                <input
                  type="number"
                  step="0.00001"
                  className="w-full px-3 py-2 rounded-lg bg-white/10 border border-white/10 text-white focus:outline-none focus:border-vulcan-accent"
                  placeholder="1.25500"
                />
              </div>
              <div>
                <label className="block text-xs text-white/50 mb-1">Setup Type</label>
                <select className="w-full px-3 py-2 rounded-lg bg-white/10 border border-white/10 text-white focus:outline-none focus:border-vulcan-accent">
                  <option value="q2">Q2 Manipulation</option>
                  <option value="ote">OTE Retracement</option>
                  <option value="fvg">FVG Fill</option>
                  <option value="breaker">Breaker Block</option>
                  <option value="liquidity">Liquidity Sweep</option>
                </select>
              </div>
              <div className="col-span-2">
                <label className="block text-xs text-white/50 mb-1">Notes</label>
                <input
                  type="text"
                  className="w-full px-3 py-2 rounded-lg bg-white/10 border border-white/10 text-white focus:outline-none focus:border-vulcan-accent"
                  placeholder="Trade notes..."
                />
              </div>
              <div className="col-span-2 md:col-span-4 flex justify-end gap-2">
                <Button variant="secondary" type="button" onClick={() => setShowForm(false)}>
                  Cancel
                </Button>
                <Button variant="primary" type="submit">
                  Log Trade
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {/* Trades Table */}
      <Card>
        <CardHeader
          title="Trade History"
          subtitle={`${trades.length} trades logged`}
          action={
            !showForm && (
              <Button variant="primary" size="sm" onClick={() => setShowForm(true)}>
                <svg className="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                New Trade
              </Button>
            )
          }
        />
        <CardContent className="-mx-4 -mb-4">
          <table className="w-full">
            <TableHeader>
              <TableRow>
                <TableHead>Pair</TableHead>
                <TableHead>Direction</TableHead>
                <TableHead>Entry</TableHead>
                <TableHead>SL / TP</TableHead>
                <TableHead>Setup</TableHead>
                <TableHead>R-Multiple</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Time</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {trades.map((trade) => (
                <TableRow key={trade.id} className="cursor-pointer">
                  <TableCell className="font-mono font-medium">{trade.pair}</TableCell>
                  <TableCell>
                    <Badge variant={trade.direction === "long" ? "success" : "error"} size="sm">
                      {trade.direction.toUpperCase()}
                    </Badge>
                  </TableCell>
                  <TableCell className="font-mono">{trade.entry.toFixed(trade.entry > 100 ? 2 : 5)}</TableCell>
                  <TableCell className="font-mono text-xs">
                    <span className="text-red-400">{trade.stopLoss.toFixed(trade.stopLoss > 100 ? 2 : 5)}</span>
                    {" / "}
                    <span className="text-green-400">{trade.takeProfit.toFixed(trade.takeProfit > 100 ? 2 : 5)}</span>
                  </TableCell>
                  <TableCell className="text-white/70">{trade.setup}</TableCell>
                  <TableCell>
                    {trade.rMultiple !== null ? (
                      <span className={trade.rMultiple > 0 ? "text-green-400" : "text-red-400"}>
                        {trade.rMultiple > 0 ? "+" : ""}{trade.rMultiple.toFixed(2)}R
                      </span>
                    ) : (
                      <span className="text-white/30">-</span>
                    )}
                  </TableCell>
                  <TableCell>
                    <Badge
                      variant={
                        trade.status === "win"
                          ? "success"
                          : trade.status === "loss"
                          ? "error"
                          : trade.status === "open"
                          ? "info"
                          : "warning"
                      }
                      size="sm"
                    >
                      {trade.status.toUpperCase()}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-white/40 text-xs">
                    {formatDistanceToNow(trade.timestamp, { addSuffix: true })}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
