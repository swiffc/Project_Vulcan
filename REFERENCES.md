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

### Web Interface (Node.js)

| Package | Version | Purpose | Install Command |
|---------|---------|---------|-----------------|
| @anthropic-ai/sdk | ^0.30.0 | Claude API client | `npm install @anthropic-ai/sdk` |
| next | 14.2.0 | React framework | `npm install next` |
| react | 18.3.0 | UI library | `npm install react` |
| axios | 1.7.0 | HTTP client | `npm install axios` |

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
