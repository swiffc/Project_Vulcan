# Project Vulcan: Master Task List

**Status**: Phase 6 Complete - Ready for Production
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

---

## ✅ Completed Sprint

### Trading Bot Conversion (Python)
- [x] Convert `trading-agent/src/*.ts` → Python adapters
- [x] `strategy_adapter.py` - Wraps strategy logic (~96 lines)
- [x] `tradingview_bridge.py` - TradingView control via MCP (~150 lines)
- [x] `journal_adapter.py` - Memory Brain integration (~109 lines)

### Inspector Bot Enhancement
- [x] `audit_adapter.py` - LLM-as-Judge wrapper (~141 lines)
- [x] `report_bridge.py` - PDF/Markdown report generation (~200 lines)

---

## ✅ Phase 5: Integration - Complete

- [x] CrewAI orchestrator adapter (`agents/core/orchestrator_adapter.py` ~200 lines)
- [x] End-to-end workflow tests (`tests/test_workflows.py` ~235 lines)
- [x] Health dashboard API (`agents/core/health_dashboard.py` ~200 lines)

---

## ✅ Phase 6: Polish - Complete

- [x] Voice command adapter (`agents/core/voice_adapter.py` ~190 lines)
- [x] Mobile PWA wrapper (`apps/web/public/manifest.json`, `sw.js`, layout updates)
- [x] Metrics visualization (`agents/core/metrics_viz.py` ~200 lines)

---

## 📋 Backlog

### Phase 7: Production Hardening
- [ ] Rate limiting middleware
- [ ] Auth adapter (JWT/OAuth)
- [ ] Monitoring alerts (PagerDuty/Slack)

---

## 📁 Current Adapters & Bridges

| File | Type | Wraps | Lines |
|------|------|-------|-------|
| `agents/system-manager/adapter.py` | Adapter | APScheduler, psutil | ~80 |
| `agents/cad-agent/adapters/pdf_bridge.py` | Bridge | pytesseract, pdf2image | ~90 |
| `agents/cad-agent/adapters/ecn_adapter.py` | Adapter | chromadb | ~70 |
| `agents/cad-agent/adapters/gdrive_bridge.py` | Bridge | google-api / MCP | ~85 |
| `agents/trading-agent/adapters/strategy_adapter.py` | Adapter | ICT/BTMM logic | ~96 |
| `agents/trading-agent/adapters/journal_adapter.py` | Adapter | Memory Brain | ~109 |
| `agents/trading-agent/adapters/tradingview_bridge.py` | Bridge | MCP Desktop | ~150 |
| `agents/inspector-bot/adapters/audit_adapter.py` | Adapter | LLM-as-Judge | ~141 |
| `agents/inspector-bot/adapters/report_bridge.py` | Bridge | reportlab/markdown | ~200 |
| `desktop-server/com/solidworks_com.py` | Adapter | pywin32 COM | ~200 |
| `desktop-server/com/inventor_com.py` | Adapter | pywin32 COM | ~160 |
| `agents/core/orchestrator_adapter.py` | Adapter | CrewAI routing | ~200 |
| `agents/core/health_dashboard.py` | Bridge | httpx, health checks | ~200 |
| `agents/core/voice_adapter.py` | Adapter | Whisper (local/API) | ~190 |
| `agents/core/metrics_viz.py` | Bridge | Dashboard charts | ~200 |

---

## 🎯 Success Criteria

| Metric | Target |
|--------|--------|
| Chat response | < 5 sec |
| Core files | < 80 |
| Adapter size | < 250 lines |
| Agent size | < 500 lines |
| System Manager uptime | > 7 days |
| CAD reconstruction | > 90% accuracy |

---

## 📚 Key References

- `REFERENCES.md` - All external packages
- `config/mcp-servers.json` - MCP registry
- `RULES.md` - Architecture rules
- `CLAUDE.md` - AI instructions
