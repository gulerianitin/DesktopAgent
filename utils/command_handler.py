import subprocess
import os
from typing import Optional
from .claude_client import ClaudeClient

class ConversationalCommandHandler:
    def __init__(self, watch_folder: str):
        self.watch_folder = watch_folder
        self.claude_client = ClaudeClient()
    
    def execute_conversational_command(self, natural_command: str) -> Optional[str]:
        """Convert natural language to shell command and execute it"""
        try:
            # Prompt Claude to convert natural language to shell command
            prompt = f"""Convert this natural language command to a shell command:
"{natural_command}"

Context: Working directory is {self.watch_folder}

Return ONLY the shell command, no explanation. Examples:
"find the number of images in the images folder" -> find Images -type f \( -iname "*.jpg" -o -iname "*.png" -o -iname "*.gif" -o -iname "*.bmp" \) | wc -l
"check disk usage" -> du -sh
"list recent files" -> ls -lt | head -10
"show folder sizes" -> du -h --max-depth=1 | sort -hr

Shell command:"""

            shell_command = self.claude_client.call(prompt, sanitize=False)
            if not shell_command:
                return "Error: Could not interpret command - Claude API may have failed"
            
            # Clean the response
            shell_command = shell_command.strip().replace('```', '').replace('bash', '').strip()
            
            # Execute the shell command
            result = subprocess.run(
                shell_command, 
                shell=True, 
                cwd=self.watch_folder,
                capture_output=True, 
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                output = result.stdout.strip()
                return f"Command: {shell_command}\nResult:\n{output}" if output else f"Command executed: {shell_command}"
            else:
                return f"Command failed: {shell_command}\nError: {result.stderr.strip()}"
                
        except subprocess.TimeoutExpired:
            return "Command timed out after 30 seconds"
        except Exception as e:
            return f"Error executing command: {e}"