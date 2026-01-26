#!/bin/bash
# Desktop Agent - Web Chatbot with VNC Desktop
set -e

echo "🤖 Desktop Agent - Web Interface"
echo "================================="
echo ""

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker stop agent-chatbot 2>/dev/null || true
docker stop agent-unified 2>/dev/null || true

# Build
echo "🔨 Building Docker image..."
docker build -f Dockerfile.chatbot -t desktop-agent-chatbot .

echo ""
echo "🚀 Starting container..."

# Run
docker run -d --rm \
    --name agent-chatbot \
    -p 8000:8000 \
    -p 6080:6080 \
    -v "$(pwd)/.env:/app/.env:ro" \
    desktop-agent-chatbot

sleep 6

echo ""
echo "✅ Container started!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🌐 Access Your Desktop Agent"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  Open in browser:"
echo "  👉 http://localhost:8000"
echo ""
echo "  You'll see:"
echo "  • Left: AI Chatbot (install apps)"
echo "  • Right: VNC Desktop (launch apps)"
echo "  • All in ONE browser window!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "💡 Try this workflow:"
echo ""
echo "  1. In chatbot: 'Install GIMP'"
echo "  2. Watch it install in real-time"
echo "  3. In VNC panel (right), open terminal"
echo "  4. Type: gimp &"
echo "  5. Watch GIMP launch!"
echo ""
echo "🛑 To stop: docker stop agent-chatbot"
echo ""
