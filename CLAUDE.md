# CLAUDE.md - AI Operating Instructions

This file contains specific behavioral instructions for AI assistants (Claude, Cursor, etc.) working on Project Vulcan.

---

## 🎯 Project Context

**Vulcan** is a Personal AI Operating System that physically controls Windows PC for Trading and CAD workflows. Key components:

| Component | Purpose | Location |
|-----------|---------|----------|
| Trading Bot | Chart analysis, trade execution, journaling | `agents/trading-bot/` |
| CAD Agent AI | PDF→CAD pipeline, ECN tracking | `agents/cad-agent-ai/` |
| Inspector Bot | LLM-as-Judge auditing | `agents/inspector-bot/` |
| System Manager | Background daemon (David's Worker) | `agents/system-manager/` |
| Desktop Server | MCP for physical control | `desktop-server/` |
| Memory Brain | Persistent RAG knowledge | `mcp-servers/memory-vec/` |
| Web Interface | Next.js chat UI | `apps/web/` |

---

## 🛠️ Development Workflow

### 1. PRD First
If the user asks for a feature, first look for or create a PRD in `docs/prds/`. The main project PRD is `PROJECT-VULCAN-PRD.md`.

### 2. Task Management
Maintain `task.md` in the **project root** as the single source of truth. **DO NOT** create duplicate files.

### 3. Research Spikes
Conduct a spike (web search + docs) before proposing code. Check:
- MCP Protocol docs: https://modelcontextprotocol.org
- CAD-MCP repo: https://github.com/daobataotie/CAD-MCP
- Anthropic MCP servers: https://github.com/anthropics/mcp-servers

### 4. Atomic Commits
Format: `[Component] Task: Description`

Examples:
- `[trading-bot] Add: Strategy engine for ICT rules`
- `[cad-agent] Fix: PDF parser dimension extraction`
- `[desktop-server] Update: Add OCR controller`

---

## 🤖 AI-Specific Optimal Processes

### Context First
Read these files before every new task:
1. `.ai/CONTEXT.md` (if available)
2. `RULES.md`
3. `task.md` (for current sprint)
4. Relevant agent's `src/` directory

### Lazy Imports
When writing Python, prefer inner-function imports for heavy libraries:

```python
# GOOD - Lazy import
def capture_screen():
    import pyautogui  # Only loaded when needed
    return pyautogui.screenshot()

# BAD - Top-level import
import pyautogui  # Loaded on module import
```

Heavy libraries to lazy-load: `pyautogui`, `win32com`, `cv2`, `pytesseract`, `chromadb`

### File Limits
- If a file hits **300 lines**, propose a split immediately
- Agents: 100-300 lines max
- Adapters: 50-100 lines max
- Controllers: 50-150 lines max

### Config Over Code
Propose JSON/YAML for new strategies instead of hard-coding:

```python
# GOOD - Config-driven
with open("config/strategies/trading.json") as f:
    strategies = json.load(f)

# BAD - Hard-coded
STRATEGIES = {"ict": {...}, "btmm": {...}}
```

---

## ✍️ Documentation Standards

### File Paths
Always wrap in backticks: `path/to/file.py`

### Markdown Spacing
Headings and lists **must** be surrounded by exactly one blank line:

```markdown
## Section Header

- Item 1
- Item 2

Next paragraph here.
```

### Code Blocks
Always specify language tag:

```python
def example():
    pass
```

### Emoji Status Markers
Use consistently in task lists and logs:
- ✅ Complete / Success
- 📊 Analyzing / In Progress
- 📈 Trade Placed / Building
- 🛑 Error / Blocked
- 🔄 Building / In Development
- ❌ Not Started / Failed

---

## 🛡️ Safety & Reliability

### HITL Check (Rule 8/11)
If an action involves physical desktop movement or external data mutation, **ASK for approval first** by listing exactly what you will do:

```
I will perform the following actions:
1. Move mouse to (500, 300)
2. Click left button
3. Type "EURUSD" in symbol search
4. Press Enter

Approve? (yes/no)
```

### Error Recovery
If a tool call fails:
1. Analyze the error message
2. Report it clearly to the user
3. Suggest a correction
4. **DO NOT** retry blindly

### Least Privilege
Only request files and tools necessary for the immediate task.

---

## 📡 Memory & Context Pattern

### Log Decisions
Use `BlackBoxLogger` for critical logic flow:

```python
from agents.core.logging import BlackBoxLogger

logger = BlackBoxLogger("trading-bot")
logger.log_decision(
    action="scan_pair",
    inputs={"pair": "EURUSD", "timeframe": "15"},
    reasoning="Q2 phase detected, looking for manipulation",
    output={"setup_found": True}
)
```

### Visual Verify
Use `VisualVerifier` for CAD output validation:

```python
from desktop_server.controllers.verifier import verifier

result = verifier.capture_and_compare(
    reference_path="references/flange_complete.png",
    threshold=0.95
)
```

### MCP First
Interact with desktop via `mcp_server.py` tools rather than raw `pyautogui`:

```python
# GOOD - Via MCP
result = await mcp_client.call_tool("mouse_click", {"x": 500, "y": 300})

# BAD - Direct pyautogui
pyautogui.click(500, 300)
```

### Memory Integration
All agents should store important data in Memory Brain:

```python
await memory_client.store(
    key=f"trade:{trade_id}",
    content=f"Trade {pair} {bias} resulted in {result}",
    metadata=trade_record.__dict__
)
```

---

## 🏗️ Component Patterns

### Agent Structure

```
agents/{agent-name}/
├── src/
│   ├── __init__.py          # Exports main class
│   ├── {main_logic}.py      # Core business logic
│   └── {helpers}.py         # Utility functions
├── knowledge/               # Domain-specific docs
├── templates/               # Prompt templates, report formats
├── requirements.txt         # Agent-specific dependencies
└── README.md               # Agent documentation
```

### MCP Server Structure

```
mcp-servers/{server-name}/
├── config.json              # Server configuration
├── start.sh                 # Startup script
└── README.md               # Server documentation
```

### Controller Structure

```python
"""
Controller Template
Single responsibility: {describe purpose}
"""

class ControllerName:
    def __init__(self):
        # Minimal init, lazy-load heavy deps
        pass
        
    def action_name(self, param: type) -> ReturnType:
        """Brief description. Used by {which agents}."""
        # Implementation
        pass
```

---

## 🚨 Common Pitfalls to Avoid

1. **Don't clone repos** - Use remote references via GitHubFetcher
2. **Don't hard-code strategies** - Use config files
3. **Don't bypass MCP** - Always route through desktop server
4. **Don't duplicate files** - Update existing authoritative docs
5. **Don't exceed file limits** - Split at 300 lines
6. **Don't skip HITL** - Always ask for high-stake actions
7. **Don't ignore memory** - Log everything important

---

## 📋 Quick Reference

### Start Desktop Server
```bash
cd desktop-server && START_MCP.bat
```

### Run Trading Bot
```bash
cd agents/trading-bot && python -m src.main
```

### Run Inspector Audit
```bash
cd agents/inspector-bot && python -m src.judge --target trades
```

### Deploy to Render
```bash
git push origin main  # Auto-deploys via render.yaml
```

---

> [!TIP]
> **Taskmaster Pattern**: Plan the work → Work the plan → Verify the output
> 
> Every task should follow: PRD → Task breakdown → Implementation → Observability → Verification

---

**Last Updated**: December 20, 2025
