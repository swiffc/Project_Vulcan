# Project Vulcan - API Documentation

This document provides a comprehensive reference for the Project Vulcan API.

## 🔐 Authentication

All endpoints (except `/api/health`) require an API key to be passed in the `X-API-Key` header.
For local development, use the `VULCAN_API_KEY` defined in your `.env` file.

---

## 📡 Core Endpoints

### Health & Metrics

- `GET /api/health` - System health status.
- `GET /api/metrics` - Performance metrics and token usage.

### AI Chat & Orchestration

- `POST /api/chat` - Process a chat message.
  - **Body**: `{ "messages": [...] }`
  - **Returns**: SSE stream of agent responses and screenshots.

### Desktop Proxy

- `POST /api/desktop/command` - Proxy a raw command to the local desktop server.
- `GET /api/desktop/health` - Check connectivity to the local node.

---

## 🏗️ CAD Automation

### Validations

- `GET /api/cad/validations/recent` - Fetch latest validation results.
- `GET /api/cad/validations/{id}` - Fetch detailed validation report.
- `POST /api/cad/validate` - Start a new validation job.

---

## 📊 Trading Journal

### Trades

- `POST /api/trading/journal` - Create a new trade entry.
- `GET /api/trading/journal` - List all trades.
- `GET /api/trading/journal/{id}` - Get trade details.
- `PUT /api/trading/journal/{id}` - Update a trade.
- `DELETE /api/trading/journal/{id}` - Remove a trade.

---

## 💼 Work Hub & Integrations

### J2 Tracker

- `POST /api/work/j2/sync` - Sync local J2 tracking data to cloud.
- `GET /api/work/j2/stats` - Fetch professional productivity stats.

### Microsoft Suite

- `GET /api/work/microsoft/auth` - Initiate OAuth flow.
- `POST /api/work/microsoft/sync` - Sync Outlook/Calendar events.

---

## 🖥️ Desktop Server (Local Only)

These endpoints are exposed by the `desktop_server` running on your local machine (`http://localhost:8000`).

- `POST /mouse/click` - Perform a click.
- `POST /keyboard/type` - Send keystrokes.
- `POST /screen/screenshot` - Capture current screen.
- `POST /window/focus` - Focus a specific application.
- `POST /memory/rag/augment` - Get context-aware memory snippets.