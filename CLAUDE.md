# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Quick Start

### Running the Chatbot (Recommended)
```bash
# Modern web-based chat interface
./start_chatbot.sh
# Access at http://localhost:8000

# Requires .env file with:
# CLAUDE_API_KEY=sk-ant-your-key-here
```

### Running the Original GUI (Deprecated)
```bash
# Primary method - launches Docker with VNC auto-connect
./run.sh

# Development mode (local testing)
source venv/bin/activate
python main.py

# Manual Docker build
docker build -t desktop-agent .
docker run -d --rm --name desktop-agent-running -p 5901:5901 \
  -v "$(pwd)/.env:/app/.env:ro" desktop-agent
```

### Stopping the Application
```bash
# Stop Docker container
docker stop desktop-agent-running

# View logs
docker logs -f desktop-agent-running
tail -f logs/guide_executor.log
```

## Architecture Overview

Simple, focused architecture for AI-powered installation automation:

### Core Components

**GUI**: `gui/app.py` - Simplified tkinter interface with:
- Activity log display
- Guide text editor
- One-button installation start
- Auto-loads demo on startup

**Guide Processing**:
- `utils/guide_parser.py` - Parses installation text into executable steps
- `utils/guide_executor.py` - Executes steps with security validation
- `agents/autonomous_mode.py` - Autonomous execution with delays and error handling

**Security**: `utils/security.py` - Command validation and sanitization
- Blocks dangerous patterns (rm -rf, etc.)
- Comprehensive logging
- Docker isolation for all operations

### Simplified Workflow

1. User runs `./run.sh`
2. Docker container starts with XFCE desktop + VNC server
3. VNC viewer auto-connects to localhost:5901
4. GUI loads with demo guide pre-loaded
5. User clicks "▶ Start Installation"
6. Agent autonomously executes each step with 3-second delays
7. User watches live installation progress in VNC window

## Configuration

### Environment Variables (.env)
```bash
CLAUDE_API_KEY=your_claude_api_key_here
WATCH_FOLDER=/tmp/test_files  # Used by file organizer (optional feature)
```

### Key Dependencies
- **AI**: anthropic (Claude API)
- **GUI**: tkinter (built-in Python)
- **Desktop**: XFCE4 + TigerVNC server (in Docker)
- **Security**: Custom command validator

## Key Files to Know

- `run.sh` - Main entry point, builds & launches Docker with VNC
- `gui/app.py` - Simplified GUI (lines 31-115: UI setup, 153-192: installation logic)
- `Dockerfile` - XFCE desktop environment with VNC server
- `utils/guide_executor.py` - Core step execution engine
- `agents/autonomous_mode.py` - Auto-execution with delays

## Making Changes

**Modifying the GUI**: Edit `gui/app.py`
- UI layout: `_setup_ui()` method (line 31)
- Installation logic: `start_installation()` method (line 153)

**Changing Docker Setup**: Edit `Dockerfile`
- VNC password set on line ~35
- Desktop startup on line ~40

**Security Rules**: Edit `utils/security.py`
- Blocked commands list
- Validation patterns