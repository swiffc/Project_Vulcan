# Project Vulcan

**Personal AI Operating System** - A unified web chatbot that physically controls your Windows PC.

## What This Is

One chat interface that controls your entire digital life, powered by LLM-driven orchestration:
- **Trading Agent** - Controls TradingView, analyzes charts, executes paper trades (+ RAG Memory)
- **CAD Agent** - Controls SolidWorks, Inventor, AutoCAD, Bentley
- **General Assistant** - Route actions, general help

All agents share a **Desktop Control Server** (Mcp Server) that physically operates your Windows PC.

## Current Capabilities

### ✅ Core & Connectivity
- **Unified Chat Interface** (Next.js) accessible from anywhere via **Tailscale**.
- **Orchestrator** intelligent routing of user intent to specialized agents.
- **MCP Server** (`desktop_server`) exposing standard tools for Mouse, Keyboard, Screen, and Logs.

### ✅ Advanced Intelligence (Phase 1 & 2)
- **RAG Memory**: Integrated memory system stores trades and lessons for future context (`journal.ts`).
- **Weekly Review**: Automated performance analysis agent (`agents/review_agent`).
- **Trade Logging**: Structured logging of every trade setup and result.

### ✅ Observability & Verification (Phase 3)
- **Black Box Logging**: JSONL audit trails for every decision (`agents/core/logging.py`).
- **Visual Replay**: On-demand screen recording tool (`controllers/recorder.py`).
- **Visual Verification**: CAD "Visual Diffing" to compare screen state against reference images (`controllers/verifier.py`).
- **LLM-as-a-Judge**: Automated auditor that critiques agent decisions (`agents/review_agent/src/judge.py`).

## Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│                    RENDER.COM (Cloud)                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              WEB CHATBOT (Next.js)                   │   │
│  │             Accessible from anywhere                 │   │
│  └─────────────────────────┬───────────────────────────┘   │
│                            │                                │
│  ┌─────────────────────────▼───────────────────────────┐   │
│  │    ORCHESTRATOR + AGENTS (Trading, CAD, General)    │   │
│  └─────────────────────────┬───────────────────────────┘   │
│                            │                                │
└────────────────────────────┼────────────────────────────────┘
                             │
                       TAILSCALE VPN
                             │
 ┌───────────────────────────▼────────────────────────────────┐
 │                   YOUR WINDOWS PC                           │
 │  ┌─────────────────────────────────────────────────────┐   │
 │  │           DESKTOP CONTROL SERVER (MCP)              │   │
 │  │  🖱️ Mouse  ⌨️ Keyboard  📸 Screenshot  📹 Replay    │   │
 │  │  ⚖️ Verifier  🧠 Vector Memory                        │   │
 │  └─────────────────────────┬───────────────────────────┘   │
 │                            │                                │
 │      ┌─────────────────────┼─────────────────────┐         │
 │      ▼                     ▼                     ▼         │
 │  TradingView          SolidWorks            System         │
 └─────────────────────────────────────────────────────────────┘
```

## Quick Start

### 1. Start Desktop Control Server
The standardized MCP server handles all desktop interactions.

```bash
cd desktop_server
START_MCP.bat
```

This will:
- Set up the Python virtual environment
- Install dependencies (including `mcp`, `opencv`, `anthropic`)
- Start the `mcp_server.py`

### 2. Available Agents & Scripts

*   **Weekly Review Agent**: 
    *   Run Manually: `agents/review_agent/run_review.bat`
    *   Schedule: `agents/review_agent/SCHEDULE_REVIEW.bat` (Fridays @ 5PM)

*   **Judge Agent**:
    *   Run Audit: `agents/review_agent/run_judge.bat`

## Project Structure

```text
Project_Vulcan/
├── desktop_server/          # MCP Server & Controllers
│   ├── mcp_server.py       # Main MCP Interface
│   ├── controllers/        # recorder, verifier, mouse, etc.
│   └── requirements.txt    # Python dependencies
├── apps/web/              # Next.js Chat Interface & Orchestrator
├── agents/                # Specialized Agents
│   ├── trading_agent/      # Journaling & logic
│   ├── review_agent/       # Weekly Review & Judge
│   └── core/              # Shared libs (logging, llm)
├── core/                  # Shared Root Libs (memory, llm)
├── storage/               # Logs, Recordings, Judgments
└── task.md               # Master Todo List
```

## Documentation

- **[CLAUDE.md](CLAUDE.md)**: AI Assistant instructions and patterns.
- **[RULES.md](RULES.md)**: Comprehensive engineering rules and architectural guidelines.
- **[task.md](task.md)**: Current roadmap and outstanding items.

## License

Private project - All rights reserved.
