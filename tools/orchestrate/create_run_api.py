from pathlib import Path
import uuid
import shutil
import subprocess
import sys
import os
import yaml
import threading
from flask import Flask, request, jsonify
from . import status_db

try:
    import jsonschema
    HAS_JSONSCHEMA = True
except Exception:
    HAS_JSONSCHEMA = False


REPO = Path(__file__).resolve().parents[2]
RUNS = REPO / 'runs'
EXAMPLE = REPO / 'runs' / 'example_run' / 'meta.example.yaml'

app = Flask(__name__)

# Simple JSON Schema for metadata validation (can be extended)
# Try to load an external schema file (more descriptive), otherwise fallback
SCHEMA_PATH = REPO / 'tools' / 'orchestrate' / 'meta_schema.json'
if SCHEMA_PATH.exists():
    try:
        with SCHEMA_PATH.open('r', encoding='utf8') as f:
            import json

            META_SCHEMA = json.load(f)
    except Exception:
        META_SCHEMA = {
            'type': 'object',
            'required': ['provenance', 'approvals', 'push_authorized_by'],
            'properties': {
                'provenance': {'type': 'object'},
                'approvals': {'type': 'object'},
                'push_authorized_by': {},
            },
        }
else:
    META_SCHEMA = {
        'type': 'object',
        'required': ['provenance', 'approvals', 'push_authorized_by'],
        'properties': {
            'provenance': {'type': 'object'},
            'approvals': {'type': 'object'},
            'push_authorized_by': {},
        },
    }


def validate_meta_schema(meta: dict) -> tuple[bool, str | None]:
    if not HAS_JSONSCHEMA:
        return False, 'jsonschema package is not installed'
    try:
        jsonschema.validate(instance=meta, schema=META_SCHEMA)
        return True, None
    except jsonschema.ValidationError as e:
        return False, str(e.message)


def _run_runner_and_write(dest: Path):
    runner = REPO / 'tools' / 'debate' / 'run_real_debate_inproc.py'
    try:
        proc = subprocess.run([sys.executable, str(runner)], capture_output=True, text=True, timeout=20)
        out = proc.stdout + proc.stderr
        (dest / 'results.txt').write_text(out)
        # persist status in DB
        status_db.set_status(dest.name, 'completed', str(dest / 'results.txt'))
        # attempt to create a Linear issue if configured
        try:
            from . import linear_integration

            # load meta.yaml if present to include provenance
            import yaml

            meta = None
            meta_path = dest / 'meta.yaml'
            if meta_path.exists():
                meta = yaml.safe_load(meta_path.read_text())
            issue_id = linear_integration.create_issue_for_run(dest.name, meta or {})
            if issue_id:
                # store external id in DB as part of results_path field (quick hack)
                status_db.set_status(dest.name, 'completed', str(dest / 'results.txt'))
                # attach an auxiliary file with mapping
                (dest / 'external_issue_id.txt').write_text(issue_id)
        except Exception:
            pass
    except Exception as e:
        (dest / 'results.txt').write_text(str(e))
        status_db.set_status(dest.name, 'error', None)


def require_token(req) -> tuple[bool, str | None]:
    token = os.environ.get('RAILWEB_API_TOKEN')
    if not token:
        return False, 'RAILWEB_API_TOKEN not configured on server'
    auth = req.headers.get('Authorization') or ''
    if auth.startswith('Bearer '):
        auth_token = auth.split(' ', 1)[1]
    else:
        auth_token = auth
    if auth_token != token:
        return False, 'invalid or missing Authorization token'
    return True, None


@app.route('/internal/create_run', methods=['POST'])
def create_run_api():
    # auth
    ok, err = require_token(request)
    if not ok:
        return jsonify({'ok': False, 'error': err}), 401

    payload = request.get_json(force=True) or {}
    run_id = payload.get('run_id') or f"run-{uuid.uuid4().hex[:8]}"
    meta = payload.get('meta')

    # validate meta if provided
    if meta is not None:
        valid, msg = validate_meta_schema(meta)
        if not valid:
            return jsonify({'ok': False, 'error': msg}), 400

    dest = RUNS / run_id
    try:
        dest.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        return jsonify({'ok': False, 'error': 'run_id already exists'}), 400

    # write meta.yaml
    if meta is not None:
        (dest / 'meta.yaml').write_text(yaml.safe_dump(meta, sort_keys=False))
    else:
        if EXAMPLE.exists():
            shutil.copy(EXAMPLE, dest / 'meta.yaml')
        else:
            (dest / 'meta.yaml').write_text('run_id: ' + run_id)

    # start runner in background thread and return 202
    # mark running
    status_db.set_status(run_id, 'running', None)
    thread = threading.Thread(target=_run_runner_and_write, args=(dest,), daemon=True)
    thread.start()
    return jsonify({'ok': True, 'run_id': run_id, 'status_url': f"/internal/create_run/{run_id}"}), 202


@app.route('/internal/create_run/<run_id>', methods=['GET'])
def create_run_status(run_id: str):
    dest = RUNS / run_id
    if not dest.exists():
        return jsonify({'ok': False, 'error': 'run not found'}), 404
    # read from DB
    status = status_db.get_status(run_id)
    results = dest / 'results.txt'
    return jsonify({'ok': True, 'run_id': run_id, 'status': status or {'status': 'running'}, 'results': str(results) if results.exists() else None}), 200


if __name__ == '__main__':
    # default port chosen to avoid colliding with other dev services
    app.run(host='127.0.0.1', port=5001)
