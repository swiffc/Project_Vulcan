/**
 * Pair Selector Component
 * TradingView-style pair selector with search and categories
 */

"use client";

import { useState, useRef, useEffect } from "react";
import { TRADING_PAIRS, TYPICAL_ADR } from "@/lib/trading/constants";
import type { TradingPair } from "@/lib/trading/types";

interface PairSelectorProps {
  selectedPair: string;
  onPairChange: (pair: string) => void;
  isOpen: boolean;
  onToggle: () => void;
}

export function PairSelector({
  selectedPair,
  onPairChange,
  isOpen,
  onToggle,
}: PairSelectorProps) {
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState<"all" | "major" | "minor">("all");
  const dropdownRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Close on outside click
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        if (isOpen) onToggle();
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [isOpen, onToggle]);

  // Focus input when opened
  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  const filteredPairs = TRADING_PAIRS.filter((pair) => {
    const matchesSearch =
      pair.symbol.toLowerCase().includes(search.toLowerCase()) ||
      pair.displayName.toLowerCase().includes(search.toLowerCase());
    const matchesCategory = category === "all" || pair.category === category;
    return matchesSearch && matchesCategory;
  });

  const currentPair = TRADING_PAIRS.find((p) => p.symbol === selectedPair);

  return (
    <div className="relative" ref={dropdownRef}>
      {/* Selected Pair Display */}
      <button
        onClick={onToggle}
        className="flex items-center gap-3 px-4 py-2 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 transition-all"
      >
        <div className="flex items-center gap-2">
          <span className="text-lg font-bold text-white">{selectedPair}</span>
          {currentPair && (
            <span className="text-xs text-white/40">ADR: {currentPair.typicalADR}</span>
          )}
        </div>
        <svg
          className={`w-4 h-4 text-white/50 transition-transform ${isOpen ? "rotate-180" : ""}`}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* Dropdown */}
      {isOpen && (
        <div className="absolute top-full left-0 mt-2 w-80 glass rounded-xl border border-white/10 shadow-2xl overflow-hidden z-50">
          {/* Search Input */}
          <div className="p-3 border-b border-white/10">
            <div className="relative">
              <svg
                className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/40"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                />
              </svg>
              <input
                ref={inputRef}
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search pairs..."
                className="w-full pl-10 pr-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white placeholder-white/30 focus:outline-none focus:border-vulcan-accent"
              />
            </div>
          </div>

          {/* Category Tabs */}
          <div className="flex px-3 py-2 gap-1 border-b border-white/10">
            {(["all", "major", "minor"] as const).map((cat) => (
              <button
                key={cat}
                onClick={() => setCategory(cat)}
                className={`px-3 py-1 text-xs font-medium rounded-lg transition-all ${
                  category === cat
                    ? "bg-vulcan-accent text-white"
                    : "text-white/50 hover:text-white hover:bg-white/5"
                }`}
              >
                {cat.charAt(0).toUpperCase() + cat.slice(1)}
              </button>
            ))}
          </div>

          {/* Pairs List */}
          <div className="max-h-64 overflow-y-auto">
            {filteredPairs.length === 0 ? (
              <div className="p-4 text-center text-white/40 text-sm">No pairs found</div>
            ) : (
              filteredPairs.map((pair) => (
                <PairRow
                  key={pair.symbol}
                  pair={pair}
                  isSelected={pair.symbol === selectedPair}
                  onClick={() => {
                    onPairChange(pair.symbol);
                    onToggle();
                    setSearch("");
                  }}
                />
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}

function PairRow({
  pair,
  isSelected,
  onClick,
}: {
  pair: TradingPair;
  isSelected: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className={`w-full flex items-center justify-between px-4 py-2.5 hover:bg-white/5 transition-all ${
        isSelected ? "bg-vulcan-accent/20" : ""
      }`}
    >
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-white/5 flex items-center justify-center">
          <span className="text-xs font-bold text-white/60">
            {pair.symbol.split("/")[0].slice(0, 2)}
          </span>
        </div>
        <div className="text-left">
          <div className="font-medium text-white">{pair.symbol}</div>
          <div className="text-xs text-white/40">{pair.displayName}</div>
        </div>
      </div>
      <div className="text-right">
        <div className="text-xs text-white/50">ADR</div>
        <div className="text-sm font-medium text-white">{pair.typicalADR}</div>
      </div>
    </button>
  );
}
