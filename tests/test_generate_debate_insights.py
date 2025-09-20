import json
import os
from pathlib import Path
from types import SimpleNamespace


REPO_ROOT = Path(__file__).resolve().parents[1]


def make_local_tmp(test_name: str) -> Path:
    tmp = REPO_ROOT / '.pytest_local_tmp' / test_name
    if tmp.exists():
        # clear previous runs
        for p in tmp.iterdir():
            if p.is_file():
                p.unlink()
            else:
                # rmtree for dirs
                import shutil

                shutil.rmtree(p)
    else:
        tmp.mkdir(parents=True, exist_ok=True)
    return tmp


def make_resp(text: str):
    class R:
        def __init__(self, text):
            self._text = text

        def raise_for_status(self):
            return None

        def json(self):
            return {'text': self._text}

    return R(text)


def test_extracts_json_from_noisy_response(tmp_path, monkeypatch):
    # create a fake debate_summary.md in a repo-local tmp dir
    ds_dir = make_local_tmp('test_extracts_json_from_noisy_response')
    ds = ds_dir / 'debate_summary.md'
    ds.write_text('mock debate summary')

    # messy response with surrounding text
    messy = 'Here is my analysis:\n```\nSome intro\n```\n{"summary": "Consensus.", "score": 0.9, "actions": ["Action A"]}\nThanks.'

    def fake_post(url, json, timeout):
        return make_resp(messy)

    monkeypatch.setattr('requests.post', fake_post)

    # run the script from tools/debate
    cwd = os.getcwd()
    try:
        os.chdir(ds_dir)
        import importlib
        spec = importlib.util.spec_from_file_location('generate', str(REPO_ROOT / 'tools' / 'debate' / 'generate_debate_insights.py'))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        res = mod.main()
        assert res == 0
        # outputs created
        assert (ds_dir / 'debate_insights.json').exists()
        j = json.loads((ds_dir / 'debate_insights.json').read_text())
        assert j['score'] == 0.9
    finally:
        os.chdir(cwd)


def test_retry_on_bad_response_then_success(tmp_path, monkeypatch):
    ds_dir = make_local_tmp('test_retry_on_bad_response_then_success')
    ds = ds_dir / 'debate_summary.md'
    ds.write_text('mock debate summary')

    # first response has no JSON, second is valid
    first = 'Sorry I cannot produce that.'
    second = '{"summary": "OK", "score": 0.5, "actions": ["Do B"]}'

    calls = {'n': 0}

    def fake_post(url, json, timeout):
        calls['n'] += 1
        if calls['n'] == 1:
            return make_resp(first)
        return make_resp(second)

    monkeypatch.setattr('requests.post', fake_post)

    cwd = os.getcwd()
    try:
        os.chdir(ds_dir)
        import importlib
        spec = importlib.util.spec_from_file_location('generate', str(REPO_ROOT / 'tools' / 'debate' / 'generate_debate_insights.py'))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        res = mod.main()
        assert res == 0
        j = json.loads((ds_dir / 'debate_insights.json').read_text())
        assert j['score'] == 0.5
        assert calls['n'] == 2
    finally:
        os.chdir(cwd)


def test_validation_fails_on_bad_score(tmp_path, monkeypatch):
    ds_dir = make_local_tmp('test_validation_fails_on_bad_score')
    ds = ds_dir / 'debate_summary.md'
    ds.write_text('mock debate summary')

    # adapter returns JSON but with invalid score
    bad = '{"summary": "Bad", "score": 1.5, "actions": ["Do B"]}'

    def fake_post(url, json, timeout):
        return make_resp(bad)

    monkeypatch.setattr('requests.post', fake_post)

    cwd = os.getcwd()
    try:
        os.chdir(ds_dir)
        import importlib
        spec = importlib.util.spec_from_file_location('generate', str(REPO_ROOT / 'tools' / 'debate' / 'generate_debate_insights.py'))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        res = mod.main()
        # our script returns 4 on validation failure
        assert res == 4
        # ensure file either doesn't exist or contains the same invalid object (we chose to not write on validation fail)
        assert not (ds_dir / 'debate_insights.json').exists()
    finally:
        os.chdir(cwd)
