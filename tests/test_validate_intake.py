from pathlib import Path
import subprocess


def test_validate_good(tmp_path):
    p = tmp_path / 'good.md'
    p.write_text('''---\ntitle: Example\ntype: requirement\nprovenance:\n  source: openai\n  model: gpt-4o-mini\n  model_version: 1\n  prompt_id: default_sysml_prompt_v1\n  run_id: run-123\n  timestamp: 2025-09-20T12:00:00Z\n---\n\nThis is a requirement.''')
    res = subprocess.run(['python', 'tools/validate_intake.py', str(p)], capture_output=True)
    assert res.returncode == 0, res.stderr.decode() + res.stdout.decode()


def test_validate_bad(tmp_path):
    p = tmp_path / 'bad.md'
    p.write_text('''---\ntitle: Example\n# missing type and provenance\n---\n\nBad.''')
    res = subprocess.run(['python', 'tools/validate_intake.py', str(p)], capture_output=True)
    assert res.returncode != 0
