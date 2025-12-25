# Project Vulcan Reference Documentation

This document maintains all external dependencies and architectural references for the Project Vulcan agentic ecosystem.

## Installed Packages (via pip/npm - NOT in project folder)

### Desktop Server (Python)

| Package | Version | Purpose | Install Command |
|---------|---------|---------|-----------------|
| fastapi | 0.109.0 | Web framework for API | `pip install fastapi` |
| uvicorn | 0.27.0 | ASGI server | `pip install uvicorn[standard]` |
| pyautogui | 0.9.54 | Mouse/keyboard automation | `pip install pyautogui` |
| pywin32 | 306 | Windows COM for CAD control | `pip install pywin32` |
| pillow | 10.2.0 | Image processing | `pip install pillow` |
| mss | 9.0.1 | Fast screenshots | `pip install mss` |
| pytesseract | 0.3.10 | OCR text recognition | `pip install pytesseract` |
| pdf2image | 1.16.3 | PDF to image conversion | `pip install pdf2image` |
| pyyaml | 6.0.1 | Config file parsing | `pip install pyyaml` |

### System Manager (Python)

| Package | Version | Purpose | Install Command |
|---------|---------|---------|-----------------|
| APScheduler | 3.10.4 | Job scheduling | `pip install APScheduler` |
| psutil | 5.9.7 | System metrics | `pip install psutil` |
| aiohttp | 3.9.1 | Async HTTP for health checks | `pip install aiohttp` |

### Google Drive Integration (Python)

| Package | Version | Purpose | Install Command |
|---------|---------|---------|-----------------|
| google-api-python-client | 2.111.0 | Drive API | `pip install google-api-python-client` |
| google-auth | 2.25.2 | Authentication | `pip install google-auth` |

### Memory & RAG (Python)

| Package | Version | Purpose | Install Command |
|---------|---------|---------|-----------------|
| chromadb | 0.4.22 | Vector database (local) | `pip install chromadb` |
| sentence-transformers | 2.2.2 | Embedding models | `pip install sentence-transformers` |

### AI Agent & Research (Python)

| Package | Version | Purpose | Install Command |
|---------|---------|---------|-----------------|
| claude-agent-sdk | latest | Claude Agent SDK (official) | `pip install claude-agent-sdk` |
| tavily-python | 0.5.0 | Web search API | `pip install tavily-python` |
| duckduckgo_search | 8.1.1 | Free web search fallback | `pip install duckduckgo_search` |
| langchain-anthropic | 1.2.0 | LangChain + Claude | `pip install langchain-anthropic` |

### Monitoring & Observability (Python)

| Package | Version | Purpose | Install Command |
|---------|---------|---------|-----------------|
| sentry-sdk | 1.40.0 | Error tracking and performance monitoring | `pip install sentry-sdk` |
| python-json-logger | 2.0.7 | JSON structured logging | `pip install python-json-logger` |

### Database (Python)

| Package | Version | Purpose | Install Command |
|---------|---------|---------|-----------------|
| psycopg2-binary | 2.9.9 | PostgreSQL adapter | `pip install psycopg2-binary` |

### Web Interface (Node.js)

| Package | Version | Purpose | Install Command |
|---------|---------|---------|-----------------|
| @anthropic-ai/sdk | ^0.30.0 | Claude API client | `npm install @anthropic-ai/sdk` |
| @anthropic-ai/claude-code | ^2.0.75 | Claude Agent SDK (Node.js) | `npm install @anthropic-ai/claude-code` |
| next | 14.2.0 | React framework | `npm install next` |
| react | 18.3.0 | UI library | `npm install react` |
| axios | 1.7.0 | HTTP client | `npm install axios` |
| @sentry/nextjs | ^8.0.0 | Sentry error tracking for Next.js | `npm install @sentry/nextjs` |
| @prisma/client | ^5.0.0 | Prisma database ORM client | `npm install @prisma/client` |
| prisma | ^5.0.0 | Prisma CLI and migrations | `npm install -D prisma` |

---

## MCP Servers (Reference Only - Not Cloned)

