# CLAUDE.md - AI Operating Instructions

This file contains specific behavioral instructions for AI assistants (Claude, Cursor, etc.) working on Project Vulcan.

---

## 🛠️ Development Workflow

1. **PRD First**: If the user asks for a feature, first look for or create a PRD in `docs/prds/`.
2. **Task Management**: Maintain the `task.md` file in the **project root** as the single source of truth. **DO NOT** create duplicate files.
3. **Research Spikes**: Conduct a spike (web search + docs) before proposing code.
4. **Atomic Commits**: Format `Task: Description`.

## 🤖 AI-Specific Optimal Processes

- **Context First**: Read `.ai/CONTEXT.md` (if available) and `RULES.md` before every new task.
- **Lazy Imports**: When writing Python, prefer inner-function imports for heavy libraries (e.g., `win32com`, `cv2`, `pyautogui`) to keep startup fast.
- **File Limit**: If a file you are editing hits 300 lines, propose a split immediately.
- **Config Over Code**: Propose JSON or Markdown for new strategies instead of hard-coding values.

## ✍️ Documentation Standards

- **File Paths**: Always wrap file paths and identifiers in backticks: `path/to/file.py`.
- **Markdown Spacing**: Headings and lists **must** be surrounded by exactly one blank line.
- **Code Blocks**: Always specify the language tag for code blocks (e.g., ```python).

## 🛡️ Safety & Reliability

- **HITL Check (Rule 8/11)**: If an action involves physical desktop movement or external data mutation, ASK for approval first by listing exactly what you will do.
- **Error Recovery**: If a tool call fails, analyze the error, report it, and suggest a correction rather than retrying blindly.
- **Least Privilege**: Only request files and tools necessary for the immediate task.

## 📡 Memory & Context Pattern

- **Log Decision**: Use `BlackBoxLogger` (`core/logging.py`) for critical logic flow.
- **Visual Verify**: Use `VisualVerifier` (`desktop_server/controllers/verifier.py`) for CAD output validation.
- **MCP First**: Interact with the desktop via `mcp_server.py` tools rather than raw `pyautogui` where possible.

---

> [!TIP]
> Use the "Taskmaster" pattern: Plan the work, work the plan, and verify the output (Observability + Verification).
