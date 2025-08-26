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
    # Set up signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    load_dotenv()
    watch_folder = os.getenv("WATCH_FOLDER")
    if not watch_folder or not os.path.exists(watch_folder):
        print(f"Error: WATCH_FOLDER '{watch_folder}' does not exist or is not set in .env")
        sys.exit(1)

    try:
        root = tk.Tk()
        app = DesktopAgentApp(root, watch_folder)
        root.mainloop()
    except KeyboardInterrupt:
        print("\nShutting down...")
        sys.exit(0)

if __name__ == "__main__":
    main()
