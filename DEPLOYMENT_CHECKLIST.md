# Project Vulcan - Deployment Verification Checklist

**Last Updated**: Dec 22, 2025
**Purpose**: Verify all components are properly deployed and connected

---

## 🎯 **PRE-DEPLOYMENT CHECKLIST**

### **1. Environment Variables**

#### **Root `.env` (Orchestrator)**
- [ ] `ANTHROPIC_API_KEY` - Get from https://console.anthropic.com
- [ ] `DESKTOP_SERVER_URL` - Your PC's Tailscale IP `http://100.x.x.x:8000`
- [ ] `REDIS_URL` - Auto-populated by Render or `redis://localhost:6379`
- [ ] `TAILSCALE_AUTHKEY` - Get from https://login.tailscale.com/admin/settings/keys

#### **Desktop Server `.env`**
- [ ] `TOKEN_STORE_PATH` - `./data/tokens.enc`
- [ ] `TOKEN_ENCRYPTION_KEY` - Generate: `python -c "import secrets; print(secrets.token_hex(32))"`
- [ ] `ORCHESTRATOR_URL` - Render URL `https://vulcan-orchestrator.onrender.com`

#### **Web App `.env.local`**
- [ ] `ANTHROPIC_API_KEY` - Same as orchestrator
- [ ] `NEXT_PUBLIC_ORCHESTRATOR_URL` - `https://vulcan-orchestrator.onrender.com`
- [ ] `DESKTOP_SERVER_URL` - Tailscale IP `http://100.x.x.x:8000`

### **2. Render.com Setup**
- [ ] Create Render account
- [ ] Connect GitHub repo `swtflc/Project_Vulcan`
- [ ] Create `vulcan-redis` service (Free plan)
- [ ] Create `vulcan-orchestrator` service (Free plan)
- [ ] Create `vulcan-web` service (Free plan)
- [ ] All environment variables added to Render dashboard

### **3. Tailscale Setup**
- [ ] Install Tailscale on Windows PC: `winget install tailscale.tailscale`
- [ ] Run `tailscale up` on PC
- [ ] Get PC's Tailscale IP: `tailscale ip -4` → `100.x.x.x`
- [ ] Get Tailscale auth key from https://login.tailscale.com/admin/settings/keys
- [ ] Add `TAILSCALE_AUTHKEY` to Render environment

### **4. Local Development**
- [ ] Python 3.11 installed
- [ ] Node.js 18+ installed
- [ ] SolidWorks/Inventor installed (if using CAD features)
- [ ] Playwright installed: `pip install playwright && playwright install chromium`
- [ ] All `requirements.txt` dependencies installed

---

## 🚀 **DEPLOYMENT STEPS**

### **Phase 1: Render Services**

#### **Step 1.1: Deploy Redis**
```bash
# Should auto-deploy from render.yaml
# Verify status: Dashboard → vulcan-redis → Status: Live
```
- [ ] Redis service status: **Live** ✅
- [ ] Copy internal connection string: `redis://red-xxxxx:6379`

#### **Step 1.2: Deploy Orchestrator**
```bash
# Should auto-deploy from render.yaml
# Build command: pip install -r requirements.txt
# Start command: uvicorn core.api:app --host 0.0.0.0 --port 8080
```
- [ ] Orchestrator service status: **Live** ✅
- [ ] Build logs show: "Successfully installed anthropic..." ✅
- [ ] Runtime logs show: "Uvicorn running on http://0.0.0.0:8080" ✅
- [ ] Health check passes: `curl https://vulcan-orchestrator.onrender.com/health` ✅

#### **Step 1.3: Deploy Web Frontend**
```bash
# Should auto-deploy from render.yaml
# Build command: npm install && npm run build
# Start command: npm run start
```
- [ ] Web service status: **Live** ✅
- [ ] Build logs show: "Build successful" ✅
- [ ] Can access: `https://vulcan-web.onrender.com` ✅

### **Phase 2: Local Desktop Server**

#### **Step 2.1: Start Tailscale**
```bash
# On your Windows PC
tailscale up
tailscale status
# Note your IP: 100.x.x.x
```
- [ ] Tailscale connected ✅
- [ ] PC IP noted: `100.___.___.___`

