/**
 * BTMM Trading Constants
 * Session times, EMA settings, and other trading configuration
 */

import type { SetupType, SessionName, TradingPair, EMAConfig, TDIConfig, ChecklistItem } from "./types";

// Session Times (EST)
export const SESSIONS: Record<SessionName, { start: string; end: string; color: string }> = {
  asian: { start: "19:00", end: "02:00", color: "#a371f7" },
  london: { start: "02:00", end: "08:00", color: "#58a6ff" },
  newyork: { start: "08:00", end: "17:00", color: "#3fb950" },
  gap: { start: "17:00", end: "19:00", color: "#6e7681" },
};

// True Opens (EST)
export const TRUE_OPENS = {
  daily: "17:00",
  london: "01:30",
  newyork: "07:30",
};

// Kill Zones (EST) - Best trading windows
export const KILL_ZONES = {
  london: { start: "02:00", end: "05:00" },
  newyork: { start: "08:00", end: "11:00" },
  asianClose: { start: "00:00", end: "01:00" },
};

// EMA Settings (BTMM Standard)
export const EMA_SETTINGS: Record<string, EMAConfig> = {
  mustard: { period: 5, color: "#FFD700", name: "Mustard (5)" },
  ketchup: { period: 13, color: "#FF4444", name: "Ketchup (13)" },
  water: { period: 50, color: "#4A9EFF", name: "Water (50)" },
  mayo: { period: 200, color: "#E0E0E0", name: "Mayo (200)" },
  blueberry: { period: 800, color: "#1E3A8A", name: "Blueberry (800)" },
};

// TDI Settings
export const TDI_SETTINGS: TDIConfig = {
  rsiPeriod: 13,
  fastMAPeriod: 2,
  slowMAPeriod: 7,
  bands: { lower: 32, middle: 50, upper: 68 },
};

// Setup Type Labels
export const SETUP_LABELS: Record<SetupType, string> = {
  "1a": "Type 1a - Standard Reversal",
  "1b": "Type 1b - Deep Retracement",
  "1c": "Type 1c - Extended Move",
  "2a": "Type 2a - Standard Continuation",
  "2b": "Type 2b - Shallow Pullback",
  "2c": "Type 2c - Range Breakout",
  "3a": "Type 3a - Counter-Trend Entry",
  "3b": "Type 3b - Failed Breakout",
  "3c": "Type 3c - Trap & Reverse",
  "4a": "Type 4a - 1H 50/50 Standard",
  "4b": "Type 4b - 1H EMA Bounce",
  "4c": "Type 4c - 1H Momentum",
};

// Setup Descriptions
export const SETUP_DESCRIPTIONS: Record<SetupType, string> = {
  "1a": "Price reverses at major level with M/W pattern and TDI confirmation",
  "1b": "Deep retracement to key EMA with candlestick confirmation",
  "1c": "Extended move after initial reversal signal",
  "2a": "Trend continuation after pullback to EMA",
  "2b": "Quick continuation with shallow pullback",
  "2c": "Breakout from consolidation range",
  "3a": "Counter-trend entry at exhaustion point",
  "3b": "Entry after failed breakout and trap",
  "3c": "MM trap followed by reversal",
  "4a": "Standard 1H chart 50/50 setup",
  "4b": "Bounce off 1H timeframe EMA",
  "4c": "Momentum-based 1H entry",
};

// ADR Values (Typical pips)
export const TYPICAL_ADR: Record<string, number> = {
  "EUR/USD": 80,
  "GBP/USD": 110,
  "USD/JPY": 70,
  "EUR/JPY": 120,
  "GBP/JPY": 150,
  "AUD/USD": 70,
  "USD/CAD": 80,
  "NZD/USD": 60,
  "EUR/GBP": 50,
  "USD/CHF": 60,
  "EUR/CHF": 40,
  "GBP/CHF": 100,
  "AUD/JPY": 90,
  "CAD/JPY": 80,
  "CHF/JPY": 70,
  "EUR/AUD": 110,
  "GBP/AUD": 150,
  "EUR/CAD": 100,
  "GBP/CAD": 130,
  "AUD/CAD": 80,
  "NZD/JPY": 80,
  "AUD/NZD": 60,
};

