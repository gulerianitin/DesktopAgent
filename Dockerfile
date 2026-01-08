# MINIMAL Ubuntu Desktop - Start with almost nothing to show installations clearly
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install ONLY the absolute minimum for desktop + VNC
RUN apt-get update && apt-get install -y \
    xfce4 \
    xfce4-terminal \
    x11vnc \
    xvfb \
    python3 \
    python3-pip \
    python3-venv \
    python3-tk \
    wget \
    curl \
    sudo \
    gpg \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release \
    && rm -rf /var/lib/apt/lists/*

# Explicitly REMOVE any pre-installed apps that might confuse the demo
RUN apt-get update && apt-get remove -y \
    firefox \
    thunderbird \
    libreoffice* \
    gimp \
    inkscape \
    vlc \
    2>/dev/null || true && \
    rm -rf /var/lib/apt/lists/*

# Create app user with sudo privileges and NO password for auto-login
RUN useradd -m -s /bin/bash -G sudo appuser && \
    passwd -d appuser && \
    echo "appuser ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

WORKDIR /app

# Copy application files
COPY requirements.txt .
RUN python3 -m venv /app/venv && \
    /app/venv/bin/pip install --upgrade pip && \
    /app/venv/bin/pip install -r requirements.txt

ENV PATH="/app/venv/bin:$PATH"

COPY --chown=appuser:appuser . .

# Create necessary directories
RUN mkdir -p /home/appuser/Downloads /app/logs && \
    chown -R appuser:appuser /app /home/appuser

USER appuser
WORKDIR /app

# Environment variables
ENV DISPLAY=:1
ENV WATCH_FOLDER=/home/appuser/Downloads
ENV USER=appuser
ENV HOME=/home/appuser

EXPOSE 5901

# Configure XFCE to auto-login and not lock screen
RUN mkdir -p /home/appuser/.config/xfce4/xfconf/xfce-perchannel-xml && \
    echo '<?xml version="1.0" encoding="UTF-8"?>\n\
<channel name="xfce4-session" version="1.0">\n\
  <property name="general" type="empty">\n\
    <property name="AutoSave" type="bool" value="false"/>\n\
    <property name="SaveOnExit" type="bool" value="false"/>\n\
  </property>\n\
  <property name="sessions" type="empty"/>\n\
</channel>' > /home/appuser/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-session.xml && \
    chown -R appuser:appuser /home/appuser/.config

# Create helper script with proper permissions
RUN cat > /home/appuser/check-apps.sh << 'EOFSCRIPT'
#!/bin/bash
echo "═══════════════════════════════════════════════════════"
echo "  📦 INSTALLED GUI APPLICATIONS"
echo "═══════════════════════════════════════════════════════"
echo ""
echo "Checking for installed applications..."
echo ""

installed_apps=""

# Check GIMP
if command -v gimp &> /dev/null; then
    echo "✅ GIMP - Image editor (gimp)"
    installed_apps="yes"
fi

# Check Inkscape
if command -v inkscape &> /dev/null; then
    echo "✅ Inkscape - Vector graphics (inkscape)"
    installed_apps="yes"
fi

# Check LibreOffice
if command -v libreoffice &> /dev/null; then
    echo "✅ LibreOffice - Office suite (libreoffice)"
    installed_apps="yes"
fi

# Check VLC
if command -v vlc &> /dev/null; then
    echo "✅ VLC - Media player (vlc)"
    installed_apps="yes"
fi

# Check VS Code
if command -v code &> /dev/null; then
    echo "✅ VS Code - Code editor (code)"
    installed_apps="yes"
fi

if [ -z "$installed_apps" ]; then
    echo "❌ No GUI applications installed yet"
    echo ""
    echo "Run the DesktopAgent installation guide to install apps!"
fi

echo ""
echo "═══════════════════════════════════════════════════════"
echo ""
echo "To launch an app, click Applications menu (top-left)"
echo "or type the command name in terminal."
echo ""
read -p "Press Enter to close..."
EOFSCRIPT

RUN chmod +x /home/appuser/check-apps.sh && \
    chown appuser:appuser /home/appuser/check-apps.sh

# Create desktop shortcut
RUN mkdir -p /home/appuser/Desktop && \
    cat > /home/appuser/Desktop/check-apps.desktop << 'EOFDESKTOP'
[Desktop Entry]
Version=1.0
Type=Application
Name=Check Installed Apps
Comment=See what applications are installed
Exec=/home/appuser/check-apps.sh
Icon=system-search
Terminal=true
Categories=Utility;
EOFDESKTOP

RUN chmod +x /home/appuser/Desktop/check-apps.desktop && \
    chown appuser:appuser /home/appuser/Desktop/check-apps.desktop

# Create startup script
RUN echo '#!/bin/bash\n\
export USER=appuser\n\
export HOME=/home/appuser\n\
export DISPLAY=:1\n\
\n\
# Start virtual framebuffer\n\
Xvfb :1 -screen 0 1920x1080x24 &\n\
sleep 2\n\
\n\
# Start window manager\n\
DISPLAY=:1 startxfce4 &\n\
sleep 4\n\
\n\
# Trust desktop files\n\
gio set /home/appuser/Desktop/check-apps.desktop metadata::trusted true 2>/dev/null || true\n\
\n\
# Start x11vnc server\n\
x11vnc -display :1 -forever -shared -rfbport 5901 -passwd password &\n\
sleep 2\n\
\n\
# Start DesktopAgent GUI\n\
DISPLAY=:1 python3 /app/main.py &\n\
\n\
echo "================================================="\n\
echo "✅ VNC server: localhost:5901 (password: password)"\n\
echo "✅ DesktopAgent GUI started"\n\
echo "✅ Desktop shortcut: Check Installed Apps"\n\
echo ""\n\
echo "💡 After installation, click Applications menu to"\n\
echo "   launch installed apps!"\n\
echo "================================================="\n\
\n\
# Keep container running\n\
tail -f /dev/null' > /app/start.sh && chmod +x /app/start.sh

CMD ["/app/start.sh"]
