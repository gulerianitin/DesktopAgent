import os
import shutil
import time
from pathlib import Path
from typing import Set, Optional, Callable, List
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class FileHandler(FileSystemEventHandler):
    def __init__(self, callback: Callable[[str], None]):
        self.callback = callback
        
    def on_created(self, event):
        if not event.is_directory:
            self.callback(os.path.basename(event.src_path))

class FileOrganizerAgent:
    def __init__(self, watch_folder: str, llm_client, logger: Callable[[str], None]):
        if not os.path.exists(watch_folder):
            raise ValueError(f"Watch folder does not exist: {watch_folder}")
            
        self.watch_folder = Path(watch_folder).resolve()
        self.llm = llm_client
        self.logger = logger
        self.new_files: Set[str] = set()
        self.observer = None
        
        self.prompt_template = (
            "You are a file organizer. For these files:\n{files}\n"
            "Suggest appropriate folder names. Examples:\n"
            "document.pdf -> Documents\n"
            "image.jpg -> Images\n"
            "video.mp4 -> Videos\n"
            "Return ONLY lines in format: filename -> folder_name"
        )

    def start_watching(self) -> None:
        """Start monitoring folder for new files"""
        if self.observer:
            return
            
        handler = FileHandler(self._on_new_file)
        self.observer = Observer()
        self.observer.schedule(handler, str(self.watch_folder), recursive=False)
        self.observer.start()
        self.logger("Started watching folder for new files")
    
    def stop_watching(self) -> None:
        """Stop monitoring folder"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
            self.logger("Stopped watching folder")
    
    def _on_new_file(self, filename: str) -> None:
        """Callback for new files detected"""
        if self._is_valid_file(filename):
            self.new_files.add(filename)
    
    def _is_valid_file(self, filename: str) -> bool:
        """Check if file is valid for processing"""
        if filename.startswith('.') or filename.startswith('~'):
            return False
        return True
    
    def get_new_files(self) -> Set[str]:
        """Get and clear new files list"""
        files = self.new_files.copy()
        self.new_files.clear()
        return files

    def think(self, files: Set[str], prompt_override: Optional[str] = None) -> Optional[str]:
        if not files:
            return None
            
        # Filter out files that no longer exist
        existing_files = {f for f in files if (self.watch_folder / f).exists()}
        if not existing_files:
            return None
            
        file_list = "\n".join(sorted(existing_files))
        prompt = (prompt_override or self.prompt_template).format(files=file_list)
        return self.llm.call(prompt)

    def act(self, decision_text: Optional[str]) -> bool:
        """Execute file organization decisions"""
        if not decision_text:
            return False
            
        success_count = 0
        for line in decision_text.strip().splitlines():
            if '->' not in line:
                continue
                
            try:
                filename, folder = [s.strip() for s in line.split('->', 1)]
                if self._move_file_safely(filename, folder):
                    success_count += 1
            except Exception as e:
                self.logger(f"Error processing line '{line}': {e}")
        
        return success_count > 0
    
    def _move_file_safely(self, filename: str, folder_name: str) -> bool:
        """Safely move file with validation"""
        try:
            src_path = self.watch_folder / filename
            
            # Validate source file exists
            if not src_path.exists() or not src_path.is_file():
                self.logger(f"Source file not found: {filename}")
                return False
            
            # Sanitize and validate folder name
            clean_folder = self._sanitize_folder_name(folder_name)
            if not clean_folder:
                self.logger(f"Invalid folder name: {folder_name}")
                return False
            
            dest_folder = self.watch_folder / clean_folder
            dest_folder.mkdir(exist_ok=True)
            
            dest_path = dest_folder / filename
            
            # Handle duplicate names
            counter = 1
            while dest_path.exists():
                name, ext = os.path.splitext(filename)
                dest_path = dest_folder / f"{name}_{counter}{ext}"
                counter += 1
            
            shutil.move(str(src_path), str(dest_path))
            self.logger(f"[{time.strftime('%H:%M:%S')}] Moved '{filename}' to '{clean_folder}'")
            return True
            
        except Exception as e:
            self.logger(f"Error moving '{filename}': {e}")
            return False
    
    def _sanitize_folder_name(self, folder_name: str) -> Optional[str]:
        """Sanitize folder name to prevent security issues"""
        if not folder_name or len(folder_name.strip()) == 0:
            return None
            
        # Remove dangerous characters and patterns
        import re
        clean = re.sub(r'[<>:"|?*\\]', '', folder_name.strip())
        clean = re.sub(r'[./]{2,}', '', clean)
        clean = clean.strip('./\\ ')
        
        # Limit length and ensure it's safe
        if len(clean) > 50 or not clean or clean in ['.', '..']:
            return None
            
        return clean
