"""
Security utilities for DesktopAgent
Provides secure command execution, input validation, and logging
"""
import shlex
import subprocess
import re
import logging
from typing import List, Optional, Dict, Any
from urllib.parse import urlparse
import os

class SecurityError(Exception):
    """Raised when security validation fails"""
    pass

class SecureCommandExecutor:
    """Secure command execution with validation and sandboxing"""
    
    # Whitelist of allowed commands for security
    SAFE_COMMANDS = {
        # File operations
        'ls', 'dir', 'find', 'locate', 'grep', 'cat', 'head', 'tail', 'wc',
        'sort', 'uniq', 'cut', 'awk', 'sed', 'diff', 'file', 'stat',
        
        # Directory operations  
        'pwd', 'cd', 'mkdir', 'rmdir', 'tree',
        
        # System info
        'du', 'df', 'ps', 'top', 'whoami', 'id', 'uname', 'uptime', 'date',
        'free', 'which', 'whereis', 'history',
        
        # Network (limited)
        'ping', 'wget', 'curl',
        
        # Package management (controlled)
        'apt', 'snap', 'flatpak', 'pip', 'npm',
        
        # Development
        'git', 'python', 'python3', 'node', 'npm', 'docker',
        
        # Media
        'vlc', 'galculator', 'mousepad'
    }
    
    # Commands that require sudo
    SUDO_COMMANDS = {
        'apt', 'snap', 'systemctl', 'service', 'mount', 'umount'
    }
    
    # Dangerous patterns to block
    DANGEROUS_PATTERNS = [
        r'rm\s+-rf?\s+/',           # rm -rf /
        r'dd\s+if=',                # dd commands
        r'>\s*/dev/sd[a-z]',        # Writing to disk devices
        r'mkfs\.',                  # Format commands
        r'fdisk',                   # Partition commands
        r'crontab\s+-r',           # Remove crontab
        r'killall\s+-9',           # Force kill all
        r'chmod\s+777',            # Overly permissive chmod
        r'chown\s+.*:.*\s+/',      # Chown on root
        r'mv\s+.*\s+/bin/',        # Moving to system dirs
        r'cp\s+.*\s+/bin/',        # Copying to system dirs
        r'.*\|\s*sh',              # Piping to shell
        r'.*\|\s*bash',            # Piping to bash
        r'curl.*\|\s*sh',          # Curl pipe to shell
        r'wget.*\|\s*sh',          # Wget pipe to shell
    ]
    
    def __init__(self, work_directory: str = "/tmp", allowed_sudo: bool = False):
        self.work_directory = work_directory
        self.allowed_sudo = allowed_sudo
        self.logger = logging.getLogger(__name__)
        
    def validate_command(self, command: str) -> bool:
        """Validate if command is safe to execute"""
        if not command or not command.strip():
            return False
            
        # Check for dangerous patterns
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                raise SecurityError(f"Dangerous command pattern detected: {pattern}")
                
        # Parse command safely
        try:
            command_parts = shlex.split(command)
        except ValueError as e:
            raise SecurityError(f"Invalid command syntax: {e}")
            
        if not command_parts:
            return False
            
        base_command = command_parts[0]
        
        # Handle sudo commands
        if base_command == 'sudo':
            if not self.allowed_sudo:
                raise SecurityError("Sudo commands not allowed in this context")
            if len(command_parts) < 2:
                raise SecurityError("Invalid sudo command")
            base_command = command_parts[1]
            
        # Check if command is in whitelist
        if base_command not in self.SAFE_COMMANDS:
            raise SecurityError(f"Command '{base_command}' not in whitelist")
            
        return True
        
    def execute_command(self, command: str, timeout: int = 30) -> Dict[str, Any]:
        """Safely execute a validated command"""
        try:
            # Validate command first
            self.validate_command(command)
            
            # Parse command safely
            command_parts = shlex.split(command)
            
            # Log sanitized command (remove potential secrets)
            sanitized_cmd = self._sanitize_for_logging(command)
            self.logger.info(f"Executing command: {sanitized_cmd}")
            
            # Execute with shell=False for security
            result = subprocess.run(
                command_parts,
                shell=False,  # NEVER use shell=True
                cwd=self.work_directory,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=self._get_safe_environment()
            )
            
            # Sanitize output for logging
            stdout_clean = self._sanitize_for_logging(result.stdout) if result.stdout else ""
            stderr_clean = self._sanitize_for_logging(result.stderr) if result.stderr else ""
            
            return {
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'command': command,
                'success': result.returncode == 0
            }
            
        except subprocess.TimeoutExpired:
            raise SecurityError(f"Command timed out after {timeout} seconds")
        except FileNotFoundError:
            raise SecurityError(f"Command not found: {command_parts[0] if command_parts else 'unknown'}")
        except Exception as e:
            raise SecurityError(f"Command execution failed: {e}")
            
    def _sanitize_for_logging(self, text: str) -> str:
        """Remove sensitive information from logs"""
        if not text:
            return ""
            
        # Remove potential API keys, tokens, passwords
        patterns = [
            (r'(api[_-]?key|token|password|secret)\s*[=:]\s*[\'"]?([a-zA-Z0-9_-]+)[\'"]?', r'\1=***'),
            (r'sk-[a-zA-Z0-9-]{20,}', 'sk-***'),  # OpenAI/Anthropic API keys
            (r'ghp_[a-zA-Z0-9]{36}', 'ghp_***'),  # GitHub tokens
            (r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '***@***.***'),  # Email addresses
        ]
        
        sanitized = text
        for pattern, replacement in patterns:
            sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)
            
        return sanitized[:1000]  # Limit log length
        
    def _get_safe_environment(self) -> Dict[str, str]:
        """Get a safe environment for command execution"""
        # Start with minimal environment
        safe_env = {
            'PATH': '/usr/local/bin:/usr/bin:/bin',
            'HOME': self.work_directory,
            'USER': 'desktop-agent',
            'LANG': 'en_US.UTF-8',
            'TERM': 'xterm-256color'
        }
        
        # Add specific variables if needed
        if 'DISPLAY' in os.environ:
            safe_env['DISPLAY'] = os.environ['DISPLAY']
            
        return safe_env


