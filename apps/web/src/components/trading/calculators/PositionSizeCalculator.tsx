/**
 * Position Size Calculator
 * Calculates position size based on account balance, risk %, and stop loss
 */

"use client";

import { useState, useMemo } from "react";
import { TRADING_PAIRS, TYPICAL_ADR } from "@/lib/trading/constants";

interface PositionSizeCalculatorProps {
  selectedPair: string;
  riskPercent: number;
}

export function PositionSizeCalculator({
  selectedPair,
  riskPercent,
}: PositionSizeCalculatorProps) {
  const [accountBalance, setAccountBalance] = useState("10000");
  const [stopLossPips, setStopLossPips] = useState("25");
  const [customRisk, setCustomRisk] = useState(riskPercent.toString());

  const currentPair = TRADING_PAIRS.find((p) => p.symbol === selectedPair);
  const pipValue = currentPair?.pipValue || 0.0001;
  const isJPY = selectedPair.includes("JPY");

  const calculations = useMemo(() => {
    const balance = parseFloat(accountBalance) || 0;
    const slPips = parseFloat(stopLossPips) || 0;
    const risk = parseFloat(customRisk) || 0;

    if (balance <= 0 || slPips <= 0 || risk <= 0) {
      return {
        riskAmount: 0,
        positionSize: 0,
        lots: 0,
        microLots: 0,
        pipValuePerLot: 0,
      };
    }

    // Risk amount in dollars
    const riskAmount = (balance * risk) / 100;

    // Pip value per standard lot (100,000 units)
    // For USD pairs: ~$10 per pip per lot
    // For JPY pairs: ~$9.20 per pip per lot (varies with USD/JPY rate)
    const pipValuePerLot = isJPY ? 9.2 : 10;

    // Position size in lots
    const lots = riskAmount / (slPips * pipValuePerLot);

    // Position size in units
    const positionSize = lots * 100000;

    // Micro lots (1000 units)
    const microLots = lots * 100;

    return {
      riskAmount,
      positionSize: Math.round(positionSize),
      lots: parseFloat(lots.toFixed(2)),
      microLots: parseFloat(microLots.toFixed(1)),
      pipValuePerLot,
    };
  }, [accountBalance, stopLossPips, customRisk, isJPY]);

  return (
    <div className="p-3 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium text-white">Position Size Calculator</h3>
        <span className="text-xs text-vulcan-accent">{selectedPair}</span>
      </div>

      {/* Account Balance */}
      <div>
        <label className="text-xs text-white/40 uppercase tracking-wider mb-1 block">
          Account Balance ($)
        </label>
        <input
          type="number"
          value={accountBalance}
          onChange={(e) => setAccountBalance(e.target.value)}
          className="trading-input"
          placeholder="10000"
        />
      </div>

      {/* Risk Percentage */}
      <div>
        <label className="text-xs text-white/40 uppercase tracking-wider mb-2 block">
          Risk Percentage
        </label>
        <div className="flex gap-1 mb-2">
          {["0.5", "1", "2", "3"].map((r) => (
            <button
              key={r}
              onClick={() => setCustomRisk(r)}
              className={`flex-1 py-1.5 rounded text-xs font-medium transition-all ${
                customRisk === r
                  ? "bg-vulcan-accent text-white"
                  : "bg-white/5 text-white/50 hover:bg-white/10"
              }`}
            >
              {r}%
            </button>
          ))}
        </div>
        <input
          type="number"
          value={customRisk}
          onChange={(e) => setCustomRisk(e.target.value)}
          className="trading-input"
          placeholder="1.0"
          step="0.1"
        />
      </div>

      {/* Stop Loss Pips */}
      <div>
        <label className="text-xs text-white/40 uppercase tracking-wider mb-1 block">
          Stop Loss (Pips)
        </label>
        <input
          type="number"
          value={stopLossPips}
          onChange={(e) => setStopLossPips(e.target.value)}
          className="trading-input"
          placeholder="25"
        />
        <div className="flex justify-between mt-1 text-xs text-white/30">
          <span>ADR: {currentPair?.typicalADR || "N/A"} pips</span>
          <span>25% ADR = ~{Math.round((currentPair?.typicalADR || 80) * 0.25)} pips</span>
        </div>
      </div>

      {/* Results */}
      <div className="space-y-2">
        <div className="p-3 rounded-lg bg-white/5 border border-white/10">
          <div className="flex justify-between items-center mb-2">
            <span className="text-xs text-white/40">Risk Amount</span>
            <span className="text-lg font-bold text-trading-bearish">
              ${calculations.riskAmount.toFixed(2)}
            </span>
          </div>
          <div className="h-px bg-white/10 my-2" />
          <div className="grid grid-cols-2 gap-3 text-sm">
            <div>
              <div className="text-white/40 text-xs">Standard Lots</div>
              <div className="font-bold text-white">{calculations.lots}</div>
            </div>
            <div>
              <div className="text-white/40 text-xs">Micro Lots</div>
              <div className="font-bold text-white">{calculations.microLots}</div>
            </div>
          </div>
        </div>

        <div className="p-3 rounded-lg bg-vulcan-accent/10 border border-vulcan-accent/30">
          <div className="flex justify-between items-center">
            <span className="text-xs text-vulcan-accent">Position Size</span>
            <span className="text-lg font-bold text-vulcan-accent">
              {calculations.positionSize.toLocaleString()} units
            </span>
          </div>
        </div>
      </div>

      {/* Quick Reference */}
      <div className="text-xs text-white/30 space-y-1">
        <div className="flex justify-between">
          <span>1 Standard Lot</span>
          <span>100,000 units</span>
        </div>
        <div className="flex justify-between">
          <span>1 Mini Lot</span>
          <span>10,000 units</span>
        </div>
        <div className="flex justify-between">
          <span>1 Micro Lot</span>
          <span>1,000 units</span>
        </div>
      </div>
    </div>
  );
}
