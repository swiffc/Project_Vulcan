# Project Vulcan: Unified Master Task List

> [!IMPORTANT]
> This is the single source of truth for Project Vulcan. It combines the rule restoration history, the technical roadmap from the Elite Task List, and the scaling optimization tasks.

---

## Phase 0: Restoration & Rule Enhancement [x]

- [x] **Rule Reversion**: Re-created `RULES.md`, deleted `CLAUDE.md` (legacy), updated `README` & `REFERENCES`.
- [x] **Rule Enhancement**: Researched safety/orchestration, added Rules 8-12 to `RULES.md`.
- [x] **SSOT Policy**: Added Rule 13 (No Duplication) and consolidated all task lists into root `task.md`.
- [x] **AI Manual**: Updated `CLAUDE.md` to enforce project root task management.
- [x] **PRD Rebuild**: Created `docs/prds/PRD_VULCAN_REBUILT.md` with ECN tracking and memory support.

## Phase 1: Foundation & Core Infrastructure [x]

- [x] Create and Verify Rebuilt PRD (with Memory/ECN support)
- [x] **Desktop Server** (completed in previous session)
  - FastAPI server with kill switch
  - Mouse, keyboard, screen, window controllers
  - SolidWorks and Inventor COM adapters
- [x] **Initialize Frontend Workspace** (`apps/web`)
  - [x] Created Next.js 14 app with App Router, TypeScript
  - [x] Glassmorphism theme with Tailwind CSS
  - [x] Chat component with streaming SSE support
  - [x] Chat component with streaming SSE support
  - [x] Orchestrator for agent routing (Trading/CAD)
  - [x] Claude API client with Ollama fallback
  - [x] Desktop server proxy client
- [x] **Connectivity & Security** [x]
  - [x] Configure Tailscale and Security Protocols. (Logic in `server.py` and `run.bat`)
  - [x] Create `render.yaml` Blueprint for Cloud Infrastructure.
  - [x] Draft PRD-002: Cloud Infrastructure & Deployment.
  - [x] Setup Docker/Render deployment hooks. (Implemented in `render.yaml` and `Dockerfile`)

## Phase 1.5: Elite Patterns Implementation [x]

- [x] **The Queue** (Desktop Server)
  - [x] Implement `asyncio.Queue` in `desktop-server/server.py`.
  - [x] Create `/queue/add` and `/queue/status` endpoints.
- [x] **The Circuit Breaker** (Agents Core)
  - [x] Create `agents/core/patterns/circuit_breaker.py`.
  - [x] Implement error counting and auto-reset logic.
- [x] **The Digital Twin** (Strategies)
  - [x] Create `strategies/schema.py` for lightweight validations.
- [x] **MCP Standardization** (Desktop Server)
  - [x] Research `fastmcp` or `mcp-python-sdk` for SSE support.
  - [x] Refactor `server.py` endpoints to match MCP tool definitions (Implemented `mcp_server.py`).

## Phase 1.6: Memory & RAG System (PRD-001) [x]

- [x] **Chroma Setup**
  - [x] Add `chromadb` and `sentence-transformers` to `requirements.txt`
  - [x] Create `core/memory/__init__.py`
  - [x] Create `core/memory/chroma_store.py` (~140 lines)
  - [x] Create `core/memory/embeddings.py` (~45 lines)
  - [x] Create `config/memory.yaml`

- [x] **RAG Engine**
  - [x] Create `core/memory/rag_engine.py` (~140 lines)
  - [x] Create `core/memory/ingest.py` (~170 lines)
  - [x] Implement `augment_prompt()` method
  - [x] Implement TradeIngestor, LessonIngestor, AnalysisIngestor, CADIngestor

- [x] **Weekly Review Agent**
  - [x] Create `agents/review-agent/src/weekly_review.py` (~230 lines)
  - [x] Create `agents/review-agent/src/__init__.py`
  - [x] Create `agents/review-agent/templates/weekly_summary.md`
  - [x] Implement statistics calculation (by setup, day, session)
  - [x] Implement pattern identification
  - [x] Implement strategy JSON update (with HITL)

- [x] **Integration** (Next Phase) [x]
  - [x] Integrate memory with Trading Agent (`journal.ts`)
  - [x] Add trade logging to memory after each trade (`logTrade`)
  - [x] Add RAG to orchestrator query pipeline (`augmentSystemPrompt` in `orchestrator.ts`)
  - [x] Schedule weekly review (Created `schedule_review.bat`)

## Phase 1.7: UX Elite & Quick Wins [x]

- [x] **Streaming Responses**: SSE streaming in `apps/web/src/app/api/chat/route.ts`
- [x] **Rich Formatting**: ReactMarkdown with emoji status markers in `ChatMessage.tsx`
- [x] **Auto-Attached Screenshots**: Screenshot attachment support in chat API
- [x] **Quick Command Buttons**: `QuickCommands.tsx` with preset actions
- [x] **Voice Input**: Web Speech API integration in `ChatInput.tsx`

## Phase 2: Technical Intelligence & Domain Agents [x]

- [x] **Trading Agent** (`agents/trading-agent/src/`)
  - [x] `index.ts` - Main agent with scanPair, executePaperTrade, logTrade
  - [x] `tradingview-control.ts` - Chart navigation, timeframes, screenshots
  - [x] `analysis.ts` - ICT/BTMM/Burke/Quarterly Theory setup detection
  - [x] `journal.ts` - Trade logging to memory, weekly review
- [x] **CAD Agent** (`agents/cad-agent/src/`)
  - [x] `index.ts` - Main agent with executeCommand, buildFlange
  - [x] `cad-control.ts` - SolidWorks/Inventor COM control
  - [x] `command-parser.ts` - Natural language to CAD operations
- [x] **Memory Integration**
  - [x] `desktop-server/controllers/memory.py` - REST API for RAG
  - [x] `apps/web/src/lib/memory-client.ts` - Web client for memory

## Phase 2: AI-Optimization & Maintenance [x]

- [x] **Enforce No-Duplication / Update-Only Policy** (Rule 13)
- [x] **Implement Monorepo Structure** (apps/, agents/, desktop-server/)
- [x] **Establish Configuration-over-Code for Strategies**
- [x] **Creation of .ai/CONTEXT.md for AI Assistants**
- [x] **Setup Pruning Ritual & Dependency Pinning Rules**

## Phase 3: Scaling & Optimization [ ]

- [ ] **Observability**
  - Implement "Black Box" Decision Logging.
  - Setup Visual Replay/Video recording for high-stake actions.
- [ ] **Verification**
  - Setup Visual Diffing for CAD Verification.
  - Integrate "LLM-as-a-Judge" Review Loop (Rule 11).
- [ ] **Recovery**
  - Build Automated Workspace Recovery (Rule 12 ext.).

## Phase 4: Advanced Intelligence [ ]

- [ ] **Daily/Weekly Briefings**: Proactive bot reports on designs/trades.
- [ ] **Multi-Modal Input**: Photo-to-CAD (Upload sketch → building part).
- [ ] **Global RAG Search**: Ask complex questions over years of journal data.
- [ ] **Voice Mode**: Full Whisper/TTS conversation loop.
- [ ] **Mobile Wrapper**: PWA/Capacitor for iOS/Android feel.

## Phase 5: Master Orchestration & Elite Polish [ ]

- [ ] **CrewAI Orchestrator**
  - Define `TradingCrew` and `DesignCrew` with specific agent roles.
- [ ] **Final Integration**
  - System-wide "Flange-to-Trade" validation test.
  - Dashboard health analytics.
