#!/usr/bin/env python3
"""
Expert Debate using OpenAI Responses API (new pattern)
Replaces traditional assistant/chat completions pattern
"""

import json
import os
import time
from pathlib import Path

def get_openai_key():
    """Get OpenAI API key from environment only."""
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("❌ OPENAI_API_KEY environment variable not set")
        print("   Set it with: $env:OPENAI_API_KEY = \"your-key-here\"")
        return None
    
    print(f"✅ Found API key (length: {len(api_key)})")
    return api_key

def setup_openai_client(api_key):
    """Set up OpenAI client."""
    try:
        from openai import OpenAI
        return OpenAI(api_key=api_key)
    except ImportError:
        print("❌ OpenAI library not installed. Run: pip install openai")
        return None

class ResponsesAPIExpert:
    """Expert agent using new Responses API pattern."""
    
    def __init__(self, expert_name: str, role_description: str, client):
        self.expert_name = expert_name
        self.role_description = role_description
        self.client = client
    
    def analyze_problem(self, problem_statement: str) -> dict:
        """Analyze problem using Responses API."""
        
        # Create expert prompt using new pattern
        expert_input = f"""You are {self.role_description}.

Analyze this problem and provide expert insights:

{problem_statement}

Provide your analysis as JSON with these fields:
- expert: your role title
- analysis: detailed analysis (200+ words)
- key_concerns: array of 3-4 main concerns
- recommendations: array of 3-4 specific recommendations
- confidence: confidence level (0.0-1.0)

Focus on your area of expertise and provide actionable insights."""

        try:
            # Use new Responses API syntax
            response = self.client.responses.create(
                model="gpt-4",  # Use gpt-4 from your usage limits
                input=expert_input
            )
            
            response_text = response.output_text
            
            # Try to parse JSON
            try:
                analysis = json.loads(response_text)
                analysis['raw_response'] = response_text
                analysis['parse_status'] = 'success'
                return analysis
            except json.JSONDecodeError:
                # Fallback if not JSON
                return {
                    "expert": self.expert_name,
                    "analysis": response_text,
                    "key_concerns": [],
                    "recommendations": [],
                    "confidence": 0.7,
                    "raw_response": response_text,
                    "parse_status": "fallback"
                }
                
        except Exception as e:
            return {
                "expert": self.expert_name,
                "status": "error",
                "error": str(e),
                "analysis": f"Expert {self.expert_name} encountered an error during analysis."
            }

def run_responses_api_debate():
    """Run expert debate using new Responses API."""
    print("🚀 Expert Debate: Responses API Pattern")
    print("=" * 50)
    
    # Get API key
    api_key = get_openai_key()
    if not api_key:
        print("❌ Cannot proceed without OpenAI API key")
        return False
    
    # Setup OpenAI
    client = setup_openai_client(api_key)
    if not client:
        return False
    
    print("✅ OpenAI client ready (Responses API)")
    
    # Problem statement
    problem_statement = """
    Design an automated SysML-based system to manage the Software Development Life Cycle (SDLC) 
    from planning through requirements to design that is:
    
    1. SELF-DOCUMENTING: The system automatically generates and maintains documentation
    2. FULLY TRACEABLE: Complete bidirectional traceability from requirements to implementation
    3. AUTOMATED: Minimal manual intervention in SDLC process management
    4. SYSML-BASED: Uses SysML v2 as the foundational modeling language
    
    The system should integrate:
    - Project planning and milestone tracking
    - Requirements capture and management  
    - System architecture and design
    - Verification and validation
    - Change management and impact analysis
    
    Consider: SysML v2 constructs, tool integration, automation workflows, traceability mechanisms,
    and how to maintain consistency across all SDLC phases.
    """
    
    # Define expert team
    experts = [
        ResponsesAPIExpert(
            "SysML Systems Architect", 
            "a senior systems architect specializing in SysML v2 modeling and systems engineering automation",
            client
        ),
        ResponsesAPIExpert(
            "Requirements Engineering Lead",
            "a requirements engineering expert focused on traceability, automation, and requirements management systems", 
            client
        ),
        ResponsesAPIExpert(
            "SDLC Process Engineer",
            "a software process engineering expert specializing in SDLC automation, DevOps integration, and self-documenting systems",
            client
        )
    ]
    
    print(f"\n📋 Expert Panel (Responses API):")
    for expert in experts:
        print(f"   • {expert.expert_name}")
    
    print(f"\n🎯 Problem Statement:")
    print(problem_statement)
    
    # Run expert analyses
    analyses = {}
    
    for i, expert in enumerate(experts, 1):
        print(f"\n{i}. 🔬 {expert.expert_name} Analysis:")
        print("   " + "=" * 40)
        
        analysis = expert.analyze_problem(problem_statement)
        analyses[expert.expert_name] = analysis
        
        if analysis.get('status') == 'error':
            print(f"   ❌ Error: {analysis.get('error', 'Unknown error')}")
        else:
            print(f"   ✅ Analysis complete (Responses API)")
            
            # Show key points
            if 'analysis' in analysis:
                preview = analysis['analysis'][:200] + "..." if len(analysis['analysis']) > 200 else analysis['analysis']
                print(f"   Preview: {preview}")
    
    # Save results
    results = {
        "problem_statement": problem_statement,
        "expert_analyses": analyses,
        "debate_timestamp": time.time(),
        "api_type": "responses_api",
        "model_used": "gpt-4"
    }
    
    results_file = Path("docs/Responses_API_Expert_Debate_Results.json")
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n📊 Debate Summary:")
    print(f"   API Type: Responses API")
    print(f"   Experts analyzed: {len(experts)}")
    print(f"   Detailed results: {results_file}")
    
    return True

if __name__ == "__main__":
    success = run_responses_api_debate()
    if success:
        print("\n🎉 Responses API expert debate completed!")
        print("   Check the generated documents for detailed analysis.")
    else:
        print("\n❌ Responses API expert debate failed - check setup and try again.")