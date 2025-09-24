#!/usr/bin/env python3
"""Multi-Backend Expert Debate System.

Supports both OpenAI and Perplexity APIs for AI Expert debates.
Choose your backend based on availability and preference.
"""
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Any, Optional

class AIBackendConfig:
    """Configuration for different AI backends."""
    
    OPENAI = "openai"
    PERPLEXITY = "perplexity"
    
    @staticmethod
    def detect_available_backends():
        """Detect which AI backends are available."""
        backends = {}
        
        # Check OpenAI
        try:
            from openai import OpenAI
            api_key = os.getenv('OPENAI_API_KEY')
            backends[AIBackendConfig.OPENAI] = {
                "available": True,
                "has_key": bool(api_key),
                "library": "openai",
                "models": ["gpt-4", "gpt-3.5-turbo"]
            }
        except ImportError:
            backends[AIBackendConfig.OPENAI] = {
                "available": False,
                "has_key": False,
                "error": "OpenAI library not installed"
            }
        
        # Check Perplexity
        try:
            import requests
            api_key = os.getenv('PERPLEXITY_API_KEY')
            backends[AIBackendConfig.PERPLEXITY] = {
                "available": True,
                "has_key": bool(api_key),
                "library": "requests (HTTP)",
                "models": ["llama-3.1-sonar-small-128k-online", "llama-3.1-sonar-large-128k-online"]
            }
        except ImportError:
            backends[AIBackendConfig.PERPLEXITY] = {
                "available": False,
                "has_key": False,
                "error": "requests library not installed"
            }
        
        return backends

