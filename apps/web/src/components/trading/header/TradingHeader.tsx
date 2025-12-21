/**
 * Trading Header Component
 * TradingView-inspired header with session clock, pair selector, and mode toggle
 */

"use client";

import { useState } from "react";
import { EnhancedSessionClock } from "./EnhancedSessionClock";
import { PairSelector } from "./PairSelector";
import { ModeToggle } from "./ModeToggle";
import type { SessionName } from "@/lib/trading/types";
import { SESSIONS, SESSION_LABELS } from "@/lib/trading/constants";

interface TradingHeaderProps {
  selectedPair: string;
  onPairChange: (pair: string) => void;
  isAdvancedMode: boolean;
  onModeToggle: () => void;
}

export function TradingHeader({
  selectedPair,
  onPairChange,
  isAdvancedMode,
  onModeToggle,
}: TradingHeaderProps) {
  const [showPairSearch, setShowPairSearch] = useState(false);

  return (
    <header className="trading-header glass-dark sticky top-0 z-40 border-b border-white/10">
      <div className="flex items-center justify-between h-14 px-4">
        {/* Left: Pair Selector */}
        <div className="flex items-center gap-4">
          <PairSelector
            selectedPair={selectedPair}
            onPairChange={onPairChange}
            isOpen={showPairSearch}
            onToggle={() => setShowPairSearch(!showPairSearch)}
          />

          {/* Quick Pair Switcher */}
          <div className="hidden md:flex items-center gap-1">
            {["EUR/USD", "GBP/USD", "USD/JPY"].map((pair) => (
              <button
                key={pair}
                onClick={() => onPairChange(pair)}
                className={`px-2 py-1 text-xs font-medium rounded transition-all ${
                  selectedPair === pair
                    ? "bg-trading-bullish/20 text-trading-bullish border border-trading-bullish/30"
                    : "text-white/50 hover:text-white hover:bg-white/5"
                }`}
              >
                {pair.replace("/", "")}
              </button>
            ))}
          </div>
        </div>

        {/* Center: Session Clock */}
        <div className="flex-1 flex justify-center">
          <EnhancedSessionClock />
        </div>

        {/* Right: Controls */}
        <div className="flex items-center gap-3">
          {/* Kill Zone Alert */}
          <KillZoneIndicator />

          {/* Mode Toggle */}
          <ModeToggle isAdvanced={isAdvancedMode} onToggle={onModeToggle} />

          {/* Quick Actions */}
          <div className="hidden lg:flex items-center gap-2">
            <button className="p-2 rounded-lg hover:bg-white/5 text-white/50 hover:text-white transition-colors">
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}

function KillZoneIndicator() {
  const [isKillZone, setIsKillZone] = useState(false);
  const [currentSession, setCurrentSession] = useState<SessionName | null>(null);

  // Check kill zone status on client
  if (typeof window !== "undefined") {
    const now = new Date();
    const estHour = parseInt(
      now.toLocaleTimeString("en-US", {
        timeZone: "America/New_York",
        hour: "2-digit",
        hour12: false,
      })
    );

    // London Kill Zone: 02:00 - 05:00 EST
    // NY Kill Zone: 08:00 - 11:00 EST
    const inLondonKZ = estHour >= 2 && estHour < 5;
    const inNYKZ = estHour >= 8 && estHour < 11;

    if ((inLondonKZ || inNYKZ) !== isKillZone) {
      setIsKillZone(inLondonKZ || inNYKZ);
      setCurrentSession(inLondonKZ ? "london" : inNYKZ ? "newyork" : null);
    }
  }

  if (!isKillZone) return null;

  return (
    <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-trading-bearish/20 border border-trading-bearish/30">
      <div className="w-2 h-2 rounded-full bg-trading-bearish animate-pulse" />
      <span className="text-xs font-bold text-trading-bearish uppercase tracking-wide">
        {currentSession === "london" ? "LDN" : "NY"} Kill Zone
      </span>
    </div>
  );
}
