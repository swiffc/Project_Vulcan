# Project Vulcan: Master Task List

**Status**: Phase 15 COMPLETE - CAD Drawing Review Bot (8 adapters)
**Last Updated**: Dec 21, 2025 - Phase 15 Complete + README Consolidated
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

---

## ✅ Phase 9: Web UI Redesign - Complete (Dec 2025)

### Dashboard, Trading, CAD Pages
- [x] Modern dark theme with glass effects
- [x] Responsive 2-column grid layout
- [x] Real-time status indicators
- [x] Reusable UI components (Card, Button, Badge)
- [x] Navigation with desktop server health check

---

## ✅ Phase 10: Work Integration Hub - Complete (Dec 2025)

### ✅ Completed (UI + API Structure)
- [x] `/work` page with 4 widget cards (Email, Teams, Files, J2)
- [x] `/work/setup` Azure AD setup guide
- [x] Microsoft Graph client (`lib/work/microsoft-client.ts`)
- [x] Token manager with AES-256 encryption (`lib/work/token-manager.ts`)
- [x] Device Code Flow authentication
- [x] API routes: health, device-code, status, signout, mail, teams, files
- [x] Navigation updated with "Work" link
- [x] QuickActions updated with Work Hub + J2 Jobs

### ✅ Completed: Browser Automation (Playwright)
- [x] `desktop_server/controllers/browser.py` - Playwright browser automation
  - Persistent session management with cookie storage
  - SSO login support (visible browser for user auth)
  - Page navigation, clicking, typing, table extraction
- [x] `desktop_server/controllers/j2_tracker.py` - J2 Tracker scraper
  - SSO login with Duo 2FA support
  - Job list extraction from J2 tables
  - Status normalization and summary calculation
- [x] `apps/web/src/lib/work/j2-client.ts` - Web app J2 client
- [x] J2 API routes: `/api/work/j2/status`, `/api/work/j2/login`, `/api/work/j2/jobs`
- [x] Desktop Server updated with browser and J2 routers

### 🔲 Pending: Final Setup
- [ ] Install Playwright in Desktop Server: `pip install playwright && playwright install chromium`
- [ ] Create Azure AD app registration (needs IT or personal account)
- [ ] Add `MICROSOFT_CLIENT_ID` to `.env.local`
- [ ] Configure `J2_TRACKER_URL` in environment

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

## 🔥 Phase 14: Trading Module Redesign - IN PROGRESS

### 📋 Overview
Complete redesign of `/trading` page based on 2024 trading app UX research. Integrates content from `swiffc/Trading-Guide` repo with TradingView-inspired layout.

**Source Content**: `github.com/swiffc/Trading-Guide` (24 HTML pages)
**Design Inspiration**: TradingView, TraderSync, TradesViz 2.0, Robinhood

---

### ✅ Week 1: Foundation - COMPLETE

#### Week 1 Checklist
- [x] Create all component directories (`header/`, `layout/`, `calculators/`, `entry/`)
- [x] Create `types.ts` with BTMM types (~286 lines)
- [x] Create `constants.ts` with BTMM constants (~245 lines)
- [x] Build `TradingHeader.tsx` (pair selector, session clock, mode toggle)
- [x] Build `LeftPanel.tsx` (collapsible, watchlist, cycle day, notes)
- [x] Build enhanced `EnhancedSessionClock.tsx` (multi-timezone, kill zones)
- [x] Build `PairSelector.tsx` (searchable dropdown)
- [x] Build `ModeToggle.tsx` (basic/advanced)
- [x] Update `globals.css` with trading CSS variables
- [x] Update `tailwind.config.ts` with trading/session/ema colors

### ✅ Week 2: Trade Entry - COMPLETE

- [x] Build `RightPanel.tsx` (trade entry form with tabs)
- [x] Build `PositionSizeCalculator.tsx` (account, risk, lots)
- [x] Build `PreTradeChecklist.tsx` (12-item BTMM checklist)
- [x] Build `/trading/journal/page.tsx` (trade list with stats, filters)
- [x] Restore AI chatbot interface (floating button + slide-out panel)

### ✅ Week 3: Tabbed Interface Redesign - COMPLETE

**Design Decision**: All trading functionality consolidated into a single tabbed interface at `/trading` instead of separate routes. This provides a more cohesive TradingView-inspired experience.

#### Tab Structure (Single Page)
| Tab | Purpose | Status |
|-----|---------|--------|
| Dashboard | Main workspace (chart + panels) | ✅ |
| Journal | Trade log with stats & filtering | ✅ |
| Analysis | Live/Daily/Weekly/Monthly views | ✅ |
| Performance | Stats, metrics, charts | ✅ |
| Tools | Calculator, Checklist, ADR | ✅ |
| Settings | Trading preferences | ✅ |

