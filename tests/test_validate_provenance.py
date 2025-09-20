import subprocess
import sys
from pathlib import Path


def run_validator(schema, file_path):
    py = sys.executable
    cmd = [py, "tools/validate_provenance.py", "--schema", schema, str(file_path)]
    res = subprocess.run(cmd, capture_output=True)
    return res


def test_validator_accepts_valid_intake(tmp_path):
    valid = tmp_path / "valid.yml"
    valid.write_text("""
id: sample
title: Sample
source:
  name: NEM
  url: https://example.org
  version: "2025"
items:
  - type: requirement
    value: something
""")
    res = run_validator("intake.schema.json", valid)
    assert res.returncode == 0, res.stderr.decode()


def test_validator_rejects_invalid_intake(tmp_path):
    bad = tmp_path / "bad.yml"
    bad.write_text("""
title: Missing id and source
""")
    res = run_validator("intake.schema.json", bad)
    assert res.returncode != 0
