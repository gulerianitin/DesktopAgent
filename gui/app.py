import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import threading
import time
from concurrent.futures import ThreadPoolExecutor

from agents.autonomous_mode import AutonomousExecutor
from utils.guide_parser import GuideParser
from utils.guide_executor import GuideExecutor

class DesktopAgentApp:
    def __init__(self, root: tk.Tk, watch_folder: str):
        self.root = root
        self.root.title("Desktop Agent - AI Installation Assistant")
        self.root.geometry("1000x700")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self._setup_ui()
        self._setup_agent(watch_folder)

        self.executor = ThreadPoolExecutor(max_workers=2)
        self.installation_running = False  # Track if installation is in progress

        # Auto-load demo guide
        self.root.after(500, self.load_demo_guide)

    def _setup_ui(self) -> None:
        """Initialize UI components - DARK THEME"""
        # Configure dark theme colors
        self.root.configure(bg='#1e1e1e')

        # Header
        header = tk.Label(
            self.root,
            text="🤖 Desktop Agent - AI Installation Assistant",
            font=('Arial', 14, 'bold'),
            bg='#0d7377',
            fg='#ffffff',
            pady=10
        )
        header.pack(fill=tk.X)

        # Logging widget
        tk.Label(
            self.root,
            text="Activity Log:",
            font=('Arial', 10, 'bold'),
            bg='#1e1e1e',
            fg='#d4d4d4'
        ).pack(pady=(10, 5), anchor='w', padx=10)

        self.log_text = ScrolledText(
            self.root,
            width=100,
            height=15,
            state='normal',
            bg='#0d1117',
            fg='#58d68d',  # Green text like terminal
            insertbackground='#58d68d',
            font=('Courier New', 10)
        )
        self.log_text.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        self.log_text.bind("<Key>", self._handle_log_key)

        # Guide section
        separator1 = tk.Frame(self.root, height=2, bg='#3d3d3d')
        separator1.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(
            self.root,
            text="Installation Guide:",
            font=('Arial', 10, 'bold'),
            bg='#1e1e1e',
            fg='#d4d4d4'
        ).pack(pady=(5, 5), anchor='w', padx=10)

        guide_button_frame = tk.Frame(self.root, bg='#1e1e1e')
        guide_button_frame.pack(pady=5, padx=10, fill=tk.X)

        tk.Button(
            guide_button_frame,
            text="📂 Load Demo Guide",
            command=self.load_demo_guide,
            font=('Arial', 10),
            bg='#323232',
            fg='#d4d4d4',
            activebackground='#404040',
            relief=tk.FLAT,
            padx=10,
            pady=5
        ).pack(side=tk.LEFT, padx=5)

        # Guide text area
        self.guide_text = ScrolledText(
            self.root,
            width=100,
            height=8,
            bg='#0d1117',
            fg='#c9d1d9',
            insertbackground='#c9d1d9',
            font=('Courier New', 9)
        )
        self.guide_text.pack(padx=10, pady=5)
        self.guide_text.insert(tk.END, "Click 'Load Demo Guide' or paste installation commands here...")

        # Execution controls
        separator2 = tk.Frame(self.root, height=2, bg='#3d3d3d')
        separator2.pack(fill=tk.X, padx=10, pady=10)

        control_frame = tk.Frame(self.root, bg='#1e1e1e')
        control_frame.pack(pady=10, padx=10, fill=tk.X)

        # Left side - status
        status_frame = tk.Frame(control_frame, bg='#1e1e1e')
        status_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.step_info_label = tk.Label(
            status_frame,
            text="No guide loaded",
            font=('Arial', 10),
            fg="#808080",
            bg='#1e1e1e'
        )
        self.step_info_label.pack(anchor='w')

        # Right side - buttons
        button_frame = tk.Frame(control_frame, bg='#1e1e1e')
        button_frame.pack(side=tk.RIGHT)

        tk.Button(
            button_frame,
            text="▶ Start Installation",
            command=self.start_installation,
            font=('Arial', 11, 'bold'),
            bg='#238636',
            fg='white',
            activebackground='#2ea043',
            relief=tk.FLAT,
            padx=20,
            pady=8
        ).pack(side=tk.LEFT, padx=5)

        self.stop_button = tk.Button(
            button_frame,
            text="⏹ Stop",
            command=self.emergency_stop,
            state='disabled',
            font=('Arial', 11),
            bg='#da3633',
            fg='white',
            activebackground='#e5534b',
            relief=tk.FLAT,
            disabledforeground='#808080',
            padx=20,
            pady=8
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)

        tk.Button(
            button_frame,
            text="🔍 Check Installed Apps",
            command=self.check_installed_apps,
            font=('Arial', 11),
            bg='#1f6feb',
            fg='white',
            activebackground='#388bfd',
            relief=tk.FLAT,
            padx=20,
            pady=8
        ).pack(side=tk.LEFT, padx=5)

        # Hidden elements for compatibility
        self.prompt_text = ScrolledText(self.root, width=1, height=1)
        self.command_entry = tk.Entry(self.root)
        self.autonomous_var = tk.BooleanVar(value=True)  # Always autonomous
        self.delay_var = tk.StringVar(value="3")

    def _setup_agent(self, watch_folder: str) -> None:
        """Initialize agent and client"""
        try:
            self.guide_parser = GuideParser()
            self.guide_executor = GuideExecutor(watch_folder, self.log)
            self.autonomous_executor = AutonomousExecutor(self.guide_executor, self.log)
            self.log("🤖 Desktop Agent ready")
            self.log("👉 Click 'Load Demo Guide' to see example installation")
        except Exception as e:
            self.log(f"❌ Failed to initialize: {e}")

    def log(self, message: str) -> None:
        """Thread-safe logging to GUI and file"""
        def _log():
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            full_message = f"{timestamp} | {message}\n"
            
            self.log_text.insert(tk.END, full_message)
            self.log_text.see(tk.END)
            
            print(full_message.strip())
            
            # Log to file
            try:
                with open("agent.log", "a", encoding='utf-8') as f:
                    f.write(full_message)
            except Exception:
                pass  # Silent fail for logging
        
        # Schedule on GUI thread
        self.root.after(0, _log)

    def start_installation(self) -> None:
        """Simplified start button - loads and executes guide automatically"""
        # Check if installation is already running
        if self.installation_running:
            self.log("⚠️ Installation is already running! Please wait for it to complete.")
            self.log("💡 If stuck, restart the container: ./restart.sh")
            return

        input_text = self.guide_text.get('1.0', tk.END).strip()

        if not input_text or input_text.startswith("Click 'Load Demo"):
            self.log("⚠️ Please load a guide first by clicking 'Load Demo Guide'")
            return

        self.installation_running = True
        self.log("🚀 Starting installation...")
        self.stop_button.config(state='normal')

        def execute_guide():
            try:
                # Parse guide
                steps = self.guide_parser.parse_text(input_text)
                if not steps:
                    self.log("❌ No installation steps found")
                    return

                # Load into executor
                self.guide_executor.load_guide(steps, "Installation Guide")
                self.log(f"✅ Found {len(steps)} installation steps")

                # Enable autonomous mode
                self.autonomous_executor.enable_autonomous_mode(True)

                # Execute all with 3-second delay
                result = self.autonomous_executor.execute_all_autonomous(delay=3.0, stop_on_error=False)

                if result["success"]:
                    self.log(f"\n✅ Installation completed! ({result['executed_steps']} steps)")
                else:
                    self.log(f"\n⚠️ Installation finished with {result['failed_steps']} failures")

            except Exception as e:
                self.log(f"❌ Error: {e}")
            finally:
                self.installation_running = False
                self.root.after(0, lambda: self.stop_button.config(state='disabled'))

        threading.Thread(target=execute_guide, daemon=True).start()
    
    def _handle_log_key(self, event) -> str:
        """Allow copy operations but prevent editing"""
        # Allow Ctrl+C, Ctrl+A, and arrow keys
        if event.state & 0x4:  # Ctrl key pressed
            if event.keysym in ('c', 'a', 'C', 'A'):
                return None  # Allow copy and select all
        if event.keysym in ('Up', 'Down', 'Left', 'Right', 'Home', 'End', 'Prior', 'Next'):
            return None  # Allow navigation
        return "break"  # Block other keys
    
    def load_demo_guide(self) -> None:
        """Load the demo guide file"""
        try:
            with open('demo-simple-install.txt', 'r') as f:
                content = f.read()

            self.guide_text.delete('1.0', tk.END)
            self.guide_text.insert(tk.END, content)
            self.log("✅ Demo guide loaded")
            self.log("👉 Click '▶ Start Installation' when ready")
        except Exception as e:
            self.log(f"❌ Failed to load demo: {e}")

    def emergency_stop(self) -> None:
        """Emergency stop button"""
        self.log("🛑 Stopping installation...")
        self.autonomous_executor.emergency_stop()
        self.stop_button.config(state='disabled')

    def check_installed_apps(self) -> None:
        """Check what apps are installed and show launcher window"""
        import subprocess

        self.log("🔍 Checking installed applications...")

        def check_and_show():
            apps = {
                'GIMP': 'gimp',
                'Inkscape': 'inkscape',
                'LibreOffice': 'libreoffice',
                'VLC Media Player': 'vlc',
                'VS Code': 'code'
            }

            installed = {}
            for name, cmd in apps.items():
                try:
                    result = subprocess.run(['which', cmd], capture_output=True, text=True, timeout=2)
                    if result.returncode == 0:
                        installed[name] = cmd
                        self.log(f"✅ Found: {name}")
                except:
                    pass

            # Show launcher window
            self.root.after(0, lambda: self._show_app_launcher(installed))

        threading.Thread(target=check_and_show, daemon=True).start()

    def _show_app_launcher(self, installed_apps: dict) -> None:
        """Show window with installed apps and launch buttons - DARK THEME"""
        launcher = tk.Toplevel(self.root)
        launcher.title("Installed Applications")
        launcher.geometry("500x400")
        launcher.configure(bg='#1e1e1e')

        tk.Label(
            launcher,
            text="📦 Installed Applications",
            font=('Arial', 14, 'bold'),
            bg='#0d7377',
            fg='white',
            pady=10
        ).pack(fill=tk.X)

        info_frame = tk.Frame(launcher, bg='#1e1e1e')
        info_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        if not installed_apps:
            tk.Label(
                info_frame,
                text="❌ No applications installed yet\n\n"
                     "Click '▶ Start Installation' to install apps!",
                font=('Arial', 11),
                fg='#808080',
                bg='#1e1e1e',
                justify=tk.LEFT
            ).pack(pady=50)
        else:
            tk.Label(
                info_frame,
                text=f"Found {len(installed_apps)} installed applications:\n",
                font=('Arial', 11, 'bold'),
                bg='#1e1e1e',
                fg='#d4d4d4'
            ).pack(anchor='w')

            for name, cmd in installed_apps.items():
                app_frame = tk.Frame(info_frame, bg='#1e1e1e')
                app_frame.pack(fill=tk.X, pady=5)

                tk.Label(
                    app_frame,
                    text=f"✅ {name}",
                    font=('Arial', 10),
                    width=25,
                    anchor='w',
                    bg='#1e1e1e',
                    fg='#58d68d'
                ).pack(side=tk.LEFT)

                tk.Button(
                    app_frame,
                    text="🚀 Launch",
                    command=lambda c=cmd, n=name: self._launch_app(c, n),
                    bg='#238636',
                    fg='white',
                    activebackground='#2ea043',
                    relief=tk.FLAT,
                    font=('Arial', 9),
                    padx=10
                ).pack(side=tk.RIGHT, padx=5)

            tk.Label(
                info_frame,
                text="\n💡 Tip: You can also launch apps from the Applications menu",
                font=('Arial', 9),
                fg='#808080',
                bg='#1e1e1e'
            ).pack(pady=20)

        tk.Button(
            launcher,
            text="Close",
            command=launcher.destroy,
            font=('Arial', 10),
            bg='#323232',
            fg='#d4d4d4',
            activebackground='#404040',
            relief=tk.FLAT,
            padx=15,
            pady=5
        ).pack(pady=10)

    def _launch_app(self, command: str, name: str) -> None:
        """Launch an application"""
        import subprocess

        self.log(f"🚀 Launching {name}...")

        def launch():
            try:
                subprocess.Popen([command],
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL)
                self.log(f"✅ {name} started")
            except Exception as e:
                self.log(f"❌ Failed to launch {name}: {e}")

        threading.Thread(target=launch, daemon=True).start()

    def on_closing(self) -> None:
        """Handle application shutdown"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=True)
        self.root.destroy()
