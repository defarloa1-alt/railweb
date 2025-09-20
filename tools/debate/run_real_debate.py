from tools.debate.manager import DebateManager
from tools.debate.llm_agent import LLMAgent


def run_real_debate():
    dm = DebateManager()
    # two agents pointing to the local mock adapter
    alice = LLMAgent('Alice', adapter_url='http://127.0.0.1:3001', mode='summarize')
    bob = LLMAgent('Bob', adapter_url='http://127.0.0.1:3001', mode='explain')
    dm.register(alice)
    dm.register(bob)

    context = {'run_id': 'real-debate-1', 'artifacts': ['file1', 'file2'], 'intent': 'decide on approach', 'diff_text': 'Change X -> Y', 'goal': 'choose best approach'}

    history = dm.run_rounds(context, rounds=3, include_meta=True)
    for i, round_res in enumerate(history, start=1):
        print(f"--- Round {i} ---")
        for r in round_res:
            print(r)


if __name__ == '__main__':
    run_real_debate()
