#!/bin/bash
# Startup script for Vulcan Orchestrator with Tailscale

set -e

echo "Starting Tailscale..."

# Start Tailscale daemon
tailscaled --state=/var/lib/tailscale/tailscaled.state --socket=/var/run/tailscale/tailscaled.sock &

# Wait for tailscaled to start
sleep 2

# Authenticate with Tailscale
if [ -n "$TAILSCALE_AUTHKEY" ]; then
    echo "Authenticating with Tailscale..."
    tailscale up --authkey="$TAILSCALE_AUTHKEY" --hostname="vulcan-orchestrator"
    
    # Get Tailscale IP
    TAILSCALE_IP=$(tailscale ip -4)
    echo "Tailscale connected! IP: $TAILSCALE_IP"
else
    echo "WARNING: TAILSCALE_AUTHKEY not set. Skipping Tailscale authentication."
fi

echo "Starting Vulcan Orchestrator..."

# Start the orchestrator
exec uvicorn core.api:app --host 0.0.0.0 --port 8080
