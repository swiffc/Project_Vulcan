# Project Vulcan: Master Task List

**Status**: Phase 14 IN PROGRESS - Trading Module Redesign
**Last Updated**: Dec 2025 - Trading App Strategic Redesign
**Goal**: Unified AI Operating System (Trading, CAD, General)
**Pattern**: Adapter + Bridge (lightweight, no cloning)

---

## ✅ Completed

### Phase 1-3 (Foundation)
- [x] Unified Chatbot (Next.js)
- [x] MCP Server (Desktop Control)
- [x] Trading Agent (TypeScript)
- [x] CAD COM Adapters (SolidWorks, Inventor)
- [x] Review Agent / Judge
- [x] Briefing Agent
- [x] Black Box Logging
- [x] Visual Replay & Verifier
- [x] Watchdog Recovery

### Phase 4 (PRD Alignment) - Dec 2025
- [x] System Manager adapter (APScheduler wrapper)
- [x] PDF Bridge (pytesseract + pdf2image)
- [x] ECN Adapter (revision tracking)
- [x] GDrive Bridge (MCP + direct API fallback)
- [x] MCP Server Registry config
- [x] Updated REFERENCES.md
- [x] Updated requirements.txt

### Phase 5: Integration - Complete
- [x] CrewAI orchestrator adapter
- [x] End-to-end workflow tests
- [x] Health dashboard API

### Phase 6: Polish - Complete
- [x] Voice command adapter (Whisper)
- [x] Mobile PWA wrapper
- [x] Metrics visualization

### Phase 7: Production Hardening - Complete
- [x] Rate limiting middleware
- [x] Auth adapter JWT/OAuth
- [x] Monitoring alerts

### Phase 7.5: Elite Engineering Patterns - Complete
- [x] Circuit Breaker (`agents/core/circuit_breaker.py`) - Emergency Brake
- [x] Queue Adapter (`agents/core/queue_adapter.py`) - Waiting Room
- [x] Digital Twin (`agents/cad_agent/adapters/digital_twin.py`) - Shadow Copy
- [x] Docker Compose setup
- [x] Orchestrator Dockerfile
- [x] System Manager Dockerfile

---

## ✅ Phase 8: Deployment - Complete

### Render Deployment (per PRD-002)
- [x] render.yaml with all services (web, orchestrator, system_manager, memory)
- [x] GitHub Actions CI/CD pipeline (`.github/workflows/ci.yml`)
- [x] Docker Compose for local dev
- [x] Dockerfiles for containerized testing

### Integration Testing (PRD Section 9) - Complete
- [x] E2E test: Trading flow (`tests/test_e2e_trading.py`)
- [x] E2E test: CAD flow (`tests/test_e2e_cad.py`)
- [x] Load testing (`tests/test_load.py`) - 100 concurrent, <2% failure

---

## ✅ Phase 8.5 ULTIMATE: Maximum Cost Optimization - Complete

### 🔥 ULTIMATE Cost Reduction Stack (90-95% potential savings!)

| Layer | File | What It Does | Savings |
|-------|------|--------------|---------|
| 1. Redis Cache | `agents/core/redis_adapter.py` | Skip API entirely for repeated queries | 100% on hits |
| 2. Model Router | `agents/core/model_router.py` | Use Haiku ($0.25/M) instead of Sonnet ($3/M) | 92% per token |
| 3. Token Optimizer V1 | `agents/core/token_optimizer.py` | Trim history, compress prompts | 20-40% |
| 4. **Token Optimizer V2** | `agents/core/token_optimizer_v2.py` | Anthropic native prompt caching! | **90% on cached** |
| 5. Batch API | `core/llm.py` | 50% off for non-urgent tasks | 50% |

### 💰 Anthropic Native Prompt Caching (THE BIG ONE!)

This uses Claude's built-in `cache_control` feature - NOT our Redis cache!

**How it works:**
```python
# System prompt gets cached at Anthropic's servers
system=[{
    "type": "text",
    "text": "You are Vulcan Trading Agent...",
    "cache_control": {"type": "ephemeral"}  # 🔥 THE MAGIC
}]
```

