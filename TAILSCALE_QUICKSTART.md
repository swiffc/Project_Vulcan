# Quick Start: Tailscale VPN Setup

## For Your PC (Windows)

### 1. Install Tailscale
```powershell
winget install tailscale.tailscale
```

### 2. Start Tailscale
```powershell
tailscale up
```

### 3. Verify Connection
```powershell
tailscale status
```

---

## For Render.com

### 1. Get Tailscale Auth Key
- Visit: https://login.tailscale.com/admin/settings/keys
- Create new key (Reusable: Yes, Ephemeral: No)
- Copy the key (starts with `tskey-auth-...`)

### 2. Add to Render Environment
- Go to: https://dashboard.render.com
- Select: `vulcan-orchestrator`
- Environment tab → Add Variable:
  - **Key**: `TAILSCALE_AUTHKEY`
  - **Value**: `tskey-auth-...`
  - **Secret**: ✅

### 3. Deploy
```bash
git add render.yaml
git commit -m "feat: Add Tailscale VPN support"
git push origin main
```

---

## Test Connection

```powershell
# After Render deploys, check logs for Tailscale IP
# Then test connection:
curl http://100.x.x.x:8080/health
```

---

## Important Notes

✅ **Your architecture is already correct!**
- All Anthropic API calls happen on Render.com (cloud)
- Your PC only does mouse/keyboard control
- Cisco firewall won't block API calls

🔒 **Tailscale Benefits:**
- Secure encrypted tunnel between PC and Render
- No public ports needed
- Bypasses corporate firewall for PC ↔ Render communication

📖 **Full Documentation**: See `TAILSCALE_SETUP.md`

---

## Troubleshooting

**Can't install Tailscale?**
- Use personal hotspot instead of corporate WiFi
- Or use Render's public URL (no VPN needed for API calls)

**API calls still blocked?**
- Check Render logs (not local logs)
- API calls should work because they run in cloud
- Cisco only affects your local PC, not Render.com
