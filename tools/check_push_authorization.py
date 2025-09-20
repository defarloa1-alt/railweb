#!/usr/bin/env python3
"""
Check push authorization presence for changed intake/run files.

This script looks for any changed files under intake/ or runs/ and enforces
that the repository contains a YAML metadata file (runs/*/meta.yaml or
intake/*/meta.yaml) that includes the authorization field named in the
agent operational contract (default: push_authorized_by).

Usage: python tools/check_push_authorization.py <file1> [file2 ...]
Exits with 0 when checks pass, non-zero when missing authorization.
"""
import sys
import yaml
from pathlib import Path

CONTRACT_PATH = Path('intake/agent_operational_contract.yaml')


def load_contract():
    if not CONTRACT_PATH.exists():
        print(f"Contract not found at {CONTRACT_PATH}")
        sys.exit(1)
    return yaml.safe_load(CONTRACT_PATH.read_text())


def find_meta_files():
    # look for runs/*/meta.yaml and intake/*/meta.yaml
    metas = []
    for p in Path('runs').glob('*'):
        m = p / 'meta.yaml'
        if m.exists():
            metas.append(m)
    for p in Path('intake').glob('*'):
        m = Path('intake') / p.name / 'meta.yaml'
        # also check intake/meta.yaml directly
        alt = Path('intake') / 'meta.yaml'
        if m.exists():
            metas.append(m)
    if alt.exists():
        metas.append(alt)
    return list(set(metas))


def check_meta_for_authorization(meta_path: Path, field_name: str):
    try:
        data = yaml.safe_load(meta_path.read_text())
        if not isinstance(data, dict):
            return False
        return field_name in data and data[field_name]
    except Exception:
        return False


def main():
    if len(sys.argv) <= 1:
        print('No files provided; nothing to check')
        return 0
    contract = load_contract()
    push_field = contract.get('push_gates', {}).get('authorization_field', 'push_authorized_by')
    # if push gates not required, pass
    if not contract.get('push_gates', {}).get('require_push_authorization', False):
        print('Push authorization not required by contract; skipping')
        return 0

    changed = [Path(f) for f in sys.argv[1:]]
    # If no changed files in intake/runs, skip
    relevant = [p for p in changed if any(str(p).startswith(prefix) for prefix in ('intake/', 'runs/'))]
    if not relevant:
        print('No intake/runs files changed; skipping push authorization check')
        return 0

    metas = find_meta_files()
    if not metas:
        print('ERROR: No meta.yaml files found under runs/ or intake/; require push authorization')
        sys.exit(1)

    for m in metas:
        ok = check_meta_for_authorization(m, push_field)
        if ok:
            print(f'Authorization found in {m}')
            return 0

    print(f'ERROR: No meta.yaml contains the required authorization field "{push_field}"')
    print('Add the field to a run meta (runs/<id>/meta.yaml) or intake/*/meta.yaml to authorize this push')
    sys.exit(1)


if __name__ == '__main__':
    main()
