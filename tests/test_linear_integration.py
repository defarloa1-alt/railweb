import os
import json
from unittest.mock import patch

from tools.orchestrate.linear_integration import create_issue_for_run


def test_create_issue_no_key():
    # ensure function returns None when no API key configured
    if 'LINEAR_API_KEY' in os.environ:
        del os.environ['LINEAR_API_KEY']
    res = create_issue_for_run('run-x', {})
    assert res is None


def test_create_issue_success(monkeypatch):
    monkeypatch.setenv('LINEAR_API_KEY', 'sk_test')

    class DummyResp:
        def raise_for_status(self):
            return None

        def json(self):
            return {'data': {'issueCreate': {'issue': {'id': 'ISSUE-123'}}}}

    with patch('requests.post', return_value=DummyResp()):
        issue = create_issue_for_run('run-x', {'provenance': {'source': {'id': 's'}}})
        assert issue == 'ISSUE-123'


def test_create_issue_with_assignee_and_labels(monkeypatch):
    monkeypatch.setenv('LINEAR_API_KEY', 'sk_test')

    class DummyResp:
        def raise_for_status(self):
            return None

        def json(self):
            return {'data': {'issueCreate': {'issue': {'id': 'ISSUE-456'}}}}

    # capture the payload passed to requests.post to assert variables
    captured = {}

    def fake_post(url, headers=None, data=None, timeout=None):
        captured['url'] = url
        captured['headers'] = headers
        captured['data'] = data
        return DummyResp()

    with patch('requests.post', side_effect=fake_post):
        issue = create_issue_for_run('run-y', {'assignee': 'USER-1', 'labels': ['L1', 'L2']})
        assert issue == 'ISSUE-456'
        # ensure variables included assigneeId and labelIds
        assert 'assigneeId' in json.loads(captured['data'])['variables']['input']
        assert 'labelIds' in json.loads(captured['data'])['variables']['input']


def test_github_fallback(monkeypatch):
    # ensure Linear key missing
    if 'LINEAR_API_KEY' in os.environ:
        del os.environ['LINEAR_API_KEY']

    # patch github_integration.create_github_issue_for_run
    from unittest.mock import patch

    with patch('tools.orchestrate.github_integration.create_github_issue_for_run', return_value='GH#999'):
        res = create_issue_for_run('run-fallback', {})
        assert res == 'GH#999'
