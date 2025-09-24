#!/usr/bin/env python3
"""
Expert Debate: Automated SysML-based SDLC Management System

Problem Statement: Design an automated SysML-based system to manage the SDLC 
from planning, requirements and design that is self-documenting and fully traceable and without manual intervention.
"""

import json
import os
import sys
import time
from pathlib import Path

def get_openai_key():
    """Get OpenAI API key from environment only."""
    # Only try environment - no prompting
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

class SDLCExpertAgent:
    """Expert agent focused on SysML SDLC system design."""
    
    def __init__(self, expert_name: str, role_description: str, client):
        self.expert_name = expert_name
        self.role_description = role_description
        self.client = client
    
    def analyze_sdlc_problem(self, problem_statement: str) -> dict:
        """Analyze the SysML SDLC automation problem."""
        system_prompt = f"""You are {self.expert_name}, {self.role_description}

You are participating in an expert debate about designing an automated SysML-based SDLC management system.

Focus on your domain expertise and provide structured analysis in JSON format:
{{
    "expert": "{self.expert_name}",
    "analysis": "Your detailed technical analysis...",
    "key_concerns": ["concern1", "concern2", "concern3"],
    "recommendations": ["rec1", "rec2", "rec3"],
    "sysml_components": ["component1", "component2"],
    "traceability_strategy": "Your approach to traceability...",
    "automation_level": "Description of automation scope...",
    "confidence": 0.85
}}

Be specific about SysML v2 constructs, SDLC integration points, and automation mechanisms."""

        user_prompt = f"""Problem to analyze:

{problem_statement}

Provide your expert analysis focusing on:
1. SysML v2 modeling approach for SDLC automation
2. Self-documentation mechanisms
3. Full traceability implementation 
4. Integration with planning/requirements/design phases
5. Automation opportunities and constraints

Give concrete, implementable recommendations from your expertise perspective."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=1500,
                temperature=0.7
            )
            
            response_text = response.choices[0].message.content
            
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

def run_sdlc_expert_debate():
    """Run the expert debate on SysML SDLC automation."""
    print("🚀 Expert Debate: Automated SysML-based SDLC System")
    print("=" * 60)
    
    # Get API key
    api_key = get_openai_key()
    if not api_key:
        print("❌ Cannot proceed without OpenAI API key")
        return False
    
    # Setup OpenAI
    client = setup_openai_client(api_key)
    if not client:
        return False
    
    print("✅ OpenAI client ready")
    
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
        SDLCExpertAgent(
            "SysML Systems Architect", 
            "a senior systems architect specializing in SysML v2 modeling and systems engineering automation",
            client
        ),
        SDLCExpertAgent(
            "Requirements Engineering Lead",
            "a requirements engineering expert focused on traceability, automation, and requirements management systems", 
            client
        ),
        SDLCExpertAgent(
            "SDLC Process Engineer",
            "a software process engineering expert specializing in SDLC automation, DevOps integration, and self-documenting systems",
            client
        )
    ]
    
    print(f"\n📋 Expert Panel:")
    for expert in experts:
        print(f"   • {expert.expert_name}")
    
    print(f"\n🎯 Problem Statement:")
    print(problem_statement)
    
    # Run expert analyses
    analyses = {}
    
    for i, expert in enumerate(experts, 1):
        print(f"\n{i}. 🔬 {expert.expert_name} Analysis:")
        print("   " + "=" * 40)
        
        analysis = expert.analyze_sdlc_problem(problem_statement)
        analyses[expert.expert_name] = analysis
        
        if analysis.get('status') == 'error':
            print(f"   ❌ Error: {analysis.get('error', 'Unknown error')}")
        else:
            print(f"   ✅ Analysis complete")
            
            # Show key points
            if 'analysis' in analysis:
                preview = analysis['analysis'][:200] + "..." if len(analysis['analysis']) > 200 else analysis['analysis']
                print(f"   Preview: {preview}")
            
            if 'confidence' in analysis:
                print(f"   Confidence: {analysis['confidence']}")
    
    # Save detailed results
    results = {
        "problem_statement": problem_statement,
        "expert_analyses": analyses,
        "debate_timestamp": time.time(),
        "model_used": "gpt-4"
    }
    
    output_file = "docs/SDLC_Expert_Debate_Results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n📊 Debate Summary:")
    print(f"   Experts analyzed: {len(analyses)}")
    print(f"   Detailed results: {output_file}")
    
    # Generate summary document
    generate_summary_document(results)
    
    return True

def generate_summary_document(results):
    """Generate a readable summary of the expert debate."""
    summary_file = "docs/SDLC_Expert_Debate_Summary.md"
    
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("# Expert Debate: Automated SysML-based SDLC Management System\n\n")
        f.write(f"**Generated:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## Problem Statement\n\n")
        f.write(results['problem_statement'])
        f.write("\n\n")
        
        f.write("## Expert Analyses\n\n")
        
        for expert_name, analysis in results['expert_analyses'].items():
            f.write(f"### {expert_name}\n\n")
            
            if analysis.get('status') == 'error':
                f.write(f"❌ **Error:** {analysis.get('error')}\n\n")
                continue
            
            if 'analysis' in analysis:
                f.write(f"**Analysis:**\n{analysis['analysis']}\n\n")
            
            if 'key_concerns' in analysis and analysis['key_concerns']:
                f.write("**Key Concerns:**\n")
                for concern in analysis['key_concerns']:
                    f.write(f"- {concern}\n")
                f.write("\n")
            
            if 'recommendations' in analysis and analysis['recommendations']:
                f.write("**Recommendations:**\n")
                for rec in analysis['recommendations']:
                    f.write(f"- {rec}\n")
                f.write("\n")
            
            if 'confidence' in analysis:
                f.write(f"**Confidence:** {analysis['confidence']}\n\n")
            
            f.write("---\n\n")
    
    print(f"   Summary document: {summary_file}")

if __name__ == "__main__":
    success = run_sdlc_expert_debate()
    if success:
        print("\n🎉 Expert debate completed successfully!")
        print("   Check the generated documents for detailed analysis.")
    else:
        print("\n❌ Expert debate failed - check setup and try again.")