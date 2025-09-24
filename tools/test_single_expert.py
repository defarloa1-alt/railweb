#!/usr/bin/env python3
"""
Test single expert with debug output
"""

import os
import sys
from pathlib import Path

# Add the tools directory to the path
sys.path.append(str(Path(__file__).parent))

def test_single_expert():
    """Test a single expert to debug issues."""
    
    # Check API key
    api_key = os.getenv('OPENAI_API_KEY')
    print(f"API Key found: {bool(api_key)}")
    print(f"API Key length: {len(api_key) if api_key else 0}")
    
    if not api_key:
        print("❌ No API key found")
        return
    
    # Test OpenAI import
    try:
        from openai import OpenAI
        print("✅ OpenAI library imported")
    except ImportError as e:
        print(f"❌ OpenAI import failed: {e}")
        return
    
    # Test client creation
    try:
        client = OpenAI(api_key=api_key)
        print("✅ OpenAI client created")
    except Exception as e:
        print(f"❌ Client creation failed: {e}")
        return
    
    # Test simple API call
    try:
        print("🧪 Testing simple API call...")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Say hello"}],
            max_tokens=50
        )
        
        result = response.choices[0].message.content
        print(f"✅ API call successful: {result}")
        
    except Exception as e:
        print(f"❌ API call failed: {e}")
        print(f"Error type: {type(e)}")
        return
    
    print("🎉 All tests passed!")

if __name__ == "__main__":
    test_single_expert()