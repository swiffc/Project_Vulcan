# 🚀 RENDER DEPLOYMENT - DO THIS NOW

**Current Time**: Dec 22, 2025
**Goal**: Get vulcan-orchestrator running on Render in next 60 minutes

---

## ⏱️ **60-MINUTE DEPLOYMENT PLAN**

### **Phase 1: Fix Render Environment (15 minutes)**

#### **Step 1.1: Get Your Anthropic API Key** (5 min)
1. Go to: https://console.anthropic.com/settings/keys
2. Click **"Create Key"**
3. Name it: `Vulcan Production`
4. Copy the key: `sk-ant-api-03-xxxxxxxxxxxxxxxxxxxxx`
5. **SAVE IT SOMEWHERE SAFE** (you'll need it in next step)

#### **Step 1.2: Update Render Dashboard** (10 min)
1. Open your Render dashboard: https://dashboard.render.com
2. Click **"vulcan-orchestrator"** service
3. Click **"Environment"** in left sidebar
4. Click **"Edit"** button (top right)

**Add this variable**:
```
Key: ANTHROPIC_API_KEY
Value: [Paste your key from Step 1.1]
```

**Rename this variable**:
```
OLD: TAILSCALE_AUTH
NEW: TAILSCALE_AUTHKEY
(Keep the same value, just change the name)
```

**Delete this variable**:
```
DELETE: DATABASE_URL
(We don't have PostgreSQL yet)
```

**Verify these exist**:
```
✅ PYTHON_VERSION = 3.11
✅ DESKTOP_SERVER_URL = ************
✅ TAILSCALE_AUTHKEY = ************ (just renamed)
✅ REDIS_URL = redis://red-xxxxx:6379 (auto-populated)
✅ ANTHROPIC_API_KEY = sk-ant-api-03-****** (just added)
```

5. Click **"Save Changes"**
6. Service will redeploy automatically (2-3 minutes)

---

### **Phase 2: Verify Deployment** (10 minutes)

#### **Step 2.1: Watch Build Logs** (3 min)
1. In Render dashboard, stay on **vulcan-orchestrator**
2. Click **"Logs"** tab (left sidebar)
3. Wait for build to complete

**Look for SUCCESS**:
```bash
==> Running 'pip install -r requirements.txt'
Successfully installed anthropic-0.18.1...
==> Build successful!
==> Starting service...
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8080
```

**If you see ERRORS**:
```bash
ERROR: Could not find ANTHROPIC_API_KEY
→ Go back to Step 1.2, add the key

ModuleNotFoundError: No module named 'X'
→ Missing dependency in requirements.txt
→ Share error with me
```

#### **Step 2.2: Check Service Status** (2 min)
1. Go to **Render Dashboard** → **My Workspace**
2. Verify ALL services show **"Live"** ✅:
   ```
   vulcan-redis         ● Live
   vulcan-orchestrator  ● Live  ← Should be green now!
   vulcan-web           ● Live
   ```

#### **Step 2.3: Test Health Endpoint** (5 min)
Open Command Prompt and run:
```bash
curl https://vulcan-orchestrator.onrender.com/health
```

**EXPECTED RESPONSE**:
```json
{
  "status": "healthy",
  "desktop_server": "unreachable",
  "desktop_url": "http://localhost:8765",
  "version": "1.0.0"
}
```

**Note**: `desktop_server: "unreachable"` is NORMAL (we haven't started it yet)

**If you get ERROR**:
```bash
Could not resolve host
→ Service not deployed yet, wait 1 more minute

Timeout
→ Service crashed, check logs in Step 2.1
```

---

### **Phase 3: Test Web Frontend** (5 minutes)

#### **Step 3.1: Check Web Service**
```bash
curl https://vulcan-web.onrender.com
```

**EXPECTED**: HTML page with "Project Vulcan"

#### **Step 3.2: Open in Browser**
1. Open browser: https://vulcan-web.onrender.com
2. You should see the chat interface
3. **Don't test chat yet** (orchestrator needs Anthropic key to work)

---

### **Phase 4: Setup Tailscale** (15 minutes)

#### **Step 4.1: Install Tailscale on Your PC** (5 min)
Open PowerShell as Administrator:
```powershell
# Install Tailscale
winget install tailscale.tailscale

# Start Tailscale
tailscale up

# Check status
tailscale status
```

**EXPECTED OUTPUT**:
```
100.x.x.x   your-pc-name   -
logged in as: your-email@example.com
```

#### **Step 4.2: Get Your Tailscale IP** (2 min)
```powershell
tailscale ip -4
```

**EXAMPLE OUTPUT**: `100.101.102.103`

**IMPORTANT**: Write this down! You'll need it in next step:
```
MY TAILSCALE IP: 100.___.___.___
```

#### **Step 4.3: Update Render with Tailscale IP** (5 min)
1. Go back to Render Dashboard → **vulcan-orchestrator** → **Environment**
2. Click **"Edit"**
3. Find `DESKTOP_SERVER_URL`
4. Change value from `************` to:
   ```
   http://100.YOUR.IP.HERE:8000
   ```
   Example: `http://100.101.102.103:8000`
5. Click **"Save Changes"**
6. Wait for redeploy (2 min)

#### **Step 4.4: Open Windows Firewall** (3 min)
Open PowerShell as Administrator:
```powershell
# Allow port 8000 for Desktop Server
netsh advfirewall firewall add rule name="Vulcan Desktop Server" dir=in action=allow protocol=TCP localport=8000

# Verify rule added
netsh advfirewall firewall show rule name="Vulcan Desktop Server"
```

---

### **Phase 5: Start Desktop Server** (10 minutes)

#### **Step 5.1: Navigate to Desktop Server** (1 min)
Open Command Prompt:
```bash
cd C:\Users\DCornealius\Documents\GitHub\Project_Vulcan_Fresh\desktop_server
```

#### **Step 5.2: Create .env File** (3 min)
```bash
# Copy example to .env
copy .env.example .env

# Edit .env with Notepad
notepad .env
```

**Update these values in .env**:
```bash
# Change this line:
ORCHESTRATOR_URL=http://100.x.x.x:8080

# To your Render URL:
ORCHESTRATOR_URL=https://vulcan-orchestrator.onrender.com

# Save and close Notepad
```

#### **Step 5.3: Start Server** (2 min)
```bash
python server.py
```

**EXPECTED OUTPUT**:
```
INFO: Tailscale IP detected: 100.101.102.103
INFO: Server running on http://100.101.102.103:8000
INFO: Press CTRL+C to quit
```

#### **Step 5.4: Test Locally** (2 min)
**Keep server running**, open NEW Command Prompt:
```bash
curl http://localhost:8000/health
```

**EXPECTED RESPONSE**:
```json
{
  "status": "healthy",
  "tailscale_ip": "100.101.102.103",
  "version": "1.0.0"
}
```

#### **Step 5.5: Test from Tailscale IP** (2 min)
```bash
curl http://100.YOUR.IP.HERE:8000/health
```

**Should get same response as Step 5.4**

---

### **Phase 6: End-to-End Verification** (5 minutes)

#### **Step 6.1: Test Orchestrator → Desktop Connection** (2 min)
```bash
curl https://vulcan-orchestrator.onrender.com/health
```

**NOW desktop_server should be "connected"**:
```json
{
  "status": "healthy",
  "desktop_server": "connected",  ← Should say "connected" now!
  "desktop_url": "http://100.101.102.103:8000",
  "version": "1.0.0"
}
```

#### **Step 6.2: Test Web UI Chat** (3 min)
1. Open browser: https://vulcan-web.onrender.com
2. Type in chat: `"Hello, are you working?"`
3. Press Enter
4. **Should get AI response within 5 seconds**

**If chat works**: ✅ **DEPLOYMENT COMPLETE!**

**If chat doesn't work**:
- Open browser console (F12)
- Look for error messages
- Share the error with me

---

## ✅ **SUCCESS CHECKLIST**

Mark these as you complete them:

- [ ] Phase 1: Render environment variables updated
- [ ] Phase 2: All 3 Render services show "Live"
- [ ] Phase 3: Web frontend loads
- [ ] Phase 4: Tailscale installed and IP obtained
- [ ] Phase 5: Desktop server running on PC
- [ ] Phase 6: End-to-end chat works

---

## 🆘 **TROUBLESHOOTING**

### **Issue: Orchestrator won't start**
**Check Render Logs**:
```
Render Dashboard → vulcan-orchestrator → Logs

Look for:
"ANTHROPIC_API_KEY not found"
→ Add the key in Environment

"Cannot connect to redis"
→ Check vulcan-redis service is Live
```

### **Issue: Desktop server won't start**
**Check Python errors**:
```bash
# Make sure you're in desktop_server directory
cd desktop_server

# Check Python version
python --version
# Should be 3.11 or higher

# Install dependencies if missing
pip install -r requirements.txt

# Try again
python server.py
```

### **Issue: Can't access Tailscale IP**
**Verify Tailscale is running**:
```bash
tailscale status
# Should show "logged in"

# Try ping
ping 100.YOUR.IP.HERE
# Should respond

# Check firewall
netsh advfirewall firewall show rule name="Vulcan Desktop Server"
# Should show rule exists
```

### **Issue: Chat doesn't work**
**Open browser console (F12)**:
```
Look for errors like:
"CORS policy"
→ Check core/api.py allow_origins

"Cannot connect to orchestrator"
→ Check NEXT_PUBLIC_ORCHESTRATOR_URL in web .env

"Network error"
→ Check orchestrator health endpoint first
```

---

## 📊 **DEPLOYMENT STATUS TRACKER**

Use this to track your progress:

| Step | Task | Status | Time |
|------|------|--------|------|
| 1.1 | Get Anthropic API key | ⚪ | 5 min |
| 1.2 | Update Render environment | ⚪ | 10 min |
| 2.1 | Watch build logs | ⚪ | 3 min |
| 2.2 | Check service status | ⚪ | 2 min |
| 2.3 | Test health endpoint | ⚪ | 5 min |
| 3.1 | Test web service | ⚪ | 5 min |
| 4.1 | Install Tailscale | ⚪ | 5 min |
| 4.2 | Get Tailscale IP | ⚪ | 2 min |
| 4.3 | Update Render with IP | ⚪ | 5 min |
| 4.4 | Open firewall | ⚪ | 3 min |
| 5.1 | Navigate to desktop_server | ⚪ | 1 min |
| 5.2 | Create .env file | ⚪ | 3 min |
| 5.3 | Start server | ⚪ | 2 min |
| 5.4 | Test locally | ⚪ | 2 min |
| 5.5 | Test via Tailscale | ⚪ | 2 min |
| 6.1 | Test orchestrator connection | ⚪ | 2 min |
| 6.2 | Test web UI chat | ⚪ | 3 min |

**Legend**: ⚪ Not Started | 🟡 In Progress | ✅ Complete | ❌ Failed

---

## 🎯 **WHAT YOU'LL HAVE AFTER THIS**

✅ Vulcan orchestrator running on Render (cloud)
✅ Web UI accessible from anywhere
✅ Desktop server connected via Tailscale
✅ End-to-end chat working
✅ Can control your PC remotely
✅ Production-ready architecture

---

## 📞 **GET HELP**

If stuck at any step:
1. **Take a screenshot** of the error
2. **Copy the error message**
3. **Tell me which step you're on**
4. I'll help you debug!

---

**START NOW with Phase 1, Step 1.1!** ⏱️
