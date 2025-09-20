from __future__ import annotations
from typing import List, Protocol, Any, Dict, Union


class Agent(Protocol):
    name: str

    def propose(self, context: Any) -> str:
        ...


class DebateManager:
    def __init__(self) -> None:
        self.agents: List[Agent] = []

    def register(self, agent: Agent) -> None:
        if any(a.name == agent.name for a in self.agents):
            raise ValueError(f"Agent with name {agent.name} already registered")
        self.agents.append(agent)

    def run_rounds(self, context: Any, rounds: int = 1, include_meta: bool = False) -> List[List[Union[str, Dict[str, Any]]]]:
        if rounds < 1:
            raise ValueError("rounds must be >= 1")
        history: List[List[str]] = []
        for r in range(rounds):
            round_responses: List[Union[str, Dict[str, Any]]] = []
            for agent in self.agents:
                resp = agent.propose(context)
                # Agent can return either a plain string or a structured dict {"text":..., "meta": {...}}
                if isinstance(resp, str):
                    if include_meta:
                        round_responses.append({"agent": agent.name, "text": resp, "meta": None})
                    else:
                        round_responses.append(f"{agent.name}: {resp}")
                elif isinstance(resp, dict):
                    text = resp.get("text")
                    meta = resp.get("meta") or resp.get("provenance") or None
                    if include_meta:
                        round_responses.append({"agent": agent.name, "text": text, "meta": meta})
                    else:
                        round_responses.append(f"{agent.name}: {text}")
                else:
                    # Fallback to stringification
                    s = str(resp)
                    if include_meta:
                        round_responses.append({"agent": agent.name, "text": s, "meta": None})
                    else:
                        round_responses.append(f"{agent.name}: {s}")
            history.append(round_responses)
        return history
