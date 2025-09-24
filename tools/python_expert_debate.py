#!/usr/bin/env python3
"""Python-Only Minimal Expert Debate System.

This provides the absolute minimum needed to start expert debates without
requiring Node.js or external servers - just Python + OpenAI API.
"""
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Any, Optional

# Check if OpenAI is available
try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
    print("⚠️  OpenAI library not found. Install with: pip install openai")

class PythonExpertAgent:
    """Expert agent using direct OpenAI calls (no adapter needed)."""
    
    def __init__(self, expert_name: str, expert_persona_path: str):
        self.expert_name = expert_name
        self.persona = self._load_persona(expert_persona_path)
        self.conversation_history = []
        
        if not HAS_OPENAI:
            raise RuntimeError("OpenAI library required for expert agents")
        
        # Set up OpenAI
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY environment variable required")
        
        self.client = OpenAI(api_key=api_key)
    
    def _load_persona(self, persona_path: str) -> Dict:
        """Load expert persona from markdown file."""
        persona_file = Path(persona_path)
        if not persona_file.exists():
            raise FileNotFoundError(f"Expert persona not found: {persona_path}")
        
        content = persona_file.read_text(encoding='utf-8')
        
        return {
            "name": self.expert_name,
            "content": content,
            "role": f"You are the {self.expert_name} AI expert with the following persona.",
            "specialization": self._extract_specialization(content)
        }
    
    def _extract_specialization(self, content: str) -> str:
        """Extract key specialization from persona content."""
        if "Requirements Engineer" in content:
            return "requirements analysis and SysML v2 compliance"
        elif "Project Planner" in content:
            return "project planning and resource management"
        elif "System Architect" in content:
            return "system architecture and technical design"
        elif "SysML Advisor" in content:
            return "SysML v2 compliance and standards evolution"
        else:
            return "domain expertise"
    
    def analyze(self, input_artifact: Dict, context: Dict = None) -> Dict:
        """Analyze an input artifact from the expert's perspective."""
        context = context or {}
        
        # Build expert-specific prompt
        messages = [
            {
                "role": "system",
                "content": self._build_system_prompt()
            },
            {
                "role": "user", 
                "content": self._build_analysis_prompt(input_artifact, context)
            }
        ]
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )
            
            return self._parse_expert_response(response.choices[0].message.content)
            
        except Exception as e:
            return {
                "expert": self.expert_name,
                "status": "error",
                "error": str(e),
                "analysis": f"Expert {self.expert_name} encountered an error during analysis."
            }
    
    def _build_system_prompt(self) -> str:
        """Build system prompt with persona."""
        return f"""You are the {self.expert_name} AI expert with expertise in {self.persona['specialization']}.

PERSONA CONTEXT:
{self.persona['content'][:2000]}

You must respond in valid JSON format with the following structure:
{{
    "expert": "{self.expert_name}",
    "analysis": "Your detailed analysis...",
    "key_concerns": ["concern1", "concern2"],
    "recommendations": ["rec1", "rec2"],
    "compliance_notes": "Any standards/compliance observations",
    "confidence": 0.85,
    "rationale": "Why you have this confidence level"
}}

Always return valid JSON and nothing else."""
    
    def _build_analysis_prompt(self, artifact: Dict, context: Dict) -> str:
        """Build prompt for expert analysis."""
        return f"""Analyze the following artifact from your expert perspective:

ARTIFACT:
Title: {artifact.get('title', 'Unknown')}
Type: {artifact.get('type', 'Unknown')}
Description: {artifact.get('description', '')}
Content: {artifact.get('content', '')[:1500]}

CONTEXT:
{json.dumps(context, indent=2)}

ANALYSIS REQUIREMENTS:
1. Provide your expert analysis from your domain perspective
2. Identify key concerns specific to your expertise area
3. Suggest concrete improvements or alternatives
4. Note any compliance or standards issues
5. Rate your confidence in this analysis (0.0-1.0)

Respond in the JSON format specified in your system prompt."""
    
    def _parse_expert_response(self, response_text: str) -> Dict:
        """Parse expert analysis response."""
        try:
            # Try to parse as JSON
            parsed = json.loads(response_text)
            parsed['raw_response'] = response_text
            parsed['parse_status'] = 'success'
            
            self.conversation_history.append({
                'type': 'analysis',
                'timestamp': time.time(),
                'analysis': parsed.get('analysis', ''),
                'response': parsed
            })
            return parsed
            
        except json.JSONDecodeError:
            # Try to extract JSON from the response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            
            if json_match:
                try:
                    parsed = json.loads(json_match.group())
                    parsed['raw_response'] = response_text
                    parsed['parse_status'] = 'extracted'
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
                "parse_status": "fallback"
            }
            
            self.conversation_history.append({
                'type': 'analysis',
                'timestamp': time.time(),
                'analysis': response_text,
                'response': fallback
            })
            return fallback


