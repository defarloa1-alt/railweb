import json
from pathlib import Path
import shutil
import time
import os

import pytest


REPO = Path(__file__).resolve().parents[1]
RUNS = REPO / 'runs'


def test_create_run_api_happy_path(tmp_path, monkeypatch):
    from tools.orchestrate import create_run_api

    tmp_runs = tmp_path / 'runs'
    tmp_runs.mkdir()
    monkeypatch.setattr(create_run_api, 'RUNS', tmp_runs)

    # set auth token
    monkeypatch.setenv('RAILWEB_API_TOKEN', 'test-token')

    client = create_run_api.app.test_client()

    # call endpoint without meta -> should copy example or write minimal meta
    resp = client.post('/internal/create_run', json={}, headers={'Authorization': 'Bearer test-token'})
    assert resp.status_code == 202
    data = resp.get_json()
    assert data['ok'] is True
    run_id = data['run_id']

    run_dir = tmp_runs / run_id
    assert (run_dir / 'meta.yaml').exists()

    # poll status until results.txt exists (background thread)
    status_url = data['status_url']
    for _ in range(20):
        sresp = client.get(status_url)
        assert sresp.status_code == 200
        sdata = sresp.get_json()
        if sdata.get('status') and 'completed' in sdata.get('status'):
            break
        time.sleep(0.1)

    assert (run_dir / 'results.txt').exists()


def test_create_run_api_validation_and_auth_errors(tmp_path, monkeypatch):
    from tools.orchestrate import create_run_api

    tmp_runs = tmp_path / 'runs'
    tmp_runs.mkdir()
    monkeypatch.setattr(create_run_api, 'RUNS', tmp_runs)

    client = create_run_api.app.test_client()

    # no token configured on server: ensure env var not present
    monkeypatch.delenv('RAILWEB_API_TOKEN', raising=False)

    # should receive 401 because server token not set/configured
    resp = client.post('/internal/create_run', json={})
    assert resp.status_code == 401

    # now set token and test validation error
    monkeypatch.setenv('RAILWEB_API_TOKEN', 'test-token')
    bad_meta = {'run_id': 'x'}
    resp = client.post('/internal/create_run', json={'meta': bad_meta}, headers={'Authorization': 'Bearer test-token'})
    # server uses jsonschema; if missing, returns 500; otherwise 400 for validation
    assert resp.status_code in (400, 500)
