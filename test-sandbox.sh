#!/bin/bash
# Script to test the Desktop Agent in a safe Docker sandbox

echo "🐳 Building sandbox container..."
docker build -f Dockerfile.sandbox -t desktop-agent-sandbox .

echo "🚀 Starting sandbox (GUI will appear on your Windows desktop)..."
echo "Note: Close the application window to exit the container"

# For WSL with Windows Docker Desktop
if command -v docker.exe &> /dev/null; then
    echo "Using Windows Docker Desktop..."
    docker run --rm \
        -e DISPLAY=$DISPLAY \
        -v "$(pwd)":/home/testuser/app \
        desktop-agent-sandbox
else
    echo "Using WSL Docker Engine..."
    docker run --rm \
        -e DISPLAY=$DISPLAY \
        -v /tmp/.X11-unix:/tmp/.X11-unix \
        -v "$(pwd)":/home/testuser/app \
        desktop-agent-sandbox
fi

echo "✅ Sandbox session ended - your system is unchanged!"