// Trading Pairs
export const TRADING_PAIRS: TradingPair[] = [
  // Majors
  { symbol: "EUR/USD", displayName: "Euro / US Dollar", pipValue: 0.0001, typicalADR: 80, category: "major" },
  { symbol: "GBP/USD", displayName: "British Pound / US Dollar", pipValue: 0.0001, typicalADR: 110, category: "major" },
  { symbol: "USD/JPY", displayName: "US Dollar / Japanese Yen", pipValue: 0.01, typicalADR: 70, category: "major" },
  { symbol: "USD/CHF", displayName: "US Dollar / Swiss Franc", pipValue: 0.0001, typicalADR: 60, category: "major" },
  { symbol: "AUD/USD", displayName: "Australian Dollar / US Dollar", pipValue: 0.0001, typicalADR: 70, category: "major" },
  { symbol: "USD/CAD", displayName: "US Dollar / Canadian Dollar", pipValue: 0.0001, typicalADR: 80, category: "major" },
  { symbol: "NZD/USD", displayName: "New Zealand Dollar / US Dollar", pipValue: 0.0001, typicalADR: 60, category: "major" },

  // Crosses
  { symbol: "EUR/GBP", displayName: "Euro / British Pound", pipValue: 0.0001, typicalADR: 50, category: "minor" },
  { symbol: "EUR/JPY", displayName: "Euro / Japanese Yen", pipValue: 0.01, typicalADR: 120, category: "minor" },
  { symbol: "GBP/JPY", displayName: "British Pound / Japanese Yen", pipValue: 0.01, typicalADR: 150, category: "minor" },
  { symbol: "EUR/CHF", displayName: "Euro / Swiss Franc", pipValue: 0.0001, typicalADR: 40, category: "minor" },
  { symbol: "GBP/CHF", displayName: "British Pound / Swiss Franc", pipValue: 0.0001, typicalADR: 100, category: "minor" },
  { symbol: "AUD/JPY", displayName: "Australian Dollar / Japanese Yen", pipValue: 0.01, typicalADR: 90, category: "minor" },
  { symbol: "CAD/JPY", displayName: "Canadian Dollar / Japanese Yen", pipValue: 0.01, typicalADR: 80, category: "minor" },
  { symbol: "CHF/JPY", displayName: "Swiss Franc / Japanese Yen", pipValue: 0.01, typicalADR: 70, category: "minor" },
  { symbol: "EUR/AUD", displayName: "Euro / Australian Dollar", pipValue: 0.0001, typicalADR: 110, category: "minor" },
  { symbol: "GBP/AUD", displayName: "British Pound / Australian Dollar", pipValue: 0.0001, typicalADR: 150, category: "minor" },
  { symbol: "EUR/CAD", displayName: "Euro / Canadian Dollar", pipValue: 0.0001, typicalADR: 100, category: "minor" },
  { symbol: "GBP/CAD", displayName: "British Pound / Canadian Dollar", pipValue: 0.0001, typicalADR: 130, category: "minor" },
  { symbol: "AUD/CAD", displayName: "Australian Dollar / Canadian Dollar", pipValue: 0.0001, typicalADR: 80, category: "minor" },
  { symbol: "NZD/JPY", displayName: "New Zealand Dollar / Japanese Yen", pipValue: 0.01, typicalADR: 80, category: "minor" },
  { symbol: "AUD/NZD", displayName: "Australian Dollar / New Zealand Dollar", pipValue: 0.0001, typicalADR: 60, category: "minor" },
];

