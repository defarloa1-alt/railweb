#!/usr/bin/env python3
"""Simple test to verify OpenAI connection."""

def main():
    print("🔧 Quick OpenAI Test")
    print("=" * 30)
    
    # Manual API key input for testing
    print("Enter your OpenAI API key:")
    api_key = input("Key (sk-...): ").strip()
    
    if not api_key:
        print("❌ No key provided")
        return
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        print("🧪 Testing API call...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say 'OpenAI working for expert debates!'"}],
            max_tokens=20
        )
        
        message = response.choices[0].message.content
        print(f"✅ SUCCESS: {message}")
        print("\n🎉 Ready for expert debates!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()