# Project Vulcan: Master Task List

<<<<<<< HEAD
**Status**: Phase 8.5 ULTIMATE - Maximum Cost Optimized & Production Ready
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

---

## 📋 Backlog

### Phase 9: Advanced Features
- [ ] Multi-user support
- [ ] Custom strategy upload
- [ ] Real broker integration (paper trading first)
- [ ] AR/VR CAD preview

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
=======
**Status**: Strategic Rebuild In-Progress  
**Goal**: Unified AI Operating System (Trading, CAD, General) per PRD v1.0  
**Target**: Claude CLI / Render Cloud + Local Windows MCP

---

## 🎯 Current Sprint: Phase 1 - Infrastructure Foundation

### Active Tasks

- [ ] **1.1 Repository Restructure**
  - [ ] Rename `agents/trading-agent/` → `agents/trading-bot/`
  - [ ] Rename `agents/cad-agent/` → `agents/cad-agent-ai/`
  - [ ] Rename `agents/review-agent/` → `agents/inspector-bot/`
  - [ ] Create `agents/system-manager/` directory
  - [ ] Create `mcp-servers/` directory structure
  - [ ] Update all import paths

- [ ] **1.2 System Manager Skeleton**
  - [ ] Create `agents/system-manager/src/__init__.py`
  - [ ] Create `agents/system-manager/src/scheduler.py`
  - [ ] Create `agents/system-manager/src/backup.py`
  - [ ] Create `agents/system-manager/src/health_monitor.py`
  - [ ] Create `agents/system-manager/src/metrics_collector.py`
  - [ ] Create `agents/system-manager/src/main.py`
  - [ ] Create `agents/system-manager/requirements.txt`

- [ ] **1.3 MCP Server Configurations**
  - [ ] Create `mcp-servers/memory-vec/config.json`
  - [ ] Create `mcp-servers/memory-vec/start.sh`
  - [ ] Create `mcp-servers/google-drive/config.json`
  - [ ] Create `mcp-servers/google-drive/start.sh`
  - [ ] Create `mcp-servers/cad-mcp/config.json`

- [ ] **1.4 Render Deployment Update**
  - [ ] Update root `render.yaml` for multi-service
  - [ ] Add vulcan-orchestrator worker
  - [ ] Add vulcan-system-manager worker
  - [ ] Add vulcan-memory worker
  - [ ] Configure environment variables

---

## 📅 Full Roadmap (7-Week Plan)

### ✅ Completed Phases (Legacy)

#### Phase 1-3 (Original): Foundation, Agents, Observability
- [x] Unified Chatbot (Next.js)
- [x] MCP Server (Desktop Control)
- [x] Trading Agent (TypeScript - to be converted)
- [x] CAD Agent Blueprint
- [x] Review Agent / Judge
- [x] Briefing Agent
- [x] Black Box Logging
- [x] Visual Replay & Verifier
- [x] Watchdog Recovery

---

### 🚀 Phase 1: Infrastructure Foundation (Week 1)

- [ ] **1.1** Restructure repository to PRD spec
- [ ] **1.2** Create System Manager agent skeleton
- [ ] **1.3** Configure MCP server definitions
- [ ] **1.4** Update Render deployment (multi-service)
- [ ] **1.5** Update all requirements.txt files
- [ ] **1.6** Verify Tailscale connectivity

---

### 🚀 Phase 2: Trading Bot Upgrade (Week 2)

- [ ] **2.1** Convert Trading Agent TypeScript → Python
  - [ ] `strategy_engine.py` - ICT/BTMM/Quarterly Theory
  - [ ] `chart_analyzer.py` - LLM vision analysis
  - [ ] `journal.py` - Trade logging with RAG
  - [ ] `tradingview.py` - Desktop control bridge

- [ ] **2.2** Trading Strategy Configuration
  - [ ] Create `config/strategies/trading.json`
  - [ ] Define ICT rules
  - [ ] Define BTMM rules
  - [ ] Define Stacey Burke rules

- [ ] **2.3** Memory Integration
  - [ ] Connect journal to Memory Brain MCP
  - [ ] Implement trade recall queries
  - [ ] Test weekly stats aggregation

- [ ] **2.4** Testing
  - [ ] Unit tests for strategy engine
  - [ ] Integration test: Scan pair → Log trade

---

### 🚀 Phase 3: CAD Agent AI Build (Weeks 3-4)

- [ ] **3.1** PDF Parser Implementation
  - [ ] `pdf_parser.py` - pytesseract OCR
  - [ ] Dimension extraction regex
  - [ ] Title block parsing
  - [ ] Multi-page support

- [ ] **3.2** Parameter Generator
  - [ ] `param_generator.py` - Feature params from dimensions
  - [ ] GD&T symbol interpretation
  - [ ] Material property mapping

- [ ] **3.3** CAD Executor
  - [ ] `cad_executor.py` - CAD-MCP bridge
  - [ ] `ecn_tracker.py` - Revision history
  - [ ] SolidWorks adapter enhancement
  - [ ] Inventor adapter (new)

- [ ] **3.4** Memory Integration
  - [ ] Store all ECN records
  - [ ] Cumulative modification tracking
  - [ ] Part/Assembly history queries