// Pre-Trade Checklist Default Items
export const DEFAULT_CHECKLIST: ChecklistItem[] = [
  { id: "session", label: "Correct Session", description: "Trading during London or NY kill zone", required: true, checked: false },
  { id: "cycle", label: "Cycle Day Confirmed", description: "Know what day of the 3-day cycle we are on", required: true, checked: false },
  { id: "level", label: "Level Identified", description: "Level I, II, or III identified on chart", required: true, checked: false },
  { id: "mw", label: "M or W Pattern", description: "Clear M or W pattern visible", required: true, checked: false },
  { id: "ema", label: "EMA Alignment", description: "EMAs aligned in direction of trade", required: true, checked: false },
  { id: "tdi", label: "TDI Confirmation", description: "TDI shows valid signal", required: true, checked: false },
  { id: "candle", label: "Candlestick Pattern", description: "Entry candle pattern present", required: false, checked: false },
  { id: "asian", label: "Asian Range Check", description: "Considered Asian range size", required: false, checked: false },
  { id: "adr", label: "ADR Check", description: "Room left in ADR for move", required: false, checked: false },
  { id: "news", label: "News Check", description: "No major news during trade", required: true, checked: false },
  { id: "risk", label: "Risk Calculated", description: "Position size calculated", required: true, checked: false },
  { id: "plan", label: "Exit Plan Ready", description: "TP and SL levels set", required: true, checked: false },
];

// Cycle Day Descriptions
export const CYCLE_DAY_INFO = {
  1: {
    name: "Day 1 - Accumulation",
    description: "MM accumulates positions, expect range-bound or small move",
    typical: "Consolidation, fake breakouts, stop hunting",
    strategy: "Wait for setup, don't chase",
  },
  2: {
    name: "Day 2 - Manipulation",
    description: "MM manipulates price to trigger stops before the move",
    typical: "Fake moves, traps, stop hunts before reversal",
    strategy: "Look for traps, wait for reversal signals",
  },
  3: {
    name: "Day 3 - Distribution",
    description: "MM distributes positions, expect trending move",
    typical: "Strong directional move, trend day",
    strategy: "Trade with the trend, trail stops",
  },
} as const;

// Level Descriptions
export const LEVEL_INFO = {
  I: {
    name: "Level I - Major",
    description: "Major swing high/low, weekly/monthly levels",
    importance: "Highest probability reversals",
    color: "#3fb950",
  },
  II: {
    name: "Level II - Intermediate",
    description: "Daily swing points, key EMAs",
    importance: "Good for continuation trades",
    color: "#58a6ff",
  },
  III: {
    name: "Level III - Minor",
    description: "4H/1H swing points, Asian range",
    importance: "Short-term bounces, scalp opportunities",
    color: "#a371f7",
  },
} as const;

// Session Labels
export const SESSION_LABELS: Record<SessionName, string> = {
  asian: "Asian Session",
  london: "London Session",
  newyork: "New York Session",
  gap: "Gap Session",
};

// Default Trading Settings
export const DEFAULT_TRADING_SETTINGS = {
  defaultRiskPercent: 1,
  maxDailyTrades: 3,
  maxDailyLoss: 3, // percent
  preferredPairs: ["EUR/USD", "GBP/USD", "USD/JPY"],
  preferredSessions: ["london", "newyork"] as SessionName[],
  showAdvancedMode: false,
  autoSaveScreenshots: true,
  soundAlerts: true,
  timezone: "America/New_York",
};

// Color Themes
export const TRADING_COLORS = {
  bullish: "#3fb950",
  bearish: "#f85149",
  neutral: "#6e7681",
  warning: "#d29922",
  info: "#58a6ff",
  profit: "#3fb950",
  loss: "#f85149",
  breakeven: "#d29922",
};

// TradingView Widget Settings
export const TRADINGVIEW_CONFIG = {
  theme: "dark",
  style: "1", // Candlestick
  interval: "60", // 1H
  timezone: "America/New_York",
  studies: [
    "MAExp@tv-basicstudies", // EMA
    "RSI@tv-basicstudies",
  ],
  locale: "en",
  toolbar_bg: "#0d1117",
  enable_publishing: false,
  hide_top_toolbar: false,
  hide_legend: false,
  save_image: true,
  container_id: "tradingview_chart",
};
