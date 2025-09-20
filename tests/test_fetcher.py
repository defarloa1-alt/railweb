import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'prototype' / 'readwise_audio'))

from fetcher import fetch_sample_highlights, filter_highlights


def test_fetch_sample_highlights():
    s = fetch_sample_highlights()
    assert isinstance(s, list)
    assert len(s) >= 1
    for h in s:
        assert 'provenance' in h
        assert 'checksum' in h['provenance']


def test_filter_highlights():
    s = fetch_sample_highlights()
    # filter by a tag that doesn't exist should return empty
    out = filter_highlights(s, tags_whitelist=['no-such-tag'])
    assert out == []
