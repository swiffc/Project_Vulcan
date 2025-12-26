/**
 * Shared Color Constants
 * Centralizes all color definitions for consistency
 */

// Cycle Day Colors (BTMM Trading)
export const CYCLE_DAY_COLORS = {
  1: {
    bg: "bg-amber-500/20",
    text: "text-amber-400",
    border: "border-amber-500",
    hex: "#fbbf24",
  },
  2: {
    bg: "bg-orange-500/20",
    text: "text-orange-400",
    border: "border-orange-500",
    hex: "#f97316",
  },
  3: {
    bg: "bg-emerald-500/20",
    text: "text-emerald-400",
    border: "border-emerald-500",
    hex: "#22c55e",
  },
} as const;

// Trading Status Colors
export const TRADING_COLORS = {
  bullish: {
    bg: "bg-green-500/20",
    text: "text-green-400",
    border: "border-green-500",
    hex: "#3fb950",
  },
  bearish: {
    bg: "bg-red-500/20",
    text: "text-red-400",
    border: "border-red-500",
    hex: "#f85149",
  },
  neutral: {
    bg: "bg-gray-500/20",
    text: "text-gray-400",
    border: "border-gray-500",
    hex: "#6e7681",
  },
} as const;

// Session Colors
export const SESSION_COLORS = {
  asian: {
    bg: "bg-purple-500/20",
    text: "text-purple-400",
    hex: "#a371f7",
  },
  london: {
    bg: "bg-blue-500/20",
    text: "text-blue-400",
    hex: "#58a6ff",
  },
  newYork: {
    bg: "bg-green-500/20",
    text: "text-green-400",
    hex: "#3fb950",
  },
  gap: {
    bg: "bg-gray-500/20",
    text: "text-gray-400",
    hex: "#6e7681",
  },
} as const;

// Validation Status Colors
export const VALIDATION_COLORS = {
  passed: {
    bg: "bg-emerald-500/20",
    text: "text-emerald-400",
    border: "border-emerald-500",
    hex: "#10b981",
  },
  failed: {
    bg: "bg-red-500/20",
    text: "text-red-400",
    border: "border-red-500",
    hex: "#ef4444",
  },
  warning: {
    bg: "bg-amber-500/20",
    text: "text-amber-400",
    border: "border-amber-500",
    hex: "#f59e0b",
  },
  info: {
    bg: "bg-blue-500/20",
    text: "text-blue-400",
    border: "border-blue-500",
    hex: "#3b82f6",
  },
  critical: {
    bg: "bg-rose-500/20",
    text: "text-rose-400",
    border: "border-rose-500",
    hex: "#f43f5e",
  },
} as const;

// System Status Colors
export const STATUS_COLORS = {
  online: {
    bg: "bg-emerald-500/20",
    text: "text-emerald-400",
    dot: "bg-emerald-400",
    hex: "#10b981",
  },
  offline: {
    bg: "bg-red-500/20",
    text: "text-red-400",
    dot: "bg-red-400",
    hex: "#ef4444",
  },
  checking: {
    bg: "bg-amber-500/20",
    text: "text-amber-400",
    dot: "bg-amber-400",
    hex: "#f59e0b",
  },
  degraded: {
    bg: "bg-orange-500/20",
    text: "text-orange-400",
    dot: "bg-orange-400",
    hex: "#f97316",
  },
} as const;

// Vulcan Theme Colors
export const VULCAN_COLORS = {
  accent: "#6366f1",
  dark: "#1e1b4b",
  darker: "#0d1117",
  light: "#4338ca",
  success: "#10b981",
  warning: "#f59e0b",
  error: "#ef4444",
} as const;

// Dark Mode Colors
export const DARK_MODE = {
  background: "#121212",
  surface: "#1e1e1e",
  surfaceHover: "#2a2a2a",
  border: "#2d2d2d",
  text: "#e4e4e7",
  textMuted: "#a1a1aa",
} as const;

// Chart Colors (for Tremor/Recharts)
export const CHART_COLORS = {
  primary: ["#6366f1", "#8b5cf6", "#a855f7", "#d946ef"],
  success: ["#10b981", "#34d399", "#6ee7b7", "#a7f3d0"],
  danger: ["#ef4444", "#f87171", "#fca5a5", "#fecaca"],
  mixed: ["#6366f1", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6"],
} as const;

// Validator Category Colors
export const VALIDATOR_COLORS = {
  api_661: { bg: "bg-indigo-500/20", text: "text-indigo-400", hex: "#6366f1" },
  asme: { bg: "bg-blue-500/20", text: "text-blue-400", hex: "#3b82f6" },
  aws: { bg: "bg-orange-500/20", text: "text-orange-400", hex: "#f97316" },
  osha: { bg: "bg-yellow-500/20", text: "text-yellow-400", hex: "#eab308" },
  aisc: { bg: "bg-cyan-500/20", text: "text-cyan-400", hex: "#06b6d4" },
  hpc: { bg: "bg-purple-500/20", text: "text-purple-400", hex: "#a855f7" },
  gdt: { bg: "bg-pink-500/20", text: "text-pink-400", hex: "#ec4899" },
  bom: { bg: "bg-teal-500/20", text: "text-teal-400", hex: "#14b8a6" },
} as const;

export type CycleDay = keyof typeof CYCLE_DAY_COLORS;
export type TradingStatus = keyof typeof TRADING_COLORS;
export type SessionType = keyof typeof SESSION_COLORS;
export type ValidationStatus = keyof typeof VALIDATION_COLORS;
export type SystemStatus = keyof typeof STATUS_COLORS;
export type ValidatorCategory = keyof typeof VALIDATOR_COLORS;