#### **Step 2.2: Update Render Environment**
```bash
# In Render dashboard → vulcan-orchestrator → Environment
# Update DESKTOP_SERVER_URL to: http://100.x.x.x:8000
```
- [ ] `DESKTOP_SERVER_URL` updated with Tailscale IP ✅
- [ ] Service redeployed with new variable ✅

#### **Step 2.3: Start Desktop Server**
```bash
cd desktop_server
python server.py
# Should show: "Tailscale IP detected: 100.x.x.x"
# Should show: "Server running on http://100.x.x.x:8000"
```
- [ ] Desktop server running ✅
- [ ] Port 8000 open in Windows Firewall ✅
- [ ] Can access locally: `http://localhost:8000/health` ✅

---

## ✅ **VERIFICATION TESTS**

### **Test 1: Render Services Health**
```bash
# Test Redis
curl https://vulcan-orchestrator.onrender.com/health
# Expected: {"status": "healthy", "redis": "connected", ...}

# Test Orchestrator
curl https://vulcan-orchestrator.onrender.com/docs
# Expected: Swagger UI showing API endpoints

# Test Web Frontend
curl https://vulcan-web.onrender.com
# Expected: HTML page with "Project Vulcan"
```
- [ ] Orchestrator health check: **PASS** ✅
- [ ] Orchestrator API docs accessible: **PASS** ✅
- [ ] Web frontend loads: **PASS** ✅

### **Test 2: Tailscale Connectivity**
```bash
# From your PC, test Render can reach you
curl http://100.x.x.x:8000/health
# Expected: {"status": "healthy", "tailscale_ip": "100.x.x.x"}

# From Render, test it can reach your PC
# (Check orchestrator logs for desktop server connection)
```
- [ ] Desktop server reachable from PC: **PASS** ✅
- [ ] Orchestrator logs show desktop connection: **PASS** ✅

### **Test 3: End-to-End Chat**
```bash
# Open browser: https://vulcan-web.onrender.com
# Type message: "Hello, test connection"
# Expected: AI responds within 5 seconds
```
- [ ] Web UI loads ✅
- [ ] Chat input works ✅
- [ ] AI responds ✅
- [ ] No CORS errors in browser console ✅

### **Test 4: Desktop Control (Optional)**
```bash
# In web chat, type: "Take a screenshot"
# Expected: AI captures screenshot via desktop server
```
- [ ] Desktop commands route correctly ✅
- [ ] Screenshot captured ✅
- [ ] Image displayed in chat ✅

### **Test 5: CAD Integration (Optional)**
```bash
# Start SolidWorks on your PC
# In web chat, type: "Create a simple cube in SolidWorks"
# Expected: AI controls SolidWorks via desktop server
```
- [ ] SolidWorks launches ✅
- [ ] Part created via automation ✅

---

## 🔧 **TROUBLESHOOTING**

### **Issue: Orchestrator won't start**
**Symptoms**: Build succeeds, but service shows "Deploy failed"

**Checks**:
```bash
# 1. Check environment variables
✅ ANTHROPIC_API_KEY is set
✅ REDIS_URL is set (from vulcan-redis)
✅ DESKTOP_SERVER_URL is set

# 2. Check logs
Render Dashboard → vulcan-orchestrator → Logs
Look for: "ModuleNotFoundError" or "KeyError"

# 3. Common fixes:
- Missing ANTHROPIC_API_KEY → Add in Render dashboard
- Wrong Python version → Set PYTHON_VERSION=3.11
- Missing dependency → Check requirements.txt
```
- [ ] Issue resolved ✅

### **Issue: Can't connect to Desktop Server**
**Symptoms**: Orchestrator logs show "desktop_server: unreachable"

**Checks**:
```bash
# 1. Verify Tailscale on PC
tailscale status
# Should show: "logged in"

# 2. Verify desktop server running
curl http://localhost:8000/health
# Should return: {"status": "healthy"}

# 3. Check firewall
netsh advfirewall firewall add rule name="Vulcan Desktop Server" dir=in action=allow protocol=TCP localport=8000

# 4. Verify DESKTOP_SERVER_URL in Render
# Should be: http://100.x.x.x:8000 (NOT localhost!)
```
- [ ] Issue resolved ✅

### **Issue: CORS errors in browser**
**Symptoms**: Browser console shows "CORS policy" errors

