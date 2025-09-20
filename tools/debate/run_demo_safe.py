from tools.debate.llm_agent import LLMAgent
import traceback


def main():
    try:
        agent = LLMAgent('Demo', adapter_url='http://127.0.0.1:3001', mode='summarize')
        out = agent.propose({'run_id': 'demo', 'artifacts': [], 'intent': 'demo'})
        print('SUCCESS:', out)
    except Exception:
        print('EXCEPTION:')
        traceback.print_exc()


if __name__ == '__main__':
    main()
