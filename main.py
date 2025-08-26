import os
from dotenv import load_dotenv
import sys
import signal
import tkinter as tk
from gui.app import DesktopAgentApp

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\nShutting down...")
    sys.exit(0)

def main():
    load_dotenv()
    watch_folder = os.getenv("WATCH_FOLDER")
    if not watch_folder or not os.path.exists(watch_folder):
        print(f"Error: WATCH_FOLDER '{watch_folder}' does not exist or is not set in .env")
        sys.exit(1)

    root = tk.Tk()
    app = DesktopAgentApp(root, watch_folder)
    
    # Handle Ctrl+C by checking for KeyboardInterrupt periodically
    def check_for_interrupt():
        try:
            root.after(100, check_for_interrupt)  # Check every 100ms
        except KeyboardInterrupt:
            print("\nShutting down...")
            root.quit()
            sys.exit(0)
    
    # Set up signal handler that works with tkinter
    def signal_handler(sig, frame):
        print("\nShutting down...")
        root.quit()
        root.destroy()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Start the periodic interrupt check
    root.after(100, check_for_interrupt)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\nShutting down...")
        sys.exit(0)
    finally:
        if hasattr(app, 'executor'):
            app.executor.shutdown(wait=False)

if __name__ == "__main__":
    main()
