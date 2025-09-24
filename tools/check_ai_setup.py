#!/usr/bin/env python3
"""Simple backend detection and configuration helper."""

import os
import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.multi_backend_expert_debate import AIBackendConfig

def main():
    print("🔧 AI Backend Setup Guide")
    print("=" * 40)
    
    backends = AIBackendConfig.detect_available_backends()
    
    print("\n📊 Current Status:")
    for name, config in backends.items():
        status = "✅ READY" if config.get("available") and config.get("has_key") else "⚠️ NEEDS SETUP"
        print(f"  {name.upper()}: {status}")
        
        if config.get("available"):
            if config.get("has_key"):
                print(f"    • Library: {config['library']}")
                print(f"    • Models: {', '.join(config['models'])}")
            else:
                key_name = f"{name.upper()}_API_KEY"
                print(f"    • Missing: {key_name} environment variable")
        else:
            print(f"    • Error: {config.get('error', 'Unknown')}")
    
    print("\n🛠️ Setup Options:")
    print("\nOption 1 - OpenAI (Most Tested):")
    print("  1. Get API key from: https://platform.openai.com/api-keys")
    print("  2. Set environment variable:")
    print("     set OPENAI_API_KEY=your_openai_key_here")
    print("  3. Models: GPT-4, GPT-3.5-turbo")
    
    print("\nOption 2 - Perplexity (Alternative):")
    print("  1. Get API key from: https://www.perplexity.ai/settings/api")
    print("  2. Set environment variable:")
    print("     set PERPLEXITY_API_KEY=your_perplexity_key_here")
    print("  3. Models: Llama 3.1 Sonar series")
    
    # Check current environment
    print("\n🔍 Current Environment:")
    openai_key = os.getenv('OPENAI_API_KEY')
    perplexity_key = os.getenv('PERPLEXITY_API_KEY')
    
    if openai_key:
        print(f"  OPENAI_API_KEY: Set (starts with {openai_key[:10]}...)")
    else:
        print(f"  OPENAI_API_KEY: Not set")
    
    if perplexity_key:
        print(f"  PERPLEXITY_API_KEY: Set (starts with {perplexity_key[:10]}...)")
    else:
        print(f"  PERPLEXITY_API_KEY: Not set")
    
    # Recommendations
    ready_count = sum(1 for config in backends.values() if config.get("available") and config.get("has_key"))
    
    if ready_count == 0:
        print("\n💡 Recommendation: Set up OpenAI first (most reliable)")
    elif ready_count == 1:
        print("\n💡 Great! You have one backend ready. Consider setting up both for redundancy.")
    else:
        print("\n🎉 Excellent! Multiple backends available for maximum flexibility.")

if __name__ == "__main__":
    main()