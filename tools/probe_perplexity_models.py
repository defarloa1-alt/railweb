#!/usr/bin/env python3
"""Probe Perplexity API models to find which ones work with your API key."""

import os
import requests
import json
import time

def probe_perplexity_models():
    """Test different Perplexity models to see which are accessible."""
    api_key = os.getenv('PERPLEXITY_API_KEY')
    if not api_key:
        print("❌ PERPLEXITY_API_KEY not set")
        return []
    
    print(f"🔍 Probing Perplexity Models")
    print(f"   API Key: {api_key[:10]}...")
    print("=" * 50)
    
    # All known Perplexity models (different tiers)
    models_to_test = [
        # Basic/Free tier models
        "llama-3.1-sonar-small-128k-chat",
        "llama-3.1-sonar-large-128k-chat", 
        
        # Online models (with search)
        "llama-3.1-sonar-small-128k-online",
        "llama-3.1-sonar-large-128k-online",
        "llama-3.1-sonar-huge-128k-online",
        
        # Pro models
        "llama-3.1-70b-instruct",
        "llama-3.1-8b-instruct",
        "mixtral-8x7b-instruct",
        
        # Older models
        "pplx-7b-chat",
        "pplx-70b-chat", 
        "pplx-7b-online",
        "pplx-70b-online",
        
        # Alternative naming
        "sonar-small-chat",
        "sonar-medium-chat",
        "sonar-small-online",
        "sonar-medium-online"
    ]
    
    working_models = []
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    test_message = {
        "messages": [
            {
                "role": "user", 
                "content": "Say 'Hello' in JSON format: {\"response\": \"Hello\"}"
            }
        ],
        "max_tokens": 50,
        "temperature": 0.1
    }
    
    for i, model in enumerate(models_to_test, 1):
        print(f"\n{i:2d}. Testing {model}...")
        
        data = {**test_message, "model": model}
        
        try:
            response = requests.post(
                "https://api.perplexity.ai/chat/completions",
                headers=headers,
                json=data,
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                print(f"    ✅ SUCCESS: {content[:50]}...")
                working_models.append({
                    "model": model,
                    "response": content,
                    "tier": classify_model_tier(model)
                })
            elif response.status_code == 401:
                print(f"    ❌ UNAUTHORIZED (model not in your plan)")
            elif response.status_code == 400:
                try:
                    error_info = response.json()
                    error_msg = error_info.get("error", {}).get("message", "Bad request")
                    print(f"    ❌ BAD REQUEST: {error_msg}")
                except:
                    print(f"    ❌ BAD REQUEST: {response.text[:100]}")
            else:
                print(f"    ❌ ERROR {response.status_code}: {response.text[:100]}")
                
        except requests.exceptions.Timeout:
            print(f"    ⏱️ TIMEOUT (might work but slow)")
        except Exception as e:
            print(f"    ❌ EXCEPTION: {e}")
        
        # Small delay to be nice to the API
        time.sleep(0.5)
    
    return working_models

def classify_model_tier(model_name):
    """Classify model by likely tier/subscription level."""
    if "huge" in model_name or "70b" in model_name:
        return "Pro/Premium"
    elif "large" in model_name or "medium" in model_name:
        return "Standard"
    elif "small" in model_name or "7b" in model_name:
        return "Basic/Free"
    else:
        return "Unknown"

def recommend_best_model(working_models):
    """Recommend the best working model."""
    if not working_models:
        print("\n❌ No working models found!")
        return None
    
    print(f"\n🎉 Found {len(working_models)} working models:")
    print("=" * 50)
    
    # Sort by preference (online > chat, larger > smaller)
    def model_score(model_info):
        name = model_info["model"]
        score = 0
        
        # Prefer online models (have search)
        if "online" in name:
            score += 1000
        
        # Prefer larger models
        if "huge" in name:
            score += 500
        elif "large" in name:
            score += 300
        elif "medium" in name:
            score += 200
        elif "70b" in name:
            score += 400
        
        # Prefer newer versions
        if "3.1" in name:
            score += 100
        
        return score
    
    sorted_models = sorted(working_models, key=model_score, reverse=True)
    
    for i, model_info in enumerate(sorted_models, 1):
        name = model_info["model"]
        tier = model_info["tier"]
        print(f"{i:2d}. {name} ({tier})")
    
    best_model = sorted_models[0]
    print(f"\n🥇 RECOMMENDED: {best_model['model']}")
    print(f"   Tier: {best_model['tier']}")
    print(f"   Reason: Best balance of capabilities and availability")
    
    return best_model

def update_expert_system_with_best_model(best_model):
    """Update the expert system to use the best working model."""
    if not best_model:
        return False
    
    model_name = best_model["model"]
    print(f"\n🔧 Updating expert system to use: {model_name}")
    
    # Update the multi-backend expert system
    try:
        with open("tools/multi_backend_expert_debate.py", "r") as f:
            content = f.read()
        
        # Replace the default model
        old_model = 'model": "llama-3.1-sonar-small-128k-online"'
        new_model = f'model": "{model_name}"'
        
        if old_model in content:
            content = content.replace(old_model, new_model)
            with open("tools/multi_backend_expert_debate.py", "w") as f:
                f.write(content)
            print(f"   ✅ Updated default model to {model_name}")
            return True
        else:
            print(f"   ⚠️ Could not find model string to replace")
            return False
            
    except Exception as e:
        print(f"   ❌ Error updating file: {e}")
        return False

def main():
    """Main probing workflow."""
    print("🚀 Perplexity Model Probe")
    print("=" * 50)
    print("Testing which Perplexity models work with your API key...")
    print("This will help find the best model for your subscription tier.")
    
    working_models = probe_perplexity_models()
    
    if working_models:
        best_model = recommend_best_model(working_models)
        if best_model:
            update_expert_system_with_best_model(best_model)
            
            print(f"\n🎯 NEXT STEPS:")
            print(f"1. Test the expert system with: python tools/multi_backend_expert_debate.py")
            print(f"2. If it works, you're ready for expert debates!")
            print(f"3. If not, try setting up OpenAI as backup")
    else:
        print(f"\n💡 RECOMMENDATIONS:")
        print(f"1. Check your Perplexity subscription at https://www.perplexity.ai/settings/api")
        print(f"2. Verify your API key is correct")
        print(f"3. Consider setting up OpenAI as alternative:")
        print(f"   set OPENAI_API_KEY=your_openai_key")

if __name__ == "__main__":
    main()