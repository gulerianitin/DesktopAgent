#!/bin/bash

echo "🐳 Testing Desktop Agent Issue #3 in Docker with GUI"

# Allow X11 forwarding from Docker
xhost +local:docker

# Build the Docker image
echo "📦 Building Docker image with GUI support..."
docker build -f Dockerfile.gui-test -t desktop-agent-gui .

# Create a test guide script inside container
echo "🧪 Creating VLC installation test guide..."

# Run container with X11 forwarding
echo "🚀 Starting Docker container with GUI support..."
docker run -it --rm \
    --name desktop-agent-test \
    -e DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
    -v $PWD:/home/testuser/app \
    desktop-agent-gui bash -c "
        echo '=== Testing VLC Installation Guide ===';
        echo 'Step 1: Update package list';
        sudo apt update;
        echo '';
        echo 'Step 2: Install VLC media player';
        sudo apt install -y vlc;
        echo '';
        echo 'Step 3: Launch VLC to verify installation';
        vlc --intf qt &
        sleep 3;
        echo '';
        echo 'Step 4: Test Desktop Agent guide system';
        python3 test-guide-locally.py;
        echo '';
        echo '=== VLC should now be visible on your desktop! ===';
        echo 'Press Enter to continue or Ctrl+C to exit...';
        read;
        pkill vlc;
    "

# Reset X11 permissions
xhost -local:docker

echo "✅ Docker GUI test completed!"