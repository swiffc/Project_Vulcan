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
| pyyaml | 6.0.1 | Config file parsing | `pip install pyyaml` |
| python-multipart | 0.0.6 | Form data parsing | `pip install python-multipart` |

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

## External Services

| Service | Purpose | Documentation |
|---------|---------|---------------|
| Anthropic Claude API | AI brain for agents | [docs.anthropic.com](https://docs.anthropic.com) |
| Ollama | Local LLM fallback | [ollama.ai](https://ollama.ai) |
| Tailscale | Secure VPN connection | [tailscale.com](https://tailscale.com/kb) |
| Render.com | Cloud hosting for web UI | [render.com](https://render.com/docs) |
| TradingView | Chart platform (automated via UI) | [tradingview.com](https://www.tradingview.com) |

---

## System Requirements

### Windows PC (Desktop Server)

| Requirement | Details |
|-------------|---------|
| OS | Windows 10/11 |
| Python | 3.10+ |
| Tesseract OCR | Required for OCR features |
| Tailscale | For remote access |
| SolidWorks | For CAD automation (licensed) |
| Inventor | For CAD automation (licensed) |

### Tesseract OCR Installation

```bash
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
# Add to PATH: C:\Program Files\Tesseract-OCR
```

---

## GitHub Repos (REFERENCE ONLY - Not Cloned)

These are reference repositories for learning patterns. We do NOT clone them.

| Repo | Stars | Purpose | Key Patterns |
|------|-------|---------|--------------|
| [pyautogui](https://github.com/asweigart/pyautogui) | 9k+ | Desktop automation | Mouse/keyboard control |
| [mss](https://github.com/BoboTiG/python-mss) | 1k+ | Fast screenshots | Cross-platform capture |
| [claude-task-master](https://github.com/eyaltoledano/claude-task-master) | N/A | AI Task Management | PRD-led workflow and rules |

---

## CAD COM References

### SolidWorks COM API

```python
# ProgID: "SldWorks.Application"
# Documentation: SolidWorks API Help (installed with SW)
# Key interfaces:
#   - ISldWorks (main application)
#   - IModelDoc2 (part/assembly document)
#   - ISketchManager (sketch operations)
#   - IFeatureManager (features like extrude)
```

### Inventor COM API

```python
# ProgID: "Inventor.Application"
# Documentation: Inventor API Help (installed with Inventor)
# Key interfaces:
#   - Application (main application)
#   - PartDocument (part documents)
#   - Sketch (sketch operations)
#   - PartFeatures (features like extrude)
```

---

## Trading Knowledge Sources

| Source | Type | Content |
|--------|------|---------|
| [ICT Trading Concepts](https://tradingrage.com/learn/ict-trading-concepts-101) | Article | Order Blocks, FVG, OTE |
| [BTMM Strategy](https://howtotrade.com/trading-strategies/beat-the-market-maker/) | Article | Three-day cycle, Stop Hunt |
| [Quarterly Theory](https://www.writofinance.com/quarterly-theory-smc-and-ict/) | Article | AMDX model, True Open |
| [Stacey Burke Trading](https://theforexgeek.com/stacey-burke-trading-strategy/) | Article | ACB setups, Session trading |

---

## Memory & RAG References

| Resource | Type | Purpose |
|----------|------|---------|
| [Chroma Docs](https://docs.trychroma.com/) | Documentation | Vector DB setup and queries |
| [Sentence Transformers](https://www.sbert.net/) | Documentation | Embedding model selection |
| [all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) | Model | Default embedding model (22MB, fast) |

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
