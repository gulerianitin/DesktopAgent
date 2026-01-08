"""
Autonomous Mode for DesktopAgent
Enables automatic step-by-step execution without user confirmation
"""
import time
from typing import Callable, Optional, Dict, Any
from utils.guide_executor import GuideExecutor


class AutonomousExecutor:
    """Wraps GuideExecutor with autonomous execution capabilities"""

    def __init__(self, guide_executor: GuideExecutor, logger: Callable[[str], None]):
        self.executor = guide_executor
        self.logger = logger
        self.autonomous_mode = False
        self.delay_between_steps = 2  # seconds
        self.stop_on_error = True
        self.should_stop = False  # Emergency stop flag

    def enable_autonomous_mode(self, enabled: bool = True):
        """Enable or disable autonomous mode"""
        self.autonomous_mode = enabled
        self.logger(f"🤖 Autonomous mode: {'ENABLED' if enabled else 'DISABLED'}")

    def emergency_stop(self):
        """Emergency stop - halts autonomous execution immediately"""
        self.should_stop = True
        self.logger("🛑 EMERGENCY STOP requested - halting execution...")

    def execute_all_autonomous(self, delay: float = 2.0, stop_on_error: bool = True) -> Dict[str, Any]:
        """
        Execute all steps autonomously

        Args:
            delay: Delay between steps in seconds
            stop_on_error: Stop execution if a step fails

        Returns:
            Summary of execution
        """
        if not self.autonomous_mode:
            return {
                "success": False,
                "message": "Autonomous mode not enabled"
            }

        self.logger("🚀 Starting autonomous execution...")
        self.logger(f"⚙️  Settings: delay={delay}s, stop_on_error={stop_on_error}")

        # Reset stop flag
        self.should_stop = False
        executed_steps = 0
        failed_steps = 0

        while True:
            # Check for emergency stop
            if self.should_stop:
                self.logger("🛑 Execution halted by emergency stop")
                break
            step_info = self.executor.get_step_info()

            # Check if all steps completed
            if step_info.get("completed"):
                self.logger("✅ All steps completed successfully!")
                break

            # Get current step details
            current_step = self.executor.get_current_step()
            if not current_step:
                break

            # Log step info
            self.logger(f"\n{'='*60}")
            self.logger(f"📍 Step {step_info['step_number']}/{step_info['progress'].split('/')[1]}")
            self.logger(f"📝 Description: {step_info['description']}")
            if step_info.get('command'):
                self.logger(f"💻 Command: {step_info['command']}")
            self.logger(f"{'='*60}\n")

            # Wait before execution (except for first step)
            if executed_steps > 0:
                self.logger(f"⏳ Waiting {delay} seconds before next step...")
                # Check for emergency stop during delay (check every 0.5 seconds)
                for _ in range(int(delay * 2)):
                    if self.should_stop:
                        self.logger("🛑 Execution halted during delay")
                        break
                    time.sleep(0.5)

            # Execute step autonomously (auto-confirm)
            self.logger(f"⚡ Auto-executing step {step_info['step_number']}...")
            result = self.executor.execute_current_step(user_confirmed=True)

            executed_steps += 1

            # Check result
            if result.get("success"):
                self.logger(f"✅ Step {step_info['step_number']} completed successfully")
                if result.get("output"):
                    # Show more output for better visibility
                    output_lines = result["output"].strip().split('\n')
                    if len(output_lines) <= 10:
                        self.logger(f"📤 Output:\n{result['output'][:1000]}")
                    else:
                        # Show first 5 and last 5 lines
                        preview = '\n'.join(output_lines[:5]) + '\n[...]\n' + '\n'.join(output_lines[-5:])
                        self.logger(f"📤 Output:\n{preview[:1000]}")
            else:
                failed_steps += 1
                self.logger(f"❌ Step {step_info['step_number']} failed: {result.get('message', 'Unknown error')}")
                if result.get("output"):
                    self.logger(f"📤 Error output:\n{result['output'][:500]}")

                if stop_on_error:
                    self.logger("🛑 Stopping execution due to error (stop_on_error=True)")
                    break
                else:
                    self.logger("⚠️  Continuing despite error (stop_on_error=False)")

        # Final summary
        summary = self.executor.get_guide_summary()
        self.logger(f"\n{'='*60}")
        self.logger(f"📊 EXECUTION SUMMARY")
        self.logger(f"{'='*60}")
        self.logger(f"Total steps: {summary['total_steps']}")
        self.logger(f"Successful: {summary.get('successful_steps', 0)}")
        self.logger(f"Failed: {summary['failed_steps']}")
        self.logger(f"Success rate: {summary.get('success_rate', 0):.1f}%")
        self.logger(f"{'='*60}\n")

        return {
            "success": failed_steps == 0,
            "executed_steps": executed_steps,
            "failed_steps": failed_steps,
            "summary": summary
        }

    def execute_next_autonomous(self) -> Dict[str, Any]:
        """Execute just the next step autonomously"""
        if not self.autonomous_mode:
            return {
                "success": False,
                "message": "Autonomous mode not enabled"
            }

        step_info = self.executor.get_step_info()

        if step_info.get("completed"):
            return {
                "success": True,
                "message": "All steps already completed"
            }

        self.logger(f"⚡ Auto-executing step {step_info['step_number']}...")
        result = self.executor.execute_current_step(user_confirmed=True)

        return result
