#!/usr/bin/env python3
"""Test Perplexity API directly."""

import os
import requests
import json

def test_perplexity_api():
    """Test a simple Perplexity API call."""
    api_key = os.getenv('PERPLEXITY_API_KEY')
    if not api_key:
        print("❌ PERPLEXITY_API_KEY not set")
        return False
    
    print(f"🔧 Testing Perplexity API...")
    print(f"   Key: {api_key[:10]}...")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "llama-3.1-sonar-small-128k-online",
        "messages": [
            {
                "role": "system", 
                "content": "You are a helpful AI assistant. Respond with a simple JSON object."
            },
            {
                "role": "user", 
                "content": "Please respond with this exact JSON: {\"status\": \"success\", \"message\": \"Perplexity API working\"}"
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
            print(f"   ✅ Response: {content}")
            return True
        else:
            print(f"   ❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False

if __name__ == "__main__":
    success = test_perplexity_api()
    if success:
        print("\n🎉 Perplexity API is working!")
    else:
        print("\n💡 Consider using OpenAI instead")