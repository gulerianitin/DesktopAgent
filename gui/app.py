import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import threading
import time
from typing import Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor

from agents.file_organizer import FileOrganizerAgent
from utils.claude_client import ClaudeClient

class DesktopAgentApp:
    def __init__(self, root: tk.Tk, watch_folder: str):
        self.root = root
        self.root.title("Desktop File Organizer Agent")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self._setup_ui()
        self._setup_agent(watch_folder)
        
        self.running = False
        self.process_thread: Optional[threading.Thread] = None
        self.executor = ThreadPoolExecutor(max_workers=2)

    def _setup_ui(self) -> None:
        """Initialize UI components"""
        # Logging widget
        self.log_text = ScrolledText(self.root, width=80, height=20, state='disabled')
        self.log_text.pack(padx=10, pady=10)

        # Prompt editor
        tk.Label(self.root, text="Edit Prompt Template:").pack(pady=(10, 0))
        self.prompt_text = ScrolledText(self.root, width=80, height=6)
        self.prompt_text.pack(padx=10, pady=5)

        default_prompt = (
            "You are a file organizer. For these files:\n{files}\n"
            "Suggest appropriate folder names. Examples:\n"
            "document.pdf -> Documents\n"
            "image.jpg -> Images\n"
            "Return ONLY lines in format: filename -> folder_name"
        )
        self.prompt_text.insert(tk.END, default_prompt)

        # Buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)
        
        self.update_prompt_button = tk.Button(
            button_frame, text="Update Prompt", command=self.update_prompt
        )
        self.update_prompt_button.pack(side=tk.LEFT, padx=5)

        self.toggle_button = tk.Button(
            button_frame, text="Start Monitoring", command=self.toggle_monitoring
        )
        self.toggle_button.pack(side=tk.LEFT, padx=5)
        
        # Status label
        self.status_label = tk.Label(self.root, text="Status: Stopped", fg="red")
        self.status_label.pack(pady=5)

    def _setup_agent(self, watch_folder: str) -> None:
        """Initialize agent and client"""
        try:
            self.llm_client = ClaudeClient()
            self.agent = FileOrganizerAgent(watch_folder, self.llm_client, self.log)
            self.agent_prompt_template = self.prompt_text.get("1.0", tk.END).strip()
            self.log(f"Agent initialized for folder: {watch_folder}")
        except Exception as e:
            self.log(f"Failed to initialize agent: {e}")
            self.toggle_button.config(state='disabled')

    def log(self, message: str) -> None:
        """Thread-safe logging to GUI and file"""
        def _log():
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            full_message = f"{timestamp} | {message}\n"
            
            self.log_text.config(state='normal')
            self.log_text.insert(tk.END, full_message)
            self.log_text.see(tk.END)
            self.log_text.config(state='disabled')
            
            print(full_message.strip())
            
            # Log to file
            try:
                with open("agent.log", "a", encoding='utf-8') as f:
                    f.write(full_message)
            except Exception:
                pass  # Silent fail for logging
        
        # Schedule on GUI thread
        self.root.after(0, _log)

    def update_prompt(self) -> None:
        """Update the prompt template"""
        new_prompt = self.prompt_text.get("1.0", tk.END).strip()
        if new_prompt:
            self.agent_prompt_template = new_prompt
            self.log("Prompt template updated")
        else:
            self.log("Invalid prompt template")

    def toggle_monitoring(self) -> None:
        """Start/stop file monitoring"""
        if not self.running:
            self._start_monitoring()
        else:
            self._stop_monitoring()

    def _start_monitoring(self) -> None:
        """Start the monitoring process"""
        try:
            self.running = True
            self.toggle_button.config(text="Stop Monitoring")
            self.status_label.config(text="Status: Running", fg="green")
            
            self.agent.start_watching()
            self.process_thread = threading.Thread(target=self._process_loop, daemon=True)
            self.process_thread.start()
            
            self.log("Started monitoring folder")
        except Exception as e:
            self.log(f"Failed to start monitoring: {e}")
            self._stop_monitoring()

    def _stop_monitoring(self) -> None:
        """Stop the monitoring process"""
        self.running = False
        self.toggle_button.config(text="Start Monitoring")
        self.status_label.config(text="Status: Stopped", fg="red")
        
        if hasattr(self, 'agent'):
            self.agent.stop_watching()
        
        self.log("Stopped monitoring folder")

    def _process_loop(self) -> None:
        """Main processing loop running in background thread"""
        while self.running:
            try:
                new_files = self.agent.get_new_files()
                if new_files:
                    self.log(f"Processing files: {', '.join(sorted(new_files))}")
                    
                    # Run LLM call in thread pool to avoid blocking
                    future = self.executor.submit(
                        self.agent.think, new_files, self.agent_prompt_template
                    )
                    
                    try:
                        decision = future.result(timeout=30)  # 30 second timeout
                        if decision:
                            self.log(f"Claude decision:\n{decision}")
                            success = self.agent.act(decision)
                            if not success:
                                self.log("No files were moved")
                        else:
                            self.log("No valid decision from Claude")
                    except Exception as e:
                        self.log(f"Error processing files: {e}")
                
                time.sleep(2)  # Check every 2 seconds
                
            except Exception as e:
                self.log(f"Error in processing loop: {e}")
                time.sleep(5)  # Wait longer on error

    def on_closing(self) -> None:
        """Handle application shutdown"""
        self._stop_monitoring()
        self.executor.shutdown(wait=True)
        self.root.destroy()
