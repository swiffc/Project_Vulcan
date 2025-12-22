# Project Vulcan API Documentation

**Version**: 1.0.0  
**Last Updated**: December 22, 2025

---

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Orchestrator API](#orchestrator-api)
4. [Web API (Next.js)](#web-api-nextjs)
5. [Desktop Server API](#desktop-server-api)
6. [Error Handling](#error-handling)
7. [Rate Limiting](#rate-limiting)

---

## Overview

Project Vulcan consists of three main API layers:

1. **Orchestrator API** (FastAPI) - Cloud-hosted on Render, routes requests to agents
2. **Web API** (Next.js) - Frontend API routes, proxies to orchestrator
3. **Desktop Server API** (FastAPI) - Local PC control via Tailscale VPN

### Architecture

```
User → Web UI → Next.js API → Orchestrator API → Desktop Server
                                      ↓
                                  AI Agents
```

---

## Authentication

### API Key Authentication

All orchestrator and desktop server endpoints require API key authentication.

**Header**: `X-API-Key`  
**Value**: Your API key from environment variables

**Example**:
```bash
curl -H "X-API-Key: your-api-key-here" https://vulcan-orchestrator.onrender.com/health
```

**Error Response** (401):
```json
{
  "detail": "Invalid API Key"
}
```

---

## Orchestrator API

**Base URL**: `https://vulcan-orchestrator.onrender.com`

### Health Check

**GET** `/health`

Check orchestrator and desktop server connectivity.

**Response**:
```json
{
  "status": "healthy",
  "desktop_server": "connected",
  "desktop_url": "http://100.68.144.20:8000"
}
```

**Desktop Server Status Values**:
- `connected` - Desktop server reachable
- `unreachable` - Cannot connect to desktop server
- `error` - Desktop server returned error
- `unknown` - Status check not performed

---

### Chat

**POST** `/chat`

Process a chat message and return AI response.

**Headers**:
- `X-API-Key`: Your API key
- `Content-Type`: application/json

**Request Body**:
```json
{
  "messages": [
    {
      "role": "user",
      "content": "Analyze the GBP/USD setup"
    }
  ],
  "agent": "trading"
}
```

**Fields**:
- `messages` (required): Array of chat messages
  - `role`: "user" or "assistant"
  - `content`: Message text
- `agent` (optional): "trading", "cad", or "general" (auto-detected if not provided)

**Response**:
```json
{
  "response": "Based on the current GBP/USD setup...",
  "agent": "trading"
}
```

**Agent Detection Keywords**:
- **Trading**: trade, forex, gbp, usd, setup, bias, ict, btmm, order block, fvg, liquidity
- **CAD**: cad, solidworks, inventor, part, sketch, extrude, flange, model, 3d, drawing
- **General**: Default for all other queries

**Error Responses**:
- `400`: No messages provided
- `500`: LLM generation failed

---

### Desktop Command

**POST** `/desktop/command`

Proxy a command to the local desktop server via Tailscale.

**Headers**:
- `X-API-Key`: Your API key
- `Content-Type`: application/json

**Request Body**:
```json
{
  "endpoint": "/mouse/move",
  "method": "POST",
  "payload": {
    "x": 500,
    "y": 300
  }
}
```

**Fields**:
- `endpoint` (required): Desktop server endpoint path
- `method` (optional): HTTP method (default: "POST")
- `payload` (optional): Request payload for POST requests

**Response**:
```json
{
  "status": 200,
  "data": {
    "success": true,
    "message": "Mouse moved to (500, 300)"
  }
}
```

**Error Responses**:
- `503`: Cannot connect to desktop server
- `504`: Desktop server timeout (30s)
- `500`: Other errors

---

### Desktop Health

**GET** `/desktop/health`

Check desktop server connectivity directly.

**Headers**:
- `X-API-Key`: Your API key

**Response**:
```json
{
  "status": "ok",
  "tailscale_ip": "100.68.144.20"
}
```

**Error Response** (503):
```json
{
  "detail": "Desktop unreachable: Connection refused"
}
```

---

### Trading Journal API

**Base Path**: `/api/trading/journal`

#### Create Trade Entry

**POST** `/api/trading/journal`

**Request Body**:
```json
{
  "symbol": "GBPUSD",
  "direction": "long",
  "entry_price": 1.2650,
  "exit_price": 1.2750,
  "quantity": 1.0,
  "notes": "Clean order block setup with FVG"
}
```

**Response**:
```json
{
  "id": "uuid-here",
  "symbol": "GBPUSD",
  "direction": "long",
  "entry_price": 1.2650,
  "exit_price": 1.2750,
  "quantity": 1.0,
  "notes": "Clean order block setup with FVG",
  "created_at": "2025-12-22T13:30:00Z"
}
```

#### List Trades

**GET** `/api/trading/journal`

**Query Parameters**:
- `limit` (optional): Number of trades to return (default: 50)
- `offset` (optional): Pagination offset (default: 0)

**Response**:
```json
{
  "trades": [
    {
      "id": "uuid-here",
      "symbol": "GBPUSD",
      "direction": "long",
      "entry_price": 1.2650,
      "exit_price": 1.2750,
      "quantity": 1.0,
      "notes": "Clean order block setup with FVG",
      "created_at": "2025-12-22T13:30:00Z"
    }
  ],
  "total": 1
}
```

#### Get Trade

**GET** `/api/trading/journal/{id}`

**Response**: Same as create response

#### Update Trade

**PUT** `/api/trading/journal/{id}`

**Request Body**: Same as create request

**Response**: Updated trade object

#### Delete Trade

**DELETE** `/api/trading/journal/{id}`

**Response**:
```json
{
  "success": true,
  "message": "Trade deleted"
}
```

---

### Validation History API

**Base Path**: `/api/cad/validations`

#### List Recent Validations

**GET** `/api/cad/validations/recent`

**Query Parameters**:
- `limit` (optional): Number of validations to return (default: 20)

**Response**:
```json
{
  "validations": [
    {
      "id": "uuid-here",
      "job_id": "job-123",
      "status": "complete",
      "report_path": "/path/to/report.pdf",
      "created_at": "2025-12-22T13:00:00Z",
      "completed_at": "2025-12-22T13:05:00Z"
    }
  ]
}
```

#### Get Validation Details

**GET** `/api/cad/validations/{id}`

**Response**:
```json
{
  "id": "uuid-here",
  "job_id": "job-123",
  "status": "complete",
  "report_path": "/path/to/report.pdf",
  "checks": [
    {
      "name": "Material Specification",
      "status": "pass",
      "message": "ASTM A36 verified"
    },
    {
      "name": "Weld Size",
      "status": "fail",
      "message": "1/4\" fillet weld undersized"
    }
  ],
  "created_at": "2025-12-22T13:00:00Z",
  "completed_at": "2025-12-22T13:05:00Z"
}
```

---

## Web API (Next.js)

**Base URL**: `https://vulcan-web.onrender.com/api` (or `http://localhost:3000/api` for local dev)

All Next.js API routes proxy to the orchestrator API with added session management and error handling.

### Chat

**POST** `/api/chat`

Proxy to orchestrator `/chat` endpoint with session management.

**Request/Response**: Same as orchestrator `/chat`

---

### CAD Chat

**POST** `/api/chat/cad`

Specialized chat endpoint for CAD agent (forces agent="cad").

**Request/Response**: Same as orchestrator `/chat`

---

### CAD Validation

**POST** `/api/cad/validate`

Trigger CAD validation on a drawing file.

**Request Body**:
```json
{
  "file_path": "/path/to/drawing.pdf",
  "validation_types": ["gdt", "welding", "material", "ache"]
}
```

**Response**:
```json
{
  "job_id": "job-123",
  "status": "queued",
  "message": "Validation job created"
}
```

---

### Health Check

**GET** `/api/health`

Check web app and orchestrator health.

**Response**:
```json
{
  "status": "healthy",
  "orchestrator": "connected",
  "timestamp": "2025-12-22T13:30:00Z"
}
```

---

### Desktop Health

**GET** `/api/desktop/health`

Proxy to orchestrator `/desktop/health`.

**Response**: Same as orchestrator `/desktop/health`

---

### Work Hub - Microsoft 365

**Base Path**: `/api/work/microsoft`

#### Device Code Authentication

**POST** `/api/work/microsoft/auth/device-code`

Initiate Microsoft device code authentication flow.

**Response**:
```json
{
  "user_code": "ABC-DEF-GHI",
  "device_code": "device-code-here",
  "verification_uri": "https://microsoft.com/devicelogin",
  "expires_in": 900
}
```

#### Authentication Status

**GET** `/api/work/microsoft/auth/status`

Check authentication status.

**Response**:
```json
{
  "authenticated": true,
  "user": "user@example.com",
  "expires_at": "2025-12-22T14:30:00Z"
}
```

#### Sign Out

**POST** `/api/work/microsoft/auth/signout`

Sign out from Microsoft 365.

**Response**:
```json
{
  "success": true
}
```

#### List Files

**GET** `/api/work/microsoft/files`

List OneDrive files.

**Query Parameters**:
- `folder` (optional): Folder path (default: root)

**Response**:
```json
{
  "files": [
    {
      "id": "file-id",
      "name": "document.docx",
      "size": 12345,
      "modified": "2025-12-22T13:00:00Z"
    }
  ]
}
```

#### List Mail

**GET** `/api/work/microsoft/mail`

List recent emails.

**Query Parameters**:
- `limit` (optional): Number of emails (default: 10)

**Response**:
```json
{
  "messages": [
    {
      "id": "msg-id",
      "subject": "Meeting tomorrow",
      "from": "sender@example.com",
      "received": "2025-12-22T13:00:00Z",
      "preview": "Let's meet at 2pm..."
    }
  ]
}
```

#### List Teams Messages

**GET** `/api/work/microsoft/teams`

List recent Teams messages.

**Response**:
```json
{
  "messages": [
    {
      "id": "msg-id",
      "channel": "General",
      "from": "user@example.com",
      "content": "Project update...",
      "timestamp": "2025-12-22T13:00:00Z"
    }
  ]
}
```

---

### Work Hub - J2 Tracker

**Base Path**: `/api/work/j2`

#### Login

**POST** `/api/work/j2/login`

Login to J2 Tracker.

**Request Body**:
```json
{
  "username": "user",
  "password": "pass"
}
```

**Response**:
```json
{
  "success": true,
  "session_id": "session-id-here"
}
```

#### List Jobs

**GET** `/api/work/j2/jobs`

List active jobs from J2 Tracker.

**Response**:
```json
{
  "jobs": [
    {
      "id": "J2-12345",
      "title": "Vessel Fabrication",
      "status": "In Progress",
      "due_date": "2025-12-31"
    }
  ]
}
```

#### Job Status

**GET** `/api/work/j2/status`

Get detailed status for a specific job.

**Query Parameters**:
- `job_id` (required): Job ID

**Response**:
```json
{
  "job_id": "J2-12345",
  "title": "Vessel Fabrication",
  "status": "In Progress",
  "progress": 65,
  "tasks": [
    {
      "name": "Welding",
      "status": "Complete",
      "assigned_to": "John Doe"
    }
  ]
}
```

---

### Metrics

**GET** `/api/metrics/cost`

Get API cost metrics.

**Response**:
```json
{
  "total_cost": 12.50,
  "requests": 1250,
  "avg_cost_per_request": 0.01,
  "period": "2025-12"
}
```

---

## Desktop Server API

**Base URL**: `http://100.68.144.20:8000` (via Tailscale) or `http://localhost:8000` (local)

### Root

**GET** `/`

Get server information.

**Response**:
```json
{
  "name": "Project Vulcan - Desktop Control Server",
  "version": "1.0.0",
  "status": "running",
  "kill_switch": false,
  "loaded_controllers": [
    "mouse",
    "keyboard",
    "screen",
    "window",
    "cad_solidworks",
    "cad_inventor",
    "tradingview",
    "browser",
    "j2_tracker",
    "cad_validation"
  ]
}
```

---

### Health Check

**GET** `/health`

Check server health.

**Response**:
```json
{
  "status": "ok",
  "tailscale_ip": "100.68.144.20"
}
```

---

### Kill Switch

**POST** `/kill`

Emergency stop - activate kill switch to abort all operations.

**Response**:
```json
{
  "success": true,
  "message": "Kill switch activated - all operations stopped"
}
```

---

### Resume

**POST** `/resume`

Resume operations after kill switch (if mouse is away from corner).

**Response**:
```json
{
  "success": true,
  "message": "Operations resumed"
}
```

**Error Response** (400):
```json
{
  "detail": "Cannot resume - mouse still in corner"
}
```

---

### Action Logs

**GET** `/logs`

Get recent action logs.

**Query Parameters**:
- `limit` (optional): Number of logs to return (default: 100)

**Response**:
```json
{
  "logs": [
    {
      "timestamp": "2025-12-22T13:30:00Z",
      "action": "mouse_move",
      "params": {"x": 500, "y": 300},
      "success": true
    }
  ]
}
```

---

### Command Queue

#### Add to Queue

**POST** `/queue/add`

Add a command to the execution queue.

**Request Body**:
```json
{
  "type": "mouse",
  "action": "move",
  "params": {"x": 500, "y": 300},
  "priority": 1
}
```

**Response**:
```json
{
  "success": true,
  "message": "Command added to queue",
  "queue_size": 5
}
```

#### Queue Status

**GET** `/queue/status`

Get current queue status.

**Response**:
```json
{
  "queue_size": 5,
  "processing": true,
  "current_command": {
    "type": "mouse",
    "action": "move"
  }
}
```

---

### Mouse Control

**Base Path**: `/mouse`

#### Move Mouse

**POST** `/mouse/move`

**Request Body**:
```json
{
  "x": 500,
  "y": 300
}
```

**Response**:
```json
{
  "success": true,
  "message": "Mouse moved to (500, 300)"
}
```

#### Click

**POST** `/mouse/click`

**Request Body**:
```json
{
  "button": "left",
  "clicks": 1
}
```

**Fields**:
- `button`: "left", "right", or "middle"
- `clicks`: Number of clicks (default: 1)

**Response**:
```json
{
  "success": true,
  "message": "Clicked left button 1 time(s)"
}
```

#### Scroll

**POST** `/mouse/scroll`

**Request Body**:
```json
{
  "amount": -3
}
```

**Fields**:
- `amount`: Scroll amount (negative = down, positive = up)

**Response**:
```json
{
  "success": true,
  "message": "Scrolled -3 units"
}
```

---

### Keyboard Control

**Base Path**: `/keyboard`

#### Type Text

**POST** `/keyboard/type`

**Request Body**:
```json
{
  "text": "Hello, World!"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Typed 13 characters"
}
```

#### Press Key

**POST** `/keyboard/press`

**Request Body**:
```json
{
  "key": "enter"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Pressed key: enter"
}
```

#### Hotkey

**POST** `/keyboard/hotkey`

**Request Body**:
```json
{
  "keys": ["ctrl", "c"]
}
```

**Response**:
```json
{
  "success": true,
  "message": "Executed hotkey: ctrl+c"
}
```

---

### Screen Control

**Base Path**: `/screen`

#### Take Screenshot

**POST** `/screen/screenshot`

**Request Body** (optional):
```json
{
  "region": {
    "x": 0,
    "y": 0,
    "width": 1920,
    "height": 1080
  }
}
```

**Response**:
```json
{
  "success": true,
  "image_base64": "iVBORw0KGgoAAAANSUhEUgAA...",
  "width": 1920,
  "height": 1080
}
```

#### Get Screen Size

**GET** `/screen/size`

**Response**:
```json
{
  "width": 1920,
  "height": 1080
}
```

---

### Window Control

**Base Path**: `/window`

#### List Windows

**GET** `/window/list`

**Response**:
```json
{
  "windows": [
    {
      "title": "SolidWorks 2023",
      "pid": 12345,
      "active": true
    }
  ]
}
```

#### Activate Window

**POST** `/window/activate`

**Request Body**:
```json
{
  "title": "SolidWorks 2023"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Activated window: SolidWorks 2023"
}
```

---

### CAD Control (SolidWorks)

**Base Path**: `/cad/solidworks`

#### Create Part

**POST** `/cad/solidworks/part/create`

**Request Body**:
```json
{
  "name": "Flange"
}
```

**Response**:
```json
{
  "success": true,
  "part_name": "Flange",
  "message": "Part created"
}
```

#### Create Sketch

**POST** `/cad/solidworks/sketch/create`

**Request Body**:
```json
{
  "plane": "Front"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Sketch created on Front plane"
}
```

#### Draw Circle

**POST** `/cad/solidworks/sketch/circle`

**Request Body**:
```json
{
  "center_x": 0,
  "center_y": 0,
  "radius": 50
}
```

**Response**:
```json
{
  "success": true,
  "message": "Circle drawn at (0, 0) with radius 50mm"
}
```

#### Extrude

**POST** `/cad/solidworks/feature/extrude`

**Request Body**:
```json
{
  "distance": 100,
  "direction": "normal"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Extruded 100mm"
}
```

---

### CAD Validation

**Base Path**: `/cad/validate`

#### Validate Drawing

**POST** `/cad/validate`

**Request Body**:
```json
{
  "file_path": "/path/to/drawing.pdf",
  "validation_types": ["gdt", "welding", "material", "ache"]
}
```

**Response**:
```json
{
  "job_id": "job-123",
  "status": "queued",
  "validations": ["gdt", "welding", "material", "ache"]
}
```

#### Get Validation Status

**GET** `/cad/validate/{job_id}`

**Response**:
```json
{
  "job_id": "job-123",
  "status": "complete",
  "report_path": "/path/to/report.pdf",
  "checks_passed": 45,
  "checks_failed": 3,
  "checks_total": 48
}
```

---

## Error Handling

### Standard Error Response

All APIs return errors in this format:

```json
{
  "detail": "Error message here"
}
```

### HTTP Status Codes

- `200` - Success
- `400` - Bad Request (invalid parameters)
- `401` - Unauthorized (invalid API key)
- `404` - Not Found
- `429` - Too Many Requests (rate limit exceeded)
- `500` - Internal Server Error
- `503` - Service Unavailable (desktop server unreachable)
- `504` - Gateway Timeout (desktop server timeout)

---

## Rate Limiting

### Orchestrator API

- **Limit**: 100 requests per 60 seconds per IP
- **Response** (429):
```json
{
  "detail": "Too Many Requests"
}
```

### Bypass Rate Limiting

Rate limiting is per-IP. Use different IPs or wait for the window to reset.

---

## Security Headers

All responses include security headers:

- `Content-Security-Policy`: Restricts resource loading
- `X-Content-Type-Options`: nosniff
- `X-Frame-Options`: DENY

---

## CORS Policy

### Allowed Origins

**Orchestrator**:
- `https://vulcan-web.onrender.com`
- `http://localhost:3000`

**Desktop Server**:
- `http://localhost:3000`
- `http://127.0.0.1:3000`
- `https://*.onrender.com`

---

## Examples

### Complete Chat Flow

```bash
# 1. Send chat message
curl -X POST https://vulcan-orchestrator.onrender.com/chat \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Create a flange in SolidWorks"}
    ]
  }'

# 2. Execute desktop command (if needed)
curl -X POST https://vulcan-orchestrator.onrender.com/desktop/command \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{
    "endpoint": "/cad/solidworks/part/create",
    "payload": {"name": "Flange"}
  }'
```

### CAD Validation Flow

```bash
# 1. Trigger validation
curl -X POST http://localhost:3000/api/cad/validate \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "/path/to/drawing.pdf",
    "validation_types": ["gdt", "welding"]
  }'

# Response: {"job_id": "job-123", "status": "queued"}

# 2. Check status
curl http://localhost:8000/cad/validate/job-123

# 3. Get validation history
curl http://localhost:3000/api/cad/validations/recent?limit=10
```

---

## Changelog

### Version 1.0.0 (December 22, 2025)
- Initial API documentation
- Documented all orchestrator endpoints
- Documented all web API routes
- Documented all desktop server endpoints
- Added examples and error handling guide

---

**For support or questions, contact the Project Vulcan team.**
