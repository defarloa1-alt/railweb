"""Builds a concise prompt for the LLM and calls OpenAI (supports DRY_RUN)."""
import os
from typing import List, Dict

DRY_RUN = os.getenv("DRY_RUN")


def build_prompt(highlights: List[Dict]) -> str:
    lead = "You are producing a short host script for an audio summary of recent highlights. Keep it under 120 words and conversational."
    bullets = "\n".join([f"- {h['title']}: {h['excerpt']}" for h in highlights])
    prompt = f"{lead}\n\nHighlights:\n{bullets}\n\nReturn a JSON object with keys: script, show_notes."
    return prompt


def call_llm(prompt: str) -> Dict:
    if DRY_RUN:
        return {"script": "Here are the top highlights from this run: Converter outputs match hand-checked results. Hardware changes require opt-in.", "show_notes": "2 highlights: scale conversion validated; DCC safety reminder."}
    import openai
    openai.api_key = os.environ.get("OPENAI_API_KEY")
    resp = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": "You are a concise assistant that returns JSON."}, {"role": "user", "content": prompt}],
        max_tokens=400,
        temperature=0.2
    )
    # Expect the model to return a JSON string in resp.choices[0].message.content
    text = resp.choices[0].message.content
    import json
    try:
        return json.loads(text)
    except Exception:
        # best-effort extraction
        import re
        m = re.search(r"\{.*\}", text, re.S)
        if m:
            return json.loads(m.group(0))
        raise


if __name__ == "__main__":
    import json
    sample = [
        {"title": "Scale conversion validation", "excerpt": "Converter outputs match hand-checked results"},
        {"title": "DCC safety", "excerpt": "Hardware control requires explicit opt-in and safety gating."}
    ]
    p = build_prompt(sample)
    print(p)
    print(json.dumps(call_llm(p), indent=2))
