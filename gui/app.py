import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import threading
import time
from typing import Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor

from agents.file_organizer import FileOrganizerAgent
from utils.claude_client import ClaudeClient
from utils.command_handler import ConversationalCommandHandler
from utils.guide_parser import GuideParser
from utils.guide_executor import GuideExecutor

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
        
        # Command input section
        tk.Label(self.root, text="Conversational Commands:").pack(pady=(10, 0))
        command_frame = tk.Frame(self.root)
        command_frame.pack(pady=5, padx=10, fill=tk.X)
        
        self.command_entry = tk.Entry(command_frame, width=60)
        self.command_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.command_entry.bind('<Return>', self.execute_command)
        
        self.execute_button = tk.Button(
            command_frame, text="Execute", command=self.execute_command
        )
        self.execute_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Guide section
        tk.Label(self.root, text="Step-by-Step Guides:").pack(pady=(10, 0))
        guide_frame = tk.Frame(self.root)
        guide_frame.pack(pady=5, padx=10, fill=tk.X)
        
        self.guide_url_entry = tk.Entry(guide_frame, width=40)
        self.guide_url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.guide_url_entry.insert(0, "Enter URL or paste installation steps...")
        self.guide_url_entry.bind('<FocusIn>', self._clear_guide_placeholder)
        
        self.load_guide_button = tk.Button(
            guide_frame, text="Load Guide", command=self.load_guide
        )
        self.load_guide_button.pack(side=tk.LEFT, padx=(5, 0))
        
        # Guide control buttons
        guide_control_frame = tk.Frame(self.root)
        guide_control_frame.pack(pady=5, padx=10, fill=tk.X)
        
        self.step_info_label = tk.Label(guide_control_frame, text="No guide loaded", fg="gray")
        self.step_info_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.execute_step_button = tk.Button(
            guide_control_frame, text="Execute Step", command=self.execute_step, state='disabled'
        )
        self.execute_step_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        self.skip_step_button = tk.Button(
            guide_control_frame, text="Skip Step", command=self.skip_step, state='disabled'
        )
        self.skip_step_button.pack(side=tk.RIGHT, padx=(5, 0))

    def _setup_agent(self, watch_folder: str) -> None:
        """Initialize agent and client"""
        try:
            self.llm_client = ClaudeClient()
            self.agent = FileOrganizerAgent(watch_folder, self.llm_client, self.log)
            self.command_handler = ConversationalCommandHandler(watch_folder)
            self.guide_parser = GuideParser()
            self.guide_executor = GuideExecutor(watch_folder, self.log)
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
    
    def execute_command(self, event=None) -> None:
        """Execute conversational command"""
        command = self.command_entry.get().strip()
        if not command:
            return
            
        self.command_entry.delete(0, tk.END)
        self.log(f"Executing: {command}")
        
        # Run command in thread to avoid blocking GUI
        def run_command():
            try:
                result = self.command_handler.execute_conversational_command(command)
                self.log(result)
            except Exception as e:
                self.log(f"Command error: {e}")
        
        threading.Thread(target=run_command, daemon=True).start()
    
    def _clear_guide_placeholder(self, event) -> None:
        """Clear placeholder text when guide entry is focused"""
        if self.guide_url_entry.get() == "Enter URL or paste installation steps...":
            self.guide_url_entry.delete(0, tk.END)
    
    def load_guide(self) -> None:
        """Load guide from URL or text"""
        input_text = self.guide_url_entry.get().strip()
        if not input_text or input_text == "Enter URL or paste installation steps...":
            self.log("❌ Please enter a URL or paste installation steps")
            return
        
        self.log(f"📚 Loading guide from: {input_text[:100]}...")
        
        def load_guide_async():
            try:
                # Determine if input is URL or text
                if input_text.startswith(('http://', 'https://')):
                    steps = self.guide_parser.parse_url(input_text)
                    guide_name = f"Guide from {input_text}"
                else:
                    steps = self.guide_parser.parse_text(input_text)
                    guide_name = "Custom Guide"
                
                if not steps:
                    self.log("❌ No actionable steps found in the guide")
                    return
                
                # Load into executor
                self.guide_executor.load_guide(steps, guide_name)
                
                # Update UI
                self.root.after(0, self._update_guide_ui)
                
                self.log(f"✅ Guide loaded successfully with {len(steps)} steps")
                
            except Exception as e:
                self.log(f"❌ Failed to load guide: {e}")
        
        threading.Thread(target=load_guide_async, daemon=True).start()
    
    def execute_step(self) -> None:
        """Execute current step"""
        step_info = self.guide_executor.get_step_info()
        if step_info.get("completed"):
            self.log("🎉 All steps completed!")
            self._update_guide_ui()
            return
        
        self.log(f"⚡ Executing step {step_info['step_number']}: {step_info['description']}")
        
        def execute_async():
            try:
                result = self.guide_executor.execute_current_step(user_confirmed=True)
                
                if result["success"]:
                    self.log(f"✅ Step completed: {result['message']}")
                    if result.get("output"):
                        self.log(f"Output: {result['output'][:500]}...")
                else:
                    self.log(f"❌ Step failed: {result['message']}")
                
                # Update UI
                self.root.after(0, self._update_guide_ui)
                
            except Exception as e:
                self.log(f"❌ Error executing step: {e}")
        
        threading.Thread(target=execute_async, daemon=True).start()
    
    def skip_step(self) -> None:
        """Skip current step"""
        step_info = self.guide_executor.get_step_info()
        if step_info.get("completed"):
            return
        
        result = self.guide_executor.skip_current_step("User requested skip")
        self.log(f"⏭️ {result['message']}")
        self._update_guide_ui()
    
    def _update_guide_ui(self) -> None:
        """Update guide-related UI elements"""
        step_info = self.guide_executor.get_step_info()
        
        if step_info.get("completed"):
            self.step_info_label.config(text="🎉 Guide completed!", fg="green")
            self.execute_step_button.config(state='disabled')
            self.skip_step_button.config(state='disabled')
        else:
            # Show current step info
            step_text = f"Step {step_info['progress']}: {step_info['description'][:60]}..."
            if step_info.get("step_type") == "command":
                step_text += f" [CMD: {step_info.get('command', '')[:30]}...]"
            
            self.step_info_label.config(text=step_text, fg="blue")
            self.execute_step_button.config(state='normal')
            self.skip_step_button.config(state='normal')

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
                            self.log(f"DEBUG: Decision passed to agent: {repr(decision)}")
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
