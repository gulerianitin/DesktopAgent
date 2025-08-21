# 🧠 Desktop AI Agent (MVP)

A local-first intelligent assistant that can:
- Organize files automatically
- Execute shell commands from natural language
- Follow web-based installation and troubleshooting instructions
- Perform basic web automation (login and scraping)
- Integrate these tasks into a CrewAI-based agent framework



## 🚀 Project Goals

This project is a proof-of-concept for a local AI desktop assistant that can help automate common tasks with minimal human input. The long-term vision includes autonomous workflows, multi-agent collaboration, and persistent background tasks.



## ✅ Features (Easy MVP Phase)

- [x] **File Organizer Agent**  
- [x] **Natural Language to Shell Executor**  
- [x] **Step-by-Step Instruction Follower**  
- [x] **Simple Web Automation Agent (Playwright)**  
- [x] **CrewAI Agent Integration**



## 🛠️ Tech Stack (Python)

| Area                  | Library/Tool        |
|-----------------------|---------------------|
| Agent framework       | `crewai`            |
| Language models       | `openai` (API) or `ollama` (local)  
| Shell execution       | `subprocess`, `shlex`  
| Folder monitoring     | `watchdog`  
| Web automation        | `playwright` (Python)  
| Logging/debugging     | `loguru`, `rich`  
| Environment           | Python 3.10+, WSL2 with Ubuntu 22.04



## 🧪 Local Setup

```bash
# 1. Create virtual env
python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Install Playwright dependencies
playwright install


## 📂 Project Structure

desktop_agent/
├── agents/
│   ├── __init__.py
│   └── file_organizer.py
├── gui/
│   ├── __init__.py
│   └── app.py
├── utils/
│   ├── __init__.py
│   └── claude_client.py
├── .env
├── agent.log
├── main.py
├── requirements.txt
└── README.md

## Organizing files in Downloads folder

# Desktop File Organizer Agent

Minimal Python desktop agent prototype that watches a folder and uses Claude LLM to organize files.

## Features
- Monitors a target folder for new files (polling every 10 seconds)
- Dynamically prompts Claude LLM for file categorization
- Moves files into categorized subfolders
- Simple Tkinter GUI with logs and prompt editor
- Logs actions to console and `agent.log`
- Uses `.env` for config and secrets

## Setup

```bash
python3 -m venv venv
source venv/bin/activate      # Linux / WSL
venv\Scripts\activate.bat     # Windows cmd
pip install -r requirements.txt



## 📈 Roadmap

See [GitHub Issues](../../issues) for tasks.


## 🤝 Contributing

This is a solo MVP, but feedback and ideas are welcome. Open an issue for discussions or feature requests.