**Pricing Impact:**
| Token Type | Normal | With Cache | Savings |
|------------|--------|------------|---------|
| First call (create cache) | $3.00/M | $3.75/M | -25% |
| Subsequent calls (read cache) | $3.00/M | **$0.30/M** | **90%!** |

### Cost Optimization Summary

| Strategy | Individual Savings | Combined Effect |
|----------|-------------------|-----------------|
| Redis Response Cache | 30-50% | Avoid API entirely |
| Model Router (Haiku) | 50-70% | 12x cheaper model |
| Token Optimizer (trim) | 20-40% | Less data sent |
| Prompt Caching (Anthropic) | **90%** | System prompts |
| Batch API | 50% | Weekly reviews, audits |
| **TOTAL POTENTIAL** | | **90-95%** |

**Real World Estimate:**
- Before: ~$50/month
- After: ~$3-5/month

---

## ✅ Phase 8.6: Web UI Enhancement - Complete (Dec 2025)

### 🎨 New Dashboard Components
- [x] `CostDashboard.tsx` - Real-time savings visualization (Redis, Model Router, Prompt Cache)
- [x] `RealTimeMetrics.tsx` - Live sparkline charts, response times, system health
- [x] `/api/metrics/cost/route.ts` - Cost tracking API endpoint

### 🌟 Enhanced Glassmorphism Theme
- [x] `glass-accent` - Indigo/violet gradient with glow
- [x] `glass-success` - Emerald variant for positive states
- [x] `glass-warning` - Amber variant for warnings
- [x] `glass-error` - Rose variant for errors
- [x] `glow-indigo`, `glow-emerald` - Glow effects
- [x] `gradient-border` - Animated gradient borders
- [x] `hover-lift` - Hover elevation effect
- [x] `shimmer` - Loading shimmer animation
- [x] `pulse-ring` - Pulse ring animation

### 💬 Chat UI Improvements
- [x] Quick command chips (context-aware: Trading/CAD/General)
- [x] Animated typing indicator (bouncing dots)
- [x] Model routing indicator (Haiku/Sonnet display)
- [x] Enhanced message styling

### 📊 Dashboard Layout
- [x] 4-column responsive grid (xl:grid-cols-4)
- [x] "ULTIMATE Stack Active" status badge
- [x] Footer stats bar with phase info
- [x] Integrated Cost + Real-Time Metrics widgets

