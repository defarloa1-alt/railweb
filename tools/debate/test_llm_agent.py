import json

from tools.debate.llm_agent import LLMAgent


class DummyResp:
    def __init__(self, status_code=200, body=None):
        self.status_code = status_code
        self._body = body or {"ok": True, "text": "DUMMY RESPONSE"}

    def json(self):
        return self._body

    @property
    def text(self):
        return json.dumps(self._body)


def test_llm_agent_propose_monkeypatch(monkeypatch):
    # Simulate requests.post returning a successful JSON payload
    def fake_post(url, json=None, timeout=None):
        assert "/api/llm/summarizeRun" in url
        return DummyResp(200, {"ok": True, "text": "SIMULATED SUMMARY"})

    monkeypatch.setattr("requests.post", fake_post)

    agent = LLMAgent("LLMTest", adapter_url="http://localhost:3001", mode="summarize")
    ctx = {"run_id": "r1", "artifacts": [], "intent": "test"}
    out = agent.propose(ctx)
    # LLMAgent.propose returns a dict with 'text' and optional 'meta'
    assert isinstance(out, dict)
    assert "SIMULATED SUMMARY" in out.get("text", "")
