from __future__ import annotations
from typing import List, Protocol, Any


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

    def run_rounds(self, context: Any, rounds: int = 1) -> List[List[str]]:
        if rounds < 1:
            raise ValueError("rounds must be >= 1")
        history: List[List[str]] = []
        for r in range(rounds):
            round_responses: List[str] = []
            for agent in self.agents:
                resp = agent.propose(context)
                round_responses.append(f"{agent.name}: {resp}")
            history.append(round_responses)
        return history
