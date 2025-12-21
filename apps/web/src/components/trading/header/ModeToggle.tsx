/**
 * Mode Toggle Component
 * Toggle between Basic and Advanced trading modes
 */

"use client";

interface ModeToggleProps {
  isAdvanced: boolean;
  onToggle: () => void;
}

export function ModeToggle({ isAdvanced, onToggle }: ModeToggleProps) {
  return (
    <button
      onClick={onToggle}
      className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 transition-all"
      title={isAdvanced ? "Switch to Basic Mode" : "Switch to Advanced Mode"}
    >
      {/* Toggle Track */}
      <div className="relative w-10 h-5 rounded-full bg-white/10 transition-colors">
        <div
          className={`absolute top-0.5 w-4 h-4 rounded-full transition-all duration-200 ${
            isAdvanced
              ? "left-5 bg-vulcan-accent shadow-lg shadow-vulcan-accent/30"
              : "left-0.5 bg-white/60"
          }`}
        />
      </div>

      {/* Label */}
      <span className={`text-xs font-medium ${isAdvanced ? "text-vulcan-accent" : "text-white/50"}`}>
        {isAdvanced ? "Advanced" : "Basic"}
      </span>
    </button>
  );
}
