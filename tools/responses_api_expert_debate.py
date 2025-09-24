#!/usr/bin/env python3
"""Expert Debate orchestration using OpenAI Responses API.

Enhancements:
- Centralised model / org / project configuration (override via env vars)
- Multi-round persona debate with contextual critiques
- Robust response parsing with code-fence removal and schema normalisation
"""

from __future__ import annotations

import json
import os
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

DEFAULT_MODEL = os.getenv("OPENAI_RESPONSES_MODEL", "gpt-4.1-nano-2025-04-14")
ORGANIZATION_ID = os.getenv("OPENAI_ORG_ID", "org-Wjv8zEw9hES0hFwnpZxOoDEm")
PROJECT_ID = os.getenv("OPENAI_PROJECT_ID", "proj_zsBBVeSxc1MunoV5yGAVAgih")
MAX_ROUNDS = max(1, int(os.getenv("RESPONSES_DEBATE_ROUNDS", "3")))
SUMMARY_MAX_ITEMS = 330
SUMMARY_MAX_CHARS = 1000

REQUIRED_FIELDS = {
    "expert": "",
    "analysis": "",
    "system_architecture": "",
    "use_cases": [],
    "roles_responsibilities": "",
    "feedback_loops": "",
    "technical_specifications": "",
    "integration_points": "",
    "validation_criteria": "",
    "implementation_phases": "",
    "risk_mitigation": "",
    "key_concerns": [],
    "recommendations": [],
    "confidence": 0.0,
}


def get_openai_key() -> Optional[str]:
    """Return OPENAI_API_KEY from environment, printing guidance if missing."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("[WARN] OPENAI_API_KEY environment variable not set.")
        print("       Set it with: $env:OPENAI_API_KEY = 'your-key-here'")
        return None
    print(f"[INFO] Found API key (length: {len(api_key)})")
    return api_key


def setup_openai_client(api_key: str):
    """Initialise OpenAI client using Responses API."""
    try:
        from openai import OpenAI
    except ImportError:  # pragma: no cover
        print("[ERROR] OpenAI library not installed. Run: pip install openai")
        return None

    return OpenAI(api_key=api_key, organization=ORGANIZATION_ID, project=PROJECT_ID)


def clean_json_content(text: str) -> str:
    """Strip Markdown code fences and surrounding whitespace."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```[a-zA-Z0-9_-]*\n", "", cleaned, count=1)
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3].rstrip()
    return cleaned


def normalise_analysis(expert_name: str, payload: Dict[str, object], raw: str, parse_status: str) -> Dict[str, object]:
    """Ensure required keys exist and add metadata fields."""
    data = dict(REQUIRED_FIELDS)
    data.update(payload)
    data.setdefault("expert", expert_name)
    if not data.get("expert"):
        data["expert"] = expert_name

    for key, default in REQUIRED_FIELDS.items():
        if isinstance(default, list):
            value = data.get(key)
            if not isinstance(value, list):
                data[key] = [value] if value else []
        elif isinstance(default, float):
            try:
                data[key] = float(data.get(key, default))
            except (TypeError, ValueError):
                data[key] = default
        else:
            value = data.get(key, default)
            data[key] = value if isinstance(value, str) else str(value)

    data["raw_response"] = raw
    data["parse_status"] = parse_status
    return data


def parse_response(expert_name: str, response_text: str) -> Dict[str, object]:
    """Parse Responses API output into structured payload."""
    cleaned = clean_json_content(response_text)
    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        return normalise_analysis(
            expert_name,
            {
                "analysis": response_text,
                "key_concerns": [],
                "recommendations": [],
                "confidence": 0.5,
            },
            raw=response_text,
            parse_status="fallback",
        )

    return normalise_analysis(
        expert_name,
        parsed,
        raw=response_text,
        parse_status="success",
    )


def summarise_analysis(analysis: Dict[str, object]) -> str:
    """Create a compact summary for use in subsequent debate rounds."""
    snippets: List[str] = []

    concerns = analysis.get("key_concerns") or []
    recommendations = analysis.get("recommendations") or []

    if concerns:
        snippets.append("Concerns: " + "; ".join(str(c) for c in concerns[:SUMMARY_MAX_ITEMS]))
    if recommendations:
        snippets.append("Recommendations: " + "; ".join(str(r) for r in recommendations[:SUMMARY_MAX_ITEMS]))

    if not snippets:
        text = str(analysis.get("analysis", ""))
        snippets.append("Summary: " + text[:SUMMARY_MAX_CHARS])

    return " | ".join(snippets)


