#!/bin/bash
# Simple script to check if apps are installed in the container

echo "Testing app detection in container..."
echo ""

echo "1. Testing 'which' command:"
docker exec desktop-agent-running which gimp inkscape libreoffice vlc code 2>&1

echo ""
echo "2. Testing package list:"
docker exec desktop-agent-running dpkg -l 2>&1 | grep -E '^ii.*(gimp|inkscape|libreoffice|vlc|code)'

echo ""
echo "3. Testing direct execution:"
docker exec desktop-agent-running bash -c "command -v gimp && echo 'GIMP found' || echo 'GIMP not found'"
docker exec desktop-agent-running bash -c "command -v inkscape && echo 'Inkscape found' || echo 'Inkscape not found'"
docker exec desktop-agent-running bash -c "command -v libreoffice && echo 'LibreOffice found' || echo 'LibreOffice not found'"
docker exec desktop-agent-running bash -c "command -v vlc && echo 'VLC found' || echo 'VLC not found'"
docker exec desktop-agent-running bash -c "command -v code && echo 'VS Code found' || echo 'VS Code not found'"

echo ""
echo "4. Checking desktop shortcut:"
docker exec desktop-agent-running cat /home/appuser/check-apps.sh 2>&1 | head -20

echo ""
echo "5. Running check script:"
docker exec desktop-agent-running /home/appuser/check-apps.sh < /dev/null 2>&1
