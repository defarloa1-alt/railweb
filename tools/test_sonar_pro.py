#!/usr/bin/env python3
"""Test the sonar-pro model that was found in legacy code."""

import os
import requests
import json

def test_sonar_pro():
    """Test the sonar-pro model specifically."""
    api_key = os.getenv('PERPLEXITY_API_KEY')
    if not api_key:
        print("❌ PERPLEXITY_API_KEY not set")
        return False
    
    print(f"🔧 Testing Perplexity sonar-pro model (found in legacy code)")
    print(f"   Key: {api_key[:10]}...")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Test the exact model from legacy code
    data = {
        "model": "sonar-pro",
        "messages": [
            {
                "role": "user", 
                "content": "Test: Respond with JSON {\"status\": \"success\", \"model\": \"sonar-pro\"}"
            }
        ],
        "max_tokens": 100,
        "temperature": 0.1
    }
    
    try:
        response = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            print(f"   ✅ SUCCESS with sonar-pro!")
            print(f"   Response: {content}")
            return True
        else:
            print(f"   ❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False

if __name__ == "__main__":
    success = test_sonar_pro()
    if success:
        print("\n🎉 Found working Perplexity model: sonar-pro")
        print("   This model works with your API key!")
    else:
        print("\n💡 sonar-pro didn't work either - proceed with OpenAI")