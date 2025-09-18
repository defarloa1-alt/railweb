"""Builds a concise prompt for the LLM and calls OpenAI (supports DRY_RUN).

This module evaluates DRY_RUN at call time and allows configuring the
OpenAI model via `OPENAI_MODEL` env var.
"""
import os
import time
from typing import List, Dict


def _is_dry_run() -> bool:
    v = os.getenv("DRY_RUN", "0")
    return v.lower() in ("1", "true", "yes", "on")


def _retry_call(func, retries=3, backoff=0.5, *args, **kwargs):
    last_exc = None
    for i in range(retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            last_exc = e
            time.sleep(backoff * (2 ** i))
    raise last_exc


def build_prompt(highlights: List[Dict]) -> str:
    lead = "You are producing a short host script for an audio summary of recent highlights. Keep it under 120 words and conversational."
    bullets = "\n".join([f"- {h['title']}: {h['excerpt']}" for h in highlights])
    prompt = f"{lead}\n\nHighlights:\n{bullets}\n\nReturn a JSON object with keys: script, show_notes."
    return prompt


def call_llm(prompt: str) -> Dict:
    if _is_dry_run():
        return {
            "script": "Here are the top highlights from this run: Converter outputs match hand-checked results. Hardware changes require opt-in.",
            "show_notes": "2 highlights: scale conversion validated; DCC safety reminder.",
        }

    import openai
    import json

    openai.api_key = os.environ.get("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL") or "gpt-4o"

    def _call():
        return openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "system", "content": "You are a concise assistant that returns JSON."}, {"role": "user", "content": prompt}],
            max_tokens=400,
            temperature=0.2,
        )

    resp = _retry_call(_call, retries=3, backoff=0.5)
    text = resp.choices[0].message.content
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
