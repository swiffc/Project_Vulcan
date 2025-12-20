# Project Vulcan: Master Task List

**Status**: PRD Alignment In-Progress  
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

## 🚀 Active Sprint

### Trading Bot Conversion (Python)
- [ ] Convert `trading-agent/src/*.ts` → Python adapters
- [ ] `strategy_adapter.py` - Wraps strategy logic
- [ ] `tradingview_bridge.py` - TradingView control via MCP
- [ ] `journal_adapter.py` - Memory Brain integration

### Inspector Bot Enhancement
- [ ] `audit_adapter.py` - LLM-as-Judge wrapper
- [ ] `report_bridge.py` - PDF/Markdown report generation

---

## 📋 Backlog

### Phase 5: Integration
- [ ] CrewAI orchestrator adapter
- [ ] End-to-end workflow tests
- [ ] Health dashboard UI

### Phase 6: Polish
- [ ] Voice command adapter (Whisper)
- [ ] Mobile PWA wrapper
- [ ] Metrics visualization

---

## 📁 Current Adapters & Bridges

| File | Type | Wraps | Lines |
|------|------|-------|-------|
| `agents/system-manager/adapter.py` | Adapter | APScheduler, psutil | ~80 |
| `agents/cad-agent/adapters/pdf_bridge.py` | Bridge | pytesseract, pdf2image | ~90 |
| `agents/cad-agent/adapters/ecn_adapter.py` | Adapter | chromadb | ~70 |
| `agents/cad-agent/adapters/gdrive_bridge.py` | Bridge | google-api / MCP | ~85 |
| `desktop-server/com/solidworks_com.py` | Adapter | pywin32 COM | ~200 |
| `desktop-server/com/inventor_com.py` | Adapter | pywin32 COM | ~160 |

---

## 🎯 Success Criteria

| Metric | Target |
|--------|--------|
| Chat response | < 5 sec |
| Core files | < 50 |
| Adapter size | < 100 lines |
| System Manager uptime | > 7 days |
| CAD reconstruction | > 90% accuracy |

---

## 📚 Key References

- `REFERENCES.md` - All external packages
- `config/mcp-servers.json` - MCP registry
- `RULES.md` - Architecture rules
- `CLAUDE.md` - AI instructions
