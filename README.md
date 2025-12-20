# 🔥 Project Vulcan

**Personal AI Operating System** — A unified web chatbot that physically controls your Windows PC for Trading and CAD workflows.

[![Render](https://img.shields.io/badge/Deployed%20on-Render-46E3B7)](https://render.com)
[![MCP](https://img.shields.io/badge/Protocol-MCP-blue)](https://modelcontextprotocol.org)

---

## 🎯 What This Is

One chat interface that controls your entire digital life, powered by LLM-driven orchestration:

| Agent | Purpose | Status |
|-------|---------|--------|
| **Trading Bot** | Controls TradingView, analyzes charts, executes paper trades, generates PDF reports | 🟢 Active |
| **CAD Agent AI** | Parses drawings, builds SolidWorks/Inventor models, tracks ECN revisions | 🔄 Building |
| **Inspector Bot** | LLM-as-Judge auditing, grades outputs, generates improvement reports | 🟢 Active |
| **System Manager** | Background daemon: scheduling, backups, health monitoring, metrics | 🟢 Active |

All agents share a **Desktop Control Server** (MCP) that physically operates your Windows PC + **Memory Brain** for persistent RAG knowledge.

### ✅ Core & Connectivity

- **Unified Chat Interface** (Next.js) accessible from anywhere via **Tailscale**.
- **Orchestrator** intelligent routing of user intent to specialized agents.
- **MCP Server** (`desktop_server`) exposing standard tools for Mouse, Keyboard, Screen, and Logs.

### ✅ Advanced Intelligence

- **RAG Memory**: Integrated memory system stores trades and lessons for future context.
- **Weekly Review**: Automated performance analysis agent.
- **Trade Logging**: Structured logging of every trade setup and result.

### ✅ Observability & Verification

- **Black Box Logging**: JSONL audit trails for every decision (`agents/core/logging.py`).
- **Visual Replay**: On-demand screen recording tool (`controllers/recorder.py`).
- **Visual Verification**: CAD "Visual Diffing" to compare screen state against reference images.
- **LLM-as-a-Judge**: Automated auditor that critiques agent decisions.

### ✅ Cost Optimization (Phase 8.5 ULTIMATE)

- **Redis Cache**: Skip API entirely for repeated queries (100% savings on hits)
- **Model Router**: Use Haiku for simple tasks (92% cheaper)
- **Token Optimizer**: Trim history, compress prompts (20-40% savings)
- **Anthropic Prompt Caching**: 90% savings on system prompts
- **Batch API**: 50% off for non-urgent tasks

**Total potential savings: 90-95%**

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

---

## 🚀 Quick Start

### 1. Start Desktop Control Server (Local Windows PC)

```bash
cd desktop_server
START_MCP.bat
```

### 2. Deploy to Render (Cloud)

```bash
git push origin main  # Auto-deploys via render.yaml
```

### 3. Access Chat Interface

Navigate to your Render URL or `http://localhost:3000` for local development.

---

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
│   ├── cad_agent/          # CAD automation
│   ├── inspector_bot/      # Weekly Review & Judge
│   └── core/              # Shared libs (logging, llm, cost optimization)
├── core/                  # Shared Root Libs (memory, llm)
├── storage/               # Logs, Recordings, Judgments
└── task.md               # Master Todo List
```

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [CLAUDE.md](CLAUDE.md) | AI assistant behavioral instructions |
| [RULES.md](RULES.md) | Engineering rules and architecture |
| [REFERENCES.md](REFERENCES.md) | External dependencies |
| [task.md](task.md) | Master task list and roadmap |

---

## 🎯 Success Criteria

| Metric | Target | Status |
|--------|--------|--------|
| Chat response | < 5 sec | ✅ |
| API cost reduction | > 50% | ✅ **90-95%!** |
| Docker deployment | Working | ✅ |
| System Manager uptime | > 7 days | 🟡 Testing |
| CAD reconstruction | > 90% accuracy | 🟡 Testing |

---

**Built with 🔥 by Vulcan Team**
