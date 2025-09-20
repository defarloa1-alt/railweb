import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'prototype' / 'readwise_audio'))

from llm_prompt import build_prompt


def test_build_prompt_returns_string():
    sample = [{
        'id': 'h1',
        'title': 'Test',
        'excerpt': 'This is a sample highlight',
        'provenance': {'checksum': 'abc123'}
    }]
    p = build_prompt(sample)
    assert isinstance(p, str)
    assert 'This is a sample highlight' in p
