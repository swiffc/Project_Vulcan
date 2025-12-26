# 🚀 Render.com Deployment Guide

Complete step-by-step guide to deploy Project Vulcan to Render.com.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Detailed Setup](#detailed-setup)
4. [Environment Variables](#environment-variables)
5. [Tailscale Configuration](#tailscale-configuration)
6. [Troubleshooting](#troubleshooting)
7. [Verification](#verification)

---

## Prerequisites

Before deploying, ensure you have:

- ✅ GitHub account with Project Vulcan repository
- ✅ Render.com account (free tier works)
- ✅ Anthropic API key ([get here](https://console.anthropic.com))
- ✅ Tailscale account ([sign up](https://login.tailscale.com/start))
- ✅ Desktop server running (for CAD integration)

---

## Quick Start

### 1. Connect GitHub to Render

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Blueprint"**
3. Connect your GitHub account
4. Select **swiffc/Project_Vulcan** repository
5. Render will detect [config/render.yaml](config/render.yaml)
6. Click **"Apply"**

Render will create all 6 services automatically:
- `vulcan-web` (Next.js frontend)
- `vulcan-orchestrator` (Python API)
- `vulcan-redis` (Cache)
- `vulcan-chroma` (Vector DB)
- `vulcan-system-manager` (Worker)
- `vulcan-postgres` (Database)

### 2. Set Critical Environment Variables

Go to each service and set required variables (see [Environment Variables](#environment-variables) section below):

**For vulcan-orchestrator:**
- `ANTHROPIC_API_KEY` - Your Claude API key
- `API_KEY` - Create a secure random key
- `TAILSCALE_AUTHKEY` - From Tailscale dashboard
- `DESKTOP_SERVER_URL` - Your desktop's Tailscale IP

**For vulcan-web:**
- Variables are auto-set by Render service links

### 3. Deploy

Once variables are set, Render will automatically deploy all services.

---

## Detailed Setup

### Step 1: Prepare Repository

Ensure your repository has:
- ✅ [config/render.yaml](config/render.yaml) - Main configuration
- ✅ All Dockerfiles in `docker/` directory
- ✅ Web app in `apps/web/`
- ✅ Python code in `core/` and `agents/`

### Step 2: Create Render Services

#### Option A: Blueprint (Recommended)

1. **Navigate to Render Dashboard**
   ```
   https://dashboard.render.com/select-repo?type=blueprint
   ```

2. **Select Repository**
   - Connect GitHub if not already connected
   - Choose `swiffc/Project_Vulcan`
   - Render detects `render.yaml` automatically

3. **Review Services**
   Render will show all 6 services from config:
   ```
   ✅ vulcan-web (Web Service)
   ✅ vulcan-orchestrator (Web Service - Docker)
   ✅ vulcan-redis (Redis)
   ✅ vulcan-chroma (Web Service - Docker)
   ✅ vulcan-system-manager (Background Worker)
   ✅ vulcan-postgres (PostgreSQL)
   ```

4. **Click "Apply"**
   - Render creates all services
   - Initial deployment starts automatically

#### Option B: Manual (Alternative)

Create each service manually:

1. **Web Frontend**
   - Type: Web Service
   - Name: `vulcan-web`
   - Runtime: Node
   - Build: `cd apps/web && npm install && npm run build`
   - Start: `cd apps/web && npm start`
   - Root Directory: `apps/web`

2. **Orchestrator**
   - Type: Web Service
   - Name: `vulcan-orchestrator`
   - Runtime: Docker
   - Dockerfile Path: `docker/Dockerfile.orchestrator.tailscale`

3. **Redis, ChromaDB, System Manager, PostgreSQL**
   - Follow [render.yaml](config/render.yaml) configuration

### Step 3: Configure Environment Variables

See [.env.render.example](.env.render.example) for complete list.

#### For `vulcan-orchestrator`:

1. Go to service → **Environment** tab
2. Add these variables:

```bash
# CRITICAL - Must set manually
ANTHROPIC_API_KEY=sk-ant-api-03-xxxx
API_KEY=your-secure-key-here
TAILSCALE_AUTHKEY=tskey-auth-xxxx
DESKTOP_SERVER_URL=http://100.x.x.x:8000

# AUTO-SET by Render (no action needed)
REDIS_URL=<from vulcan-redis service>
CHROMA_HOST=<from vulcan-chroma service>
DATABASE_URL=<from vulcan-postgres service>
```

**Important:** Mark sensitive keys with "sync: false" (they already are in render.yaml)

#### For `vulcan-web`:

```bash
# AUTO-SET by Render
NEXT_PUBLIC_ORCHESTRATOR_URL=<from vulcan-orchestrator service>
DATABASE_URL=<from vulcan-postgres service>
```

#### For `vulcan-system-manager`:

```bash
BACKUP_ENABLED=true
HEALTH_CHECK_INTERVAL=3600

# AUTO-SET by Render
REDIS_URL=<from vulcan-redis service>
```

### Step 4: Deploy Services

1. **Check Build Status**
   - Each service shows build progress
   - Watch logs for errors
   - Wait for all to show "Live"

2. **Verify URLs**
   - Web: `https://vulcan-web.onrender.com`
   - API: `https://vulcan-orchestrator.onrender.com`
   - Docs: `https://vulcan-orchestrator.onrender.com/docs`

---

## Environment Variables

### Critical Variables (Set Manually)

#### ANTHROPIC_API_KEY
**Service:** vulcan-orchestrator, vulcan-web  
**Get From:** https://console.anthropic.com/settings/keys  
**Example:** `sk-ant-api-03-xxxxxxxxxxxx`  
**Purpose:** Claude AI API access

#### API_KEY
**Service:** vulcan-orchestrator  
**Generate:** Use secure random string  
**Example:** `vulcan-prod-key-abc123xyz789`  
**Purpose:** API authentication

#### TAILSCALE_AUTHKEY
**Service:** vulcan-orchestrator  
**Get From:** https://login.tailscale.com/admin/settings/keys  
**Example:** `tskey-auth-xxxxxxxxxxxx`  
**Purpose:** Connect cloud to desktop via Tailscale VPN  
**Settings:**
- ✅ Reusable: Yes
- ✅ Expiration: Never (or long duration)
- ⚠️ Ephemeral: No (for production)

#### DESKTOP_SERVER_URL
**Service:** vulcan-orchestrator  
**Format:** `http://100.x.x.x:8000`  
**Example:** `http://100.101.102.103:8000`  
**Purpose:** Desktop CAD server address (Tailscale IP)  
**How to Find:**
```bash
# On desktop, run:
tailscale ip -4
# Returns: 100.101.102.103
```

### Auto-Set Variables (No Action Needed)

These are automatically set by Render when you link services:

- `DATABASE_URL` - PostgreSQL connection
- `REDIS_URL` - Redis connection
- `CHROMA_HOST` - ChromaDB host
- `NEXT_PUBLIC_ORCHESTRATOR_URL` - Orchestrator URL

---

## Tailscale Configuration

Tailscale creates a secure VPN between Render cloud and your desktop.

### Why Tailscale?

- ✅ Secure encrypted tunnel
- ✅ No port forwarding needed
- ✅ Works behind firewalls/NAT
- ✅ Private IP addresses (100.x.x.x)
- ✅ Free for personal use

### Setup Steps

#### 1. Install Tailscale on Desktop

**Windows:**
```powershell
# Download from https://tailscale.com/download/windows
# Or use winget:
winget install tailscale.tailscale
```

**macOS:**
```bash
brew install tailscale
```

**Linux:**
```bash
curl -fsSL https://tailscale.com/install.sh | sh
```

#### 2. Start Tailscale on Desktop

```bash
# Start Tailscale
sudo tailscale up

# Get your Tailscale IP
tailscale ip -4
# Example output: 100.101.102.103
```

#### 3. Generate Auth Key for Render

1. Go to https://login.tailscale.com/admin/settings/keys
2. Click **"Generate auth key"**
3. Configure:
   - ✅ **Reusable:** Yes
   - ✅ **Expiration:** Never (or 90 days+)
   - ⚠️ **Ephemeral:** No (for production)
   - 📝 **Description:** "Render vulcan-orchestrator"
4. Click **"Generate key"**
5. Copy key (starts with `tskey-auth-`)

#### 4. Set Tailscale Variables in Render

1. Go to **vulcan-orchestrator** service
2. Click **Environment** tab
3. Add variables:
   ```bash
   TAILSCALE_AUTHKEY=tskey-auth-xxxxx
   DESKTOP_SERVER_URL=http://100.101.102.103:8000
   ```
4. Click **"Save Changes"**
5. Service will redeploy automatically

#### 5. Verify Tailscale Connection

After orchestrator redeploys:

```bash
# From Render logs, check for:
"Starting Tailscale..."
"Authenticating with Tailscale..."
"Connected to Tailscale network"
"Tailscale IP: 100.x.x.x"
```

Check health endpoint:
```bash
curl https://vulcan-orchestrator.onrender.com/health
# Should show: "desktop_server": "connected"
```

### Tailscale Troubleshooting

**Issue:** "Tailscale auth failed"
- ✅ Check `TAILSCALE_AUTHKEY` is correct
- ✅ Verify key hasn't expired
- ✅ Ensure key is marked "Reusable"

**Issue:** "Cannot reach desktop server"
- ✅ Confirm Tailscale running on desktop
- ✅ Verify desktop server on port 8000
- ✅ Check `DESKTOP_SERVER_URL` uses Tailscale IP (100.x.x.x)
- ✅ Test locally: `curl http://100.x.x.x:8000/health`

**Issue:** "Tailscale IP changes"
- Use Tailscale hostname instead: `http://your-desktop-name:8000`
- Or enable MagicDNS in Tailscale settings

---

## Troubleshooting

### Web Frontend Shows 404

**Symptoms:**
- `https://vulcan-web.onrender.com` returns 404
- Build succeeded but site not loading

**Solutions:**

1. **Check Build Logs**
   ```
   Render Dashboard → vulcan-web → Logs → Build
   Look for: "npm run build" success
   ```

2. **Verify Start Command**
   ```
   Should be: npm start (or npm run start)
   Located in: apps/web
   ```

3. **Check Environment Variables**
   ```bash
   NEXT_PUBLIC_ORCHESTRATOR_URL should be set
   DATABASE_URL should be set
   ```

4. **Manual Deploy**
   ```
   Render Dashboard → vulcan-web → Manual Deploy → Deploy latest commit
   ```

5. **Check Next.js Config**
   - Verify [apps/web/next.config.js](apps/web/next.config.js) is valid
   - Ensure Sentry config is optional (doesn't block build)

### Orchestrator Health Shows "desktop_server: unreachable"

**Symptoms:**
- Health endpoint returns: `{"desktop_server": "unreachable"}`
- API works but can't reach desktop

**Solutions:**

1. **Verify Tailscale on Desktop**
   ```bash
   # On desktop:
   tailscale status
   # Should show: "Connected"
   
   tailscale ip -4
   # Should show your IP: 100.x.x.x
   ```

2. **Check Desktop Server Running**
   ```bash
   # On desktop:
   curl http://localhost:8000/health
   # Should return health status
   ```

3. **Verify Render Environment**
   ```bash
   DESKTOP_SERVER_URL=http://100.x.x.x:8000  # Correct Tailscale IP
   TAILSCALE_AUTHKEY=tskey-auth-xxxxx        # Valid auth key
   ```

4. **Check Tailscale Logs**
   ```
   Render Dashboard → vulcan-orchestrator → Logs
   Look for: "Connected to Tailscale network"
   ```

5. **Test Connection**
   ```bash
   # From Render shell:
   curl http://100.x.x.x:8000/health
   # Should reach desktop
   ```

### Build Failures

**Docker Build Failed:**
- Check Dockerfile paths are correct
- Verify `requirements.txt` has all dependencies
- Check Docker logs for missing packages

**NPM Build Failed:**
- Verify `package.json` is valid
- Check for missing dependencies
- Review build logs for errors

**Database Migration Failed:**
- Check `DATABASE_URL` is set
- Verify PostgreSQL service is running
- Run migrations manually if needed

### Service Crashes on Start

**Check Logs:**
```
Render Dashboard → Service → Logs → Deploy
Look for error messages
```

**Common Issues:**
- Missing environment variables
- Invalid API keys
- Port conflicts
- Database connection errors
- Missing dependencies

**Solutions:**
- Set all required environment variables
- Validate API keys
- Check service health endpoints
- Review error stack traces

---

## Verification

### 1. Check All Services Online

Visit Render Dashboard and verify:
- ✅ vulcan-web: **Live**
- ✅ vulcan-orchestrator: **Live**
- ✅ vulcan-redis: **Available**
- ✅ vulcan-chroma: **Live**
- ✅ vulcan-system-manager: **Live**
- ✅ vulcan-postgres: **Available**

### 2. Test Endpoints

**Web Frontend:**
```bash
curl -I https://vulcan-web.onrender.com/
# Expected: HTTP/2 200
```

**Orchestrator Health:**
```bash
curl https://vulcan-orchestrator.onrender.com/health | jq .
# Expected:
# {
#   "status": "healthy",
#   "desktop_server": "connected",
#   "desktop_url": "http://100.x.x.x:8000"
# }
```

**API Documentation:**
```bash
open https://vulcan-orchestrator.onrender.com/docs
# Expected: Swagger UI loads
```

### 3. Test Full Integration

**From Web UI:**
1. Open https://vulcan-web.onrender.com
2. Navigate to strategies page
3. Should connect to orchestrator
4. Should be able to query CAD desktop (if Tailscale working)

**From API:**
```bash
# Test CAD integration
curl -X POST https://vulcan-orchestrator.onrender.com/api/cad/validate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"file": "test.SLDPRT"}'
# Should reach desktop and validate file
```

### 4. Monitor Logs

**Watch for Errors:**
```
Render Dashboard → Service → Logs
Filter by: Error, Warning
```

**Check Health:**
```bash
# Set up monitoring
watch -n 30 'curl -s https://vulcan-orchestrator.onrender.com/health | jq .'
```

---

## Success Checklist

- ✅ All 6 services deployed and live
- ✅ Web frontend loads without 404
- ✅ Orchestrator health check passes
- ✅ API documentation accessible
- ✅ Desktop server connected via Tailscale
- ✅ Database queries working
- ✅ Redis caching functional
- ✅ ChromaDB memory accessible
- ✅ No errors in logs
- ✅ Environment variables set correctly

---

## Maintenance

### Updating Services

**Via Git Push:**
```bash
git push origin main
# Render auto-deploys on push
```

**Manual Deploy:**
```
Render Dashboard → Service → Manual Deploy → Deploy latest commit
```

### Rotating Secrets

**Rotate API Keys:**
1. Generate new key
2. Update in Render environment
3. Test before removing old key

**Rotate Tailscale Key:**
1. Generate new auth key
2. Update `TAILSCALE_AUTHKEY`
3. Service redeploys automatically

### Monitoring

**Health Checks:**
- All services have automatic health checks
- Render monitors and restarts if unhealthy

**Logs:**
- View real-time logs in dashboard
- Download logs for analysis

**Alerts:**
- Set up email alerts in Render settings
- Monitor service downtime

---

## Costs

**Free Tier (Current Setup):**
- ✅ 750 hours/month per service (sufficient for 1 instance)
- ✅ PostgreSQL: 1 GB storage (free)
- ✅ Redis: 25 MB (free)
- ✅ Bandwidth: Shared free tier

**Limitations:**
- ⏱️ Services spin down after 15 min inactivity
- ⏱️ Cold starts take 30-60 seconds
- 📊 Limited to 1 instance per service

**Upgrade to Paid ($7/month per service):**
- ✅ Always-on (no spin down)
- ✅ Faster instances
- ✅ More bandwidth
- ✅ Background workers always running

---

## Security Best Practices

1. ✅ **Never commit `.env` files**
2. ✅ **Use strong API keys**
3. ✅ **Rotate secrets regularly**
4. ✅ **Enable Render's secret encryption**
5. ✅ **Use Tailscale for desktop access**
6. ✅ **Restrict API access with keys**
7. ✅ **Monitor logs for suspicious activity**
8. ✅ **Keep dependencies updated**

---

## Support

**Render Documentation:** https://render.com/docs  
**Tailscale Documentation:** https://tailscale.com/kb  
**Project Issues:** https://github.com/swiffc/Project_Vulcan/issues

---

**Last Updated:** December 25, 2024  
**Version:** 1.0
