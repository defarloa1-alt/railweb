Debate framework
================

Small, testable debate manager used to run short debates between agents. This is a lightweight scaffold intended for the Multi-Agent Debate Framework POC.

Usage
-----

1. Implement an Agent with a `name` and `propose()` method.
2. Register agents with `DebateManager` and call `run_rounds()`.

LLM-backed agent and demo
-------------------------

The repository includes an `LLMAgent` that calls the local LLM adapter HTTP API and a small demo script:

- `tools/debate/llm_agent.py` -- an agent that POSTs to the adapter endpoints `/api/llm/summarizeRun` or `/api/llm/explainChange`.
- `tools/debate/demo_llm_debate.py` -- runs a short debate between an `EchoAgent` and the `LLMAgent`. Start the LLM adapter (`tools/llm_adapter/src/index.js`) locally (defaults to port 3001) before running the demo.

Run the demo:

```bash
python tools/debate/demo_llm_debate.py
```

Run tests:

```bash
pytest tools/debate -q
```

Provenance / meta capture
-------------------------


The `DebateManager.run_rounds` now supports an optional `include_meta` boolean. When `include_meta=True`, the per-agent responses will be returned as structured dicts:

```json
{"agent": "<agent name>", "text": "<text>", "meta": <optional meta/provenance>}
```

If an agent returns a plain string (the earlier behavior), `meta` will be `None`.

The provided `LLMAgent` returns a dict of the form `{"text":..., "meta": {...}}` when the adapter includes `provenance_suggestions` or `citations`. Use `include_meta=True` when you need to collect that information for PR comments or provenance tracking.

Formatter usage
---------------

The repository includes a small formatter that converts an `include_meta=True` debate history into a markdown summary suitable for a PR comment:

```python
from tools.debate.manager import DebateManager
from tools.debate.llm_agent import LLMAgent
from tools.debate.provenance import format_debate_summary

dm = DebateManager()
dm.register(LLMAgent("LLM"))
history = dm.run_rounds({"run_id": "demo"}, rounds=1, include_meta=True)
md = format_debate_summary(history, title="Debate summary")
print(md)
```