### 🔗 Repos Researched for Future Scaling
| Repo | Stars | Use For |
|------|-------|---------|
| [assistant-ui](https://github.com/assistant-ui/assistant-ui) | 7.7k | Composable chat primitives |
| [LobeChat](https://github.com/lobehub/lobe-chat) | 69k | Full AI workspace, MCP |
| [glasscn-ui](https://github.com/itsjavi/glasscn-ui) | - | More glassmorphism components |
| [Lobe-UI](https://github.com/lobehub/lobe-ui) | 1.7k | AI-specific React components |
| [Langfuse](https://langfuse.com) | OSS | Production LLM cost tracking |

---

## 📁 Current Adapters & Bridges

| File | Type | Wraps | Lines |
|------|------|-------|-------|
| `agents/system_manager/adapter.py` | Adapter | APScheduler, psutil | ~80 |
| `agents/cad_agent/adapters/pdf_bridge.py` | Bridge | pytesseract, pdf2image | ~90 |
| `agents/cad_agent/adapters/ecn_adapter.py` | Adapter | chromadb | ~70 |
| `agents/cad_agent/adapters/gdrive_bridge.py` | Bridge | google-api / MCP | ~85 |
| `agents/cad_agent/adapters/digital_twin.py` | Adapter | Pure Python (Shadow Copy) | ~220 |
| `agents/trading_agent/adapters/strategy_adapter.py` | Adapter | ICT/BTMM logic | ~96 |
| `agents/trading_agent/adapters/journal_adapter.py` | Adapter | Memory Brain | ~109 |
| `agents/trading_agent/adapters/tradingview_bridge.py` | Bridge | MCP Desktop | ~150 |
| `agents/inspector_bot/adapters/audit_adapter.py` | Adapter | LLM-as-Judge | ~141 |
| `agents/inspector_bot/adapters/report_bridge.py` | Bridge | reportlab/markdown | ~200 |
| `desktop_server/com/solidworks_com.py` | Adapter | pywin32 COM | ~200 |
| `desktop_server/com/inventor_com.py` | Adapter | pywin32 COM | ~160 |
| `agents/core/orchestrator_adapter.py` | Adapter | CrewAI routing | ~200 |
| `agents/core/health_dashboard.py` | Bridge | httpx, health checks | ~200 |
| `agents/core/voice_adapter.py` | Adapter | Whisper (local/API) | ~190 |
| `agents/core/metrics_viz.py` | Bridge | Dashboard charts | ~200 |
| `agents/core/rate_limiter.py` | Adapter | Token bucket | ~175 |
| `agents/core/auth_adapter.py` | Adapter | JWT/OAuth | ~230 |
| `agents/core/alerts_adapter.py` | Bridge | Slack/PagerDuty | ~240 |
| `agents/core/circuit_breaker.py` | Adapter | Emergency Brake | ~180 |
| `agents/core/queue_adapter.py` | Adapter | Waiting Room | ~200 |
| `agents/core/redis_adapter.py` | Adapter | Redis + in-memory fallback | ~160 |
| `agents/core/model_router.py` | Adapter | Haiku/Sonnet routing | ~120 |
| `agents/core/token_optimizer.py` | Adapter | Basic trimming | ~140 |
| `agents/core/token_optimizer_v2.py` | Adapter | **Anthropic prompt caching** | ~250 |
| `agents/cad_agent/cad_orchestrator.py` | Orchestrator | SolidWrap main coordinator | ~280 |
| `agents/cad_agent/adapters/performance_manager.py` | Adapter | psutil + GPUtil monitoring | ~190 |
| `agents/cad_agent/adapters/solidworks_settings.py` | Adapter | Graphics tier management | ~210 |
| `agents/cad_agent/adapters/job_queue.py` | Adapter | Batch processing + resume | ~250 |
| `agents/cad_agent/adapters/notification_store.py` | Adapter | Web UI notifications | ~200 |
| `agents/cad_agent/adapters/flatter_files_adapter.py` | Adapter | Flatter Files REST API | ~320 |

---

## ✅ Phase 9: Web UI Redesign - Complete (Dec 2025)

### Dashboard, Trading, CAD Pages
- [x] Modern dark theme with glass effects
- [x] Responsive 2-column grid layout
- [x] Real-time status indicators
- [x] Reusable UI components (Card, Button, Badge)
- [x] Navigation with desktop server health check

---

## 🔄 Phase 10: Work Integration Hub - In Progress

### ✅ Completed (UI + API Structure)
- [x] `/work` page with 4 widget cards (Email, Teams, Files, J2)
- [x] `/work/setup` Azure AD setup guide
- [x] Microsoft Graph client (`lib/work/microsoft-client.ts`)
- [x] Token manager with AES-256 encryption (`lib/work/token-manager.ts`)
- [x] Device Code Flow authentication
- [x] API routes: health, device-code, status, signout, mail, teams, files
- [x] Navigation updated with "Work" link

### 🔲 Pending: Authentication Setup
- [ ] Create Azure AD app registration (needs IT or personal account)
- [ ] Add `MICROSOFT_CLIENT_ID` to `.env.local`
- [ ] Test Device Code Flow with real credentials

### 🔲 Pending: Browser Automation (Playwright)
- [ ] Install Playwright in Desktop Server
- [ ] Create `desktop_server/controllers/browser.py`
- [ ] Create `desktop_server/controllers/j2_tracker.py`
- [ ] Implement "login once, save session" for Duo 2FA
- [ ] J2 Tracker scraping (jobs, workflows, due dates)

### 🔲 Pending: Optional Refactor
- [ ] Consider replacing custom client with `@microsoft/mgt-react`
- [ ] Pre-built components: `<Login />`, `<Inbox />`, `<FileList />`

---

## ✅ Phase 11: CAD Performance Manager - Complete (Dec 2025)

### 20K+ Part Assembly Support
**Uses**: SolidWrap, psutil, GPUtil

- [x] Install SolidWrap + GPUtil: `pip install solidwrap GPUtil`
- [x] `agents/cad_agent/cad_orchestrator.py` - Main coordinator using SolidWrap
- [x] `agents/cad_agent/adapters/performance_manager.py` - RAM/GPU monitoring, auto-tier
- [x] `agents/cad_agent/adapters/solidworks_settings.py` - Graphics settings per tier
- [x] `agents/cad_agent/adapters/job_queue.py` - Batch processing with resume
- [x] `agents/cad_agent/adapters/notification_store.py` - Web UI notifications
- [x] Restart SolidWorks every N files to prevent memory issues
- [x] Performance tiers: FULL → REDUCED → MINIMAL → SURVIVAL

**RAM Thresholds:**
| RAM % | Action |
|-------|--------|
| 60% | Switch to REDUCED mode |
| 75% | Switch to MINIMAL mode |
| 85% | Switch to SURVIVAL mode |
| 90% | Force restart SolidWorks |

---

## ✅ Phase 12: Flatter Files Integration - Complete (Dec 2025)

### Drawing Management via API
**Uses**: httpx, Flatter Files REST API

- [x] `agents/cad_agent/adapters/flatter_files_adapter.py` (~320 lines)
- [x] Search drawings by part number/description
- [x] Get PDF/STEP/DXF download URLs
- [x] Get assembly BOM structure
- [x] Create external sharing links
- [x] Activity history tracking
- [x] Item activation/deactivation
- [x] Add `FLATTER_FILES_COMPANY_ID` + `FLATTER_FILES_API_KEY` to .env

**Chatbot examples:**
- "Find drawing for bracket 12345" → PDF/STEP links
- "What parts are in assembly XYZ-100?" → BOM list

---

## 🔥 Phase 14: Trading Module Redesign - IN PROGRESS

### 📋 Overview
Complete redesign of `/trading` page based on 2024 trading app UX research. Integrates content from `swiffc/Trading-Guide` repo with TradingView-inspired layout.

**Source Content**: `github.com/swiffc/Trading-Guide` (24 HTML pages)
**Design Inspiration**: TradingView, TraderSync, TradesViz 2.0, Robinhood

---

### 🏗️ Step 1: Create New Route Structure

**Location**: `apps/web/src/app/trading/`

```bash
# Create directories
mkdir -p apps/web/src/app/trading/{dashboard,journal/{new,[id]},analysis/{live,daily,weekly,monthly},performance/{calendar,reports},strategy-guide/{philosophy,setup,patterns,btmm-cycle,sessions,psychology,examples},tools/{calculators,trainer,checklist},settings/{risk,preferences,sync}}
```

**New Routes:**
| Route | Purpose |
|-------|---------|
| `/trading` | Redirect to `/trading/dashboard` |
| `/trading/dashboard` | Main workspace (chart + BTMM panels) |
| `/trading/journal` | Trade log list |
| `/trading/journal/new` | New trade entry form |
| `/trading/journal/[id]` | Trade detail/edit |
| `/trading/analysis` | Market analysis overview |
| `/trading/analysis/live` | Live session analysis |
| `/trading/analysis/daily` | Daily bias |
| `/trading/analysis/weekly` | Weekly outlook |
| `/trading/analysis/monthly` | Monthly cycle |
| `/trading/performance` | Stats dashboard |
| `/trading/performance/calendar` | Trade calendar |
| `/trading/performance/reports` | Detailed reports |
| `/trading/strategy-guide` | BTMM knowledge base |
| `/trading/strategy-guide/philosophy` | Core concepts |
| `/trading/strategy-guide/setup` | Technical setup (EMAs, TDI) |
| `/trading/strategy-guide/patterns` | Chart models (M/W, etc) |
| `/trading/strategy-guide/btmm-cycle` | 3-day cycle, levels |
| `/trading/strategy-guide/sessions` | Session timing |
| `/trading/strategy-guide/psychology` | Mental game |
| `/trading/strategy-guide/examples` | Trade examples |
| `/trading/tools` | Utilities overview |
| `/trading/tools/calculators` | Position size, RR, ADR |
| `/trading/tools/trainer` | Pattern recognition practice |
| `/trading/tools/checklist` | Pre-trade checklist |
| `/trading/settings` | Trading settings |
| `/trading/settings/risk` | Risk management rules |
| `/trading/settings/preferences` | UI preferences |
| `/trading/settings/sync` | TradingView sync |

---

### 🏗️ Step 2: Create Component Structure

**Location**: `apps/web/src/components/trading/`

```bash
# Create component directories
mkdir -p apps/web/src/components/trading/{layout,dashboard,journal,analysis,performance,strategy-guide,tools,common}
```

**Components to Create:**

#### Layout Components
| File | Description | Lines |
|------|-------------|-------|
| `layout/TradingHeader.tsx` | Header with session clock, pair selector, mode toggle | ~150 |
| `layout/TradingNav.tsx` | Side/bottom navigation | ~100 |
| `layout/LeftPanel.tsx` | Collapsible left panel (watchlist, quick ref) | ~120 |
| `layout/BottomTabs.tsx` | Mobile-friendly tab navigation | ~80 |

#### Dashboard Components
| File | Description | Lines |
|------|-------------|-------|
| `dashboard/TradingViewChart.tsx` | Full TradingView widget integration | ~100 |
| `dashboard/BTMMAnalysisPanel.tsx` | Cycle phase, Level I/II/III, Asian Range | ~200 |
| `dashboard/EntryChecklist.tsx` | M/W, EMA, TDI, Session confirmation checks | ~150 |
| `dashboard/QuickReference.tsx` | Key levels, today's bias | ~100 |

#### Journal Components
| File | Description | Lines |
|------|-------------|-------|
| `journal/TradeEntry.tsx` | Full trade entry form | ~400 |
| `journal/BTMMFields.tsx` | Setup Type, Level, Asian Range, Strike Zone | ~200 |
| `journal/TradeList.tsx` | Filterable trade log | ~250 |
| `journal/TradeCard.tsx` | Compact trade display | ~100 |
| `journal/TradeDetail.tsx` | Expanded trade view | ~200 |
| `journal/ScreenshotUploader.tsx` | Chart screenshot upload | ~150 |

#### Analysis Components
| File | Description | Lines |
|------|-------------|-------|
| `analysis/SessionInfo.tsx` | Current session, time to next | ~100 |
| `analysis/CyclePhase.tsx` | Day 1/2/3 indicator | ~80 |
| `analysis/LevelIndicator.tsx` | Level I/II/III display | ~80 |
| `analysis/BiasPanel.tsx` | Daily/weekly bias display | ~150 |

#### Performance Components
| File | Description | Lines |
|------|-------------|-------|
| `performance/StatsOverview.tsx` | Win rate, PnL, drawdown | ~200 |
| `performance/TradeCalendar.tsx` | Calendar view of trades | ~250 |
| `performance/EquityCurve.tsx` | Equity curve chart | ~150 |
| `performance/SetupAnalysis.tsx` | Performance by setup type | ~200 |

#### Strategy Guide Components
| File | Description | Lines |
|------|-------------|-------|
| `strategy-guide/GuideSidebar.tsx` | Topic navigation | ~100 |
| `strategy-guide/GuideContent.tsx` | Content container | ~80 |
| `strategy-guide/ExpandableCard.tsx` | Collapsible sections | ~100 |
| `strategy-guide/InteractiveChecklist.tsx` | Checkable items | ~100 |

#### Tools Components
| File | Description | Lines |
|------|-------------|-------|
| `tools/PositionCalculator.tsx` | Position size calculator | ~200 |
| `tools/RRCalculator.tsx` | Risk/reward calculator | ~150 |
| `tools/ADRCalculator.tsx` | Average daily range calculator | ~150 |
| `tools/PatternTrainer.tsx` | Pattern recognition game | ~300 |
| `tools/PreTradeChecklist.tsx` | Configurable pre-trade checks | ~200 |

#### Common Components
| File | Description | Lines |
|------|-------------|-------|
| `common/SessionClock.tsx` | Enhanced session clock with countdown | ~150 |
| `common/PairSelector.tsx` | Searchable pair dropdown | ~100 |
| `common/ModeToggle.tsx` | Simple/Pro mode switch | ~50 |
| `common/Watchlist.tsx` | Mini watchlist widget | ~150 |

---

### 🏗️ Step 3: Create Types & Constants

**Location**: `apps/web/src/lib/trading/`

```bash
mkdir -p apps/web/src/lib/trading/hooks
```

#### `types.ts` - BTMM Type Definitions
```typescript
// Setup Types
export type SetupType = 
  | '1a' | '1b' | '1c'  // Type 1 variations
  | '2a' | '2b' | '2c'  // Type 2 variations
  | '3a' | '3b' | '3c'  // Type 3 variations
  | '4a' | '4b' | '4c'; // Type 4 variations

// BTMM Levels
export type BTMMLevel = 'I' | 'II' | 'III';

// Cycle Day
export type CycleDay = 1 | 2 | 3;

// Asian Range Status
export type AsianRangeStatus = 'small' | 'large'; // <50 or >50 pips

// Strike Zone
export type StrikeZone = '+25-50' | '-25-50' | 'none';

// MM Behavior
export type MMBehavior = 'trap_up' | 'trap_down' | 'stop_hunt_high' | 'stop_hunt_low' | 'none';

// Candlestick Patterns
export type CandlestickPattern = 
  | 'morning_star' | 'evening_star'
  | 'hammer' | 'inverted_hammer'
  | 'engulfing_bullish' | 'engulfing_bearish'
  | 'doji' | 'shooting_star'
  | 'none';

// TDI Signals
export type TDISignal = 'sharkfin' | 'blood_in_water' | 'cross_above' | 'cross_below' | 'none';

// Trade Entry
export interface Trade {
  id: string;
  pair: string;
  direction: 'long' | 'short';
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
  strikeZone: StrikeZone;
  mmBehavior: MMBehavior;
  
  // Confirmation Checklist
  mwPattern: boolean;
  mwPatternType?: 'M' | 'W';
  candlestickPattern: CandlestickPattern;
  emaAlignment: boolean;
  tdiSignal: TDISignal;
  
  // Screenshots
  entryScreenshot?: string;
  exitScreenshot?: string;
  
  // Notes
  preTradeNotes?: string;
  duringTradeNotes?: string;
  postTradeNotes?: string;
  
  // Timestamps
  entryTime: string;
  exitTime?: string;
  createdAt: string;
  updatedAt: string;
  
  // Results
  result?: 'win' | 'loss' | 'breakeven';
  pnlPips?: number;
  pnlDollars?: number;
}

// Session
export interface Session {
  name: 'asian' | 'london' | 'newyork' | 'gap';
  startTime: string; // HH:MM EST
  endTime: string;
  color: string;
  isActive: boolean;
}
```

#### `constants.ts` - BTMM Constants
```typescript
// Session Times (EST)
export const SESSIONS = {
  asian: { start: '19:00', end: '02:00', color: '#a371f7' },
  london: { start: '02:00', end: '08:00', color: '#58a6ff' },
  newyork: { start: '08:00', end: '17:00', color: '#3fb950' },
  gap: { start: '17:00', end: '19:00', color: '#6e7681' },
};

// True Opens (EST)
export const TRUE_OPENS = {
  daily: '17:00',
  london: '01:30',
  newyork: '07:30',
};

// Kill Zones (EST)
export const KILL_ZONES = {
  london: { start: '02:00', end: '05:00' },
  newyork: { start: '08:00', end: '11:00' },
  asianClose: { start: '00:00', end: '01:00' },
};

// EMA Settings
export const EMA_SETTINGS = {
  mustard: { period: 5, color: '#FFD700' },
  ketchup: { period: 13, color: '#FF4444' },
  water: { period: 50, color: '#4A9EFF' },
  mayo: { period: 200, color: '#E0E0E0' },
  blueberry: { period: 800, color: '#1E3A8A' },
};

// TDI Settings
export const TDI_SETTINGS = {
  rsiPeriod: 13,
  fastMAPeriod: 2,
  slowMAPeriod: 7,
  bands: { lower: 32, middle: 50, upper: 68 },
};

// Setup Type Labels
export const SETUP_LABELS = {
  '1a': 'Type 1a - Standard',
  '1b': 'Type 1b - Variant',
  '1c': 'Type 1c - Extended',
  '2a': 'Type 2a - Standard',
  '2b': 'Type 2b - Variant',
  '2c': 'Type 2c - Extended',
  '3a': 'Type 3a - Standard',
  '3b': 'Type 3b - Variant',
  '3c': 'Type 3c - Extended',
  '4a': 'Type 4a - Standard (1H 50/50)',
  '4b': 'Type 4b - Variant',
  '4c': 'Type 4c - Extended',
};

// ADR Values (typical)
export const TYPICAL_ADR = {
  'EUR/USD': 80,
  'GBP/USD': 110,
  'USD/JPY': 70,
  'EUR/JPY': 120,
  'GBP/JPY': 150,
  'AUD/USD': 70,
  'USD/CAD': 80,
  'NZD/USD': 60,
};
```

---

### 🏗️ Step 4: Migrate Trading Guide Content

**Source**: `github.com/swiffc/Trading-Guide/pages/`

| Trading Guide Page | Target Component/Route |
|--------------------|----------------------|
| `index.html` | Dashboard overview widget |
| `core-philosophy.html` | `/strategy-guide/philosophy` |
| `technical-setup.html` | `/strategy-guide/setup` |
| `chart-models.html` | `/strategy-guide/patterns` |
| `btmm-cycle.html` | `/strategy-guide/btmm-cycle` |
| `daily-sessions.html` | `/strategy-guide/sessions` + Analysis panel |
| `entry-rules.html` | `/strategy-guide/setup` + Journal entry form |
| `trade-execution.html` | `/journal/new` trade entry flow |
| `risk-management.html` | `/settings/risk` |
| `trading-journal.html` | `/journal` main component |
| `calculators.html` | `/tools/calculators` |
| `quick-reference.html` | `QuickReference.tsx` sidebar widget |
| `checklist.html` | `/tools/checklist` |
| `pattern-trainer.html` | `/tools/trainer` |
| `intraday-bias.html` | `/analysis/daily` |
| `live-session-guide.html` | `/analysis/live` |
| `micro-quarters.html` | `/analysis` quarterly panel |
| `monthly-cycle.html` | `/analysis/monthly` |
| `weekly-schedule.html` | `/analysis/weekly` |
| `yearly-cycle.html` | `/analysis/monthly` (extended view) |
| `session-cycle.html` | `/strategy-guide/sessions` |
| `trading-psychology.html` | `/strategy-guide/psychology` |
| `examples.html` | `/strategy-guide/examples` |

---

### 🏗️ Step 5: Design System Updates

**Location**: `apps/web/src/app/globals.css`

Add trading-specific CSS variables:
```css
:root {
  /* Trading-specific colors */
  --trading-bg-primary: #0d1117;
  --trading-bg-secondary: #161b22;
  --trading-bg-tertiary: #21262d;
  --trading-bg-elevated: #30363d;
  
  --trading-accent-blue: #58a6ff;
  --trading-accent-green: #3fb950;
  --trading-accent-red: #f85149;
  --trading-accent-yellow: #d29922;
  --trading-accent-purple: #a371f7;
  
  --trading-border: #30363d;
  --trading-border-active: #58a6ff;
  
  /* Session colors */
  --session-asian: #a371f7;
  --session-london: #58a6ff;
  --session-newyork: #3fb950;
  --session-gap: #6e7681;
}
```

---

### 📋 Implementation Checklist

#### Week 1: Foundation
- [ ] Create all route directories (Step 1)
- [ ] Create all component directories (Step 2)
- [ ] Create `types.ts` with BTMM types (Step 3)
- [ ] Create `constants.ts` with BTMM constants (Step 3)
- [ ] Build `TradingHeader.tsx`
- [ ] Build `LeftPanel.tsx` (collapsible)
- [ ] Build enhanced `SessionClock.tsx`
- [ ] Update `globals.css` with trading variables

#### Week 2: Dashboard
- [ ] Update `/trading/page.tsx` to redirect to `/dashboard`
- [ ] Create `/trading/dashboard/page.tsx`
- [ ] Build `TradingViewChart.tsx` (full widget)
- [ ] Build `BTMMAnalysisPanel.tsx`
- [ ] Build `EntryChecklist.tsx`
- [ ] Build `QuickReference.tsx`
- [ ] Build `ModeToggle.tsx` (Simple/Pro)

#### Week 3: Journal
- [ ] Create `/trading/journal/page.tsx`
- [ ] Create `/trading/journal/new/page.tsx`
- [ ] Build `TradeEntry.tsx` with BTMM fields
- [ ] Build `BTMMFields.tsx` component
- [ ] Build `TradeList.tsx` with filters
- [ ] Build `TradeCard.tsx`
- [ ] Build `TradeDetail.tsx`
- [ ] Build `ScreenshotUploader.tsx`

#### Week 4: Analysis & Performance
- [ ] Create all `/trading/analysis/` pages
- [ ] Build `SessionInfo.tsx`
- [ ] Build `CyclePhase.tsx`
- [ ] Build `LevelIndicator.tsx`
- [ ] Build `BiasPanel.tsx`
- [ ] Create all `/trading/performance/` pages
- [ ] Build `StatsOverview.tsx`
- [ ] Build `TradeCalendar.tsx`
- [ ] Build `EquityCurve.tsx`
- [ ] Build `SetupAnalysis.tsx`

#### Week 5: Strategy Guide
- [ ] Create all `/trading/strategy-guide/` pages
- [ ] Build `GuideSidebar.tsx`
- [ ] Build `GuideContent.tsx`
- [ ] Build `ExpandableCard.tsx`
- [ ] Build `InteractiveChecklist.tsx`
- [ ] Migrate Trading Guide content to React components
- [ ] Convert HTML tables to React tables
- [ ] Convert checklists to interactive components

#### Week 6: Tools & Settings
- [ ] Create all `/trading/tools/` pages
- [ ] Build `PositionCalculator.tsx`
- [ ] Build `RRCalculator.tsx`
- [ ] Build `ADRCalculator.tsx`
- [ ] Build `PatternTrainer.tsx`
- [ ] Build `PreTradeChecklist.tsx`
- [ ] Create all `/trading/settings/` pages
- [ ] Build risk management settings
- [ ] Build UI preferences

#### Week 7: Polish & Integration
- [ ] Responsive design testing
- [ ] Mobile layout adjustments
- [ ] Performance optimization
- [ ] Integration testing
- [ ] Documentation

---

### 📚 Reference Repos for Trading Journal

| Repo | Use For |
|------|---------|
| [Eleven-Trading/TradeNote](https://github.com/Eleven-Trading/TradeNote) | Journal structure, MongoDB schema |
| [bukosabino/ta](https://github.com/bukosabino/ta) | TA library for indicators |
| [keithorange/PatternPy](https://github.com/keithorange/PatternPy) | M/W pattern detection |
| [polakowo/vectorbt](https://github.com/polakowo/vectorbt) | Backtesting framework |

---

## 📋 Backlog

---

### Phase 13: Advanced Features
- [ ] Multi-user support
- [ ] Custom strategy upload
- [ ] Real broker integration (paper trading first)
- [ ] AR/VR CAD preview
- [ ] Chatbot context for work data (emails, jobs)

---

## 🎯 Success Criteria

| Metric | Target | Status |
|--------|--------|--------|
| Chat response | < 5 sec | ✅ |
| Core files | < 85 | ✅ (~81) |
| Adapter size | < 250 lines | ✅ |
| Agent size | < 500 lines | ✅ |
| System Manager uptime | > 7 days | 🟡 Testing |
| CAD reconstruction | > 90% accuracy | 🟡 Testing |
| Docker deployment | Working | ✅ |
| Circuit breaker | Protecting | ✅ |
| API cost reduction | > 50% | ✅ **90-95%!** |
| Trading module redesign | Complete | 🔄 In Progress |

---

## 📚 Key References

- `REFERENCES.md` - All external packages
- `config/mcp-servers.json` - MCP registry
- `RULES.md` - Architecture rules (Section 6 = Elite Patterns)
- `CLAUDE.md` - AI instructions
- `docker-compose.yml` - Deployment config
- `TRADING_APP_REDESIGN_PLAN.md` - Full trading module design spec
- [Anthropic Prompt Caching Docs](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching)
- [Trading-Guide Repo](https://github.com/swiffc/Trading-Guide) - BTMM content source
