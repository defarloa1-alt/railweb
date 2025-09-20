"""Generate consensus score and action items using the local LLM adapter.

This script reads `debate_summary.md`, sends it to `/api/llm/explainChange` with a goal to produce
structured JSON like: {"summary": "..", "score": 0.0-1.0, "actions": ["Action 1", ...]}.
It writes `debate_insights.json` and also writes a short `debate_digest.txt` with the summary text.

Added robustness:
- Loads the prompt template from `tools/debate/debate_insights.prompt` if present.
- Attempts to extract the first balanced JSON object from the LLM response if there is surrounding text.
- Retries the adapter call once with a stricter prompt if parsing fails.
"""
from __future__ import annotations
import json
import re
import sys
from typing import Any, Dict, Optional

import requests


DEFAULT_PROMPT = (
    'Return a JSON object with keys: summary (2-3 sentence consensus), '
    'score (a number 0.0-1.0 indicating consensus/confidence), and actions (an array of concise action items). '
    'Do not include any other text. The JSON must be the only JSON object in the response and must be parseable.'
)


def load_prompt(path: str = 'tools/debate/debate_insights.prompt') -> str:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except Exception:
        return DEFAULT_PROMPT


_JSON_OBJ_RE = re.compile(r"\{.*?\}", re.DOTALL)


def extract_first_json(s: str) -> Optional[str]:
    """Try to extract the first balanced JSON object from a string.

    This uses a conservative regex that may fail on deeply nested braces but covers common LLM artifacts
    like surrounding prose or code fences. If no object is found, return None.
    """
    if not s:
        return None
    # First, try a simple approach: find first occurrence of '{' and attempt incremental parse.
    start = s.find('{')
    if start == -1:
        return None
    for end in range(start + 1, len(s) + 1):
        try:
            candidate = s[start:end]
            obj = json.loads(candidate)
            # success
            return candidate
        except Exception:
            continue
    # fallback: regex that attempts to grab a braced block (may be imperfect)
    m = _JSON_OBJ_RE.search(s)
    if m:
        try:
            json.loads(m.group(0))
            return m.group(0)
        except Exception:
            return None
    return None


def call_adapter(summary: str, prompt: str, timeout: int = 20) -> Dict[str, Any]:
    payload = {
        'run_id': 'ci-insights',
        'diff_text': summary,
        'goal': prompt,
    }
    resp = requests.post('http://127.0.0.1:3001/api/llm/explainChange', json=payload, timeout=timeout)
    resp.raise_for_status()
    return resp.json()


def parse_insights_from_adapter_response(data: Dict[str, Any]) -> Dict[str, Any]:
    raw = data.get('text') or ''
    # Try direct parse first
    try:
        return json.loads(raw)
    except Exception:
        pass

    # Try to extract a JSON object from surrounding text
    extracted = extract_first_json(raw)
    if extracted:
        return json.loads(extracted)

    raise ValueError('No parseable JSON found in adapter response')


def _parse_score_value(raw: Any) -> float:
    """Normalize a score value into a float in the range [0.0, 1.0].

    Accepts:
    - floats/ints in [0.0, 1.0]
    - ints/floats in [0, 100] interpreted as percentages
    - strings like "0.8", "80", or "80%"

    Raises ValueError if the value cannot be interpreted.
    """
    if raw is None:
        raise ValueError('score must be a number between 0.0 and 1.0')

    # numeric types: treat ints as possible percentage (0-100), but floats must be in 0.0-1.0
    if isinstance(raw, int):
        val = float(raw)
        if 0.0 <= val <= 1.0:
            return val
        if 0.0 <= val <= 100.0:
            return val / 100.0
        raise ValueError('score must be between 0.0 and 1.0')

    if isinstance(raw, float):
        val = float(raw)
        if 0.0 <= val <= 1.0:
            return val
        # do not interpret floats > 1.0 as percentages (1.5 is invalid)
        raise ValueError('score must be between 0.0 and 1.0')

    # strings
    if isinstance(raw, str):
        s = raw.strip()
        # percent string
        if s.endswith('%'):
            try:
                v = float(s[:-1].strip())
            except Exception:
                raise ValueError('score must be between 0.0 and 1.0')
            if 0.0 <= v <= 100.0:
                return v / 100.0
            raise ValueError('score must be between 0.0 and 1.0')

        # plain numeric string
        try:
            v = float(s)
        except Exception:
            raise ValueError('score must be between 0.0 and 1.0')
        if 0.0 <= v <= 1.0:
            return v
        if 0.0 <= v <= 100.0:
            return v / 100.0
        raise ValueError('score must be between 0.0 and 1.0')

    raise ValueError('score must be a number between 0.0 and 1.0')
def validate_insights(insights: Dict[str, Any]) -> None:
    """Validate the parsed insights shape and value ranges.

    Raises ValueError on invalid shape or values.
    """
    if not isinstance(insights, dict):
        raise ValueError('insights must be a JSON object')

    # summary
    summary = insights.get('summary')
    if summary is None or not isinstance(summary, str):
        raise ValueError('summary must be a non-empty string')

    # normalize and validate score (accept percentages and strings like '80%')
    raw_score = insights.get('score')
    try:
        norm = _parse_score_value(raw_score)
    except Exception:
        raise ValueError('score must be between 0.0 and 1.0')
    # put the normalized float back into the dict for downstream use
    insights['score'] = norm

    # actions
    actions = insights.get('actions')
    if actions is None or not isinstance(actions, list):
        raise ValueError('actions must be a list of strings')
    for a in actions:
        if not isinstance(a, str):
            raise ValueError('each action must be a string')


def main() -> int:
    try:
        with open('debate_summary.md', 'r', encoding='utf-8') as f:
            summary = f.read()
    except Exception as e:
        print('Could not read debate_summary.md:', e)
        return 2

    prompt = load_prompt()

    # First attempt
    try:
        data = call_adapter(summary, prompt)
        insights = parse_insights_from_adapter_response(data)
    except Exception as e1:
        print('First parse failed, attempting stricter retry:', e1)
        # Retry with a stricter prompt asking to return only JSON and nothing else.
        stricter = (
            'IMPORTANT: Return ONLY a single JSON object and nothing else. The JSON must have keys: '
            'summary, score, actions. Example: {"summary": "...", "score": 0.8, "actions": ["..."]}.'
        )
        try:
            data = call_adapter(summary, stricter, timeout=30)
            insights = parse_insights_from_adapter_response(data)
        except Exception as e2:
            print('Retry failed:', e2)
            return 3

    # Validate shape and contents before writing
    try:
        validate_insights(insights)
    except Exception as ve:
        print('Insights validation failed:', ve)
        return 4

    out_json = 'debate_insights.json'
    with open(out_json, 'w', encoding='utf-8') as f:
        json.dump(insights, f, indent=2)

    # also write digest text for backward compatibility
    digest = insights.get('summary', '') if isinstance(insights, dict) else ''
    with open('debate_digest.txt', 'w', encoding='utf-8') as f:
        f.write(digest)

    print('Wrote', out_json)
    return 0


if __name__ == '__main__':
    sys.exit(main())