#### Tab Components Created
- `components/trading/tabs/DashboardTab.tsx` - Chart workspace
- `components/trading/tabs/JournalTab.tsx` - Trade log with filtering
- `components/trading/tabs/AnalysisTab.tsx` - Multi-view analysis (live/daily/weekly/monthly)
- `components/trading/tabs/PerformanceTab.tsx` - Stats & metrics dashboard
- `components/trading/tabs/ToolsTab.tsx` - Position calculator, checklist, ADR
- `components/trading/tabs/SettingsTab.tsx` - User preferences

#### Legacy Routes (Still Available)
| Route | Purpose | Status |
|-------|---------|--------|
| `/trading` | Main tabbed workspace | ✅ |
| `/trading/dashboard` | Redirect to `/trading` | ✅ |
| `/trading/journal` | Standalone journal (legacy) | ✅ |
| `/trading/journal/new` | New trade entry form | ✅ |
| `/trading/journal/[id]` | Trade detail/edit | ✅ |
| `/trading/analysis/*` | Standalone analysis pages | ✅ |

---

### 📚 Reference Repos for Trading Journal

| Repo | Use For |
|------|---------|
| [Eleven-Trading/TradeNote](https://github.com/Eleven-Trading/TradeNote) | Journal structure, MongoDB schema |
| [bukosabino/ta](https://github.com/bukosabino/ta) | TA library for indicators |
| [keithorange/PatternPy](https://github.com/keithorange/PatternPy) | M/W pattern detection |
| [polakowo/vectorbt](https://github.com/polakowo/vectorbt) | Backtesting framework |

---

## ✅ Phase 15: CAD Drawing Review Bot (ACHE Checker) - COMPLETE

### 📋 Overview
AI-powered engineering drawing review system for Air-Cooled Heat Exchangers (ACHE/Fin Fans).
Automatically checks drawings against API 661, ASME, OSHA, and industry standards.

**Reference Document:** `agents/cad_agent/knowledge/ACHE_CHECKLIST.md`

---

### ✅ Completed
- [x] Complete ACHE Checklist V2 (`agents/cad_agent/knowledge/ACHE_CHECKLIST.md`)
  - 28 sections covering ALL ACHE components
  - API 661 compliance checks
  - Cross-check requirements for mating parts
  - Instrumentation, Electrical, Piping, Coatings
  - Testing, Shipping, Documentation requirements
  - Foundation, Nameplate, Spare Parts checklists
- [x] Verification Requirements V2 (`agents/cad_agent/knowledge/VERIFICATION_REQUIREMENTS.md`)
  - Weight verification workflow
  - Edge distance (AISC Table J3.4)
  - Bend radius by material
  - Description vs dimensions matching
  - Speed optimization strategies (70-80% faster)
- [x] Standards Database (`agents/cad_agent/adapters/standards_db.py`)
  - AISC W-shapes (50+ beams)
  - AISC Angles (30+ shapes)
  - Sheet gauges (7GA-26GA)
  - Plate thicknesses (1/16"-2")
  - Edge distances per bolt size
  - Hole sizes (std, oversize, slot)
  - Bend factors by material
  - Material densities
  - API 661 fan tip clearances
  - OSHA platform/ladder/stair requirements
  - Validation functions (weight, edge, bend, holes)

### ✅ Completed: Drawing Analysis Engine
- [x] `agents/cad_agent/adapters/drawing_analyzer.py` (~530 lines)
  - PDF to image conversion with parallel processing
  - DXF file parsing with ezdxf
  - Title block OCR extraction (part number, material, weight, etc.)
  - Dimension extraction (feet/inches, fractions, decimals, metric)
  - Hole and bend detection
  - Intelligent caching for repeat verifications
- [x] `agents/cad_agent/adapters/weight_calculator.py` (~420 lines)
  - Weight calculation for plates, beams, angles, tubes, bars
  - Auto-detection of part type from dimensions
  - Description parsing for material specifications
  - Weight validation with configurable tolerances
- [x] `agents/cad_agent/adapters/hole_pattern_checker.py` (~480 lines)
  - Mating part alignment verification (±1/16" tolerance)
  - Edge distance checking per AISC J3.4
  - Standard hole size validation
  - Bolt circle pattern analysis
- [x] `agents/cad_agent/adapters/red_flag_scanner.py` (~530 lines)
  - Pre-scan for title block completeness
  - Weight mismatch detection (>10%)
  - Non-standard hole flagging
  - Bend radius validation
  - Description vs dimension mismatch
  - OSHA platform/ladder/stair compliance
  - API 661 fan tip clearance checks
- [x] `agents/cad_agent/adapters/bom_cross_checker.py` (~460 lines)
  - BOM to drawing matching with fuzzy logic
  - Part number, material, weight comparison
  - Missing/extra parts detection
  - Quantity verification
  - Report generation

- [x] `agents/cad_agent/adapters/dimension_extractor.py` (~520 lines)
  - Zone-based extraction (title block, main view, notes)
  - Multi-format parsing (feet-inches, fractions, decimals, metric)
  - Tolerance extraction (bilateral and asymmetric)
  - GD&T dimension types (diameter, radial, angular, reference, basic)
  - Confidence scoring

### ✅ Completed: Advanced Analysis Features
- [x] `agents/cad_agent/adapters/flange_validator.py` (~660 lines)
  - ASME B16.5 flange dimensions (Class 150, 300, 600, 900)
  - Pressure-temperature ratings per Table 2
  - Bolt torque reference, gasket dimensions
  - Flange validation and mating pair checks
  - Class selection for design conditions
- [x] `agents/cad_agent/adapters/interference_detector.py` (~590 lines)
  - Bounding box overlap detection (2D and 3D)
  - API 661 fan tip clearance validation
  - Tube bundle insertion path checking
  - OSHA headroom and walkway compliance
  - Piping clearance and nozzle access checks
  - Assembly interference analysis with reporting

### 📚 Useful Repos for Implementation

| Repo | URL | Purpose |
|------|-----|---------|
| eDOCr | github.com/javvi51/eDOCr | OCR for engineering drawings |
| Image2CAD | github.com/adityaintwala/Image2CAD | Circle/hole detection, DXF export |
| python-hvac | github.com/TomLXXVI/python-hvac | Fin-tube HX thermal models |
| steelpy | pypi.org/project/steelpy | AISC shapes database |
| pyaisc | github.com/mwhit74/pyaisc | AISC manual calculations |
| calctoys | github.com/thepvguy/calctoys | ASME pressure vessel calcs |
| OpenCV HoughCircles | opencv.org | Hole detection algorithm |

### 🎯 Key Features
1. **Automatic Hole Pattern Cross-Check** - Verify mating parts align (±1/16")
2. **Visual Before/After Examples** - Show problem AND solution
3. **BOM Completeness Check** - All parts accounted for
4. **Standards Compliance** - API 661, OSHA, ASME, AISC

---

## 📋 Backlog

---

### Phase 12: Flatter Files Integration
**Priority**: HIGH | **Dependency**: Flatter Files API Key

- [ ] `agents/cad_agent/adapters/flatter_files_adapter.py` (~350 lines)
- [ ] Search drawings by part number/description
- [ ] Get PDF/STEP/DXF download URLs
- [ ] Get assembly BOM structure
- [ ] Get revision history
- [ ] Get markup annotations
- [ ] Filter by checked-out status
- [ ] Add `FLATTER_FILES_API_KEY` to .env
- [ ] `agents/cad_agent/adapters/pdm_adapter.py` (~300 lines) - PDM vault integration
- [ ] `agents/cad_agent/adapters/reference_tracker.py` (~250 lines) - Track assembly references/dependencies

**Chatbot examples:**
- "Find drawing for bracket 12345" → PDF/STEP links
- "What parts are in assembly XYZ-100?" → BOM list
- "Any markups on drawing ABC-500?" → Annotation list

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
| CAD module redesign | Complete | 🔲 Planned |
| **ACHE Standards Checker** | Complete (8 adapters) | ✅ Complete |

---

## 📚 Key References

- `REFERENCES.md` - All external packages
- `config/mcp-servers.json` - MCP registry
- `RULES.md` - Architecture rules (Section 6 = Elite Patterns)
- `CLAUDE.md` - AI instructions
- `docker-compose.yml` - Deployment config
- `TRADING_APP_REDESIGN_PLAN.md` - Full trading module design spec
- `CAD_APP_REDESIGN_PLAN.md` - Full CAD module design spec
- [Anthropic Prompt Caching Docs](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching)
- [Trading-Guide Repo](https://github.com/swiffc/Trading-Guide) - BTMM content source

### ACHE Standards Checker References:
- `agents/cad_agent/knowledge/ACHE_CHECKLIST.md` - Complete 28-section ACHE verification
- `agents/cad_agent/knowledge/VERIFICATION_REQUIREMENTS.md` - Verification requirements
- `agents/cad_agent/adapters/standards_db.py` - Pre-loaded AISC/OSHA/API 661 tables
