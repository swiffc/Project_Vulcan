#!/bin/bash
# Quick Render Deployment Fixes
# Run this script to apply all fixes before deploying to Render

set -e

echo "🔧 Applying Render Deployment Fixes..."

# 1. Remove duplicate render.yaml if exists
if [ -f "apps/web/render.yaml" ]; then
    echo "❌ Removing duplicate apps/web/render.yaml..."
    rm -f apps/web/render.yaml
    echo "✅ Removed duplicate config"
fi

# 2. Verify main render.yaml exists
if [ ! -f "config/render.yaml" ]; then
    echo "❌ ERROR: config/render.yaml not found!"
    exit 1
fi
echo "✅ Main config/render.yaml exists"

# 3. Verify all Dockerfiles exist
echo "🔍 Checking Dockerfiles..."
DOCKERFILES=(
    "docker/Dockerfile.orchestrator.tailscale"
    "docker/Dockerfile.chroma"
    "docker/Dockerfile.system-manager"
)

for dockerfile in "${DOCKERFILES[@]}"; do
    if [ ! -f "$dockerfile" ]; then
        echo "❌ ERROR: $dockerfile not found!"
        exit 1
    fi
    echo "✅ $dockerfile exists"
done

# 4. Verify Tailscale startup script
if [ ! -f "scripts/start-with-tailscale.sh" ]; then
    echo "❌ ERROR: scripts/start-with-tailscale.sh not found!"
    exit 1
fi
echo "✅ Tailscale startup script exists"

# 5. Make startup script executable
chmod +x scripts/start-with-tailscale.sh
echo "✅ Made startup script executable"

# 6. Verify Next.js app structure
if [ ! -f "apps/web/package.json" ]; then
    echo "❌ ERROR: apps/web/package.json not found!"
    exit 1
fi
echo "✅ Next.js app structure valid"

# 7. Check for .env.render.example
if [ ! -f ".env.render.example" ]; then
    echo "⚠️  WARNING: .env.render.example not found (should be created)"
else
    echo "✅ Environment variable template exists"
fi

# 8. Verify requirements.txt
if [ ! -f "requirements.txt" ]; then
    echo "❌ ERROR: requirements.txt not found!"
    exit 1
fi
echo "✅ Python requirements.txt exists"

# 9. Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ All Render deployment fixes applied!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 Next Steps:"
echo "1. Commit and push changes to GitHub"
echo "2. Go to Render dashboard: https://dashboard.render.com"
echo "3. Create new Blueprint from repository"
echo "4. Set environment variables (see .env.render.example)"
echo "5. Deploy all services"
echo ""
echo "📖 Full guide: RENDER_DEPLOYMENT_GUIDE.md"
echo "🔑 Environment vars: .env.render.example"
echo "📊 Current status: RENDER_STATUS.md"
echo ""
