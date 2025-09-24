#!/usr/bin/env python3
"""Non-interactive OpenAI test using environment variable or file."""

import os
import sys

def test_openai_connection():
    """Test OpenAI connection without interactive input."""
    print("🔧 OpenAI Connection Test")
    print("=" * 30)
    
    # Try to get API key from environment
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("❌ OPENAI_API_KEY environment variable not set")
        print()
        print("🔧 To set it temporarily in PowerShell:")
        print('   $env:OPENAI_API_KEY = "your_api_key_here"')
        print()
        print("🔧 Or to set it permanently:")
        print('   setx OPENAI_API_KEY "your_api_key_here"')
        print("   (then restart PowerShell)")
        return False
    
    print(f"✅ Found API key: {api_key[:10]}...{api_key[-4:]}")
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        print("🧪 Testing API call...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5
        )
        
        message = response.choices[0].message.content
        print(f"✅ SUCCESS: {message}")
        print("🎉 OpenAI is working! Ready for expert debates!")
        return True
        
    except Exception as e:
        print(f"❌ API Error: {e}")
        
        if "401" in str(e):
            print("   This is an authentication error - check your API key")
        
        return False

if __name__ == "__main__":
    success = test_openai_connection()
    
    if success:
        print("\n🚀 You can now run the expert debate:")
        print("   python tools/sdlc_expert_debate.py")
    else:
        print("\n💡 Set the API key first, then try again")