class SecureURLValidator:
    """Validate URLs for safe requests"""
    
    ALLOWED_SCHEMES = {'https', 'http'}
    BLOCKED_HOSTS = {
        'localhost', '127.0.0.1', '0.0.0.0',
        '10.0.0.0/8', '172.16.0.0/12', '192.168.0.0/16'  # Private networks
    }
    
    @classmethod
    def validate_url(cls, url: str) -> bool:
        """Validate if URL is safe to request"""
        try:
            parsed = urlparse(url)
            
            # Check scheme
            if parsed.scheme not in cls.ALLOWED_SCHEMES:
                raise SecurityError(f"URL scheme '{parsed.scheme}' not allowed")
                
            # Check for blocked hosts
            if parsed.hostname in cls.BLOCKED_HOSTS:
                raise SecurityError(f"URL host '{parsed.hostname}' is blocked")
                
            # Additional checks for private networks
            if parsed.hostname and (
                parsed.hostname.startswith('192.168.') or
                parsed.hostname.startswith('10.') or
                parsed.hostname.startswith('172.')
            ):
                raise SecurityError(f"Private network access not allowed: {parsed.hostname}")
                
            return True
            
        except Exception as e:
            raise SecurityError(f"Invalid URL: {e}")


class SecureFileHandler:
    """Secure file operations with path traversal prevention"""
    
    def __init__(self, base_directory: str):
        self.base_directory = os.path.abspath(base_directory)
        
    def validate_path(self, filepath: str) -> str:
        """Validate and resolve file path securely"""
        # Resolve path and check it's within base directory
        resolved = os.path.abspath(os.path.join(self.base_directory, filepath))
        
        if not resolved.startswith(self.base_directory):
            raise SecurityError(f"Path traversal attempt detected: {filepath}")
            
        return resolved
        
    def safe_write(self, filepath: str, content: str) -> None:
        """Safely write file with path validation"""
        safe_path = self.validate_path(filepath)
        
        # Create directory if needed
        os.makedirs(os.path.dirname(safe_path), exist_ok=True)
        
        with open(safe_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
    def safe_read(self, filepath: str) -> str:
        """Safely read file with path validation"""
        safe_path = self.validate_path(filepath)
        
        with open(safe_path, 'r', encoding='utf-8') as f:
            return f.read()