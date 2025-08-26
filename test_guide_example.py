#!/usr/bin/env python3
"""
Test the guide system with sample installation steps
"""

from utils.guide_parser import GuideParser
from utils.guide_executor import GuideExecutor

def test_guide_system():
    # Sample installation guide text
    sample_guide = """
    How to Install Docker on Ubuntu:
    
    1. Update your package index
       sudo apt update
    
    2. Install required packages
       sudo apt install apt-transport-https ca-certificates curl gnupg lsb-release
    
    3. Add Docker's GPG key
       curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    
    4. Set up the stable repository
       echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    5. Update package index again
       sudo apt update
    
    6. Install Docker Engine
       sudo apt install docker-ce docker-ce-cli containerd.io
    
    7. Verify installation
       sudo docker run hello-world
    
    8. Add user to docker group (optional)
       sudo usermod -aG docker $USER
    """
    
    print("Testing Guide Parser...")
    parser = GuideParser()
    
    try:
        steps = parser.parse_text(sample_guide)
        print(f"✅ Parsed {len(steps)} steps successfully!")
        
        for i, step in enumerate(steps):
            print(f"\nStep {step.step_number}: {step.description}")
            print(f"Type: {step.step_type}")
            if step.command:
                print(f"Command: {step.command}")
            if step.notes:
                print(f"Notes: {step.notes}")
                
        # Test executor (without actually running commands)
        print("\n" + "="*50)
        print("Testing Guide Executor...")
        
        def mock_logger(message):
            print(f"LOG: {message}")
        
        executor = GuideExecutor("/tmp", mock_logger)
        executor.load_guide(steps, "Docker Installation Guide")
        
        # Show guide info
        summary = executor.get_guide_summary()
        print(f"Guide Summary: {summary}")
        
        # Show first few steps
        for i in range(min(3, len(steps))):
            step_info = executor.get_step_info()
            print(f"\nCurrent Step Info: {step_info}")
            executor.current_step_index += 1
            
        print("\n✅ Guide system test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_guide_system()