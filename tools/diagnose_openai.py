#!/usr/bin/env python3
"""Diagnose OpenAI API key issues."""

def diagnose_api_key():
    print("🔍 OpenAI API Key Diagnostic")
    print("=" * 40)
    
    print("Enter your OpenAI API key:")
    api_key = input("Key: ").strip()
    
    print(f"\n📋 Key Analysis:")
    print(f"   Length: {len(api_key)} characters")
    print(f"   Starts with: {api_key[:10]}...")
    print(f"   Ends with: ...{api_key[-10:]}")
    print(f"   Format check: {'✅ Looks correct' if api_key.startswith('sk-') and len(api_key) > 40 else '❌ Format issue'}")
    
    if len(api_key) < 40:
        print("   ⚠️  Key seems too short - might be truncated")
    
    if not api_key.startswith('sk-'):
        print("   ⚠️  Key should start with 'sk-'")
    
    print(f"\n🧪 Testing API call...")
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5
        )
        
        print("✅ SUCCESS! API key works correctly")
        print("   You can now run expert debates")
        return True
        
    except Exception as e:
        print(f"❌ API Error: {str(e)}")
        
        if "401" in str(e) or "invalid_api_key" in str(e):
            print("   💡 This is an authentication error")
            print("   Solutions:")
            print("   1. Double-check you copied the complete key")
            print("   2. Make sure the key is active (check OpenAI dashboard)")
            print("   3. Try generating a new key")
        
        return False

if __name__ == "__main__":
    success = diagnose_api_key()
    
    if success:
        print("\n🚀 Ready to run: python tools/sdlc_expert_debate.py")
    else:
        print("\n🔧 Fix the API key issue first")