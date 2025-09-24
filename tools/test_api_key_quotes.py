#!/usr/bin/env python3
"""Test API key with automatic quote removal."""

def test_with_quote_fix():
    print("🔧 OpenAI API Key Test (with quote fixing)")
    print("=" * 50)
    
    print("Enter your OpenAI API key (quotes will be automatically removed):")
    api_key = input("Key: ").strip()
    
    # Remove quotes if present
    if api_key.startswith('"') and api_key.endswith('"'):
        api_key = api_key[1:-1]
        print("   ✅ Removed double quotes")
    elif api_key.startswith("'") and api_key.endswith("'"):
        api_key = api_key[1:-1]  
        print("   ✅ Removed single quotes")
    
    print(f"   Cleaned key: {api_key[:10]}...{api_key[-4:]}")
    print(f"   Length: {len(api_key)} characters")
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        print("🧪 Testing API call...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say 'API test successful'"}],
            max_tokens=10
        )
        
        message = response.choices[0].message.content
        print(f"✅ SUCCESS: {message}")
        print("\n🎉 OpenAI API is working! Ready for expert debates!")
        return True
        
    except Exception as e:
        print(f"❌ Still failing: {e}")
        return False

if __name__ == "__main__":
    success = test_with_quote_fix()
    
    if success:
        print("\n🚀 Now you can run the expert debate:")
        print("   python tools/sdlc_expert_debate.py")
        print("   (Enter the key WITHOUT quotes when prompted)")
    else:
        print("\n💡 Try these steps:")
        print("   1. Go to https://platform.openai.com/account/api-keys")
        print("   2. Copy the key carefully (starts with sk-)")
        print("   3. Run this test again without quotes")