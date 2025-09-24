#!/usr/bin/env python3
"""Quick test for OpenAI API key setup."""

import os
import sys

def test_openai_setup():
    """Test OpenAI API key and library."""
    print("🔧 Testing OpenAI Setup")
    print("=" * 30)
    
    # Check API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY not set")
        print("   Solution: set OPENAI_API_KEY=your_key_here")
        return False
    
    if not api_key.startswith('sk-'):
        print("⚠️  API key format looks unusual")
        print(f"   Key starts with: {api_key[:10]}...")
        print("   Expected format: sk-...")
    else:
        print(f"✅ API key format correct: {api_key[:10]}...")
    
    # Check OpenAI library
    try:
        from openai import OpenAI
        print("✅ OpenAI library available")
    except ImportError:
        print("❌ OpenAI library not installed")
        print("   Solution: pip install openai")
        return False
    
    # Test simple API call
    try:
        print("🧪 Testing API connection...")
        client = OpenAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say 'Hello from OpenAI API'"}],
            max_tokens=20
        )
        
        message = response.choices[0].message.content
        print(f"✅ API test successful!")
        print(f"   Response: {message}")
        
        return True
        
    except Exception as e:
        print(f"❌ API test failed: {e}")
        print("   Check your API key and internet connection")
        return False

def main():
    print("🤖 OpenAI Expert Debate Setup Test")
    print("=" * 40)
    
    if test_openai_setup():
        print("\n🎉 SUCCESS! OpenAI is ready for expert debates!")
        print("\nNext steps:")
        print("1. Run expert debate demo:")
        print("   python tools/multi_backend_expert_debate.py")
        print("2. Analyze your SysML v2 architecture with AI experts")
    else:
        print("\n⚠️  Setup needs attention - see messages above")

if __name__ == "__main__":
    main()