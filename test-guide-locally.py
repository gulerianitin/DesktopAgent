#!/usr/bin/env python3
"""
Quick local test of the guide system without Docker
"""
import sys
import os

# Add current directory to path
sys.path.append('.')

from utils.guide_parser import GuideParser
from utils.guide_executor import GuideExecutor

def test_guide_system():
    """Test guide system with sample data"""
    
    # Sample installation guide
    sample_text = """
    Install Node.js on Ubuntu:
    
    1. Update system packages
       sudo apt update
    
    2. Install curl if not available
       sudo apt install -y curl
    
    3. Download Node.js setup script
       curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
    
    4. Install Node.js
       sudo apt install -y nodejs
    
    5. Verify installation
       node --version
    
    6. Check npm version
       npm --version
    """
    
    print("🧪 Testing Guide Parser...")
    parser = GuideParser()
    
    try:
        # Test parsing
        steps = parser.parse_text(sample_text)
        print(f"✅ Parsed {len(steps)} steps")
        
        # Show parsed steps
        for step in steps:
            print(f"\n📋 Step {step.step_number}: {step.description}")
            print(f"   Type: {step.step_type}")
            if step.command:
                print(f"   Command: {step.command}")
            if step.notes:
                print(f"   Notes: {step.notes}")
        
        # Test executor (dry run)
        print(f"\n🎯 Testing Guide Executor (dry run)...")
        
        def mock_logger(msg):
            print(f"LOG: {msg}")
        
        executor = GuideExecutor("/tmp", mock_logger)
        executor.load_guide(steps, "Node.js Installation Test")
        
        # Show current step info
        for i in range(min(3, len(steps))):
            step_info = executor.get_step_info()
            print(f"\n▶️  Current Step: {step_info}")
            executor.current_step_index += 1
        
        print("\n✅ Guide system working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Testing Guide System Locally...")
    success = test_guide_system()
    
    if success:
        print("\n🎉 Ready to test with GUI!")
        print("Run: python main.py")
        print("Then use the 'Step-by-Step Guides' section")
    else:
        print("\n💥 Fix errors before proceeding")