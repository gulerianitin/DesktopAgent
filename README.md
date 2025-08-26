# 🧠 Desktop AI Agent

A local-first intelligent assistant that can:
- **Organize files automatically** using Claude AI
- **Execute shell commands** from natural language  
- **Follow installation guides** step-by-step from URLs or text
- **Monitor folders** and process files in real-time

## ✅ Features Implemented

- ✅ **File Organization** - Automatically categorizes and moves files
- ✅ **Conversational Commands** - Natural language to shell command execution  
- ✅ **Step-by-Step Guides** - Parse and execute installation/troubleshooting guides
- ✅ **Real-time Monitoring** - Watch folders for new files
- ✅ **GUI Interface** - Tkinter-based desktop application
- ✅ **Safety Controls** - User confirmation, timeouts, comprehensive logging



## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **AI/LLM** | Claude Sonnet-4 API |
| **GUI** | tkinter (Python native) |
| **File Monitoring** | watchdog |
| **Web Parsing** | requests + Claude AI |
| **Environment** | Python 3.8+, WSL2 Ubuntu |





## 📁 Project Structure

```
DesktopAgent/
├── agents/
│   └── file_organizer.py    # File categorization logic
├── gui/
│   └── app.py               # Main GUI application  
├── utils/
│   ├── claude_client.py     # Claude API integration
│   ├── command_handler.py   # Natural language commands
│   ├── guide_parser.py      # Installation guide parser
│   └── guide_executor.py    # Step-by-step execution
├── main.py                  # Application entry point
├── requirements.txt         # Python dependencies
└── .env                     # Configuration (API keys)
```

## 🚀 Quick Start

### Prerequisites
```bash
# Ubuntu/WSL
sudo apt-get install python3 python3-pip python3-tk python3-venv

# Get Claude API key from https://console.anthropic.com
```

### Installation
```bash
# Clone repository
git clone https://github.com/gulerianitin/DesktopAgent.git
cd DesktopAgent

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/WSL
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

### Configuration
```bash
# Create .env file
echo "CLAUDE_API_KEY=your_claude_api_key_here" > .env
echo "WATCH_FOLDER=/path/to/folder/to/monitor" >> .env
```

### Usage
```bash
# Run the application
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
- **Execute**: Click through steps with confirmation
- **Examples**: Docker installation, Node.js setup, etc.



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
- `sudo apt install` commands
- System configuration changes  
- Development environment setup
- Database installations

## 🤝 Contributing

Feedback and ideas welcome! Open an issue for discussions or feature requests.





