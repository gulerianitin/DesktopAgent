#!/bin/bash
# Quick script to restart the Desktop Agent container

echo "🔄 Restarting Desktop Agent..."

# Stop existing container
docker stop desktop-agent-running 2>/dev/null || true

# Start fresh container
docker run -d --rm \
    --name desktop-agent-running \
    -p 5901:5901 \
    -v "$(pwd)/.env:/app/.env:ro" \
    -v "$(pwd)/logs:/app/logs" \
    desktop-agent

sleep 3

echo ""
echo "✅ Desktop Agent restarted!"
echo ""
echo "📺 Connect with VNC:"
echo "   vncviewer localhost:5901"
echo "   Password: password"
echo ""
echo "🛑 To stop: docker stop desktop-agent-running"
echo ""
