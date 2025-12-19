# Project Vulcan: Master Task List

**Status**: Phase 3 (Scaling) In-Progress
**Goal**: Unified AI Operating System (Trading, CAD, General)

---

## ✅ Completed Phases (Summary)

### Phase 1: Foundation (Core & Connectivity)

- **Unified Chatbot**: Next.js frontend with Tailscale-secured access.
- **MCP Server**: Standardized desktop control (Mouse, Keyboard, Screen).
- **Orchestrator**: Intelligent intent routing (Trading vs CAD vs General).
- **Security**: Kill Switch, basic logging, local-only execution.

### Phase 2: Specialized Agents

- **Trading Agent**: Journaling, RAG Memory, Strategy JSON config.
- **CAD Agent**: SolidWorks COM integration blueprint.
- (Life Agent deprecated in favor of General Assistant).

### Phase 3: Scaling (Observability & Verification)

- **Black Box Logging**: Structured JSONL logs (`agents/core/logging.py`).
- **Visual Replay**: On-demand screen recorder (`desktop-server/controllers/recorder.py`).
- **Visual Verification**: CAD diffing engine (`desktop-server/controllers/verifier.py`).
- **LLM-as-a-Judge**: Automated audit agent (`agents/review-agent/src/judge.py`).

---

## 🚀 Active Roadmap

### Phase 3: Scaling & Optimization (Final Item)

- [x] **Recovery** (Rule 12 Extension) [x]
  - [x] Implement Automated Workspace Recovery (`desktop-server/watchdog.py`).

---

### Phase 4: Advanced Intelligence [ ]

- [x] **Daily/Weekly Briefings** [x]
  - [x] Create proactive bot that pushes reports to the user.
- [ ] **Multi-Modal Input**
  - [ ] Photo-to-CAD: Allow uploading a sketch -> Generate SolidWorks part.
- [ ] **Global RAG Search**
  - [ ] "Ask My Journal": Complex queries over years of trade/project data.
- [ ] **Voice Mode**
  - [ ] Full Whisper (STT) -> LLM -> TTS conversation loop.
- [ ] **Mobile Wrapper**
  - [ ] Smart PWA/Capacitor app for native mobile feel.

---

### Phase 5: Master Orchestration & Elite Polish [ ]

- [ ] **CrewAI Orchestrator**
  - [ ] Define `TradingCrew` (Analyst + Executor + Risk Manager).
  - [ ] Define `DesignCrew` (Architect + Drafter + Reviewer).
- [ ] **Final Integration**
  - [ ] System-wide "Flange-to-Trade" validation test (End-to-End).
  - [ ] Dashboard health analytics visualization.
