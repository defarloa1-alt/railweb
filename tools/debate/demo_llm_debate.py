"""Lightweight demo to exercise LLMAgent and debate manager (placeholder)."""
from tools.debate.llm_agent import LLMAgent

def run_demo():
    agent = LLMAgent('Demo', adapter_url='http://127.0.0.1:3001', mode='summarize')
    print(agent.propose({'run_id': 'demo', 'artifacts': [], 'intent': 'demo'}))

if __name__ == '__main__':
    run_demo()