@dataclass
class ResponsesAPIExpert:
    """Expert agent wrapper for the Responses API debate."""

    expert_name: str
    role_description: str
    client: object
    model: str

    def analyze_problem(
        self,
        problem_statement: str,
        round_number: int,
        history: Dict[str, List[Dict[str, object]]],
    ) -> Dict[str, object]:
        """Run analysis for the given round and history."""
        prompt_parts: List[str] = [
            f"You are {self.role_description}.",
            f"This is round {round_number} of a multi-expert debate.",
            "Problem statement:",
            problem_statement.strip(),
        ]

        if round_number == 1:
            prompt_parts.append(
                "Initial task: provide a rigorous, implementable analysis covering the requested JSON fields."
            )
        else:
            prompt_parts.append("Context from previous rounds (summaries):")
            for name, records in history.items():
                if not records:
                    continue
                recent_records = records[-2:]
                start_round = len(records) - len(recent_records) + 1
                summaries: List[str] = []
                for idx, record in enumerate(recent_records, start=start_round):
                    summaries.append(f"Round {idx}: {summarise_analysis(record)}")
                if summaries:
                    prompt_parts.append(f"- {name}: \n  " + "\n  ".join(summaries))

            prompt_parts.append(
                "In this round you must critique gaps, resolve conflicts, and evolve your position based on the context above. Reference other experts explicitly when agreeing or disagreeing. Suggest improvements for other personas and express requirements as SysML requirement blocks so the Project Manager and Architect can act on them."
            )

            prompt_parts.append(
                "Respond strictly in JSON with the schema described. Do not include markdown code fences or commentary."
            )

        expert_input = "\n\n".join(prompt_parts)

        try:
            response = self.client.responses.create(model=self.model, input=expert_input)
            response_text = getattr(response, "output_text", "") or ""
            if not response_text:
                raise RuntimeError("Empty response from Responses API")
        except Exception as exc:  # pragma: no cover
            return {
                "expert": self.expert_name,
                "status": "error",
                "error": str(exc),
                "analysis": f"Expert {self.expert_name} encountered an error during analysis.",
            }

        return parse_response(self.expert_name, response_text)


def run_responses_api_debate(max_rounds: int = MAX_ROUNDS) -> bool:
    """Execute a multi-round expert debate using the Responses API."""
    print("=== Expert Debate: Responses API Pattern ===")

    api_key = get_openai_key()
    if not api_key:
        print("[ERROR] Cannot proceed without OpenAI API key")
        return False

    client = setup_openai_client(api_key)
    if not client:
        return False

    print(f"[INFO] OpenAI client ready (Responses API, model={DEFAULT_MODEL})")

    problem_statement = """
    Design an automated SysML-based system to manage the Software Development Life Cycle (SDLC)
    from planning through requirements to design that is WITHOUT HUMAN INTERVENTION:

    1. SELF-DOCUMENTING: The system automatically generates and maintains documentation
    2. FULLY TRACEABLE: Complete bidirectional traceability from requirements to implementation
    3. AUTOMATED: Minimal manual intervention in SDLC process management
    4. SYSML-BASED: Uses SysML v2 as the foundational modeling language
    5. CONSTRAINT: The system should enforce constraints and validate models against requirements

    The system should integrate:
    - Project planning and milestone tracking
    - Requirements capture and management
    - System architecture and design
    - Verification and validation
    - Change management and impact analysis

    Consider: SysML v2 constructs, tool integration, automation workflows, traceability mechanisms,
    and how to maintain consistency across all SDLC phases.
    """

    experts: List[ResponsesAPIExpert] = [
        ResponsesAPIExpert(
            "SysML Systems Architect",
            "a senior systems architect specialising in SysML v2 modeling and systems engineering automation",
            client,
            DEFAULT_MODEL,
        ),
        ResponsesAPIExpert(
            "Requirements Engineering Lead",
            "a requirements engineering expert focused on traceability, automation, and requirements management systems",
            client,
            DEFAULT_MODEL,
        ),
        ResponsesAPIExpert(
            "SDLC Process Engineer",
            "a software process engineering expert specialising in SDLC automation, DevOps integration, and self-documenting systems",
            client,
            DEFAULT_MODEL,
        ),
         ResponsesAPIExpert(
            "Project Manager",
            "a expert in best practices of creating work breakdown structures and milestone,and maintaining a project plan and establishing a mechanism for participants to report percentage complerte.the  PM utilizes dashboardds and reports to convy project health using standard metrics. The PM does not need to understand the domain, but understand project planning and delivery until progrect completion.",
            client,
            DEFAULT_MODEL,
        ),
    ]

    print("[INFO] Expert panel:")
    for expert in experts:
        print(f"  - {expert.expert_name}")

    analysis_history: Dict[str, List[Dict[str, object]]] = {expert.expert_name: [] for expert in experts}
    rounds: List[Dict[str, object]] = []

    for round_number in range(1, max_rounds + 1):
        print(f"\n--- Round {round_number} ---")
        round_payload: Dict[str, Dict[str, object]] = {}

        for expert in experts:
            analysis = expert.analyze_problem(problem_statement, round_number, analysis_history)
            round_payload[expert.expert_name] = analysis

            if analysis.get("status") == "error":
                print(f"[WARN] {expert.expert_name} error: {analysis.get('error', 'Unknown error')}")
            else:
                print(f"[INFO] {expert.expert_name} analysis complete (status={analysis.get('parse_status')})")

            analysis_history[expert.expert_name].append(analysis)

        rounds.append({"round": round_number, "analyses": round_payload})

    final_round_analyses = rounds[-1]["analyses"] if rounds else {}

    results = {
        "problem_statement": problem_statement,
        "rounds": rounds,
        "final_analyses": final_round_analyses,
        "debate_timestamp": time.time(),
        "api_type": "responses_api",
        "model_used": DEFAULT_MODEL,
        "max_rounds": max_rounds,
    }

    results_file = Path("docs/Responses_API_Expert_Debate_Results.json")
    results_file.parent.mkdir(parents=True, exist_ok=True)
    results_file.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")

    print("\n=== Debate Summary ===")
    print(f"Rounds: {len(rounds)}")
    print(f"Experts: {len(experts)}")
    print(f"Results file: {results_file}")

    return True


if __name__ == "__main__":  # pragma: no cover
    success = run_responses_api_debate()
    if success:
        print("\n[INFO] Responses API expert debate completed!")
        print("       Check the generated documents for detailed analysis.")
    else:
        print("\n[ERROR] Responses API expert debate failed - check setup and try again.")



