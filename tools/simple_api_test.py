#!/usr/bin/env python3
"""Simple OpenAI API key test."""

import sys

def main():
    print("🔧 OpenAI API Key Test")
    print("=" * 30)
    print()
    print("Please enter your OpenAI API key (starts with sk-):")
    print("DO NOT include quotes - just paste the raw key")
    print()
    
    try:
        api_key = input("API Key: ").strip()
        
        # Remove quotes if accidentally included
        if (api_key.startswith('"') and api_key.endswith('"')) or (api_key.startswith("'") and api_key.endswith("'")):
            api_key = api_key[1:-1]
            print("   (Removed quotes)")
        
        print(f"\nTesting key: {api_key[:10]}...{api_key[-4:]}")
        
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5
        )
        
        print("✅ SUCCESS! API key works!")
        print("🎉 Ready for expert debates!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nCheck that your key:")
        print("- Starts with 'sk-'")
        print("- Is the complete key (no missing characters)")
        print("- Is active in your OpenAI account")

if __name__ == "__main__":
    main()