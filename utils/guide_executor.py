import subprocess
import json
import time
from datetime import datetime
from typing import List, Callable, Optional, Dict, Any
from pathlib import Path
from .guide_parser import Step

class GuideExecutor:
    def __init__(self, work_directory: str, logger: Callable[[str], None]):
        self.work_directory = Path(work_directory)
        self.logger = logger
        self.current_guide = None
        self.steps: List[Step] = []
        self.current_step_index = 0
        self.guide_log = []
        
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
        """Execute a shell command safely"""
        try:
            self.logger(f"🔧 Running command: {command}")
            
            # Handle sudo commands with non-interactive flags
            if command.strip().startswith('sudo'):
                # Add non-interactive flags for apt commands
                if 'apt install' in command and '-y' not in command:
                    command = command.replace('apt install', 'apt install -y')
                if 'apt update' in command:
                    command = f"DEBIAN_FRONTEND=noninteractive {command}"
                if 'apt install' in command:
                    command = f"DEBIAN_FRONTEND=noninteractive {command}"
            
            result = subprocess.run(
                command,
                shell=True,
                cwd=str(self.work_directory),
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout for installations
            )
            
            # Log detailed command info
            self.logger(f"🔍 Command: '{command}' | Return code: {result.returncode}")
            self.logger(f"🔍 Stdout: {result.stdout[:300] if result.stdout else '(empty)'}")
            self.logger(f"🔍 Stderr: {result.stderr[:300] if result.stderr else '(empty)'}")
            
            if result.returncode == 0:
                output = result.stdout.strip()
                self.logger(f"✅ Command successful")
                return {
                    "success": True,
                    "message": "Command executed successfully",
                    "output": output,
                    "return_code": result.returncode
                }
            else:
                error = result.stderr.strip()
                self.logger(f"❌ Command failed with return code {result.returncode}")
                return {
                    "success": False,
                    "message": f"Command failed with return code {result.returncode}",
                    "output": error,
                    "return_code": result.returncode
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
        failed_steps = len([s for s in self.steps if s.completed and s.result and not s.result.get("success", True)])
        
        return {
            "guide_name": self.current_guide,
            "total_steps": len(self.steps),
            "completed_steps": completed_steps,
            "failed_steps": failed_steps,
            "progress_percentage": (completed_steps / len(self.steps) * 100) if self.steps else 100,
            "is_completed": completed_steps == len(self.steps),
            "current_step": self.current_step_index + 1 if self.current_step_index < len(self.steps) else None
        }