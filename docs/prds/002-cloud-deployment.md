# PRD-002: Cloud Infrastructure & Deployment

**Status**: Draft
**Author**: Project Vulcan
**Created**: 2024-12-19
**Priority**: High

---

## 1. Overview

Migrate the presentation and orchestration layers to **Render** to ensure 24/7 availability and global accessibility, while maintaining secure connectivity to the local **Desktop Server** (Windows) via **Tailscale**.

---

## 2. Architecture

```text
┌──────────────────────────┐          ┌──────────────────────────┐
│       RENDER CLOUD        │          │      LOCAL WINDOWS       │
│  ┌────────────────────┐   │          │  ┌────────────────────┐  │
│  │   Next.js App      │   │          │  │  Desktop Server    │  │
│  │   (Frontend)       │   │◄─────────┼─►│  (FastAPI + COM)   │  │
│  └──────────┬─────────┘   │  Secure  │  └────────────────────┘  │
│             │             │  Tunnel  │             ▲            │
│  ┌──────────▼─────────┐   │ (Tailscale)            │            │
│  │   Orchestrator     │   │          │  ┌──────────┴─────────┐  │
│  │   (CrewAI/Python)  │   │          │  │  SolidWorks/Trade  │  │
│  └────────────────────┘   │          │  └────────────────────┘  │
└──────────────────────────┘          └──────────────────────────┘
```

---

## 3. Deployment Components

### 3.1 Next.js Frontend (`apps/web`)

- **Service Type**: Render Web Service
- **Environment**: Node.js
- **Purpose**: Glassmorphism dashboard, real-time logs, trade/CAD controls.

### 3.2 Python Orchestrator (`core`)

- **Service Type**: Render Web Service
- **Runtime**: Python 3.11+
- **Purpose**: Runs CrewAI agents, manages strategy-over-code logic, and calls local physical controllers.

---

## 4. Render Blueprint (`render.yaml`)

```yaml
services:
  # Next.js Frontend
  - type: web
    name: vulcan-web
    env: node
    rootDir: apps/web
    buildCommand: npm install && npm run build
    startCommand: npm start
    envVars:
      - key: NEXT_PUBLIC_API_URL
        fromService:
          type: web
          name: vulcan-orchestrator
          property: host

  # Python Orchestrator
  - type: web
    name: vulcan-orchestrator
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn core.api:app
    envVars:
      - key: DESKTOP_SERVER_URL
        sync: false # Set to Tailscale IP of local PC
      - key: TAILSCALE_AUTH_KEY
        generateValue: true
```

---

## 5. Tailscale Connectivity (Render to Local)

To allow Render services to talk to the local Windows PC:
1. **Sidecar Approach**: Use a Docker-based deployment for the Orchestrator that includes Tailscale.
2. **Environment Variable**: Use the Tailscale IP of the Windows machine directly if the Render service is added to the Tailinet.

---

## 6. Implementation Plan

1. **Step 1**: Create `render.yaml` in the project root.
2. **Step 2**: Add `apps/web` basic Next.js structure.
3. **Step 3**: Configure the `orchestrator-api` wrapper in `core`.
4. **Step 4**: Set up Render Blueprint via the Render Dashboard.
