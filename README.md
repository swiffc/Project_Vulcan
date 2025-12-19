# Project Vulcan

**Personal AI Operating System** - A unified web chatbot that physically controls your Windows PC.

## What This Is

One chat interface that controls your entire digital life:
- **Trading Agent** - Controls TradingView, analyzes charts, executes paper trades
- **CAD Agent** - Controls SolidWorks, Inventor, AutoCAD, Bentley
- **Life Agent** - Fitness, calendar, notes, general tasks

All agents share a **Desktop Control Server** that physically operates your Windows PC.

## Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│                    RENDER.COM (Cloud)                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              WEB CHATBOT (Next.js)                   │   │
│  │             Accessible from anywhere                 │   │
│  └─────────────────────────┬───────────────────────────┘   │
│                            │                                │
│  ┌─────────────────────────▼───────────────────────────┐   │
│  │    ORCHESTRATOR + AGENTS (Trading, CAD, Life)       │   │
│  └─────────────────────────┬───────────────────────────┘   │
└────────────────────────────┼────────────────────────────────┘
                             │
                       TAILSCALE VPN
                             │
 ┌───────────────────────────▼────────────────────────────────┐
 │                   YOUR WINDOWS PC                           │
 │  ┌─────────────────────────────────────────────────────┐   │
 │  │           DESKTOP CONTROL SERVER                     │   │
 │  │  🖱️ Mouse  ⌨️ Keyboard  📸 Screenshot  🪟 Window     │   │
 │  └─────────────────────────┬───────────────────────────┘   │
 │                            │                                │
 │      ┌─────────────────────┼─────────────────────┐         │
 │      ▼                     ▼                     ▼         │
 │  TradingView          SolidWorks            Calendar       │
 └─────────────────────────────────────────────────────────────┘
```

## Quick Start

### 1. Start Desktop Control Server

```bash
cd desktop-server
run.bat
```

This will:
- Create a Python virtual environment
- Install dependencies
- Start the FastAPI server on your Tailscale IP (or localhost)

### 2. Test the API

```bash
# Health check
curl http://localhost:8000/health

# Take a screenshot
curl -X POST http://localhost:8000/screen/screenshot

# List windows
curl http://localhost:8000/window/list
```

### 3. Connect via Tailscale

1. Install Tailscale: https://tailscale.com
2. Run `tailscale up`
3. Server will automatically bind to your Tailscale IP

## Safety Features

- **Kill Switch**: Move mouse to top-left corner to stop all automation
- **App Whitelist**: Only approved apps can be controlled
- **Action Logging**: Every action is logged with timestamp
- **No Public Ports**: All traffic over Tailscale VPN

## Project Structure

```text
Project_Vulcan/
├── desktop-server/          # Python server on Windows PC
│   ├── server.py           # FastAPI main server
│   ├── controllers/        # Mouse, keyboard, screen, window
│   ├── com/               # CAD COM automation
│   └── config/            # Whitelists and settings
├── apps/web/              # Next.js chat interface
├── agents/                # Trading, CAD, Life agents
│   ├── trading-agent/
│   ├── cad-agent/
│   └── life-agent/
├── storage/               # Output files and journals
├── REFERENCES.md          # External dependencies
└── RULES.md              # Build rules
```

## API Endpoints

### Mouse Control
- `POST /mouse/move` - Move cursor
- `POST /mouse/click` - Click at position
- `POST /mouse/drag` - Drag operation
- `POST /mouse/scroll` - Scroll wheel

### Keyboard Control
- `POST /keyboard/type` - Type text
- `POST /keyboard/press` - Press key
- `POST /keyboard/hotkey` - Key combination

### Screen Control
- `POST /screen/screenshot` - Full screenshot
- `POST /screen/region` - Region screenshot
- `POST /screen/ocr` - OCR text extraction

### Window Control
- `GET /window/list` - List windows
- `POST /window/focus` - Focus window
- `POST /window/minimize` - Minimize
- `POST /window/maximize` - Maximize

### System
- `GET /health` - Health check
- `POST /kill` - Emergency stop
- `POST /resume` - Resume after kill

## Development

See [RULES.md](RULES.md) for build rules and architecture guidelines.

## License

Private project - All rights reserved.
