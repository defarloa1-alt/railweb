from __future__ import annotations
from typing import Any, Dict, Optional
import requests


class LLMAgent:
    def __init__(self, name: str, adapter_url: str = "http://localhost:3001", mode: str = "summarize") -> None:
        self.name = name
        self.adapter_url = adapter_url.rstrip('/')
        if mode not in ("summarize", "explain"):
            raise ValueError("mode must be 'summarize' or 'explain'")
        self.mode = mode

    def propose(self, context: Any) -> dict | str:
        payload: Dict[str, Any]
        if self.mode == "summarize":
            payload = {"run_id": context.get("run_id") if isinstance(context, dict) else "run-x", "artifacts": context.get("artifacts") if isinstance(context, dict) else None, "intent": context.get("intent") if isinstance(context, dict) else None}
            url = f"{self.adapter_url}/api/llm/summarizeRun"
        else:
            payload = {"run_id": context.get("run_id") if isinstance(context, dict) else "run-x", "diff_text": context.get("diff_text") if isinstance(context, dict) else str(context), "goal": context.get("goal") if isinstance(context, dict) else None}
            url = f"{self.adapter_url}/api/llm/explainChange"

        try:
            resp = requests.post(url, json=payload, timeout=10)
        except Exception as e:
            return {"text": f"(LLM error: {e})", "meta": None}

        if resp.status_code != 200:
            return {"text": f"(LLM bad status: {resp.status_code} {resp.text})", "meta": None}

        data = resp.json()
        text = data.get("text") if isinstance(data, dict) else str(data)
        meta: Optional[Dict[str, Any]] = None
        if isinstance(data, dict):
            prov = data.get("provenance_suggestions") or data.get("provenance") or None
            citations = data.get("citations")
            if prov or citations:
                meta = {"provenance_suggestions": prov, "citations": citations}

        return {"text": text or "(LLM returned no text)", "meta": meta}