class PythonDebateOrchestrator:
    """Python-only debate orchestrator - no external servers needed."""
    
    def __init__(self):
        self.experts = {}
        self.debate_history = []
        
        # Define expert persona paths
        self.expert_personas = {
            "Requirements Engineer": "intake/ai_experts/requirements_engineer.md",
            "Project Planner": "intake/ai_experts/project_planner.md", 
            "System Architect": "intake/ai_experts/system_architect.md",
            "SysML Advisor": "intake/ai_experts/sysml_advisor.md"
        }
    
    def initialize_experts(self) -> bool:
        """Initialize all expert agents."""
        print("🧠 Initializing AI Expert agents (Python-only)...")
        
        if not HAS_OPENAI:
            print("❌ OpenAI library not available")
            return False
        
        if not os.getenv('OPENAI_API_KEY'):
            print("❌ OPENAI_API_KEY environment variable not set")
            return False
        
        initialized_count = 0
        
        for expert_name, persona_path in self.expert_personas.items():
            try:
                self.experts[expert_name] = PythonExpertAgent(expert_name, persona_path)
                print(f"  ✅ {expert_name} initialized")
                initialized_count += 1
            except Exception as e:
                print(f"  ❌ {expert_name} failed: {e}")
        
        return initialized_count > 0
    
    def quick_analysis(self, input_artifact: Dict, expert_names: List[str] = None) -> Dict:
        """Run quick analysis with specified experts (or all)."""
        if not self.experts:
            if not self.initialize_experts():
                return {"error": "Failed to initialize experts"}
        
        experts_to_use = expert_names or list(self.experts.keys())
        
        print(f"\n🔍 Quick Analysis: {input_artifact.get('title', 'Unknown Artifact')}")
        print(f"Using experts: {', '.join(experts_to_use)}")
        
        analyses = {}
        
        for expert_name in experts_to_use:
            if expert_name in self.experts:
                print(f"  ⏳ {expert_name} analyzing...")
                analysis = self.experts[expert_name].analyze(input_artifact)
                analyses[expert_name] = analysis
                
                confidence = analysis.get('confidence', 0)
                status = analysis.get('parse_status', 'unknown')
                print(f"     ✅ Complete (confidence: {confidence}, status: {status})")
            else:
                print(f"  ❌ {expert_name} not available")
        
        result = {
            "artifact": input_artifact,
            "analyses": analyses,
            "expert_count": len(analyses),
            "timestamp": time.time()
        }
        
        return result
    
    def print_analysis_summary(self, result: Dict) -> None:
        """Print a summary of analysis results."""
        print(f"\n📊 Analysis Summary:")
        print(f"   Experts: {result.get('expert_count', 0)}")
        
        analyses = result.get('analyses', {})
        if not analyses:
            print("   No analyses available")
            return
        
        print(f"   Results:")
        for expert_name, analysis in analyses.items():
            confidence = analysis.get('confidence', 0)
            key_concerns = len(analysis.get('key_concerns', []))
            recommendations = len(analysis.get('recommendations', []))
            
            print(f"     {expert_name}:")
            print(f"       Confidence: {confidence}")
            print(f"       Concerns: {key_concerns}")
            print(f"       Recommendations: {recommendations}")
            
            # Show first concern and recommendation
            concerns = analysis.get('key_concerns', [])
            if concerns:
                print(f"       First concern: {concerns[0][:60]}...")
            
            recs = analysis.get('recommendations', [])
            if recs:
                print(f"       First rec: {recs[0][:60]}...")


def demo_python_expert_system():
    """Demo the Python-only expert system."""
    print("🐍 Python-Only Expert System Demo")
    print("=" * 50)
    
    # Check prerequisites
    if not HAS_OPENAI:
        print("❌ Install OpenAI: pip install openai")
        return False
    
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Set OPENAI_API_KEY environment variable")
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
    
    # Run analysis
    orchestrator = PythonDebateOrchestrator()
    
    # Test with just one expert first (faster)
    result = orchestrator.quick_analysis(test_artifact, ["Requirements Engineer"])
    
    if result.get('analyses'):
        orchestrator.print_analysis_summary(result)
        print("\n✅ Demo completed successfully!")
        return True
    else:
        print("\n❌ Demo failed - no analyses produced")
        return False


if __name__ == '__main__':
    success = demo_python_expert_system()
    if success:
        print("\n🎯 Python Expert System is working!")
        print("Ready for full expert debates with all agents.")
    else:
        print("\n❌ Setup incomplete - check error messages above.")