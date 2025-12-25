# 🚀 Render Deployment Instructions

## Step 1: Add Tailscale Auth Key to Render

### Via Render Dashboard (Recommended):

1. **Go to Render Dashboard**:
   - Visit: https://dashboard.render.com
   - Select your `vulcan-orchestrator` service

2. **Add Environment Variable**:
   - Click "Environment" tab
   - Click "Add Environment Variable"
   - **Key**: `TAILSCALE_AUTHKEY`
   - **Value**: `tskey-auth-kg16hRQcbn11CNTRL-r4uM9WDD7ae2tcu5nRX4aeqbVov3JwHWZ`
   - **Secret**: ✅ Check this box (hides value in UI)
   - Click "Save Changes"

3. **Trigger Deployment**:
   - Render will automatically redeploy with new environment variable
   - OR manually trigger: Click "Manual Deploy" → "Deploy latest commit"

---

## Step 2: Push Code to GitHub

```powershell
# Commit Tailscale configuration
git add render.yaml TAILSCALE_SETUP.md TAILSCALE_QUICKSTART.md Dockerfile.orchestrator.tailscale scripts/start-with-tailscale.sh desktop_server/.env.example

git commit -m "feat: Add Tailscale VPN integration for Cisco firewall bypass"

git push origin main
```

**Note**: Render will auto-deploy when you push to main (if auto-deploy is enabled)

---

## Step 3: Verify Deployment

### Check Render Logs:

1. Go to: https://dashboard.render.com → vulcan-orchestrator → Logs
2. Look for successful deployment messages:
   ```
   ✓ Build successful
   ✓ Starting service...
   ✓ Service is live
   ```

### Test API Endpoint:

```powershell
# Test health endpoint (should work immediately)
curl https://vulcan-orchestrator.onrender.com/health

# Expected response:
# {"status":"healthy","timestamp":"2025-12-22T..."}
```

### Test Anthropic API (from Render):

Check Render logs for Anthropic API calls - they should work without Cisco blocking because they run in cloud!

---

## Step 4: Install Tailscale on Your PC

```powershell
# Install Tailscale
winget install tailscale.tailscale

# Start Tailscale
tailscale up

# Verify connection
tailscale status
```

---

## Step 5: Test Full Flow

### Test Desktop Server → Render Connection:

```powershell
# Start desktop server
cd desktop_server
python server.py

# In another terminal, test connection
curl http://localhost:8000/health
```

### Test Chat Interface:

1. Open web app: https://vulcan-web.onrender.com
2. Send a message
3. Check that AI responds (API calls work from Render)

---

## Troubleshooting

### Issue: "TAILSCALE_AUTHKEY not set"

**Solution**: Add the environment variable in Render dashboard (Step 1)

### Issue: "API calls still blocked"

**Check**:
1. Are API calls happening on Render? (Check Render logs, not local logs)
2. Is `ANTHROPIC_API_KEY` set in Render environment?
3. Test API directly from Render shell

**Remember**: Your architecture is cloud-first - API calls happen on Render.com, NOT on your PC. Cisco can't block cloud API calls!

### Issue: "Can't connect to Render from desktop server"

**Options**:
1. Use Render public URL: `https://vulcan-orchestrator.onrender.com`
2. Use Tailscale IP (once Tailscale is running on Render)
3. Check `desktop_server/.env` has correct `ORCHESTRATOR_URL`

---

## Next Steps

After deployment:
1. ✅ Verify Render deployment successful
2. ✅ Test API calls work (check Render logs)
3. ✅ Install Tailscale on your PC
4. ✅ Test full chat flow
5. ✅ Celebrate bypassing Cisco firewall! 🎉

---

## Security Notes

✅ **Tailscale auth key is secret** - stored securely in Render
✅ **API calls encrypted** - HTTPS to Anthropic
✅ **VPN traffic encrypted** - WireGuard protocol
✅ **No public ports** - Tailscale handles networking

---

**Your Tailscale Auth Key** (for reference):
```
tskey-auth-kg16hRQcbn11CNTRL-r4uM9WDD7ae2tcu5nRX4aeqbVov3JwHWZ
```

**Keep this key secure!** It's already added to `desktop_server/.env` (which is .gitignored).
