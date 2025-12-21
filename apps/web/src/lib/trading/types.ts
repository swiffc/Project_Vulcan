/**
 * BTMM Trading Types
 * Core type definitions for the Big Trading Money Method strategy
 */

// Setup Types (1-4 with a/b/c variations)
export type SetupType =
  | "1a" | "1b" | "1c"  // Type 1 variations
  | "2a" | "2b" | "2c"  // Type 2 variations
  | "3a" | "3b" | "3c"  // Type 3 variations
  | "4a" | "4b" | "4c"; // Type 4 variations (1H 50/50)

// BTMM Levels
export type BTMMLevel = "I" | "II" | "III";

// Cycle Day
export type CycleDay = 1 | 2 | 3;

// Asian Range Status
export type AsianRangeStatus = "small" | "large"; // <50 or >50 pips

// Strike Zone
export type StrikeZone = "+25-50" | "-25-50" | "none";

// MM (Market Maker) Behavior
export type MMBehavior =
  | "trap_up"
  | "trap_down"
  | "stop_hunt_high"
  | "stop_hunt_low"
  | "none";

// Candlestick Patterns
export type CandlestickPattern =
  | "morning_star"
  | "evening_star"
  | "hammer"
  | "inverted_hammer"
  | "engulfing_bullish"
  | "engulfing_bearish"
  | "doji"
  | "shooting_star"
  | "none";

// TDI Signals
export type TDISignal =
  | "sharkfin"
  | "blood_in_water"
  | "cross_above"
  | "cross_below"
  | "none";

// Session Names
export type SessionName = "asian" | "london" | "newyork" | "gap";

// Trade Direction
export type TradeDirection = "long" | "short";

// Trade Result
export type TradeResult = "win" | "loss" | "breakeven";

// M/W Pattern Type
export type MWPatternType = "M" | "W";

// Session Interface
export interface Session {
  name: SessionName;
  startTime: string; // HH:MM EST
  endTime: string;
  color: string;
  isActive: boolean;
}

// EMA Configuration
export interface EMAConfig {
  period: number;
  color: string;
  name: string;
}

// TDI Configuration
export interface TDIConfig {
  rsiPeriod: number;
  fastMAPeriod: number;
  slowMAPeriod: number;
  bands: {
    lower: number;
    middle: number;
    upper: number;
  };
}

// Trade Entry
export interface Trade {
  id: string;
  pair: string;
  direction: TradeDirection;
  entryPrice: number;
  exitPrice?: number;
  stopLoss: number;
  takeProfit1: number;
  takeProfit2?: number;
  takeProfit3?: number;
  positionSize: number;
  riskPercent: number;

  // BTMM Fields
  setupType: SetupType;
  cycleDay: CycleDay;
  level: BTMMLevel;
  asianRange: AsianRangeStatus;
  asianRangePips?: number;
  strikeZone: StrikeZone;
  mmBehavior: MMBehavior;

  // Confirmation Checklist
  mwPattern: boolean;
  mwPatternType?: MWPatternType;
  candlestickPattern: CandlestickPattern;
  emaAlignment: boolean;
  tdiSignal: TDISignal;

  // Additional Confirmations
  sessionConfirmation: boolean;
  levelConfirmation: boolean;
  adrConfirmation: boolean;

  // Screenshots
  entryScreenshot?: string;
  exitScreenshot?: string;
  analysisScreenshot?: string;

  // Notes
  preTradeNotes?: string;
  duringTradeNotes?: string;
  postTradeNotes?: string;
  lessonsLearned?: string;

  // Timestamps
  entryTime: string;
  exitTime?: string;
  createdAt: string;
  updatedAt: string;

  // Results
  result?: TradeResult;
  pnlPips?: number;
  pnlDollars?: number;
  rMultiple?: number;

  // Session Info
  entrySession: SessionName;
}

// Daily Bias
export interface DailyBias {
  date: string;
  pair: string;
  bias: "bullish" | "bearish" | "neutral";
  cycleDay: CycleDay;
  level: BTMMLevel;
  keyLevels: {
    asianHigh: number;
    asianLow: number;
    previousHigh: number;
    previousLow: number;
    weeklyOpen: number;
    monthlyOpen: number;
  };
  notes: string;
}

// Performance Stats
export interface PerformanceStats {
  totalTrades: number;
  winningTrades: number;
  losingTrades: number;
  breakevenTrades: number;
  winRate: number;
  averageWin: number;
  averageLoss: number;
  profitFactor: number;
  expectancy: number;
  maxDrawdown: number;
  currentStreak: number;
  bestStreak: number;
  worstStreak: number;
  totalPnL: number;
  averageRMultiple: number;
}

// Setup Performance
export interface SetupPerformance {
  setupType: SetupType;
  totalTrades: number;
  winRate: number;
  averagePnL: number;
  profitFactor: number;
}

// Session Performance
export interface SessionPerformance {
  session: SessionName;
  totalTrades: number;
  winRate: number;
  averagePnL: number;
  bestTime: string;
}

// Trading Pair
export interface TradingPair {
  symbol: string;
  displayName: string;
  pipValue: number;
  typicalADR: number;
  category: "major" | "minor" | "exotic";
}

// Watchlist Item
export interface WatchlistItem {
  pair: string;
  bias: "bullish" | "bearish" | "neutral";
  cycleDay: CycleDay;
  notes: string;
  priority: "high" | "medium" | "low";
}

// Pre-Trade Checklist Item
export interface ChecklistItem {
  id: string;
  label: string;
  description?: string;
  required: boolean;
  checked: boolean;
}

// Trading Settings
export interface TradingSettings {
  defaultRiskPercent: number;
  maxDailyTrades: number;
  maxDailyLoss: number;
  preferredPairs: string[];
  preferredSessions: SessionName[];
  showAdvancedMode: boolean;
  autoSaveScreenshots: boolean;
  soundAlerts: boolean;
  timezone: string;
}

// Calculator Result Types
export interface PositionSizeResult {
  units: number;
  lots: number;
  riskAmount: number;
  stopLossPips: number;
}

export interface RiskRewardResult {
  ratio: string;
  riskPips: number;
  rewardPips: number;
  breakeven: number;
}

export interface ADRResult {
  current: number;
  average: number;
  remaining: number;
  percentUsed: number;
}

// Pattern Trainer Types
export interface PatternQuestion {
  id: string;
  imageUrl: string;
  correctPattern: MWPatternType | "none";
  timeLimit: number;
}

export interface TrainerScore {
  correct: number;
  total: number;
  averageTime: number;
  accuracy: number;
}
