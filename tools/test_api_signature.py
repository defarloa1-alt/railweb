#!/usr/bin/env python3
"""
Test OpenAI API signature and basic functionality
"""

import os
from openai import OpenAI

def test_openai_api():
    """Test the OpenAI API with current signature."""
    
    # Get API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY not set")
        return False
    
    print(f"✅ API Key found (length: {len(api_key)})")
    
    # Create client
    try:
        client = OpenAI(api_key=api_key)
        print("✅ OpenAI client created")
    except Exception as e:
        print(f"❌ Client creation failed: {e}")
        return False
    
    # Test models we have access to
    models_to_test = [
        "o1-mini",
        "o3-mini", 
        "gpt-5-mini",
        "gpt-5-nano",
        "chatgpt-4o-latest",
        "davinci-002",
        "babbage-002"
    ]
    
    for model in models_to_test:
        print(f"\n🧪 Testing model: {model}")
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": "Hello! Just say 'Working' if you can respond."}
                ],
                max_tokens=10,
                temperature=0.1
            )
            
            result = response.choices[0].message.content
            print(f"✅ {model}: {result}")
            
        except Exception as e:
            print(f"❌ {model}: {e}")
    
    return True

if __name__ == "__main__":
    test_openai_api()