| Server | Purpose | Reference | Our Adapter |
|--------|---------|-----------|-------------|
| desktop-control | Windows PC control | Built-in | `desktop_server/mcp_server.py` |
| memory-vec | Vector RAG | chromadb | `controllers/memory.py` |
| mcp-gdrive | Google Drive | [wong2/mcp-gdrive-adapter](https://github.com/wong2/mcp-gdrive-adapter) | `agents/cad_agent/adapters/gdrive_bridge.py` |
| CAD-MCP | SolidWorks/Inventor | [daobataotie/CAD-MCP](https://github.com/daobataotie/CAD-MCP) | `desktop_server/com/*.py` |
| microsoft-mcp | Outlook/Calendar/OneDrive | [elyxlz/microsoft-mcp](https://github.com/elyxlz/microsoft-mcp) | MCP Direct (Claude Desktop) |

---

## External Services

| Service | Purpose | Documentation |
|---------|---------|---------------|
| Anthropic Claude API | AI brain for agents | [docs.anthropic.com](https://docs.anthropic.com) |
| Ollama | Local LLM fallback | [ollama.ai](https://ollama.ai) |
| Tailscale | Secure VPN connection | [tailscale.com](https://tailscale.com/kb) |
| Render.com | Cloud hosting for web UI | [render.com](https://render.com/docs) |
| TradingView | Chart platform (automated via UI) | [tradingview.com](https://www.tradingview.com) |
| Google Drive | File backup & sync | [developers.google.com/drive](https://developers.google.com/drive) |

---

## Adapter & Bridge Pattern

### What is an Adapter?
```python
# 50-100 lines that wraps an external package
class SchedulerAdapter:
    def __init__(self):
        from apscheduler.schedulers.asyncio import AsyncIOScheduler  # Lazy import
        self._scheduler = AsyncIOScheduler()
```

### What is a Bridge?
```python
# Connects to MCP server OR falls back to direct API
class GDriveBridge:
    async def upload(self, path):
        if self.mcp:  # Use MCP if available
            return await self.mcp.call_tool("drive_upload", {...})
        else:  # Direct API fallback
            return self._direct_upload(path)
```

### Key Rules
1. **Never clone repos** - `pip install` + adapter
2. **Lazy imports** - Only load heavy packages when needed
3. **Max 100 lines** - If longer, split into multiple adapters
4. **Document here** - Every external dependency in this file

---

## System Requirements

### Windows PC (Desktop Server)

| Requirement | Details |
|-------------|---------|
| OS | Windows 10/11 |
| Python | 3.10+ |
| Tesseract OCR | Required for PDF OCR |
| Poppler | Required for pdf2image |
| Tailscale | For remote access |
| SolidWorks | For CAD automation (licensed) |
| Inventor | For CAD automation (licensed) |

### Tesseract OCR Installation
```bash
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
# Add to PATH: C:\Program Files\Tesseract-OCR
```

### Poppler Installation (for pdf2image)
```bash
# Download from: https://github.com/oschwartz10612/poppler-windows/releases
# Add to PATH: C:\poppler\bin
```

---

## GitHub Repos (REFERENCE ONLY - Not Cloned)

### AI Agent & Research Repos

| Repo | Purpose | Key Files We Reference |
|------|---------|------------------------|
| [claude-agent-sdk-python](https://github.com/anthropics/claude-agent-sdk-python) | Official Claude Agent SDK | Agent patterns |
| [claude-agent-sdk-demos](https://github.com/anthropics/claude-agent-sdk-demos) | Research agent patterns | Multi-agent coordination |
| [agent-browse](https://github.com/browserbase/agent-browse) | Claude + Stagehand browser | Web automation |
| [wshobson/agents](https://github.com/wshobson/agents) | 99 Claude Code agents | Production patterns |
| [RAG_Techniques](https://github.com/NirDiamant/RAG_Techniques) | Advanced RAG patterns | Self-querying, graph RAG |
| [GenAI_Agents](https://github.com/NirDiamant/GenAI_Agents) | Agent building tutorials | Implementation guides |
| [DeepAgent](https://github.com/RUC-NLPIR/DeepAgent) | 16,000+ tool discovery | Dynamic tooling |
| [Awesome-Personalized-RAG-Agent](https://github.com/Applied-Machine-Learning-Lab/Awesome-Personalized-RAG-Agent) | Personalized RAG | Learning patterns |

### Desktop & Automation Repos

| Repo | Purpose | Key Files We Reference |
|------|---------|------------------------|
| [pyautogui](https://github.com/asweigart/pyautogui) | Desktop automation | API patterns |
| [APScheduler](https://github.com/agronholm/apscheduler) | Job scheduling | AsyncIOScheduler usage |
| [CAD-MCP](https://github.com/daobataotie/CAD-MCP) | CAD control patterns | Tool definitions |
| [mcp-gdrive](https://github.com/wong2/mcp-gdrive-adapter) | Drive MCP | Server patterns |
| [microsoft-mcp](https://github.com/elyxlz/microsoft-mcp) | M365 Outlook/Calendar/OneDrive | Device Code auth |
| [TradingView-API](https://github.com/Mathieu2301/TradingView-API) | Realtime data, backtesting | Unofficial TV API |
| [tradingview-webhooks-bot](https://github.com/robswc/tradingview-webhooks-bot) | Webhook alert receiver | Flask framework |
| [pySldWrap](https://github.com/ThomasNeve/pySldWrap) | SolidWorks Python wrapper | pywin32 COM |
| [pySW](https://github.com/kalyanpi4/pySW) | SW dimension extraction | Drawing parser |
| [swtoolkit](https://github.com/Glutenberg/swtoolkit) | SW automation scripts | Batch operations |
| [pySolidWorks](https://github.com/mklanac/pySolidWorks) | SW FEA/DXF export | Full API wrapper |
| [SolidWrap](https://github.com/SeanYeatts/SolidWrap) | SW + PDM unified | 🏆 Best choice |
| [PyInventor](https://github.com/AndrewOriani/PyInventor) | Inventor API wrapper | Parametric automation |
| [InventorTools](https://github.com/mickp/InventorTools) | Inventor COM scripts | Batch operations |
| [playwright-python](https://github.com/microsoft/playwright-python) | Browser automation | J2 Tracker scraping |
| [crawlee-python](https://github.com/apify/crawlee-python) | Web scraping for AI | RAG extraction |
| [github-mcp-server](https://github.com/github/github-mcp-server) | Official GitHub MCP | Issues, PRs, Actions |
| [n8n-mcp](https://github.com/czlonkowski/n8n-mcp) | n8n workflow builder | 545 automation nodes |
| [claude-context](https://github.com/zilliztech/claude-context) | Semantic code search | Codebase RAG |

---

## Trading Knowledge Sources

| Source | Type | Content |
|--------|------|---------|
| [ICT Trading Concepts](https://tradingrage.com/learn/ict-trading-concepts-101) | Article | Order Blocks, FVG, OTE |
| [BTMM Strategy](https://howtotrade.com/trading-strategies/beat-the-market-maker/) | Article | Three-day cycle, Stop Hunt |
| [Quarterly Theory](https://www.writofinance.com/quarterly-theory-smc-and-ict/) | Article | AMDX model, True Open |
| [Stacey Burke Trading](https://theforexgeek.com/stacey-burke-trading-strategy/) | Article | ACB setups, Session trading |

---

## Architecture Principles

Based on RULES.md:

1. **No Cloning** - Use pip/npm packages, not cloned repos
2. **Thin Adapters** - 50-100 line wrappers around external APIs
3. **Max 50 Core Files** - Keep project lightweight
4. **Remote References** - Document, don't copy
5. **Desktop Server is Sacred** - All physical control through one server
6. **RAG Pipeline** - Augment queries with relevant past context
7. **HITL for Updates** - Strategy changes require user approval
8. **Lazy Imports** - Only load heavy packages when needed
9. **MCP First** - Use MCP servers when available, direct API as fallback

---

## GitHub Repo Wrappers (Rule 2: Read-Only via API)

| Repository Alias | Purpose | Key Files We Fetch |
|------------------|---------|--------------------|
| **adafruit** | [adafruit/Adafruit_CAD_Parts](https://github.com/adafruit/Adafruit_CAD_Parts) | Electronic components, PCBs | `*.step`, `*.f3d` |
| **openscad** | [tanius/openscad-models](https://github.com/tanius/openscad-models) | Parametric algorithms | `*.scad` |
| **bolt** | [bolt-design/standard-parts](https://github.com/bolt-design/standard-parts) | Standard Fasteners | `ISO 4014` |
| **ublox** | [u-blox/3D-Step-Models-Library](https://github.com/u-blox/3D-Step-Models-Library) | Mechanical Parts (STEP) | `*.step` |
| **kicad_3d** | [GeorgeIoak/3D_Component_Models](https://github.com/GeorgeIoak/3D_Component_Models) | Electronic Components | `*.step` |
| **pipecad** | [eryar/PipeCAD](https://github.com/eryar/PipeCAD) | Piping Components (Ref) | `*.cpp`, `*.h` |
| **freecad_lib** | [FreeCAD/FreeCAD-library](https://github.com/FreeCAD/FreeCAD-library) | General Mechanical Parts | `*.step`, `*.fcstd` |
| **kicad_alt** | [dhaillant/kicad-3dmodels](https://github.com/dhaillant/kicad-3dmodels) | Electronics (VRML/STEP) | `*.step` |
