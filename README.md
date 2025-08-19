# 🧠 Desktop AI Agent (MVP)

A local-first intelligent assistant that can:
- Organize files automatically
- Execute shell commands from natural language
- Follow web-based installation and troubleshooting instructions
- Perform basic web automation (login and scraping)
- Integrate these tasks into a CrewAI-based agent framework

---

## 🚀 Project Goals

This project is a proof-of-concept for a local AI desktop assistant that can help automate common tasks with minimal human input. The long-term vision includes autonomous workflows, multi-agent collaboration, and persistent background tasks.

---

## ✅ Features (Easy MVP Phase)

- [x] **File Organizer Agent**  
- [x] **Natural Language to Shell Executor**  
- [x] **Step-by-Step Instruction Follower**  
- [x] **Simple Web Automation Agent (Playwright)**  
- [x] **CrewAI Agent Integration**

---

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

---

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

---

## 📂 Project Structure
You're right — GitHub Markdown doesn’t render file trees well in preview unless formatted properly. Here's the fixed version using **code block with language hinting disabled**, ensuring it looks clean and aligned:

---

## 📂 Project Structure


desktop-ai-agent/
│
├── agents/               # CrewAI agent definitions
├── tools/                # File, shell, web automation tools
├── data/                 # Logs, extracted data, scraped content
├── utils/                # Common helper functions
├── tests/                # Unit and integration tests
│
├── main.py               # Entry point
├── requirements.txt
├── .gitignore
└── README.md


---

You can copy and paste this directly into your `README.md`, and it will preview correctly on GitHub. Let me know if you'd like the `main.py` scaffold next.

---

## 📈 Roadmap

See [GitHub Issues](../../issues) for tasks.

---

## 🤝 Contributing

This is a solo MVP, but feedback and ideas are welcome. Open an issue for discussions or feature requests.

---