class MultiBackendExpertAgent:
    """Expert agent that can use OpenAI or Perplexity APIs."""
    
    def __init__(self, expert_name: str, expert_persona_path: str, backend: str = None):
        self.expert_name = expert_name
        self.persona = self._load_persona(expert_persona_path)
        self.conversation_history = []
        
        # Auto-detect backend if not specified
        if backend is None:
            backend = self._choose_best_backend()
        
        self.backend = backend
        self.client = self._setup_client(backend)
    
    def _choose_best_backend(self) -> str:
        """Choose the best available backend."""
        backends = AIBackendConfig.detect_available_backends()
        
        # Prefer OpenAI if available and configured
        if (backends.get(AIBackendConfig.OPENAI, {}).get("available") and 
            backends.get(AIBackendConfig.OPENAI, {}).get("has_key")):
            return AIBackendConfig.OPENAI
        
        # Fall back to Perplexity
        if (backends.get(AIBackendConfig.PERPLEXITY, {}).get("available") and 
            backends.get(AIBackendConfig.PERPLEXITY, {}).get("has_key")):
            return AIBackendConfig.PERPLEXITY
        
        raise RuntimeError("No AI backend available. Set OPENAI_API_KEY or PERPLEXITY_API_KEY")
    
    def _setup_client(self, backend: str):
        """Set up the AI client for the chosen backend."""
        if backend == AIBackendConfig.OPENAI:
            try:
                from openai import OpenAI
                api_key = os.getenv('OPENAI_API_KEY')
                if not api_key:
                    raise RuntimeError("OPENAI_API_KEY environment variable required")
                return OpenAI(api_key=api_key)
            except ImportError:
                raise RuntimeError("OpenAI library not installed. Run: pip install openai")
        
        elif backend == AIBackendConfig.PERPLEXITY:
            try:
                import requests
                api_key = os.getenv('PERPLEXITY_API_KEY')
                if not api_key:
                    raise RuntimeError("PERPLEXITY_API_KEY environment variable required")
                return {
                    "api_key": api_key,
                    "base_url": "https://api.perplexity.ai/chat/completions",
                    "session": requests.Session()
                }
            except ImportError:
                raise RuntimeError("requests library not installed. Run: pip install requests")
        
        else:
            raise ValueError(f"Unknown backend: {backend}")
    
    def _load_persona(self, persona_path: str) -> Dict:
        """Load expert persona from markdown file."""
        try:
            with open(persona_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract persona info from markdown
            persona = {
                "name": self.expert_name,
                "content": content,
                "path": persona_path
            }
            return persona
        except Exception as e:
            print(f"Warning: Could not load persona from {persona_path}: {e}")
            return {"name": self.expert_name, "content": "", "path": persona_path}
    
    def analyze(self, artifact: Dict) -> Dict:
        """Analyze an artifact using the configured AI backend."""
        try:
            system_prompt = f"""You are {self.expert_name}, an expert AI agent.

{self.persona.get('content', '')}

Analyze the provided artifact and respond with structured JSON:
{{
    "expert": "{self.expert_name}",
    "analysis": "Your detailed analysis...",
    "key_concerns": ["concern1", "concern2"],
    "recommendations": ["rec1", "rec2"], 
    "confidence": 0.85
}}"""

            user_prompt = f"""Analyze this artifact:

Title: {artifact.get('title', 'Untitled')}
Type: {artifact.get('type', 'unknown')}
Description: {artifact.get('description', '')}

Content:
{artifact.get('content', '')}

Provide your expert analysis focusing on your domain expertise."""

            if self.backend == AIBackendConfig.OPENAI:
                response = self._call_openai(system_prompt, user_prompt)
            elif self.backend == AIBackendConfig.PERPLEXITY:
                response = self._call_perplexity(system_prompt, user_prompt)
            else:
                raise ValueError(f"Unknown backend: {self.backend}")
            
            return self._parse_expert_response(response)
            
        except Exception as e:
            return {
                "expert": self.expert_name,
                "status": "error",
                "error": str(e),
                "analysis": f"Expert {self.expert_name} encountered an error during analysis.",
                "backend": self.backend
            }
    
    def _call_openai(self, system_prompt: str, user_prompt: str) -> str:
        """Call OpenAI API."""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=1000,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    
    def _call_perplexity(self, system_prompt: str, user_prompt: str) -> str:
        """Call Perplexity API."""
        headers = {
            "Authorization": f"Bearer {self.client['api_key']}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "llama-3.1-sonar-small-128k-online",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "max_tokens": 1000,
            "temperature": 0.7
        }
        
        response = self.client["session"].post(
            self.client["base_url"],
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            raise Exception(f"Perplexity API error: {response.status_code} - {response.text}")
    
    def _parse_expert_response(self, response_text: str) -> Dict:
        """Parse expert analysis response."""
        try:
            # Try to parse as JSON
            parsed = json.loads(response_text)
            parsed['raw_response'] = response_text
            parsed['parse_status'] = 'success'
            parsed['backend'] = self.backend
            
            self.conversation_history.append({
                'type': 'analysis',
                'timestamp': time.time(),
                'analysis': parsed.get('analysis', ''),
                'response': parsed
            })
            return parsed
            
        except json.JSONDecodeError:
            # Try to extract JSON from response
            try:
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    parsed = json.loads(json_match.group())
                    parsed['raw_response'] = response_text
                    parsed['parse_status'] = 'extracted'
                    parsed['backend'] = self.backend
                    return parsed
            except json.JSONDecodeError:
                pass
            
            # Fallback to structured text parsing
            fallback = {
                "expert": self.expert_name,
                "analysis": response_text,
                "key_concerns": [],
                "recommendations": [],
                "confidence": 0.5,
                "raw_response": response_text,
                "parse_status": "fallback",
                "backend": self.backend
            }
            
            self.conversation_history.append({
                'type': 'analysis',
                'timestamp': time.time(),
                'analysis': response_text,
                'response': fallback
            })
            return fallback


def check_ai_backends():
    """Check available AI backends and provide setup instructions."""
    print("🤖 AI Backend Configuration Check")
    print("=" * 50)
    
    backends = AIBackendConfig.detect_available_backends()
    
    for backend_name, config in backends.items():
        print(f"\n{backend_name.upper()}:")
        if config["available"]:
            print(f"  ✅ Library available: {config['library']}")
            if config["has_key"]:
                print(f"  ✅ API key configured")
                print(f"  📋 Models: {', '.join(config['models'])}")
            else:
                key_var = f"{backend_name.upper()}_API_KEY"
                print(f"  ⚠️  API key missing: Set {key_var} environment variable")
        else:
            print(f"  ❌ Not available: {config.get('error', 'Unknown error')}")
    
    # Determine best option
    ready_backends = [
        name for name, config in backends.items() 
        if config["available"] and config["has_key"]
    ]
    
    if ready_backends:
        print(f"\n🎉 Ready to use: {', '.join(ready_backends)}")
        return True
    else:
        print(f"\n⚠️  Setup needed:")
        print(f"Option 1 - OpenAI: pip install openai && set OPENAI_API_KEY=your_key")
        print(f"Option 2 - Perplexity: pip install requests && set PERPLEXITY_API_KEY=your_key")
        return False


def demo_multi_backend_system():
    """Demo the multi-backend expert system."""
    print("🚀 Multi-Backend Expert System Demo")
    print("=" * 50)
    
    # Check backends first
    if not check_ai_backends():
        print("\n❌ Setup incomplete - configure an AI backend first")
        return False
    
    # Sample artifact
    test_artifact = {
        "title": "Model Railroad Scale Converter",
        "type": "requirement", 
        "description": "Web-based tool for converting measurements between model railroad scales",
        "content": """
        Requirements:
        1. Support N, HO, O, and G scales
        2. Convert between real measurements and scale measurements
        3. Accuracy within 0.1mm
        4. Web interface with mobile support
        5. Validate against published scale standards
        """
    }
    
    # Test with one expert
    try:
        expert = MultiBackendExpertAgent(
            "Requirements Engineer",
            "intake/ai_experts/requirements_engineer.md"
        )
        
        print(f"\n🔬 Testing {expert.expert_name} with {expert.backend} backend...")
        analysis = expert.analyze(test_artifact)
        
        print(f"✅ Analysis complete:")
        print(f"   Backend: {analysis.get('backend', 'unknown')}")
        print(f"   Status: {analysis.get('parse_status', 'unknown')}")
        print(f"   Confidence: {analysis.get('confidence', 'N/A')}")
        print(f"   Analysis preview: {analysis.get('analysis', '')[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return False


if __name__ == "__main__":
    success = demo_multi_backend_system()
    sys.exit(0 if success else 1)