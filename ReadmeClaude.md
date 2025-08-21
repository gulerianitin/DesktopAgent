# Desktop File Organizer Agent

A secure, efficient desktop agent that automatically organizes files in your Downloads folder using Claude AI.

## Features

- **Real-time monitoring**: Uses `watchdog` for efficient file detection (no polling)
- **AI-powered organization**: Claude AI suggests appropriate folder structures
- **Security hardened**: Input validation, path traversal protection, sanitized responses
- **Non-blocking GUI**: Async LLM calls prevent interface freezing
- **Robust error handling**: Comprehensive exception handling and logging
- **Customizable prompts**: Edit AI instructions through the GUI

## Quick Start

### Prerequisites
```bash
sudo apt-get install python3-tk  # Ubuntu/Debian
# or
brew install python-tk  # macOS
```

### Installation
```bash
git clone <repository>
cd DesktopAgent
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# or venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### Configuration
Create `.env` file:
```env
CLAUDE_API_KEY=your_claude_api_key_here
WATCH_FOLDER=/path/to/your/downloads/folder
```

### Run
```bash
python main.py
```

## How It Works

1. **File Detection**: Monitors Downloads folder using efficient file system events
2. **AI Analysis**: Sends new files to Claude for categorization suggestions
3. **Safe Organization**: Validates and sanitizes all paths before moving files
4. **Logging**: All actions logged to GUI and `agent.log` file

## Security Features

- **Path validation**: Prevents directory traversal attacks
- **Input sanitization**: Cleans AI responses before file operations
- **Safe file operations**: Handles duplicates and validates destinations
- **API key validation**: Ensures proper Claude API authentication

## Architecture

```
├── main.py              # Entry point and configuration
├── gui/app.py           # GUI with async operations
├── agents/file_organizer.py  # Core agent logic with watchdog
├── utils/claude_client.py    # Secure Claude API client
└── .env                 # Configuration (create this)
```

## File Organization Examples

**Input files**: `report.pdf`, `vacation.jpg`, `music.mp3`

**Claude suggestions**:
```
report.pdf -> Documents
vacation.jpg -> Images  
music.mp3 -> Media
```

**Result**: Files moved to `Downloads/Documents/`, `Downloads/Images/`, `Downloads/Media/`

## Customization

Edit the prompt template in the GUI to change how Claude categorizes files:

```
You are a file organizer. For these files:
{files}

Organize by project type:
- Work documents -> Work
- Personal photos -> Personal/Photos
- Code files -> Development

Return ONLY: filename -> folder_name
```

## Error Handling

- Invalid API responses are ignored
- Missing files are skipped
- File operation errors are logged
- GUI remains responsive during processing

## Logs

- **GUI log**: Real-time status in the application
- **File log**: `agent.log` contains detailed operation history
- **Console**: Additional debug information

## Troubleshooting

**"Claude API error"**: Check your API key in `.env`
**"Watch folder not found"**: Verify `WATCH_FOLDER` path exists
**"No files moved"**: Check Claude responses in logs for formatting issues

## Dependencies

- `anthropic`: Claude API client
- `watchdog`: File system monitoring  
- `python-dotenv`: Environment configuration
- `tkinter`: GUI framework (system package)