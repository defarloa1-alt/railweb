#!/usr/bin/env python3
"""Check available OpenAI models and their purposes."""

import os

def explain_openai_models():
    """Explain different OpenAI models and their use cases."""
    print("🤖 OpenAI Models Guide for Expert Debates")
    print("=" * 50)
    
    models = {
        "Chat/Completion Models (What we need)": {
            "gpt-4": {
                "purpose": "Most capable model for complex reasoning and analysis",
                "best_for": "Expert debates, complex analysis, detailed reasoning",
                "cost": "Higher cost but best quality",
                "recommended": "⭐ Best for expert debates"
            },
            "gpt-4-turbo": {
                "purpose": "Faster version of GPT-4 with similar capabilities",
                "best_for": "Expert debates with faster response times",
                "cost": "Moderate cost, good balance",
                "recommended": "✅ Good for expert debates"
            },
            "gpt-3.5-turbo": {
                "purpose": "Fast and efficient for most tasks",
                "best_for": "Quick analysis, cost-effective debates",
                "cost": "Lower cost, good for testing",
                "recommended": "✅ Good for testing/demos"
            }
        },
        "Specialized Models (Not for debates)": {
            "text-moderation-latest": {
                "purpose": "Content safety and moderation filtering",
                "best_for": "Checking if content violates policies",
                "cost": "Very low cost",
                "recommended": "❌ Not for expert debates"
            },
            "text-embedding-3-small": {
                "purpose": "Convert text to vector embeddings",
                "best_for": "Semantic search, similarity matching",
                "cost": "Low cost",
                "recommended": "🔍 Useful for knowledge graphs"
            },
            "dall-e-3": {
                "purpose": "Image generation",
                "best_for": "Creating diagrams and visualizations",
                "cost": "Per image cost",
                "recommended": "🎨 Future: SysML diagrams"
            }
        }
    }
    
    for category, model_dict in models.items():
        print(f"\n📋 {category}")
        print("-" * 40)
        
        for model_name, info in model_dict.items():
            print(f"\n{model_name}:")
            print(f"  Purpose: {info['purpose']}")
            print(f"  Best for: {info['best_for']}")
            print(f"  Cost: {info['cost']}")
            print(f"  For our use: {info['recommended']}")
    
    print(f"\n🎯 RECOMMENDATION FOR EXPERT DEBATES:")
    print(f"=" * 50)
    print(f"Primary: gpt-4 (best reasoning for complex SysML analysis)")
    print(f"Alternative: gpt-3.5-turbo (faster/cheaper for testing)")
    print(f"Avoid: text-moderation-latest (wrong purpose)")
    
    print(f"\n💡 The moderation model you saw is for content filtering,")
    print(f"   not for the kind of intelligent debate we need!")

def check_current_setup():
    """Check what's currently configured."""
    print(f"\n🔧 Current Setup Check:")
    print(f"=" * 30)
    
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        print(f"✅ OPENAI_API_KEY is set: {api_key[:10]}...")
        print(f"   Ready to use chat models for expert debates")
    else:
        print(f"❌ OPENAI_API_KEY not found in environment")
        print(f"   Need to set: $env:OPENAI_API_KEY = 'your_key_here'")

if __name__ == "__main__":
    explain_openai_models()
    check_current_setup()