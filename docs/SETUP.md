# Project Vulcan - Local Development Setup

**Last Updated**: December 22, 2025

This guide covers setting up Project Vulcan for local development, including all dependencies, services, and configuration.

---

## Table of Contents

1. [Prerequisites](#prerequisites-system--services)
2. [Quick Start](#quick-start)
3. [Environment Configuration](#environment-configuration)
4. [Standards Database Setup](#standards-database-setup)
5. [Desktop Server Setup](#desktop-server-setup)
6. [Web Application Setup](#web-application-setup)
7. [CAD Integration Setup](#cad-integration-setup)
8. [Work Hub Setup](#work-hub-setup)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites (System & Services)

### Local System Requirements

- **Python 3.11+** - Core backend language
- **Node.js 18+** - Frontend and Next.js
- **SolidWorks/Inventor 2020+** - For CAD integration (Windows only)
- **RAM**: 8GB minimum, 16GB recommended

### ☁️ Mandatory Cloud & External Services

1. **PostgreSQL 16+**: Used for persistence (Trades, Validations).
2. **Tailscale VPN**: Required for Cloud-to-Local connectivity.
3. **Sentry Account**: For project-wide monitoring and error tracking.
4. **Anthropic/OpenAI API Keys**: For LLM orchestration.

---

## Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/swiffc/Project_Vulcan.git
cd Project_Vulcan
```

### 2. Install Python Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Install Node.js Dependencies

```bash
cd apps/web
npm install
cd ../..
```

### 4. Configure Environment

```bash
# Copy example environment files
cp .env.example .env
cp apps/web/.env.example apps/web/.env
cp desktop_server/.env.example desktop_server/.env
```

Edit each `.env` file with your actual values (see [Environment Configuration](#environment-configuration)).

### 5. Set Up Standards Database

```bash
python scripts/pull_external_standards.py
```

This will download and cache engineering standards (AISC, fasteners, pipe fittings, materials).

### 6. Start Services

```bash
# Terminal 1: Start orchestrator
python -m uvicorn core.api:app --reload --port 8000

# Terminal 2: Start web app
cd apps/web
npm run dev

# Terminal 3: Start desktop server (Windows only)
cd desktop_server
python server.py
```

---

## Environment Configuration

### Root `.env`

Located at project root. Used by orchestrator and Python services.

```bash
# LLM Configuration
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here

# Vector Memory (ChromaDB)
CHROMA_HOST=localhost
CHROMA_PORT=8001

# Redis Cache
REDIS_URL=redis://localhost:6379

# Desktop Server
DESKTOP_SERVER_URL=http://localhost:8000

# API Security
API_KEY=your-secure-api-key-here

# Optional: Database
DATABASE_URL=postgresql://user:pass@localhost:5432/vulcan_db
```

### Web App `.env`

Located at `apps/web/.env`. Used by Next.js frontend.

```bash
# Orchestrator API
NEXT_PUBLIC_ORCHESTRATOR_URL=http://localhost:8000

# Microsoft 365 Integration
MICROSOFT_CLIENT_ID=your-client-id
MICROSOFT_CLIENT_SECRET=your-client-secret
MICROSOFT_TENANT_ID=common

# J2 Tracker
J2_TRACKER_URL=https://your-j2-instance.com
```

### Desktop Server `.env`

Located at `desktop_server/.env`. Used by local PC control server.

```bash
# Token Storage
TOKEN_STORE_PATH=./data/tokens.json
TOKEN_ENCRYPTION_KEY=your-encryption-key-here

# Orchestrator Connection
ORCHESTRATOR_URL=http://localhost:8000
```

### System Manager `.env`

Located at `agents/system_manager/.env`. Used by background worker.

```bash
# Service URLs for health monitoring
WEB_URL=http://localhost:3000
DESKTOP_SERVER_URL=http://localhost:8000
MEMORY_SERVER_URL=http://localhost:8001

# Google Drive Backup (optional)
GOOGLE_DRIVE_CREDENTIALS=path/to/credentials.json
BACKUP_DESTINATION=google_drive

# Logging
LOG_LEVEL=INFO
```

---

## Standards Database Setup

The CAD validation system requires a local standards database containing engineering specifications.

### What's Included

The standards database includes:

- **234 AISC steel shapes** (W-shapes, L-shapes, C-shapes, HSS)
- **21 fastener specifications** (bolts, nuts, washers)
- **383 pipe fittings** (ASME B16.9, B16.11, B16.5, MSS-SP-97)
- **20 material properties** (steel, stainless, aluminum)

**Total**: ~658 standards

### Initial Setup

1. **Run the import script**:

```bash
python scripts/pull_external_standards.py
```

2. **Verify output**:

```bash
# Check that the file was created
ls -lh data/standards/engineering_standards.json

# Expected size: ~500KB - 2MB depending on sources
```

3. **Verify standards loaded**:

```python
import json
with open('data/standards/engineering_standards.json') as f:
    db = json.load(f)
    
print(f"AISC Shapes: {sum(len(v) for v in db['aisc_shapes'].values())}")
print(f"Fasteners: {sum(len(v) for v in db['fasteners'].values())}")
print(f"Pipe Fittings: {sum(len(v) for v in db['pipe_fittings'].values())}")
print(f"Materials: {sum(len(v) for v in db['materials'].values())}")
```

### Data Sources

The script attempts to pull from multiple sources (in order):

1. **Python packages** (if installed):
   - `aisc-shapes` - AISC steel shapes
   - `fastener-db` - Fastener specifications
   - `fluids` - Pipe fitting dimensions

2. **GitHub repositories** (fallback):
   - Community-maintained engineering databases
   - Open-source standards collections

3. **Built-in fallback data**:
   - Minimal sample dataset
   - Ensures script always completes

### Optional: Install Source Packages

For more comprehensive data, install optional packages:

```bash
pip install aisc-shapes fastener-db fluids requests
```

Then re-run the import script:

```bash
python scripts/pull_external_standards.py
```

### Optional: Commit Standards to Repository

If you want to version-control the standards database:

```bash
git add data/standards/engineering_standards.json
git commit -m "Add standards database"
```

**Note**: The file can be large (1-2MB). Consider using Git LFS for large files.

### Automatic Updates

The System Manager automatically updates standards weekly. To manually update:

```bash
python scripts/pull_external_standards.py --force-update
```

---

## Desktop Server Setup

The desktop server enables physical PC control (mouse, keyboard, CAD automation).

### Windows Setup

1. **Install Python dependencies**:

```bash
cd desktop_server
pip install -r requirements.txt
```

2. **Install system dependencies**:

- **Tesseract OCR** (for screenshot text extraction):
  ```bash
  winget install UB-Mannheim.TesseractOCR
  ```

- **Poppler** (for PDF processing):
  Download from: https://github.com/oschwartz10612/poppler-windows/releases
  Add to PATH

3. **Configure environment**:

```bash
cp .env.example .env
# Edit .env with your settings
```

4. **Start server**:

```bash
python server.py
```

5. **Verify**:

```bash
curl http://localhost:8000/health
# Expected: {"status": "ok", "tailscale_ip": null}
```

### Tailscale Setup (Optional)

For remote access to desktop server:

1. **Install Tailscale**:

```bash
winget install tailscale.tailscale
```

2. **Authenticate**:

```bash
tailscale up
```

3. **Get IP**:

```bash
tailscale ip -4
# Example output: 100.68.144.20
```

4. **Update orchestrator**:

```bash
# In root .env:
DESKTOP_SERVER_URL=http://100.68.144.20:8000
```

See [TAILSCALE_SETUP.md](TAILSCALE_SETUP.md) for detailed instructions.

---

## Web Application Setup

### Install Dependencies

```bash
cd apps/web
npm install
```

### Configure Environment

```bash
cp .env.example .env
```

Edit `.env`:

```bash
NEXT_PUBLIC_ORCHESTRATOR_URL=http://localhost:8000
```

### Start Development Server

```bash
npm run dev
```

Open http://localhost:3000

### Build for Production

```bash
npm run build
npm start
```

---

## CAD Integration Setup

### SolidWorks Setup

1. **Enable COM API**:
   - Open SolidWorks
   - Tools → Options → System Options → General
   - Enable "Enable COM API when SolidWorks starts"

2. **Install Python COM support**:

```bash
pip install pywin32
```

3. **Test connection**:

```python
import win32com.client
sw = win32com.client.Dispatch("SldWorks.Application")
print(f"SolidWorks version: {sw.RevisionNumber()}")
```

### Inventor Setup

1. **Enable COM API**:
   - Open Inventor
   - Tools → Application Options → General
   - Enable "Enable COM API"

2. **Test connection**:

```python
import win32com.client
inv = win32com.client.Dispatch("Inventor.Application")
print(f"Inventor version: {inv.SoftwareVersion.DisplayVersion}")
```

---

## Work Hub Setup

### Microsoft 365 Integration

See [docs/WORK_HUB_SETUP.md](docs/WORK_HUB_SETUP.md) for complete guide.

**Quick Setup**:

1. **Create Azure AD app**:
   - Go to https://portal.azure.com
   - Azure Active Directory → App registrations → New registration
   - Copy Client ID and Tenant ID

2. **Configure permissions**:
   - API permissions → Add permission → Microsoft Graph
   - Add: `Files.Read`, `Mail.Read`, `Chat.Read`

3. **Update environment**:

```bash
# In apps/web/.env:
MICROSOFT_CLIENT_ID=your-client-id
MICROSOFT_TENANT_ID=common
```

### J2 Tracker Integration

1. **Get J2 Tracker URL**:

```bash
# In apps/web/.env:
J2_TRACKER_URL=https://your-j2-instance.com
```

2. **Install Playwright** (for browser automation):

```bash
cd desktop_server
pip install playwright
playwright install chromium
```

3. **Test connection**:

```bash
python check_playwright.py
```

---

## Troubleshooting

### Common Issues

#### "Module not found" errors

**Solution**: Ensure virtual environment is activated and dependencies installed:

```bash
# Activate venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/macOS

# Reinstall dependencies
pip install -r requirements.txt
```

#### "Port already in use"

**Solution**: Kill process using the port:

```bash
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/macOS:
lsof -ti:8000 | xargs kill -9
```

#### "Cannot connect to desktop server"

**Solution**: Verify desktop server is running and URL is correct:

```bash
# Check if server is running
curl http://localhost:8000/health

# Check environment variable
echo $DESKTOP_SERVER_URL  # Linux/macOS
echo %DESKTOP_SERVER_URL%  # Windows
```

#### "Standards database empty"

**Solution**: Re-run import script with verbose output:

```bash
python scripts/pull_external_standards.py
```

Check output for errors. If all sources fail, fallback data will be used.

#### "CAD COM connection failed"

**Solution**: 
1. Ensure CAD software is running
2. Verify COM API is enabled in CAD settings
3. Run as administrator if needed
4. Check Windows Event Viewer for COM errors

### Getting Help

1. **Check logs**:
   - Orchestrator: Console output
   - Web app: Browser console (F12)
   - Desktop server: `desktop_server/logs/`

2. **Enable debug logging**:

```bash
# In .env:
LOG_LEVEL=DEBUG
```

3. **Run health checks**:

```bash
# Orchestrator
curl http://localhost:8000/health

# Web app
curl http://localhost:3000/api/health

# Desktop server
curl http://localhost:8000/health
```

4. **Check documentation**:
   - [API.md](docs/API.md) - API reference
   - [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) - Deployment guide
   - [WORK_HUB_SETUP.md](docs/WORK_HUB_SETUP.md) - Work Hub setup

---

## Next Steps

After completing setup:

1. **Test the system**:
   - Open web UI at http://localhost:3000
   - Send a test chat message
   - Verify AI responds

2. **Configure agents**:
   - Trading agent: Add TradingView credentials
   - CAD agent: Test SolidWorks/Inventor connection
   - Work Hub: Authenticate Microsoft 365

3. **Run validation**:
   - Upload a test drawing
   - Run CAD validation
   - Review generated report

4. **Deploy to production**:
   - See [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)
   - Configure Render.com services
   - Set up Tailscale VPN

---

## Development Workflow

### Running Tests

```bash
# Python tests
pytest

# With coverage
pytest --cov=. --cov-report=html

# Next.js tests
cd apps/web
npm test
```

### Code Quality

```bash
# Python linting
ruff check .

# Python type checking
mypy .

# Next.js linting
cd apps/web
npm run lint
```

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/my-feature

# Make changes and commit
git add .
git commit -m "feat: Add my feature"

# Push to GitHub
git push origin feature/my-feature

# Create pull request on GitHub
```

---

**For additional help, see the [API documentation](docs/API.md) or contact the Project Vulcan team.**
