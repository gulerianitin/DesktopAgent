import os
import re
from typing import Optional
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

class ClaudeClient:
    def __init__(self):
        api_key = os.getenv("CLAUDE_API_KEY")
        if not api_key or len(api_key.strip()) < 10:
            raise ValueError("Valid CLAUDE_API_KEY required in .env")
        
        try:
            self.client = Anthropic(api_key=api_key.strip())
        except Exception as e:
            raise ValueError(f"Failed to initialize Claude client: {e}")
    
    def call(self, prompt: str) -> Optional[str]:
        if not prompt or len(prompt.strip()) == 0:
            return None
            
        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=300,
                temperature=0.1,
                messages=[{"role": "user", "content": prompt.strip()}]
            )
            
            response = message.content[0].text
            return self._sanitize_response(response)
            
        except Exception as e:
            print(f"Claude API error: {e}")
            return None
    
    def _sanitize_response(self, response: str) -> str:
        """Sanitize Claude response to prevent path traversal attacks"""
        if not response:
            return ""
        
        lines = []
        for line in response.strip().split('\n'):
            # Handle both '->' and '-' formats
            if '->' in line or (' - ' in line and not line.strip().startswith('-')):
                # Convert single dash to arrow format
                if ' - ' in line and '->' not in line:
                    line = line.replace(' - ', ' -> ')
                
                # Remove dangerous path characters
                clean_line = re.sub(r'[.]{2,}|[<>:"|?*]', '', line)
                # Ensure no absolute paths  
                clean_line = re.sub(r'^[/\\]', '', clean_line)
                lines.append(clean_line)
        
        return '\n'.join(lines)