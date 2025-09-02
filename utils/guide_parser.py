import requests
import re
import logging
from typing import List, Dict, Optional, Tuple
from urllib.parse import urlparse
from .claude_client import ClaudeClient
from .security import SecureURLValidator, SecurityError

class Step:
    def __init__(self, step_number: int, description: str, command: Optional[str] = None, 
                 step_type: str = "manual", notes: Optional[str] = None):
        self.step_number = step_number
        self.description = description
        self.command = command
        self.step_type = step_type  # "command", "manual", "verification"
        self.notes = notes
        self.completed = False
        self.result = None

class GuideParser:
    def __init__(self):
        self.claude_client = ClaudeClient()
        self.logger = logging.getLogger(__name__)
    
    def parse_url(self, url: str) -> List[Step]:
        """Parse installation/troubleshooting steps from a URL"""
        try:
            # Validate URL for security
            SecureURLValidator.validate_url(url)
            
            # Fetch webpage content securely
            response = requests.get(
                url, 
                timeout=30, 
                headers={'User-Agent': 'Mozilla/5.0 (Linux; Desktop Agent Guide Parser)'},
                verify=True,  # Verify SSL certificates
                allow_redirects=False,  # Don't follow redirects automatically
                stream=False
            )
            response.raise_for_status()
            
            # Limit response size to prevent DoS
            if len(response.content) > 10 * 1024 * 1024:  # 10MB limit
                raise SecurityError("Response too large (>10MB)")
                
        except SecurityError as e:
            self.logger.warning(f"URL security validation failed: {e}")
            raise
        except requests.exceptions.SSLError as e:
            self.logger.error(f"SSL certificate verification failed for {url}: {e}")
            raise SecurityError(f"SSL verification failed: {e}")
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Network request failed for {url}: {e}")
            raise SecurityError(f"Network request failed: {e}")
            
            # Extract steps using Claude
            prompt = f"""Extract installation or troubleshooting steps from this webpage content.

URL: {url}
Content: {response.text[:8000]}...

Parse into structured steps. For each step, identify:
1. Step number and description
2. Whether it contains a command to execute
3. Type: "command" (executable), "manual" (user action), or "verification" (check result)

Return in this exact format:
STEP 1: [description]
TYPE: [command/manual/verification]
COMMAND: [shell command if applicable, or "none"]
NOTES: [additional info if needed, or "none"]

STEP 2: [description]
TYPE: [command/manual/verification] 
COMMAND: [shell command if applicable, or "none"]
NOTES: [additional info if needed, or "none"]

Focus on actionable installation/setup/troubleshooting steps only."""

            claude_response = self.claude_client.call(prompt, sanitize=False)
            if not claude_response:
                raise Exception("Failed to parse steps from URL")
            
            return self._parse_claude_response(claude_response)
            
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch URL: {e}")
        except Exception as e:
            raise Exception(f"Failed to parse guide: {e}")
    
    def parse_text(self, text: str) -> List[Step]:
        """Parse installation/troubleshooting steps from raw text"""
        try:
            prompt = f"""Extract installation or troubleshooting steps from this text.

Text content:
{text}

Parse into structured steps. For each step, identify:
1. Step number and description  
2. Whether it contains a command to execute
3. Type: "command" (executable), "manual" (user action), or "verification" (check result)

Return in this exact format:
STEP 1: [description]
TYPE: [command/manual/verification]
COMMAND: [shell command if applicable, or "none"] 
NOTES: [additional info if needed, or "none"]

STEP 2: [description]
TYPE: [command/manual/verification]
COMMAND: [shell command if applicable, or "none"]
NOTES: [additional info if needed, or "none"]

Focus on actionable installation/setup/troubleshooting steps only."""

            claude_response = self.claude_client.call(prompt, sanitize=False)
            if not claude_response:
                raise Exception("Failed to parse steps from text")
            
            return self._parse_claude_response(claude_response)
            
        except Exception as e:
            raise Exception(f"Failed to parse guide from text: {e}")
    
    def _parse_claude_response(self, response: str) -> List[Step]:
        """Parse Claude's structured response into Step objects"""
        steps = []
        current_step = None
        
        for line in response.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('STEP '):
                # Save previous step if exists
                if current_step:
                    steps.append(current_step)
                
                # Parse step number and description
                match = re.match(r'STEP (\d+):\s*(.*)', line)
                if match:
                    step_num = int(match.group(1))
                    description = match.group(2)
                    current_step = {
                        'number': step_num,
                        'description': description,
                        'type': 'manual',
                        'command': None,
                        'notes': None
                    }
            
            elif line.startswith('TYPE:') and current_step:
                step_type = line.replace('TYPE:', '').strip().lower()
                if step_type in ['command', 'manual', 'verification']:
                    current_step['type'] = step_type
            
            elif line.startswith('COMMAND:') and current_step:
                command = line.replace('COMMAND:', '').strip()
                if command and command.lower() != 'none':
                    current_step['command'] = command
            
            elif line.startswith('NOTES:') and current_step:
                notes = line.replace('NOTES:', '').strip()
                if notes and notes.lower() != 'none':
                    current_step['notes'] = notes
        
        # Add final step
        if current_step:
            steps.append(current_step)
        
        # Convert to Step objects
        step_objects = []
        for step_data in steps:
            step = Step(
                step_number=step_data['number'],
                description=step_data['description'],
                command=step_data['command'],
                step_type=step_data['type'],
                notes=step_data['notes']
            )
            step_objects.append(step)
        
        return step_objects