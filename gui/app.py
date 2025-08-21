import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import threading
import time
from typing import Optional

from agents.file_organizer import FileOrganizerAgent
from utils.claude_client import ClaudeClient

class DesktopAgentApp:
    def __init__(self, root: tk.Tk, watch_folder: str):
        self.root = root
        self.root.title("Desktop File Organizer Agent")

        # Logging widget
        self.log_text = ScrolledText(root, width=80, height=20, state='disabled')
        self.log_text.pack(padx=10, pady=10)

        # Prompt editor label + input
        tk.Label(root, text="Edit Prompt Template:").pack(pady=(10, 0))
        self.prompt_text = ScrolledText(root, width=80, height=8)
        self.prompt_text.pack(padx=10, pady=5)

        default_prompt = (
            "You are a helpful file organizer.\n"
            "Given these new files:\n{files}\n"
            "Suggest folder names for each file type, e.g. PDFs to 'Documents/PDFs', images to 'Pictures', executables to 'Programs'.\n"
            "Return results as lines in format:\nfilename -> folder_name\n"
        )
        self.prompt_text.insert(tk.END, default_prompt)

        self.update_prompt_button = tk.Button(root, text="Update Prompt", command=self.update_prompt)
        self.update_prompt_button.pack(pady=(0, 10))

        # Start/Stop monitor button
        self.toggle_button = tk.Button(root, text="Start Monitoring", command=self.toggle_monitoring)
        self.toggle_button.pack(pady=5)

        self.running = False
        self.monitor_thread: Optional[threading.Thread] = None

        # Setup Claude client and agent
        self.llm_client = ClaudeClient()
        self.agent = FileOrganizerAgent(watch_folder, self.llm_client, self.log)
        self.agent_prompt_template = default_prompt

    def log(self, message: str) -> None:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        full_message = f"{timestamp} | {message}\n"
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, full_message)
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
        print(full_message.strip())
        # Also log to file
        with open("agent.log", "a") as f:
            f.write(full_message)

    def update_prompt(self) -> None:
        self.agent_prompt_template = self.prompt_text.get("1.0", tk.END).strip()
        self.log("Prompt template updated.")

    def agent_think(self, files):
        if not files:
            return None
        return self.agent.think(files, prompt_override=self.agent_prompt_template)

    def toggle_monitoring(self) -> None:
        if not self.running:
            self.running = True
            self.toggle_button.config(text="Stop Monitoring")
            self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
            self.monitor_thread.start()
            self.log("Started monitoring folder.")
        else:
            self.running = False
            self.toggle_button.config(text="Start Monitoring")
            self.log("Stopped monitoring folder.")

    def monitor_loop(self):
        while self.running:
            try:
                new_files = self.agent.observe()
                if new_files:
                    self.log(f"Detected new files: {', '.join(new_files)}")
                    decision = self.agent_think(new_files)
                    self.log(f"Claude decision:\n{decision}")
                    self.agent.act(decision)
                time.sleep(10)
            except Exception as e:
                self.log(f"Error in monitoring loop: {e}")
                time.sleep(10)
