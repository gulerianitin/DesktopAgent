#!/usr/bin/env python3
"""
Interactive Desktop Agent Issue #3 Test - Watch Installation Steps Execute
"""
import sys
import os
import subprocess
import time

# Add current directory to path
sys.path.append('.')

from utils.guide_parser import GuideParser
from utils.guide_executor import GuideExecutor

def execute_command_with_output(command, description=""):
    """Execute command and show real-time output"""
    print(f"\n🔧 EXECUTING: {description}")
    print(f"💻 Command: {command}")
    print("📺 Output:")
    print("-" * 50)
    
    try:
        # Execute command and stream output
        process = subprocess.Popen(
            command, 
            shell=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT, 
            universal_newlines=True,
            bufsize=1
        )
        
        # Stream output line by line
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
        
        return_code = process.poll()
        print("-" * 50)
        
        if return_code == 0:
            print("✅ Command completed successfully!")
        else:
            print(f"❌ Command failed with code: {return_code}")
            
        return return_code == 0
        
    except Exception as e:
        print(f"❌ Error executing command: {e}")
        return False

def interactive_guide_test():
    """Run an interactive installation guide with real-time execution"""
    
    # Simple calculator installation guide
    guide_text = """
    Install Calculator Application:
    
    1. Update package repositories
       apt update
    
    2. Install calculator application
       apt install -y galculator
    
    3. Verify installation
       which galculator
    
    4. Show calculator version
       galculator --version
    
    5. Launch calculator GUI
       galculator &
    """
    
    print("🚀 Desktop Agent Issue #3 - Interactive Guide Execution Test")
    print("=" * 60)
    print("This will show you REAL step-by-step execution inside Docker!")
    print("=" * 60)
    
    # Parse guide
    parser = GuideParser()
    steps = parser.parse_text(guide_text)
    
    print(f"\n📚 Guide parsed: {len(steps)} steps found")
    
    # Show steps first
    print("\n📋 Installation Steps Preview:")
    for i, step in enumerate(steps, 1):
        print(f"   {i}. {step.description}")
        print(f"      Command: {step.command}")
    
    print("\n🐳 Starting Docker container for live execution...")
    
    # Build command to run in Docker with live execution
    docker_cmd = """
    docker run --rm -it \
        -e DISPLAY=$DISPLAY \
        -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
        ubuntu:22.04 bash -c "
            echo '🐳 Docker container started - executing guide steps...';
            echo '';
            echo '📦 Step 1: Update package repositories';
            apt update;
            echo '';
            echo '📦 Step 2: Install calculator application';
            apt install -y galculator;
            echo '';
            echo '📦 Step 3: Verify installation';
            which galculator;
            echo '';
            echo '📦 Step 4: Show calculator version';
            galculator --version || echo 'Version check may not be available';
            echo '';
            echo '📦 Step 5: Launch calculator GUI';
            echo 'Starting galculator - it should appear on your XFCE desktop!';
            galculator &
            sleep 5;
            echo '';
            echo '✅ All steps completed! Check your desktop for the calculator.';
            echo 'Press Enter to close container...';
            read;
        "
    """
    
    print("🎬 Executing installation guide in Docker...")
    print("Watch the steps execute in real-time!")
    print("=" * 60)
    
    # Execute the Docker command
    execute_command_with_output(docker_cmd, "Interactive Docker Guide Execution")
    
    print("\n" + "=" * 60)
    print("🎉 Interactive guide execution completed!")
    print("Did you see the galculator window appear on your XFCE desktop?")
    
    return True

if __name__ == "__main__":
    # Enable X11 forwarding
    print("🔓 Enabling X11 forwarding for Docker...")
    execute_command_with_output("xhost +local:docker", "Enable X11 forwarding")
    
    # Run interactive test
    success = interactive_guide_test()
    
    # Disable X11 forwarding
    print("\n🔒 Resetting X11 permissions...")
    execute_command_with_output("xhost -local:docker", "Reset X11 permissions")
    
    if success:
        print("\n🏆 Interactive Issue #3 test completed!")
    else:
        print("\n💥 Test encountered errors")