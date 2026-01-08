import subprocess
import json
import time
import logging
from datetime import datetime
from typing import List, Callable, Optional, Dict, Any
from pathlib import Path
from .guide_parser import Step
from .security import SecureCommandExecutor, SecurityError

class GuideExecutor:
    def __init__(self, work_directory: str, logger: Callable[[str], None]):
        self.work_directory = Path(work_directory)
        self.logger = logger
        self.current_guide = None
        self.steps: List[Step] = []
        self.current_step_index = 0
        self.guide_log = []
        self.secure_executor = SecureCommandExecutor(work_directory=str(work_directory), allowed_sudo=True)
        self.security_logger = logging.getLogger(__name__)
        
    def load_guide(self, steps: List[Step], guide_name: str = "Guide") -> None:
        """Load a guide with steps to execute"""
        self.steps = steps
        self.current_step_index = 0
        self.current_guide = guide_name
        self.guide_log = []
        
        self.logger(f"📚 Loaded guide '{guide_name}' with {len(steps)} steps")
        self._log_guide_event("guide_loaded", {
            "guide_name": guide_name,
            "total_steps": len(steps),
            "timestamp": datetime.now().isoformat()
        })
    
    def get_current_step(self) -> Optional[Step]:
        """Get the current step to execute"""
        if not self.steps or self.current_step_index >= len(self.steps):
            return None
        return self.steps[self.current_step_index]
    
    def get_step_info(self) -> Dict[str, Any]:
        """Get information about current step and progress"""
        current_step = self.get_current_step()
        if not current_step:
            return {
                "completed": True,
                "progress": f"{len(self.steps)}/{len(self.steps)}",
                "message": "🎉 Guide completed successfully!"
            }
        
        return {
            "completed": False,
            "step_number": current_step.step_number,
            "description": current_step.description,
            "step_type": current_step.step_type,
            "command": current_step.command,
            "notes": current_step.notes,
            "progress": f"{self.current_step_index + 1}/{len(self.steps)}"
        }
    
    def execute_current_step(self, user_confirmed: bool = True) -> Dict[str, Any]:
        """Execute the current step with user confirmation"""
        current_step = self.get_current_step()
        if not current_step:
            return {"success": False, "message": "No steps remaining"}
        
        if not user_confirmed:
            return {"success": False, "message": "User cancelled step execution"}
        
        self.logger(f"⚡ Executing Step {current_step.step_number}: {current_step.description}")
        
        result = {"success": True, "message": "", "output": ""}
        
        try:
            if current_step.step_type == "command" and current_step.command:
                # Execute shell command
                result = self._execute_command(current_step.command)
                current_step.result = result
                
            elif current_step.step_type == "manual":
                # Manual step - just log and wait for confirmation
                result = {
                    "success": True,
                    "message": f"Manual step completed: {current_step.description}",
                    "output": "User completed manual action"
                }
                current_step.result = result
                
            elif current_step.step_type == "verification":
                if current_step.command:
                    # Run verification command
                    result = self._execute_command(current_step.command)
                    result["message"] = f"Verification: {result.get('message', '')}"
                else:
                    # Manual verification
                    result = {
                        "success": True,
                        "message": f"Manual verification: {current_step.description}",
                        "output": "User verified manually"
                    }
                current_step.result = result
            
            # Mark step as completed
            current_step.completed = True
            
            # Log the step execution
            self._log_guide_event("step_executed", {
                "step_number": current_step.step_number,
                "step_type": current_step.step_type,
                "description": current_step.description,
                "command": current_step.command,
                "success": result["success"],
                "output": result.get("output", ""),
                "timestamp": datetime.now().isoformat()
            })
            
            # Move to next step
            self.current_step_index += 1
            
            # Log completion if this was the last step
            if self.current_step_index >= len(self.steps):
                self._log_guide_event("guide_completed", {
                    "guide_name": self.current_guide,
                    "total_steps": len(self.steps),
                    "timestamp": datetime.now().isoformat()
                })
                self.logger("🎉 Guide completed successfully!")
            
            return result
            
        except Exception as e:
            error_result = {
                "success": False,
                "message": f"Error executing step: {e}",
                "output": str(e)
            }
            current_step.result = error_result
            
            self._log_guide_event("step_failed", {
                "step_number": current_step.step_number,
                "step_type": current_step.step_type,
                "description": current_step.description,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            
            return error_result
    
    def skip_current_step(self, reason: str = "User skipped") -> Dict[str, Any]:
        """Skip the current step"""
        current_step = self.get_current_step()
        if not current_step:
            return {"success": False, "message": "No steps remaining"}
        
        self.logger(f"⏭️ Skipping Step {current_step.step_number}: {reason}")
        
        current_step.completed = True
        current_step.result = {"success": True, "message": f"Skipped: {reason}", "output": ""}
        
        self._log_guide_event("step_skipped", {
            "step_number": current_step.step_number,
            "description": current_step.description,
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        })
        
        self.current_step_index += 1
        return {"success": True, "message": f"Step {current_step.step_number} skipped"}
    
    def next_step(self) -> bool:
        """Navigate to next step without executing"""
        if self.current_step_index < len(self.steps) - 1:
            self.current_step_index += 1
            return True
        return False
    
    def prev_step(self) -> bool:
        """Navigate to previous step"""
        if self.current_step_index > 0:
            self.current_step_index -= 1
            return True
        return False
    
    def _execute_command(self, command: str, sudo_password: str = None) -> Dict[str, Any]:
        """Execute a shell command safely with real-time progress output"""
        try:
            self.logger(f"🔧 Running command: {command}")

            # Handle sudo commands with non-interactive flags
            if command.strip().startswith('sudo'):
                # Add -y flag for apt install if not present
                if 'apt-get install' in command and '-y' not in command:
                    command = command.replace('apt-get install', 'apt-get install -y')
                if 'apt install' in command and '-y' not in command:
                    command = command.replace('apt install', 'apt install -y')

            # Check if this is an apt command that would benefit from progress display
            is_apt_command = any(x in command for x in ['apt-get', 'apt install', 'apt update', 'apt upgrade'])

            # Execute command securely
            try:
                if is_apt_command:
                    # Execute with real-time output for apt commands
                    result = self._execute_with_progress(command)
                else:
                    # Execute normally for other commands
                    result = self.secure_executor.execute_command(command, timeout=300)

                # Log sanitized command info (security-aware logging)
                self.logger(f"🔍 Command executed | Return code: {result['returncode']}")
                if result.get('stdout') and not is_apt_command:
                    # Sanitize output for logging (skip for apt - already logged)
                    clean_stdout = self.secure_executor._sanitize_for_logging(result['stdout'])
                    self.logger(f"🔍 Output: {clean_stdout[:300]}")
                if result.get('stderr') and not is_apt_command:
                    clean_stderr = self.secure_executor._sanitize_for_logging(result['stderr'])
                    self.logger(f"🔍 Error: {clean_stderr[:300]}")

            except SecurityError as e:
                self.security_logger.warning(f"Command blocked by security: {e}")
                return {
                    'returncode': -1,
                    'stdout': '',
                    'stderr': f"Security violation: {e}",
                    'command': command,
                    'success': False,
                    'execution_time': 0,
                    'timestamp': datetime.now().isoformat()
                }

            if result['success']:
                self.logger(f"✅ Command successful")
                return {
                    "success": True,
                    "message": "Command executed successfully",
                    "output": result['stdout'],
                    "return_code": result['returncode']
                }
            else:
                self.logger(f"❌ Command failed with return code {result['returncode']}")
                return {
                    "success": False,
                    "message": f"Command failed with return code {result['returncode']}",
                    "output": result['stderr'],
                    "return_code": result['returncode']
                }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "message": "Command timed out after 60 seconds",
                "output": "Timeout"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error executing command: {e}",
                "output": str(e)
            }

    def _execute_with_progress(self, command: str) -> Dict[str, Any]:
        """Execute command and show real-time download progress"""
        import re

        start_time = time.time()
        process = subprocess.Popen(
            ['/bin/bash', '-c', command],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            env={
                'PATH': '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin',
                'DEBIAN_FRONTEND': 'noninteractive',
                'DISPLAY': ':1'
            }
        )

        full_output = []
        last_progress_line = None

        # Pattern to match apt download progress
        progress_pattern = re.compile(r'(Get|Fetched|Reading|Building|Unpacking|Setting up|Processing):.*')
        percentage_pattern = re.compile(r'(\d+)%')

        for line in iter(process.stdout.readline, ''):
            if not line:
                break

            line = line.rstrip()
            full_output.append(line)

            # Check if this is a progress line
            if progress_pattern.search(line):
                # Show package download/install progress
                if 'Get:' in line or 'Fetched' in line:
                    self.logger(f"📥 {line}")
                elif 'Unpacking' in line or 'Setting up' in line:
                    self.logger(f"📦 {line}")
                elif 'Reading' in line or 'Building' in line:
                    # Only show these occasionally to avoid spam
                    if last_progress_line != line[:30]:
                        self.logger(f"⚙️  {line}")
                        last_progress_line = line[:30]
            elif percentage_pattern.search(line):
                # Show percentage updates
                self.logger(f"⏳ {line}")

        process.wait()
        execution_time = time.time() - start_time

        output = '\n'.join(full_output)

        return {
            'returncode': process.returncode,
            'stdout': output,
            'stderr': '',
            'command': command,
            'success': process.returncode == 0,
            'execution_time': execution_time,
            'timestamp': datetime.now().isoformat()
        }
    
    def _log_guide_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Log guide execution events"""
        log_entry = {
            "event_type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        self.guide_log.append(log_entry)
        
        # Also save to file
        log_file = self.work_directory / "guide_execution.log"
        try:
            with open(log_file, "a", encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception:
            pass  # Silent fail for logging
    
    def get_guide_summary(self) -> Dict[str, Any]:
        """Get summary of guide execution"""
        completed_steps = len([s for s in self.steps if s.completed])
        successful_steps = len([s for s in self.steps if s.completed and s.result and s.result.get("success", False)])
        failed_steps = len([s for s in self.steps if s.completed and s.result and not s.result.get("success", True)])

        # Calculate success rate based on successful steps vs completed steps
        if completed_steps > 0:
            success_rate = (successful_steps / completed_steps * 100)
        else:
            success_rate = 0

        return {
            "guide_name": self.current_guide,
            "total_steps": len(self.steps),
            "completed_steps": completed_steps,
            "successful_steps": successful_steps,
            "failed_steps": failed_steps,
            "progress_percentage": (completed_steps / len(self.steps) * 100) if self.steps else 100,
            "success_rate": success_rate,  # NEW: actual success rate
            "is_completed": completed_steps == len(self.steps),
            "current_step": self.current_step_index + 1 if self.current_step_index < len(self.steps) else None
        }