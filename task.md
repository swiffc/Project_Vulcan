# Project Vulcan: Master Task List

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

---

## 📚 Key References

- **PRD**: `docs/prds/PROJECT-VULCAN-PRD.md`
- **MCP Docs**: https://modelcontextprotocol.org
- **CAD-MCP**: https://github.com/daobataotie/CAD-MCP
- **Anthropic MCP Servers**: https://github.com/anthropics/mcp-servers
- **Render IaC**: https://render.com/docs/infrastructure-as-code

---

**Last Updated**: December 20, 2025  
**Next Review**: End of Week 1
