# 🤖 Desktop Agent

**AI-Powered Installation Assistant for Linux**

An intelligent desktop assistant that automates software installation using Claude AI. Watch it install applications step-by-step in a safe Docker environment with live VNC viewing.

## 🚀 Quick Start

```bash
# 1. Set your Claude API key
echo 'CLAUDE_API_KEY=your_key_here' > .env

# 2. Run the agent
./run.sh
```

That's it! The VNC viewer will auto-connect and you'll see the Desktop Agent GUI.

## ✨ Features

- **AI-Powered Installation** - Parses and executes installation guides automatically
- **Live Desktop View** - VNC connection shows real-time installation progress
- **Safe Docker Environment** - Isolated testing prevents system damage
- **Simple GUI** - Clean interface with one-click installation start
- **Comprehensive Logging** - Full audit trail of all operations

## 🛠️ Tech Stack

- **AI**: Claude Sonnet-4 API
- **GUI**: Python tkinter + XFCE desktop
- **Container**: Docker with VNC server
- **Security**: Command sanitization & validation

## 📁 Project Structure

```
DesktopAgent/
├── gui/app.py              # Main GUI application
├── agents/
│   ├── autonomous_mode.py  # Auto-execution logic
│   └── file_organizer.py   # File categorization
├── utils/
│   ├── guide_parser.py     # Installation guide parser
│   ├── guide_executor.py   # Step execution engine
│   ├── security.py         # Command validation
│   └── claude_client.py    # Claude API client
├── Dockerfile              # Desktop environment setup
├── run.sh                  # Unified launcher script
└── main.py                 # Application entry point
├── requirements.txt         # Python dependencies
└── .env                     # Configuration (API keys)
```

## 🚀 Quick Start

### One-Line Installation (Ubuntu)
```bash
curl -fsSL https://raw.githubusercontent.com/gulerianitin/DesktopAgent/main/install-ubuntu.sh | bash
```

### Manual Installation
```bash
# Prerequisites
sudo apt update && sudo apt install -y python3 python3-pip python3-tk python3-venv git docker.io

# Clone repository  
git clone https://github.com/gulerianitin/DesktopAgent.git
cd DesktopAgent

# Run installation script
chmod +x install-ubuntu.sh
./install-ubuntu.sh
```

### Configuration
```bash
# Create .env file
echo "CLAUDE_API_KEY=your_claude_api_key_here" > .env
echo "WATCH_FOLDER=/path/to/folder/to/monitor" >> .env
```

### Launch Application
```bash
# Method 1: From applications menu (after installation)
# Search for "Desktop Agent" in your application launcher

# Method 2: Command line
desktop-agent

# Method 3: Direct execution
python main.py
```

## 💡 How to Use

### 1. File Organization
- Files dropped in watch folder are automatically categorized
- AI determines appropriate folder (Documents, Images, etc.)
- Real-time monitoring with GUI feedback

### 2. Conversational Commands
```
Type: "count pdf files in home directory"
Result: find ~ -name "*.pdf" -type f | wc -l

Type: "show disk usage"  
Result: du -sh
```

### 3. Step-by-Step Guides
- **Load from URL**: Paste installation guide URL
- **Load from Text**: Copy/paste installation steps
- **Execute**: Click through steps with confirmation or "Execute All"
- **Docker Integration**: Use `docker exec container_name command` for safe testing
- **Examples**: VLC installation, Docker setup, Node.js installation, etc.



## 🔒 Safe Testing with Docker (Recommended)

For testing installation guides that modify system packages, use Docker sandbox:

### Docker Setup
```bash
# Pull Ubuntu image
docker pull ubuntu:latest

# Build sandbox container
docker build -f Dockerfile.sandbox -t desktop-agent-sandbox .
```

### Safe Testing
```bash
# Run in isolated container
./test-sandbox.sh

# Or manually:
docker run -it --rm \
    -e DISPLAY=$DISPLAY \
    -v "$(pwd)":/home/testuser/app \
    desktop-agent-sandbox
```

### Why Use Docker?
- ✅ **Complete Isolation** - No risk to host system
- ✅ **Easy Reset** - Fresh environment for each test  
- ✅ **GUI Support** - Applications display via WSLg
- ✅ **Real Testing** - Authentic Ubuntu environment
- ✅ **Professional Practice** - Industry standard for safe execution

**Perfect for testing guides like:**
- `sudo apt install` commands (VLC, Docker, Node.js, etc.)
- System configuration changes  
- Development environment setup
- Database installations
- X11 applications with GUI forwarding to Windows

## 🤝 Contributing

Feedback and ideas welcome! Open an issue for discussions or feature requests.