- [ ] **3.5** Testing
  - [ ] Unit tests for PDF parser
  - [ ] Integration test: PDF → Part → Assembly
  - [ ] Accuracy validation (>90% target)

---

### 🚀 Phase 4: Inspector Bot & Memory Brain (Week 5)

- [ ] **4.1** Inspector Bot Enhancement
  - [ ] `judge.py` - Full LLM-as-Judge
  - [ ] Trade audit prompts
  - [ ] CAD audit prompts
  - [ ] Assembly audit prompts
  - [ ] `report_generator.py` - PDF/Markdown reports

- [ ] **4.2** Memory Brain MCP Server
  - [ ] Install chromadb
  - [ ] Configure embedding model
  - [ ] Implement `memory_store` tool
  - [ ] Implement `memory_search` tool
  - [ ] Implement `memory_query` tool

- [ ] **4.3** Testing
  - [ ] Test semantic search accuracy
  - [ ] Test recall for trade lessons
  - [ ] Test ECN history retrieval

---

### 🚀 Phase 5: System Manager & Google Drive (Week 6)

- [ ] **5.1** System Manager Implementation
  - [ ] Scheduler with cron jobs
  - [ ] Daily backup automation
  - [ ] Hourly health checks
  - [ ] Metrics collection (5-min interval)
  - [ ] Weekly report generation

- [ ] **5.2** Google Drive MCP Bridge
  - [ ] OAuth setup
  - [ ] `drive_upload` tool
  - [ ] `drive_sync` tool
  - [ ] Default folder configuration

- [ ] **5.3** Web Interface Upgrade
  - [ ] Streaming responses
  - [ ] Status indicators (📊📈✅🛑)
  - [ ] Quick action buttons
  - [ ] Dashboard page

- [ ] **5.4** Testing
  - [ ] 7-day uptime test
  - [ ] Backup verification
  - [ ] Drive sync validation

---

### 🚀 Phase 6: Integration & Polish (Week 7)

- [ ] **6.1** Full Integration Testing
  - [ ] Trading workflow: Chat → Scan → Trade → Journal → Report
  - [ ] CAD workflow: PDF Upload → Parts → Assembly → Export → Drive
  - [ ] Cross-agent: Trading setup influences CAD priority

- [ ] **6.2** Performance Testing
  - [ ] Chat response < 5 seconds
  - [ ] CAD MCP + Drive upload stress test
  - [ ] < 2% failure rate at 100 runs

- [ ] **6.3** Documentation Update
  - [ ] README.md - Full rewrite
  - [ ] RULES.md - Update for new architecture
  - [ ] CLAUDE.md - AI instructions update
  - [ ] REFERENCES.md - Add new MCP servers
  - [ ] Create deployment runbook

- [ ] **6.4** Final Checklist
  - [ ] All agents respond < 5 seconds
  - [ ] Trading Bot: Automated daily/weekly reports
  - [ ] CAD Agent: >90% reconstruction accuracy
  - [ ] Inspector Bot: Coherent problem/fix suggestions
  - [ ] System Manager: >7 days continuous operation

---

## 🎯 Success Criteria (from PRD)

| Metric | Target | Current |
|--------|--------|---------|
| Chat response time | < 5 sec | TBD |
| Trading Bot PDF automation | Daily/Weekly | ❌ Manual |
| CAD reconstruction accuracy | > 90% | ❌ Not built |
| Inspector coherence | Clear fixes | 🟡 Basic |
| System Manager uptime | > 7 days | ❌ Not built |
| Memory recall accuracy | > 85% | 🟡 Basic |

---

## 🧩 Stretch Goals (Post-MVP)

- [ ] Voice Commands via Speech MCP
- [ ] Mobile Dashboard (PWA)
- [ ] AR CAD Viewer
- [ ] CNC/3D Printer Bridge MCP
- [ ] Multi-user support
>>>>>>> 3bb774a741d326374e3176484ea79e8601906724

---

## 📚 Key References

<<<<<<< HEAD
- `REFERENCES.md` - All external packages
- `config/mcp-servers.json` - MCP registry
- `RULES.md` - Architecture rules (Section 6 = Elite Patterns)
- `CLAUDE.md` - AI instructions
- `docker-compose.yml` - Deployment config
- [Anthropic Prompt Caching Docs](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching)

---

## 📁 Files That Need to Sync

### New Files
- `agents/core/redis_adapter.py`
- `agents/core/model_router.py`
- `agents/core/token_optimizer.py`
- `agents/core/token_optimizer_v2.py`
- `task.md`

### Updated Files
- `core/llm.py`
- `docker-compose.yml`
- `render.yaml`
- `requirements.txt`
=======
- **PRD**: `docs/prds/PROJECT-VULCAN-PRD.md`
- **MCP Docs**: https://modelcontextprotocol.org
- **CAD-MCP**: https://github.com/daobataotie/CAD-MCP
- **Anthropic MCP Servers**: https://github.com/anthropics/mcp-servers
- **Render IaC**: https://render.com/docs/infrastructure-as-code

---

**Last Updated**: December 20, 2025  
**Next Review**: End of Week 1
>>>>>>> 3bb774a741d326374e3176484ea79e8601906724
