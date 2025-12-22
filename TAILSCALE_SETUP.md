# Tailscale VPN Setup for Project Vulcan

**Purpose**: Bypass Cisco firewall restrictions by routing traffic through Tailscale VPN. All Anthropic API calls happen on Render.com (cloud), avoiding corporate network blocks.

---

## Architecture Overview

```
YOUR PC (Cisco Network)
├── Desktop Control Server (MCP)
│   ├── Mouse/Keyboard control ✅
│   ├── Screenshot capture ✅
│   └── NO API calls ✅
│
└── Tailscale Client
        ↓ (Encrypted VPN Tunnel)
        
RENDER.COM (Cloud - No Cisco)
├── Orchestrator + Agents
│   └── core/llm.py (ALL Anthropic API calls) ✅
│
└── Direct HTTPS → Anthropic API ✅
```

**Key Point**: Your architecture is already correct! API calls happen in cloud, not on your PC.

---

## Setup Steps

### 1. Install Tailscale on Your PC

```powershell
# Option A: Download installer
# Visit: https://tailscale.com/download/windows

# Option B: Install via winget
winget install tailscale.tailscale

# Start Tailscale
tailscale up

# Verify connection
tailscale status
```

### 2. Get Tailscale Auth Key (for Render.com)

```bash
# Visit: https://login.tailscale.com/admin/settings/keys
# Create a new auth key:
# - Description: "Render.com Orchestrator"
# - Reusable: Yes (recommended)
# - Ephemeral: No
# - Tags: render, vulcan

# Copy the key (starts with tskey-auth-...)
```

### 3. Add Tailscale to Render.com

**Option A: Add to render.yaml** (Recommended - already configured for you)

The updated `render.yaml` includes Tailscale environment variable. You just need to:

1. Go to Render Dashboard: https://dashboard.render.com
2. Select `vulcan-orchestrator` service
3. Go to "Environment" tab
4. Add new environment variable:
   - **Key**: `TAILSCALE_AUTHKEY`
   - **Value**: `tskey-auth-...` (your auth key from step 2)
   - **Secret**: ✅ (check this box)

**Option B: Use Dockerfile** (Alternative - more control)

If you want Tailscale running in the container, use the updated `Dockerfile.orchestrator.tailscale` (created for you).

### 4. Configure Desktop Server Connection

Update your desktop server to connect to Render via Tailscale:

```bash
# In desktop_server/.env (create if doesn't exist)
ORCHESTRATOR_URL=http://100.x.x.x:8080  # Tailscale IP of Render service
```

To find Render's Tailscale IP:
```bash
# On Render (check logs or run command):
tailscale ip -4
```

### 5. Test Connection

```powershell
# On your PC, test connection to Render orchestrator
curl http://100.x.x.x:8080/health

# Should return:
# {"status": "healthy", "timestamp": "..."}
```

### 6. Verify API Calls Work

```powershell
# Test that Anthropic API calls work from Render (not blocked)
# This happens automatically when you use the chatbot

# Check Render logs:
# https://dashboard.render.com → vulcan-orchestrator → Logs

# Look for successful API calls (no SSL errors, no timeouts)
```

---

## Configuration Files Created

1. ✅ **render.yaml** - Updated with Tailscale environment variable
2. ✅ **Dockerfile.orchestrator.tailscale** - Alternative Docker config with Tailscale
3. ✅ **desktop_server/.env.example** - Desktop server environment template
4. ✅ **TAILSCALE_SETUP.md** - This file

---

## Troubleshooting

### Issue: "Tailscale not connecting"

```powershell
# Check Tailscale status
tailscale status

# Restart Tailscale
tailscale down
tailscale up

# Check firewall
# Ensure Windows Firewall allows Tailscale
```

### Issue: "Can't reach Render orchestrator"

```powershell
# Verify Tailscale IPs
tailscale status

# Ping Render service
ping 100.x.x.x

# Check Render logs for Tailscale startup
```

### Issue: "API calls still blocked"

**This should NOT happen** because:
- API calls happen on Render.com (cloud)
- Render is not on your corporate network
- No Cisco firewall in cloud

If you still see errors:
1. Check Render logs (not local logs)
2. Verify `ANTHROPIC_API_KEY` is set in Render environment
3. Test API directly from Render:
   ```bash
   # In Render shell:
   curl https://api.anthropic.com/v1/messages \
     -H "x-api-key: $ANTHROPIC_API_KEY" \
     -H "anthropic-version: 2023-06-01"
   ```

---

## Security Notes

### ✅ What's Secure:

- Tailscale uses WireGuard (military-grade encryption)
- All traffic encrypted end-to-end
- No public ports opened on your PC
- Cisco can't inspect Tailscale traffic (encrypted)

### ⚠️ What to Know:

- Tailscale traffic is visible to Cisco (they see encrypted tunnel)
- Some corporate policies may block VPNs entirely
- If blocked, use personal hotspot as fallback

---

## Alternative: No Tailscale Needed

**Your current architecture doesn't require Tailscale for API calls!**

```
Option 1 (Current - Recommended):
PC → Internet → Render.com → Anthropic API ✅
(Render makes API calls, not your PC)

Option 2 (With Tailscale):
PC → Tailscale → Render.com → Anthropic API ✅
(More secure communication between PC and Render)

Option 3 (Not Recommended):
PC → Anthropic API ❌
(Blocked by Cisco)
```

**Recommendation**: Use Tailscale for secure PC ↔ Render communication, but API calls already work because they happen in cloud.

---

## Next Steps

1. ✅ Install Tailscale on your PC
2. ✅ Get Tailscale auth key
3. ✅ Add `TAILSCALE_AUTHKEY` to Render environment
4. ✅ Deploy updated render.yaml
5. ✅ Test connection
6. ✅ Verify API calls work (check Render logs)

---

**Status**: Ready to deploy! Your architecture is already cloud-first. Tailscale adds secure communication layer.
