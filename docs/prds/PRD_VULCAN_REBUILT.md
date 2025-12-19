# Rebuilt Product Requirements Document (PRD) for Project_Vulcan

This rebuilt PRD incorporates the latest specifications for Project_Vulcan as your all-in-one autonomous AI agent. It handles professional mechanical CAD design (SolidWorks and Inventor automation) and paper day trading (synchronizing ICT, BTMM, Quarterly Theory cycles, and Stacey Burke methods under a Quarterly Theory framework).

---

## 1. Product Overview

- **Name**: Project_Vulcan
- **Objective**: An always-on AI agent that automates CAD tasks (e.g., building flanges from natural language per JSON strategies) and executes paper trades (e.g., scanning GBP/USD for aligned setups in Q2 manipulation phases).
- **Target User**: Mechanical designer and trader accessing via web/phone for hands-free operation.
- **Success Metrics**: 95% uptime, <500ms responses, accurate designs/trades (tracked in journals).

## 2. User Stories

- **As a designer**: "Build a 6-inch ANSI flange with 8 bolts per strategy.json" → Bot automates SolidWorks, saves file, logs with screenshots.
- **As a trader**: "Scan GBP/USD for Q2 setup" → Bot checks alignments, executes paper trade, records lesson.
- **As a user**: Access 24/7 from phone, review journals without local PC on.

## 3. Functional Requirements

### CAD Integration
- Connect via MCP/Desktop Server over Tailscale.
- Automate: New part, sketch/extrude/revolve/save (.SLDPRT/.IPT).
- Use JSON strategies (GitHub-hosted) for rules (e.g., tolerances, materials).

### Trading Integration

- Sync under Quarterly Theory (daily quarters: Q1 accumulation, Q2 manipulation, etc.).
- Align methods: Only trade if ICT + BTMM + Burke confirm.
- Paper trading: TradingView demo via pyautogui.
- Risk: 1% per trade, focus London/NY overlaps.

### Journaling & Learning

- **Persistent Tracking**: Track full history of modifications to parts, assemblies, and drawings, including revision details (e.g., ECN sequences, change logs with file versions, and cumulative updates).
- **Excel Journals (pywin32)**: Logs, P&L, screenshots, and lessons.
- **Memory (SQLite/ChromaDB)**: Stores insights, histories, and revisions; reference for future actions (e.g., recall prior ECNs on a drawing to apply new changes without overwriting).

### Autonomy & UX Elite

- **Streaming & Rich Messaging**: Word-by-word streaming responses with markdown formatting (bold, tables, code blocks).
- **Visual Proof**: Automatic inline screenshot attachments for every physical action (CAD builds, trade entries).
- **Interactive Controls**: Command suggestion buttons and Voice Input (Hands-free) for desk-side operations.
- **Multimodal Context**: Upload sketches or screenshots for the bot to interpret and act upon.

## 4. Technical Implementation

- **Architecture**: Next.js (Chatbot) → CrewAI (Orchestrator) → Domain Agents (Trading/CAD) → Python Desktop Server (Physical Control).
- **Communication**: Tailscale VPN for secure cross-device access.
- **Integrations**: MCP (Model Context Protocol) for tool-based execution.

## 5. Build & Deployment Plan

- **Phase 1**: Foundation – Desktop Server, MCP setup, Environment configuration.
- **Phase 2**: Trading Agent – TradingView automation, strategy-sync.
- **Phase 3**: CAD Agent – SolidWorks/Inventor adapters, revision tracking system.
- **Phase 4**: Advanced Intelligence – Proactive briefings, Multi-modal CAD creation, RAG over journals.
- **Phase 5**: Orchestration & Elite Polish – CrewAI supervisor, persistent memory integration.

## 7. Future Intelligence & UX Roadmap

### 🏁 Quick Wins ( UX Polish)
- Streaming response loop (Next.js SSE).
- Status emoji markers (✅, 📈, 🛑).
- Inline file previews for CAD drawings.

### 🧠 Advanced Intelligence

- **Voice Mode**: Whisper/TTS loop for natural conversation.
- **Global RAG**: Semantic search over years of trading/design data.
- **Mobile Wrapper**: Native-feel UI via PWA.

## 6. AI-Friendly Engineering Standards

- **Monorepo & Boundaries**: Maintain clear separation between `apps/`, `agents/`, and `desktop-server/`.
- **Configuration Over Code**: Changeable logic (CAD strategies, trade plans) must reside in external JSON/Markdown files.
- **Single Responsibility**: Maintain a strictly modular architecture; files must stay under 300 lines.
- **Lazy Execution**: Use on-demand imports for heavy physical-control libraries (`pywin32`, `pyautogui`).
- **SSOT Management**: Centralized task tracking in the project-root `task.md`.
- **Pruning**: Regular ritual to remove unused adapters and dead documentation.

---

> [!IMPORTANT]
> All external logic (CAD API examples, trading libraries) must be reference-wrapped to maintain the "No Cloning" rule. One job, one file.
