/**
 * Pre-Trade Checklist Component
 * BTMM-focused checklist to validate trade setups
 */

"use client";

import { useState } from "react";
import { DEFAULT_CHECKLIST } from "@/lib/trading/constants";
import type { ChecklistItem } from "@/lib/trading/types";

export function PreTradeChecklist() {
  const [checklist, setChecklist] = useState<ChecklistItem[]>(
    DEFAULT_CHECKLIST.map((item) => ({ ...item }))
  );

  const toggleItem = (id: string) => {
    setChecklist((prev) =>
      prev.map((item) =>
        item.id === id ? { ...item, checked: !item.checked } : item
      )
    );
  };

  const resetChecklist = () => {
    setChecklist(DEFAULT_CHECKLIST.map((item) => ({ ...item, checked: false })));
  };

  const requiredItems = checklist.filter((item) => item.required);
  const optionalItems = checklist.filter((item) => !item.required);
  const requiredChecked = requiredItems.filter((item) => item.checked).length;
  const totalChecked = checklist.filter((item) => item.checked).length;

  const allRequiredMet = requiredChecked === requiredItems.length;
  const progressPercent = (requiredChecked / requiredItems.length) * 100;

  return (
    <div className="p-3 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium text-white">Pre-Trade Checklist</h3>
        <button
          onClick={resetChecklist}
          className="text-xs text-white/40 hover:text-white transition-colors"
        >
          Reset
        </button>
      </div>

      {/* Progress Bar */}
      <div>
        <div className="flex justify-between text-xs mb-1">
          <span className={allRequiredMet ? "text-trading-bullish" : "text-white/50"}>
            Required: {requiredChecked}/{requiredItems.length}
          </span>
          <span className="text-white/30">
            Total: {totalChecked}/{checklist.length}
          </span>
        </div>
        <div className="h-2 bg-white/10 rounded-full overflow-hidden">
          <div
            className={`h-full transition-all duration-300 ${
              allRequiredMet ? "bg-trading-bullish" : "bg-vulcan-accent"
            }`}
            style={{ width: `${progressPercent}%` }}
          />
        </div>
      </div>

      {/* Ready Status */}
      {allRequiredMet && (
        <div className="p-3 rounded-lg bg-trading-bullish/20 border border-trading-bullish/30 flex items-center gap-2">
          <svg className="w-5 h-5 text-trading-bullish" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span className="text-sm font-medium text-trading-bullish">Ready to Trade</span>
        </div>
      )}

      {/* Required Items */}
      <div>
        <div className="text-xs text-white/40 uppercase tracking-wider mb-2">Required</div>
        <div className="space-y-1">
          {requiredItems.map((item) => (
            <ChecklistRow
              key={item.id}
              item={item}
              onToggle={() => toggleItem(item.id)}
            />
          ))}
        </div>
      </div>

      {/* Optional Items */}
      <div>
        <div className="text-xs text-white/40 uppercase tracking-wider mb-2">Optional</div>
        <div className="space-y-1">
          {optionalItems.map((item) => (
            <ChecklistRow
              key={item.id}
              item={item}
              onToggle={() => toggleItem(item.id)}
            />
          ))}
        </div>
      </div>

      {/* Quick Reference */}
      <div className="p-3 rounded-lg bg-white/5 border border-white/10">
        <div className="text-xs text-white/40 mb-2">Quick Reference</div>
        <div className="text-xs text-white/60 space-y-1">
          <div>• Session: London (02:00-05:00) or NY (08:00-11:00)</div>
          <div>• Cycle Day confirms market phase</div>
          <div>• Level I = highest probability reversal</div>
          <div>• M/W pattern must be clear on chart</div>
        </div>
      </div>
    </div>
  );
}

function ChecklistRow({
  item,
  onToggle,
}: {
  item: ChecklistItem;
  onToggle: () => void;
}) {
  return (
    <button
      onClick={onToggle}
      className={`w-full flex items-start gap-3 p-2 rounded-lg transition-all ${
        item.checked
          ? "bg-trading-bullish/10 border border-trading-bullish/20"
          : "bg-white/5 border border-transparent hover:border-white/10"
      }`}
    >
      <div
        className={`w-5 h-5 rounded flex items-center justify-center flex-shrink-0 transition-all ${
          item.checked
            ? "bg-trading-bullish text-white"
            : "border border-white/30"
        }`}
      >
        {item.checked && (
          <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
          </svg>
        )}
      </div>
      <div className="text-left flex-1">
        <div className={`text-sm ${item.checked ? "text-trading-bullish" : "text-white/70"}`}>
          {item.label}
        </div>
        {item.description && (
          <div className="text-xs text-white/40 mt-0.5">{item.description}</div>
        )}
      </div>
    </button>
  );
}
