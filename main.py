import os
from dotenv import load_dotenv
import sys
import tkinter as tk
from gui.app import DesktopAgentApp

def main():
    load_dotenv()
    watch_folder = os.getenv("WATCH_FOLDER")
    if not watch_folder or not os.path.exists(watch_folder):
        print(f"Error: WATCH_FOLDER '{watch_folder}' does not exist or is not set in .env")
        sys.exit(1)

    root = tk.Tk()
    app = DesktopAgentApp(root, watch_folder)
    root.mainloop()

if __name__ == "__main__":
    main()
