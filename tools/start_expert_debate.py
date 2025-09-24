#!/usr/bin/env python3
"""Minimal Expert Debate System Startup.

This script provides the absolute minimum needed to start expert debates:
1. Check prerequisites
2. Start LLM adapter if needed
3. Initialize expert system
4. Run test debate
"""
import subprocess
import sys
import time
import requests
from pathlib import Path

def check_prerequisites():
    """Check if all required components are available."""
    print("🔍 Checking prerequisites...")
    
    # Check Python environment
    print(f"   Python: {sys.version}")
    
    # Check if we're in the right directory
    repo_root = Path.cwd()
    required_paths = [
        "intake/ai_experts",
        "tools/llm_adapter",
        "tools/minimal_expert_debate.py"
    ]
    
    missing = []
    for path in required_paths:
        if not (repo_root / path).exists():
            missing.append(path)
    
    if missing:
        print(f"❌ Missing required paths: {missing}")
        print(f"   Make sure you're in the railweb repository root")
        return False
    
    # Check expert personas exist
    expert_files = [
        "intake/ai_experts/requirements_engineer.md",
        "intake/ai_experts/project_planner.md", 
        "intake/ai_experts/system_architect.md",
        "intake/ai_experts/sysml_advisor.md"
    ]
    
    missing_experts = []
    for expert_file in expert_files:
        if not (repo_root / expert_file).exists():
            missing_experts.append(expert_file)
    
    if missing_experts:
        print(f"❌ Missing expert personas: {missing_experts}")
        return False
    
    print("✅ All prerequisites found")
    return True

def check_llm_adapter():
    """Check if LLM adapter is running."""
    try:
        response = requests.get("http://localhost:3001/health", timeout=2)
        print("✅ LLM Adapter is running")
        return True
    except:
        print("⚠️  LLM Adapter not running")
        return False

def start_llm_adapter():
    """Start the LLM adapter server."""
    print("🚀 Starting LLM Adapter...")
    
    adapter_dir = Path("tools/llm_adapter")
    
    # Check if node_modules exists
    if not (adapter_dir / "node_modules").exists():
        print("   Installing dependencies...")
        result = subprocess.run(["npm", "install"], cwd=adapter_dir, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ npm install failed: {result.stderr}")
            return False
    
    # Start the server in background
    print("   Starting server...")
    try:
        process = subprocess.Popen(
            ["npm", "start"],
            cwd=adapter_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a moment for startup
        time.sleep(3)
        
        # Check if it's running
        if check_llm_adapter():
            print("✅ LLM Adapter started successfully")
            return True
        else:
            print("❌ LLM Adapter failed to start")
            process.terminate()
            return False
            
    except Exception as e:
        print(f"❌ Failed to start LLM Adapter: {e}")
        return False

def test_expert_system():
    """Test the expert debate system with a simple artifact."""
    print("\n🧠 Testing Expert Debate System...")
    
    try:
        # Import and run the minimal debate system
        from tools.minimal_expert_debate import MinimalDebateOrchestrator
        
        # Create test artifact
        test_artifact = {
            "title": "Expert System Test",
            "type": "requirement", 
            "description": "Test artifact for validating expert debate system",
            "content": "Simple test to verify expert agents can analyze and debate."
        }
        
        # Run minimal test
        orchestrator = MinimalDebateOrchestrator()
        print("   Initializing experts...")
        orchestrator.initialize_experts()
        
        if orchestrator.experts:
            print(f"✅ {len(orchestrator.experts)} experts initialized")
            
            # Test single expert analysis
            expert_name = list(orchestrator.experts.keys())[0]
            expert = orchestrator.experts[expert_name]
            
            print(f"   Testing {expert_name} analysis...")
            analysis = expert.analyze(test_artifact)
            
            if analysis.get('expert') == expert_name:
                print("✅ Expert analysis working")
                return True
            else:
                print("❌ Expert analysis failed")
                return False
        else:
            print("❌ No experts initialized")
            return False
            
    except Exception as e:
        print(f"❌ Expert system test failed: {e}")
        return False

def main():
    """Main startup sequence."""
    print("🎯 Minimal Expert Debate System Startup")
    print("=" * 50)
    
    # Step 1: Check prerequisites
    if not check_prerequisites():
        print("\n❌ Prerequisites check failed")
        return 1
    
    # Step 2: Check/start LLM adapter
    if not check_llm_adapter():
        if not start_llm_adapter():
            print("\n❌ Could not start LLM adapter")
            print("Manual start: cd tools/llm_adapter && npm install && npm start")
            return 1
    
    # Step 3: Test expert system
    if not test_expert_system():
        print("\n❌ Expert system test failed")
        return 1
    
    print("\n🎉 Minimal Expert Debate System is ready!")
    print("\nNext steps:")
    print("1. Run full debate: python tools/minimal_expert_debate.py")
    print("2. Or import and use: from tools.minimal_expert_debate import MinimalDebateOrchestrator")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())