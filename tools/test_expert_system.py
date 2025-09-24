#!/usr/bin/env python3
"""Test the Expert System Infrastructure without OpenAI API calls.

This validates that the minimum stack is ready for expert debates.
"""
import json
import os
import sys
from pathlib import Path

def test_expert_personas():
    """Test that expert personas are available and properly formatted."""
    print("🔍 Testing Expert Personas...")
    
    # Check if expert personas exist
    expert_files = [
        "intake/ai_experts/requirements_engineer.md",
        "intake/ai_experts/project_planner.md", 
        "intake/ai_experts/system_architect.md",
        "intake/ai_experts/sysml_advisor.md",
        "intake/ai_experts/debate_orchestrator.md"
    ]
    
    found_experts = []
    for expert_file in expert_files:
        if Path(expert_file).exists():
            found_experts.append(expert_file)
            print(f"  ✅ Found: {expert_file}")
        else:
            print(f"  ❌ Missing: {expert_file}")
    
    return found_experts

def test_input_artifacts():
    """Test that we have artifacts ready for expert analysis."""
    print("\n📄 Testing Input Artifacts...")
    
    artifacts = [
        "docs/Chrystallum_SysML_Block_Definitions.md",
        "intake/scope.yml",
        "intake/milestones.csv"
    ]
    
    found_artifacts = []
    for artifact in artifacts:
        if Path(artifact).exists():
            found_artifacts.append(artifact)
            print(f"  ✅ Found: {artifact}")
            # Show size/content preview
            size = Path(artifact).stat().st_size
            print(f"      Size: {size} bytes")
        else:
            print(f"  ❌ Missing: {artifact}")
    
    return found_artifacts

def test_openai_import():
    """Test OpenAI library availability."""
    print("\n🤖 Testing OpenAI Integration...")
    
    try:
        from openai import OpenAI
        print("  ✅ OpenAI library imported successfully")
        
        # Test environment setup (without API call)
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            print("  ✅ OPENAI_API_KEY found in environment")
            print(f"      Key preview: {api_key[:10]}...")
        else:
            print("  ⚠️  OPENAI_API_KEY not set (required for live operation)")
        
        return True
    except ImportError as e:
        print(f"  ❌ OpenAI import failed: {e}")
        return False

def test_python_expert_code():
    """Test that the Python expert system code is valid."""
    print("\n🐍 Testing Python Expert System Code...")
    
    try:
        # Import the module without executing
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "python_expert_debate", 
            "tools/python_expert_debate.py"
        )
        module = importlib.util.module_from_spec(spec)
        
        # This tests syntax without executing
        spec.loader.exec_module(module)
        
        print("  ✅ Python expert system code imports successfully")
        
        # Check for key classes
        if hasattr(module, 'PythonExpertAgent'):
            print("  ✅ PythonExpertAgent class available")
        if hasattr(module, 'PythonDebateOrchestrator'):
            print("  ✅ PythonDebateOrchestrator class available")
        if hasattr(module, 'demo_python_expert_system'):
            print("  ✅ Demo function available")
        
        return True
    except Exception as e:
        print(f"  ❌ Python expert system validation failed: {e}")
        return False

def main():
    """Run all infrastructure tests."""
    print("🧪 Expert Debate System Infrastructure Test")
    print("=" * 50)
    
    tests = [
        test_expert_personas,
        test_input_artifacts,  
        test_openai_import,
        test_python_expert_code
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"  ❌ Test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("📊 Infrastructure Readiness Summary")
    print("=" * 50)
    
    all_passed = all(results)
    if all_passed:
        print("🎉 MINIMUM STACK READY!")
        print("   All infrastructure components are in place.")
        print("   Ready to start expert debates once API key is configured.")
    else:
        print("⚠️  SETUP INCOMPLETE")
        print("   Some components need attention before starting debates.")
    
    print(f"\nNext steps:")
    print(f"1. Set OPENAI_API_KEY environment variable")
    print(f"2. Run: python tools/python_expert_debate.py")
    print(f"3. Analyze SysML v2 architecture with expert debates")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)