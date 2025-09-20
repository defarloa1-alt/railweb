"""Minimal runner used by tests and orchestrator.

This file provides run_real_debate() which the tests import. It uses the
existing DebateManager and LLMAgent that posts to the mock adapter.
"""
from pathlib import Path
import time
from .manager import DebateManager
from .llm_agent import LLMAgent


def run_real_debate():
    # configure an LLMAgent to point at the local mock adapter (port 3001)
    adapter_url = 'http://127.0.0.1:3001'
    agent = LLMAgent(name='mock-agent', adapter_url=adapter_url)

    manager = DebateManager()
    manager.register(agent)

    # simple context used by tests/demo
    context = {'topic': 'Example debate run'}

    history = manager.run_rounds(context, rounds=1)
    # Print a short human-friendly summary for tests to assert
    for i, round_out in enumerate(history, start=1):
        print(f"Round {i}")
        for entry in round_out:
            if isinstance(entry, dict):
                print(entry.get('text', str(entry)))
            else:
                print(entry)


if __name__ == '__main__':
    run_real_debate()
