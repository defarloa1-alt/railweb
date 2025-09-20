"""Local runner for the insights unit checks.

This duplicates the intent of `tests/test_generate_debate_insights.py` but uses
absolute imports and temporary directories inside the repo so it can be run
directly when pytest's tmp_path layout makes relative imports difficult on
some Windows setups.

Run with the repo .venv: `.venv\Scripts\python.exe tools\debate\run_local_insights_checks.py`
"""
import importlib.util
import json
import os
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GEN_PATH = ROOT / 'tools' / 'debate' / 'generate_debate_insights.py'


def make_resp(text: str):
    class R:
        def __init__(self, text):
            self._text = text

        def raise_for_status(self):
            return None

        def json(self):
            return {'text': self._text}

    return R(text)


def load_module():
    spec = importlib.util.spec_from_file_location('generate', str(GEN_PATH))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run_case(name, response_text, expect_return, expect_score=None, expect_calls=None):
    print('===', name)
    tmp = ROOT / '.local_test_tmp' / name.replace(' ', '_')
    if tmp.exists():
        shutil.rmtree(tmp)
    tmp.mkdir(parents=True)
    # write debate_summary.md
    (tmp / 'debate_summary.md').write_text('mock debate summary')

    # monkeypatch requests.post by assigning into requests at runtime
    import requests

    def fake_post(url, json=None, timeout=None):
        fake_post.calls += 1
        return make_resp(response_text)

    fake_post.calls = 0
    requests_post_orig = requests.post
    requests.post = fake_post

    cwd = os.getcwd()
    try:
        os.chdir(tmp)
        mod = load_module()
        res = mod.main()
        print('return code:', res)
        ok = (res == expect_return)
        if expect_score is not None and res == 0:
            j = json.loads((tmp / 'debate_insights.json').read_text())
            ok = ok and abs(j.get('score', 0) - expect_score) < 1e-6
        if expect_calls is not None:
            ok = ok and (fake_post.calls == expect_calls)
        print('PASS' if ok else 'FAIL')
    finally:
        # restore
        requests.post = requests_post_orig
        os.chdir(cwd)


def main():
    # Case 1: noisy response with JSON embedded
    messy = 'Here is my analysis:\n```\nSome intro\n```\n{"summary": "Consensus.", "score": 0.9, "actions": ["Action A"]}\nThanks.'
    run_case('noisy_response', messy, expect_return=0, expect_score=0.9, expect_calls=1)

    # Case 2: first fails then second succeeds
    # We emulate by swapping requests.post inside run_case, so simulate by running
    # a small wrapper: first call returns non-json, second returns valid json.
    print('\n=== retry_case')
    tmp = ROOT / '.local_test_tmp' / 'retry_case'
    if tmp.exists():
        shutil.rmtree(tmp)
    tmp.mkdir(parents=True)
    (tmp / 'debate_summary.md').write_text('mock debate summary')

    import requests as _requests

    def fake_post_retry(url, json=None, timeout=None):
        fake_post_retry.calls += 1
        if fake_post_retry.calls == 1:
            return make_resp('Sorry I cannot produce that.')
        return make_resp('{"summary": "OK", "score": 0.5, "actions": ["Do B"]}')

    fake_post_retry.calls = 0
    orig = _requests.post
    _requests.post = fake_post_retry
    cwd = os.getcwd()
    try:
        os.chdir(tmp)
        mod = load_module()
        res = mod.main()
        print('return code:', res, 'calls:', fake_post_retry.calls)
        ok = (res == 0 and fake_post_retry.calls == 2)
        if ok:
            j = json.loads((tmp / 'debate_insights.json').read_text())
            ok = ok and abs(j.get('score', 0) - 0.5) < 1e-6
        print('PASS' if ok else 'FAIL')
    finally:
        _requests.post = orig
        os.chdir(cwd)

    # Case 3: invalid score -> returns 4 and no file
    bad = '{"summary": "Bad", "score": 1.5, "actions": ["Do B"]}'
    run_case('bad_score', bad, expect_return=4, expect_score=None, expect_calls=1)


if __name__ == '__main__':
    main()
