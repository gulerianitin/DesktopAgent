import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

class ClaudeClient:
    def __init__(self):
        api_key = os.getenv("CLAUDE_API_KEY")
        if not api_key:
            raise ValueError("CLAUDE_API_KEY not set in .env")
        self.client = Anthropic(api_key=api_key)
    
    def call(self, prompt: str) -> str:
        response = self.client.completions.create(
            model="claude-3-opus-20240229",
            prompt=prompt,
            max_tokens_to_sample=200,
            temperature=0.2,
            stop_sequences=["\n\n"]
        )
        return response.completion.strip()
