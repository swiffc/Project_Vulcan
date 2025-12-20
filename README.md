# 🔥 Project Vulcan

**Personal AI Operating System** — A unified web chatbot that physically controls your Windows PC for Trading and CAD workflows.

[![Render](https://img.shields.io/badge/Deployed%20on-Render-46E3B7)](https://render.com)
[![MCP](https://img.shields.io/badge/Protocol-MCP-blue)](https://modelcontextprotocol.org)
[![License](https://img.shields.io/badge/License-Private-red)]()

---

## 🎯 What This Is

One chat interface that controls your entire digital life, powered by LLM-driven orchestration:

| Agent | Purpose | Status |
|-------|---------|--------|
| **Trading Bot** | Controls TradingView, analyzes charts, executes paper trades, generates PDF reports | 🟢 Active |
| **CAD Agent AI** | Parses drawings, builds SolidWorks/Inventor models, tracks ECN revisions | 🔄 Building |
| **Inspector Bot** | LLM-as-Judge auditing, grades outputs, generates improvement reports | 🟢 Active |
| **System Manager** | Background daemon: scheduling, backups, health monitoring, metrics | 🔄 Building |

All agents share a **Desktop Control Server** (MCP) that physically operates your Windows PC + **Memory Brain** for persistent RAG knowledge.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         RENDER.COM (Cloud)                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    VULCAN CHAT WINDOW (Next.js)                      │   │
│  │                      Accessible from anywhere                        │   │
│  └─────────────────────────────────┬───────────────────────────────────┘   │
│                                    │                                        │
│  ┌─────────────────────────────────▼───────────────────────────────────┐   │
│  │                   TASK ROUTER / ORCHESTRATOR                         │   │
│  │                      (CrewAI-powered routing)                        │   │
│  └─────────────────────────────────┬───────────────────────────────────┘   │
│                                    │                                        │
│     ┌──────────────┬───────────────┼───────────────┬──────────────┐        │
│     ▼              ▼               ▼               ▼              ▼        │
│ ┌────────┐   ┌──────────┐   ┌───────────┐   ┌──────────┐   ┌─────────┐   │
│ │Trading │   │CAD Agent │   │ Inspector │   │  System  │   │ Memory  │   │
│ │  Bot   │   │    AI    │   │    Bot    │   │ Manager  │   │  Brain  │   │
│ └────────┘   └──────────┘   └───────────┘   └──────────┘   └─────────┘   │
│                                    │                                        │
└────────────────────────────────────┼────────────────────────────────────────┘
                                     │
                               TAILSCALE VPN
                                     │
┌────────────────────────────────────▼────────────────────────────────────────┐
│                          YOUR WINDOWS PC                                     │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                  MCP DESKTOP CONTROL SERVER                           │  │
│  │   🖱️ Mouse   ⌨️ Keyboard   📸 Screenshot   📹 Replay   ⚖️ Verifier    │  │
│  └──────────────────────────────────┬───────────────────────────────────┘  │
│                                     │                                       │
│            ┌────────────────────────┼────────────────────────┐             │
│            ▼                        ▼                        ▼             │
│     ┌─────────────┐          ┌─────────────┐          ┌─────────────┐     │
│     │ TradingView │          │ SolidWorks  │          │  Inventor   │     │
│     │  (Desktop)  │          │   AutoCAD   │          │   Bentley   │     │
│     └─────────────┘          └─────────────┘          └─────────────┘     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### 1. Start Desktop Control Server (Local Windows PC)

```bash
cd desktop-server
START_MCP.bat
```

This starts the MCP server with tools for mouse, keyboard, screen capture, and more.

### 2. Start Memory Brain (Local or Cloud)

```bash
cd mcp-servers/memory-vec
./start.sh
```

### 3. Deploy to Render (Cloud)

```bash
# Push to GitHub, Render auto-deploys via render.yaml
git push origin main
```

### 4. Access Chat Interface

Navigate to your Render URL or `http://localhost:3000` for local development.

---

## 📁 Project Structure

```
Project_Vulcan/
├── agents/
│   ├── trading-bot/           # Trading analysis & execution
│   │   ├── src/
│   │   │   ├── strategy_engine.py
│   │   │   ├── chart_analyzer.py
│   │   │   ├── journal.py
│   │   │   └── tradingview.py
│   │   ├── knowledge/
│   │   └── templates/
│   ├── cad-agent-ai/          # PDF→CAD pipeline
│   │   ├── src/
│   │   │   ├── pdf_parser.py
│   │   │   ├── param_generator.py
│   │   │   ├── cad_executor.py
│   │   │   └── ecn_tracker.py
│   │   └── templates/
│   ├── inspector-bot/         # LLM-as-Judge auditing
│   │   ├── src/
│   │   │   ├── judge.py
│   │   │   └── report_generator.py
│   │   └── templates/
│   ├── system-manager/        # Background daemon
│   │   ├── src/
│   │   │   ├── scheduler.py
│   │   │   ├── backup.py
│   │   │   ├── health_monitor.py
│   │   │   └── metrics_collector.py
│   │   └── config/
│   └── core/                  # Shared libraries
│       ├── llm.py
│       ├── logging.py
│       └── patterns/
├── apps/
│   └── web/                   # Next.js chat interface
│       ├── src/
│       │   ├── app/
│       │   ├── components/
│       │   └── lib/
│       └── package.json
├── mcp-servers/               # MCP server configurations
│   ├── memory-vec/
│   ├── google-drive/
│   └── cad-mcp/
├── desktop-server/            # Local Windows MCP
│   ├── mcp_server.py
│   ├── controllers/
│   └── com/
├── config/
│   ├── strategies/
│   └── cad-standards/
├── storage/                   # gitignored local data
├── docs/
│   ├── prds/
│   └── architecture/
├── CLAUDE.md                  # AI assistant instructions
├── RULES.md                   # Engineering guidelines
├── REFERENCES.md              # External dependencies
├── task.md                    # Master task list
├── render.yaml                # Render deployment config
└── README.md
```

---

## 🤖 Agent Capabilities

### Trading Bot

```
User: "Create this week's EUR/USD plan"
```

1. Analyzes TradingView charts using ICT/BTMM/Quarterly Theory
2. Identifies high-probability setups
3. Generates PDF trading plan with screenshots
4. Logs to Memory Brain for future reference

### CAD Agent AI

```
User: "Build assembly from this drawing" + [PDF upload]
```

1. OCR extracts dimensions and GD&T from PDF
2. Generates feature parameters
3. Commands SolidWorks/Inventor via CAD-MCP
4. Tracks ECN revisions in Memory Brain
5. Exports STEP/PDF to Google Drive

### Inspector Bot

```
User: "Review my trades this week"
```

1. Queries Memory Brain for trade records
2. LLM analyzes each trade decision
3. Grades performance (A-F)
4. Generates improvement recommendations

### System Manager

Runs automatically in background:
- **2:00 AM**: Daily backup to Google Drive
- **Hourly**: Health check all services
- **Every 5 min**: Collect metrics
- **Friday 5 PM**: Weekly performance report

---

## 🔧 MCP Tools Available

### Desktop Server

| Tool | Description |
|------|-------------|
| `mouse_move(x, y)` | Move cursor to coordinates |
| `mouse_click(x, y, button)` | Click at position |
| `type_text(text)` | Type string |
| `press_key(key)` | Press keyboard key |
| `get_screen_info()` | Get resolution and mouse position |
| `start_recording()` | Begin screen recording |
| `stop_recording()` | End recording |
| `verify_visual_state(ref)` | Compare screen to reference image |

### Memory Brain

| Tool | Description |
|------|-------------|
| `memory_store(key, content)` | Store with embedding |
| `memory_search(query)` | Semantic search |
| `memory_query(filter)` | Structured query |

### Google Drive

| Tool | Description |
|------|-------------|
| `drive_upload(file, folder)` | Upload file |
| `drive_sync(local, remote)` | Sync directories |

---

## 📊 Data Schemas

### Trade Record

```json
{
  "id": "trade-001",
  "pair": "EURUSD",
  "session": "NY",
  "bias": "short",
  "setup_type": "Q2_manipulation",
  "entry": 1.0850,
  "stop_loss": 1.0880,
  "take_profit": 1.0790,
  "result": "win",
  "r_multiple": 2.0,
  "lesson": "Waited for proper displacement",
  "timestamp": "2025-12-20T13:15:00Z"
}
```

### CAD Job Record

```json
{
  "job_id": "CAD-00045",
  "input_pdf": "Project_Bracket.pdf",
  "parts_built": ["Flange_01", "Bracket_02", "Shaft_03"],
  "assembly_file": "Bracket_Assembly.SLDASM",
  "export_files": ["Bracket_Assembly.step", "Drawing.pdf"],
  "mass_properties": {"mass": 1.24, "units": "kg"},
  "ecn_history": ["ECN-100", "ECN-123"],
  "created": "2025-12-20T14:50:00Z"
}
```

---

## 🛡️ Safety Features

1. **Kill Switch**: Move mouse to top-left corner (0-10px) to immediately halt all automation
2. **Human-in-the-Loop**: High-stake actions require explicit approval
3. **Circuit Breaker**: Auto-stops if >3 trades in 1 minute
4. **Black Box Logging**: All decisions logged for audit

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [CLAUDE.md](CLAUDE.md) | AI assistant behavioral instructions |
| [RULES.md](RULES.md) | Engineering rules and architecture |
| [REFERENCES.md](REFERENCES.md) | External dependencies |
| [task.md](task.md) | Master task list and roadmap |
| [docs/prds/](docs/prds/) | Product requirement documents |

---

## 🎯 Success Metrics

| Metric | Target |
|--------|--------|
| Chat response time | < 5 seconds |
| Trading Bot reports | Automated daily/weekly |
| CAD reconstruction | > 90% accuracy |
| Inspector coherence | Clear problem/fix suggestions |
| System Manager uptime | > 7 days continuous |

---

## 🔗 References

- **MCP Protocol**: https://modelcontextprotocol.org
- **CAD-MCP**: https://github.com/daobataotie/CAD-MCP
- **Anthropic MCP Servers**: https://github.com/anthropics/mcp-servers
- **Render Docs**: https://render.com/docs

---

## 📄 License

Private project - All rights reserved.

---

**Built with 🔥 by Vulcan Team**
