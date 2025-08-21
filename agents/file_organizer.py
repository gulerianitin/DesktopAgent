import os
import shutil
import time
from typing import Set, Optional, Callable

class FileOrganizerAgent:
    def __init__(self, watch_folder: str, llm_client, logger: Callable[[str], None]):
        self.watch_folder = watch_folder
        self.llm = llm_client
        self.logger = logger
        self.known_files: Set[str] = set(os.listdir(watch_folder))
        self.prompt_template = (
            "You are a helpful file organizer.\n"
            "Given these new files:\n{files}\n"
            "Suggest folder names for each file type, e.g. PDFs to 'Documents/PDFs', images to 'Pictures', executables to 'Programs'.\n"
            "Return results as lines in format:\nfilename -> folder_name\n"
        )

    def observe(self) -> Set[str]:
        current_files = set(os.listdir(self.watch_folder))
        new_files = current_files - self.known_files
        self.known_files = current_files
        return new_files

    def think(self, files: Set[str], prompt_override: Optional[str] = None) -> Optional[str]:
        if not files:
            return None
        file_list = "\n".join(files)
        prompt = (prompt_override or self.prompt_template).format(files=file_list)
        self.logger(f"Thinking with prompt:\n{prompt}\n")
        return self.llm.call(prompt)

    def act(self, decision_text: Optional[str]) -> None:
        if not decision_text:
            return
        for line in decision_text.splitlines():
            if '->' not in line:
                continue
            filename, folder = map(str.strip, line.split('->'))
            src = os.path.join(self.watch_folder, filename)
            dest_folder = os.path.join(self.watch_folder, folder)
            if not os.path.exists(dest_folder):
                os.makedirs(dest_folder)
            try:
                shutil.move(src, dest_folder)
                self.logger(f"[{time.strftime('%H:%M:%S')}] Moved '{filename}' to '{folder}'")
            except Exception as e:
                self.logger(f"Error moving '{filename}': {e}")
