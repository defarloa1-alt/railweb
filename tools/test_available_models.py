#!/usr/bin/env python3
"""
Simple OpenAI model tester - tests different models to see which ones work.
"""

import os
import json
from openai import OpenAI

def test_models():
    """Test different OpenAI models to see which are available."""
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY environment variable not set")
        return
    
    client = OpenAI(api_key=api_key)
    
    # Models to test (in order of preference)
    models_to_test = [
        "gpt-4-turbo",
        "gpt-4",
        "gpt-3.5-turbo",
        "gpt-3.5-turbo-16k"
    ]
    
    print("🧪 Testing OpenAI Models")
    print("=" * 40)
    
    working_models = []
    
    for model in models_to_test:
        print(f"Testing {model}...", end=" ")
        
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "Hello, this is a test."}],
                max_tokens=10
            )
            print("✅ WORKS")
            working_models.append(model)
        except Exception as e:
            print(f"❌ FAILED: {str(e)[:50]}...")
    
    print(f"\n📊 Summary:")
    print(f"Working models: {len(working_models)}")
    for model in working_models:
        print(f"  ✅ {model}")
    
    if working_models:
        print(f"\n💡 Recommended model for expert debate: {working_models[0]}")
        return working_models[0]
    else:
        print("\n❌ No models working - check API key permissions")
        return None

if __name__ == "__main__":
    test_models()