**Checks**:
```python
# Check core/api.py line 34:
allow_origins=[
    "https://vulcan-web.onrender.com",  # Must match your web URL
    "http://localhost:3000",
]

# Common fixes:
- Update allow_origins with correct web URL
- Redeploy orchestrator
- Clear browser cache
```
- [ ] Issue resolved ✅

### **Issue: Web app shows "Cannot connect to orchestrator"**
**Symptoms**: Chat doesn't work, shows connection error

**Checks**:
```bash
# 1. Verify NEXT_PUBLIC_ORCHESTRATOR_URL
# In Render → vulcan-web → Environment
# Should be: https://vulcan-orchestrator.onrender.com

# 2. Test orchestrator directly
curl https://vulcan-orchestrator.onrender.com/health

# 3. Check browser console for exact error
# Press F12 → Console tab
```
- [ ] Issue resolved ✅

---

## 📊 **DEPLOYMENT STATUS DASHBOARD**

| Component | Status | URL | Notes |
|-----------|--------|-----|-------|
| **Render Redis** | ⚪ Not Started | Internal only | |
| **Render Orchestrator** | ⚪ Not Started | https://vulcan-orchestrator.onrender.com | |
| **Render Web** | ⚪ Not Started | https://vulcan-web.onrender.com | |
| **Tailscale (PC)** | ⚪ Not Started | 100.x.x.x | |
| **Desktop Server** | ⚪ Not Started | http://100.x.x.x:8000 | |
| **End-to-End Chat** | ⚪ Not Tested | - | |

**Legend**: ⚪ Not Started | 🟡 In Progress | ✅ Complete | ❌ Failed

---

## 🎯 **SUCCESS CRITERIA**

All items below must be ✅ for production-ready:

- [ ] ✅ All 3 Render services deployed and **Live**
- [ ] ✅ Tailscale connected on PC with IP `100.x.x.x`
- [ ] ✅ Desktop server running and reachable via Tailscale
- [ ] ✅ Web UI loads at `https://vulcan-web.onrender.com`
- [ ] ✅ Chat works end-to-end (user → web → orchestrator → AI → response)
- [ ] ✅ Desktop commands route correctly (orchestrator → Tailscale → desktop server)
- [ ] ✅ No CORS errors in browser console
- [ ] ✅ Health checks pass for all services
- [ ] ✅ API response time < 5 seconds for chat

---

## 📅 **DEPLOYMENT TIMELINE**

**Estimated Time**: 2-3 hours (first time)

| Phase | Duration | Tasks |
|-------|----------|-------|
| **Prep** | 30 min | Get API keys, install Tailscale, create .env files |
| **Render Setup** | 45 min | Create services, configure env vars, deploy |
| **Tailscale** | 15 min | Connect PC, update DESKTOP_SERVER_URL |
| **Desktop Server** | 15 min | Start server, verify connection |
| **Testing** | 30 min | Run all verification tests |
| **Troubleshooting** | 30 min | Fix any issues found |

---

## 🔐 **SECURITY CHECKLIST**

Before going to production:

- [ ] All `.env` files in `.gitignore` ✅
- [ ] No API keys committed to GitHub ✅
- [ ] Tailscale auth key rotated after setup ✅
- [ ] Desktop server only accessible via Tailscale ✅
- [ ] CORS restricted to known origins ✅
- [ ] Rate limiting enabled (future) ⚪
- [ ] API authentication enabled (future) ⚪

---

## 📝 **POST-DEPLOYMENT**

After successful deployment:

1. **Monitor Render logs** for errors (first 24 hours)
2. **Test from multiple devices** (PC, phone, tablet)
3. **Document your Tailscale IP** in a secure location
4. **Set up monitoring** (Render alerts, Sentry)
5. **Create backup** of all environment variables
6. **Update README.md** with production URLs

---

## 🆘 **GET HELP**

If stuck:
1. Check Render logs: Dashboard → Service → Logs
2. Check browser console: F12 → Console tab
3. Test health endpoints: `/health` on all services
4. Review this checklist from the top
5. Share error logs for diagnosis

**Render Support**: https://render.com/docs
**Tailscale Docs**: https://tailscale.com/kb
**Project Issues**: https://github.com/swtflc/Project_Vulcan/issues
