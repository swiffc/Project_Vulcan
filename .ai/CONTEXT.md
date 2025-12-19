# Project_Vulcan: AI Context

This is a personal AI Operating System designed for professional CAD automation (SolidWorks/Inventor) and Paper Trading (Quarterly Theory/ICT).

## 🚀 Core Principles (READ FIRST)

1. **NO CLONING**: Do not clone external repos. Use "Thin Adapters" and remote references.
2. **SSOT**: The root `task.md` is the single source of truth for progress.
3. **Monorepo**: Keep everything in this repo with strict boundaries (`apps/`, `agents/`, `desktop-server/`).
4. **Config-Over-Code**: Business logic (strategies) lives in JSON/Markdown, not Python/Node logic.
5. **Human-in-the-Loop**: High-stake physical actions (trades/deletes) require explicit user approval.

## 🛠️ Technology Stack

- **Frontend**: Next.js (Glassmorphism UI).
- **Orchestration**: CrewAI / LangChain.
- **Physical Control**: Python Desktop Server (FastAPI + `pyautogui` + `pywin32`).
- **Connectivity**: Tailscale VPN.

## 📁 Key Files

- `RULES.md`: The Architectural Bible.
- `CLAUDE.md`: AI User Manual.
- `task.md`: Active Progress Tracking.

> [!TIP]
> Always check `REFERENCES.md` for existing package installs before suggesting new libraries.
