#!/usr/bin/env python3
"""Quick setup guide for AI Expert debates - OpenAI path."""

import os

def main():
    print("🎯 Expert Debate System - Quick Setup")
    print("=" * 50)
    print()
    
    print("📊 Current Status:")
    openai_key = os.getenv('OPENAI_API_KEY')
    perplexity_key = os.getenv('PERPLEXITY_API_KEY')
    
    if openai_key:
        print("✅ OpenAI: Ready to go!")
        print(f"   Key: {openai_key[:10]}...")
        print("   Recommended: Use OpenAI (most reliable)")
    else:
        print("⚠️  OpenAI: Need to set OPENAI_API_KEY")
    
    if perplexity_key:
        print("⚠️  Perplexity: Key found but no model access")
        print(f"   Key: {perplexity_key[:10]}...")
        print("   Issue: API key doesn't have model permissions")
    else:
        print("❌ Perplexity: Not configured")
    
    print()
    print("🎯 RECOMMENDATION: Set up OpenAI")
    print("=" * 50)
    print()
    print("OpenAI is the most tested and reliable option for expert debates.")
    print()
    print("Steps:")
    print("1. Get API key: https://platform.openai.com/api-keys")
    print("2. Set environment variable:")
    print("   set OPENAI_API_KEY=your_openai_key_here")
    print("3. Test expert system:")
    print("   python tools/multi_backend_expert_debate.py")
    print()
    print("💰 Cost estimate: ~$0.01-0.10 per expert analysis")
    print("🚀 Models: GPT-4 (best) or GPT-3.5-turbo (faster/cheaper)")
    print()
    
    if not openai_key:
        print("❗ Action needed: Set OPENAI_API_KEY to start expert debates")
    else:
        print("🎉 Ready! You can start expert debates now.")
        print()
        print("Next: Test with your SysML v2 architecture:")
        print("   python tools/multi_backend_expert_debate.py")

if __name__ == "__main__":
    main()