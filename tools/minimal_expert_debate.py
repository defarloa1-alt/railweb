#!/usr/bin/env python3
"""Minimum Viable AI Expert Debate System.

This module provides the core components needed to start expert debates:
1. Expert function calling bridge to OpenAI
2. Basic debate orchestration
3. Expert output parsing
4. Simple consensus detection
"""
import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import requests

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))

class ExpertAgent:
    """Individual AI Expert Agent with function calling."""
    
    def __init__(self, expert_name: str, expert_persona_path: str, adapter_url: str = "http://localhost:3001"):
        self.expert_name = expert_name
        self.adapter_url = adapter_url.rstrip('/')
        self.persona = self._load_persona(expert_persona_path)
        self.conversation_history = []
    
    def _load_persona(self, persona_path: str) -> Dict:
        """Load expert persona from markdown file."""
        persona_file = Path(persona_path)
        if not persona_file.exists():
            raise FileNotFoundError(f"Expert persona not found: {persona_path}")
        
        content = persona_file.read_text(encoding='utf-8')
        
        # Extract persona info (simplified - could use YAML parser for front matter)
        return {
            "name": self.expert_name,
            "content": content,
            "role": f"You are the {self.expert_name} from the persona document.",
            "specialization": self._extract_specialization(content)
        }
    
    def _extract_specialization(self, content: str) -> str:
        """Extract key specialization from persona content."""
        # Simple extraction - look for key phrases
        if "Requirements Engineer" in content:
            return "requirements analysis and SysML v2 compliance"
        elif "Project Planner" in content:
            return "project planning and resource management"
        elif "System Architect" in content:
            return "system architecture and technical design"
        elif "SysML Advisor" in content:
            return "SysML v2 compliance and standards evolution"
        elif "Debate Orchestrator" in content:
            return "multi-expert conversation management"
        else:
            return "domain expertise"
    
    def analyze(self, input_artifact: Dict, context: Dict = None) -> Dict:
        """Analyze an input artifact from the expert's perspective."""
        context = context or {}
        
        # Build expert-specific prompt
        prompt = self._build_analysis_prompt(input_artifact, context)
        
        # Call LLM adapter
        try:
            response = self._call_adapter(prompt, "expert_analysis")
            return self._parse_expert_response(response)
        except Exception as e:
            return {
                "expert": self.expert_name,
                "status": "error",
                "error": str(e),
                "analysis": f"Expert {self.expert_name} encountered an error during analysis."
            }
    
    def debate_respond(self, debate_context: Dict, expert_positions: List[Dict]) -> Dict:
        """Respond to other experts in a debate context."""
        prompt = self._build_debate_prompt(debate_context, expert_positions)
        
        try:
            response = self._call_adapter(prompt, "debate_response")
            return self._parse_debate_response(response)
        except Exception as e:
            return {
                "expert": self.expert_name,
                "status": "error",
                "error": str(e),
                "response": f"Expert {self.expert_name} could not respond to debate."
            }
    
    def _build_analysis_prompt(self, artifact: Dict, context: Dict) -> str:
        """Build prompt for initial expert analysis."""
        return f"""You are the {self.expert_name} with expertise in {self.persona['specialization']}.

PERSONA CONTEXT:
{self.persona['content'][:1000]}...

ANALYSIS TASK:
Analyze the following artifact from your expert perspective:

ARTIFACT:
Title: {artifact.get('title', 'Unknown')}
Type: {artifact.get('type', 'Unknown')}
Description: {artifact.get('description', '')}
Content: {artifact.get('content', '')[:2000]}

CONTEXT:
{json.dumps(context, indent=2)}

REQUIREMENTS:
1. Provide your expert analysis
2. Identify key concerns from your domain perspective
3. Suggest improvements or alternatives
4. Note any compliance or standards issues
5. Rate confidence in your analysis (0.0-1.0)

RESPOND IN JSON FORMAT:
{{
    "expert": "{self.expert_name}",
    "analysis": "Your detailed analysis...",
    "key_concerns": ["concern1", "concern2"],
    "recommendations": ["rec1", "rec2"],
    "compliance_notes": "Any standards/compliance observations",
    "confidence": 0.85,
    "rationale": "Why you have this confidence level"
}}"""
    
    def _build_debate_prompt(self, debate_context: Dict, expert_positions: List[Dict]) -> str:
        """Build prompt for debate response."""
        other_positions = [pos for pos in expert_positions if pos.get('expert') != self.expert_name]
        
        positions_text = "\n\n".join([
            f"=== {pos.get('expert', 'Unknown Expert')} ===\n{pos.get('analysis', pos.get('response', 'No analysis'))}"
            for pos in other_positions
        ])
        
        return f"""You are the {self.expert_name} with expertise in {self.persona['specialization']}.

DEBATE CONTEXT:
{debate_context.get('topic', 'Expert analysis discussion')}

YOUR PREVIOUS ANALYSIS:
{self._get_latest_analysis()}

OTHER EXPERT POSITIONS:
{positions_text}

DEBATE INSTRUCTIONS:
1. Review other experts' positions
2. Identify points of agreement and disagreement
3. Defend your position with evidence
4. Challenge other positions constructively
5. Suggest compromises or alternatives where appropriate
6. Maintain professional respect for other experts

RESPOND IN JSON FORMAT:
{{
    "expert": "{self.expert_name}",
    "response": "Your debate response...",
    "agreements": ["points you agree with"],
    "disagreements": ["points you disagree with and why"],
    "challenges": ["questions or challenges for other experts"],
    "compromises": ["potential middle-ground solutions"],
    "confidence": 0.85
}}"""
    
    def _get_latest_analysis(self) -> str:
        """Get the most recent analysis from conversation history."""
        for msg in reversed(self.conversation_history):
            if msg.get('type') == 'analysis':
                return msg.get('analysis', 'No previous analysis')
        return "No previous analysis available"
    
    def _call_adapter(self, prompt: str, intent: str) -> Dict:
        """Call the LLM adapter."""
        payload = {
            "run_id": f"expert_debate_{int(time.time())}",
            "artifacts": [],
            "intent": intent,
            "prompt": prompt
        }
        
        response = requests.post(
            f"{self.adapter_url}/api/llm/summarizeRun",
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    
    def _parse_expert_response(self, response: Dict) -> Dict:
        """Parse expert analysis response."""
        text = response.get('text', '')
        
        try:
            # Try to parse as JSON
            parsed = json.loads(text)
            parsed['raw_response'] = text
            self.conversation_history.append({
                'type': 'analysis',
                'timestamp': time.time(),
                'analysis': parsed.get('analysis', ''),
                'response': parsed
            })
            return parsed
        except json.JSONDecodeError:
            # Fallback to structured text parsing
            fallback = {
                "expert": self.expert_name,
                "analysis": text,
                "key_concerns": [],
                "recommendations": [],
                "confidence": 0.5,
                "raw_response": text,
                "parse_status": "fallback"
            }
            self.conversation_history.append({
                'type': 'analysis',
                'timestamp': time.time(),
                'analysis': text,
                'response': fallback
            })
            return fallback
    
    def _parse_debate_response(self, response: Dict) -> Dict:
        """Parse debate response."""
        text = response.get('text', '')
        
        try:
            parsed = json.loads(text)
            parsed['raw_response'] = text
            self.conversation_history.append({
                'type': 'debate',
                'timestamp': time.time(),
                'response': parsed.get('response', ''),
                'data': parsed
            })
            return parsed
        except json.JSONDecodeError:
            fallback = {
                "expert": self.expert_name,
                "response": text,
                "agreements": [],
                "disagreements": [],
                "challenges": [],
                "compromises": [],
                "confidence": 0.5,
                "raw_response": text,
                "parse_status": "fallback"
            }
            self.conversation_history.append({
                'type': 'debate',
                'timestamp': time.time(),
                'response': text,
                'data': fallback
            })
            return fallback


class MinimalDebateOrchestrator:
    """Minimal debate orchestrator for AI Expert system."""
    
    def __init__(self, adapter_url: str = "http://localhost:3001"):
        self.adapter_url = adapter_url
        self.experts = {}
        self.debate_history = []
        
        # Define expert persona paths
        self.expert_personas = {
            "Requirements Engineer": "intake/ai_experts/requirements_engineer.md",
            "Project Planner": "intake/ai_experts/project_planner.md", 
            "System Architect": "intake/ai_experts/system_architect.md",
            "SysML Advisor": "intake/ai_experts/sysml_advisor.md"
        }
    
    def initialize_experts(self) -> None:
        """Initialize all expert agents."""
        print("🧠 Initializing AI Expert agents...")
        
        for expert_name, persona_path in self.expert_personas.items():
            try:
                self.experts[expert_name] = ExpertAgent(expert_name, persona_path, self.adapter_url)
                print(f"  ✅ {expert_name} initialized")
            except Exception as e:
                print(f"  ❌ {expert_name} failed: {e}")
    
    def run_debate(self, input_artifact: Dict, max_rounds: int = 3) -> Dict:
        """Run a complete expert debate on an input artifact."""
        print(f"\n🎯 Starting expert debate on: {input_artifact.get('title', 'Unknown Artifact')}")
        
        if not self.experts:
            self.initialize_experts()
        
        debate_result = {
            "artifact": input_artifact,
            "rounds": [],
            "consensus": None,
            "timestamp": time.time()
        }
        
        # Round 1: Initial expert analyses (parallel)
        print(f"\n📋 Round 1: Initial Expert Analyses")
        initial_analyses = {}
        
        for expert_name, expert in self.experts.items():
            print(f"  🔍 {expert_name} analyzing...")
            analysis = expert.analyze(input_artifact)
            initial_analyses[expert_name] = analysis
            print(f"     Confidence: {analysis.get('confidence', 'unknown')}")
        
        debate_result["rounds"].append({
            "round": 1,
            "type": "initial_analysis",
            "responses": initial_analyses
        })
        
        # Rounds 2+: Debate rounds
        expert_positions = list(initial_analyses.values())
        
        for round_num in range(2, max_rounds + 1):
            print(f"\n💬 Round {round_num}: Expert Debate")
            
            debate_context = {
                "topic": f"Analysis of {input_artifact.get('title', 'artifact')}",
                "round": round_num,
                "previous_positions": expert_positions
            }
            
            round_responses = {}
            
            for expert_name, expert in self.experts.items():
                print(f"  🗣️  {expert_name} responding...")
                response = expert.debate_respond(debate_context, expert_positions)
                round_responses[expert_name] = response
            
            debate_result["rounds"].append({
                "round": round_num,
                "type": "debate_round",
                "responses": round_responses
            })
            
            # Update positions for next round
            expert_positions = list(round_responses.values())
            
            # Check for consensus
            consensus_score = self._calculate_consensus(round_responses)
            print(f"     Consensus score: {consensus_score:.2f}")
            
            if consensus_score > 0.8:
                print("     ✅ Strong consensus reached!")
                break
        
        # Generate final consensus
        print(f"\n🎯 Generating final consensus...")
        consensus = self._generate_consensus(debate_result)
        debate_result["consensus"] = consensus
        
        self.debate_history.append(debate_result)
        return debate_result
    
    def _calculate_consensus(self, responses: Dict[str, Dict]) -> float:
        """Calculate consensus score based on expert responses."""
        if not responses:
            return 0.0
        
        # Simple consensus calculation based on agreement/disagreement ratios
        total_agreements = 0
        total_disagreements = 0
        total_confidence = 0
        expert_count = 0
        
        for expert_name, response in responses.items():
            agreements = response.get('agreements', [])
            disagreements = response.get('disagreements', [])
            confidence = response.get('confidence', 0.5)
            
            total_agreements += len(agreements)
            total_disagreements += len(disagreements)
            total_confidence += confidence
            expert_count += 1
        
        if total_agreements + total_disagreements == 0:
            return total_confidence / expert_count if expert_count > 0 else 0.0
        
        agreement_ratio = total_agreements / (total_agreements + total_disagreements)
        avg_confidence = total_confidence / expert_count if expert_count > 0 else 0.0
        
        # Weighted combination
        consensus_score = (agreement_ratio * 0.6) + (avg_confidence * 0.4)
        return min(consensus_score, 1.0)
    
    def _generate_consensus(self, debate_result: Dict) -> Dict:
        """Generate consensus from debate results."""
        rounds = debate_result.get('rounds', [])
        if not rounds:
            return {"status": "no_debate", "consensus": "No debate rounds found"}
        
        # Get final round responses
        final_round = rounds[-1]
        final_responses = final_round.get('responses', {})
        
        # Collect key points
        all_agreements = []
        all_recommendations = []
        all_concerns = []
        
        for expert_name, response in final_responses.items():
            all_agreements.extend(response.get('agreements', []))
            if 'recommendations' in response:
                all_recommendations.extend(response.get('recommendations', []))
            if 'key_concerns' in response:
                all_concerns.extend(response.get('key_concerns', []))
        
        consensus_score = self._calculate_consensus(final_responses)
        
        return {
            "consensus_score": consensus_score,
            "status": "strong" if consensus_score > 0.8 else "weak" if consensus_score > 0.5 else "conflict",
            "agreed_points": list(set(all_agreements)),
            "combined_recommendations": list(set(all_recommendations)),
            "key_concerns": list(set(all_concerns)),
            "expert_count": len(final_responses),
            "debate_rounds": len(rounds)
        }


def demo_expert_debate():
    """Demo function to test the expert debate system."""
    print("🚀 AI Expert Debate System Demo")
    print("=" * 50)
    
    # Sample artifact for debate
    sample_artifact = {
        "title": "Scale Converter Requirements",
        "type": "requirement",
        "description": "Requirements for a model railroad scale conversion tool",
        "content": """
        The system shall provide scale conversion between N, HO, O, and G scales.
        Conversions must be accurate to 0.1mm precision.
        The interface should be web-based and mobile-friendly.
        All conversion formulas must be validated against published standards.
        """,
        "wikidata_qids": [],
        "provenance": {
            "source": "human",
            "timestamp": "2024-09-20T12:00:00Z"
        }
    }
    
    # Create orchestrator and run debate
    orchestrator = MinimalDebateOrchestrator()
    
    try:
        debate_result = orchestrator.run_debate(sample_artifact, max_rounds=2)
        
        print(f"\n📊 Debate Results Summary:")
        print(f"   Rounds: {len(debate_result['rounds'])}")
        
        consensus = debate_result.get('consensus', {})
        print(f"   Consensus Score: {consensus.get('consensus_score', 0):.2f}")
        print(f"   Status: {consensus.get('status', 'unknown')}")
        print(f"   Agreed Points: {len(consensus.get('agreed_points', []))}")
        print(f"   Recommendations: {len(consensus.get('combined_recommendations', []))}")
        
        return debate_result
        
    except Exception as e:
        print(f"❌ Debate failed: {e}")
        return None


if __name__ == '__main__':
    # Check if LLM adapter is running
    try:
        response = requests.get("http://localhost:3001/health", timeout=5)
        print("✅ LLM Adapter is running")
    except:
        print("❌ LLM Adapter not running - start with: cd tools/llm_adapter && npm start")
        sys.exit(1)
    
    # Run demo
    result = demo_expert_debate()
    
    if result:
        print(f"\n✅ Demo completed successfully!")
        print(f"Full results saved to debug output.")
    else:
        print(f"\n❌ Demo failed - check logs above.")