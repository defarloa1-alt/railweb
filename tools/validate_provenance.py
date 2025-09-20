#!/usr/bin/env python3
"""
Simple provenance validator.

Scans a list of files and checks for required provenance keys as defined in
`intake/agent_operational_contract.yaml`.

Usage: python tools/validate_provenance.py <file1> [file2 ...]
Exits with code 0 if all files pass, 1 if any file fails.
"""
import sys
import yaml
from pathlib import Path
import argparse

CONTRACT_PATH = Path('intake/agent_operational_contract.yaml')

def load_contract():
    if not CONTRACT_PATH.exists():
        print(f"Contract not found at {CONTRACT_PATH}")
        sys.exit(1)
    return yaml.safe_load(CONTRACT_PATH.read_text())

def check_provenance_in_mapping(mapping, required):
    # mapping is a dict; required are dotted keys
    missing = []
    for key in required:
        parts = key.split('.')
        node = mapping
        ok = True
        for p in parts:
            if isinstance(node, dict) and p in node:
                node = node[p]
            else:
                ok = False
                break
        if not ok:
            missing.append(key)
    return missing

def inspect_file(path: Path, required_fields):
    text = path.read_text(encoding='utf-8')
    # support YAML front matter in markdown
    candidates = []
    if path.suffix in ('.yml', '.yaml', '.json'):
        try:
            data = yaml.safe_load(text)
            if isinstance(data, dict):
                candidates.append(data)
        except Exception:
            pass
    if path.suffix in ('.md', '.markdown'):
        # extract YAML front matter
        if text.startswith('---'):
            parts = text.split('---', 2)
            if len(parts) >= 3:
                try:
                    data = yaml.safe_load(parts[1])
                    if isinstance(data, dict):
                        candidates.append(data)
                except Exception:
                    pass
    # check candidates
    for cand in candidates:
        missing = check_provenance_in_mapping(cand, required_fields)
        if not missing:
            return True, None
    return False, required_fields

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('files', nargs='*')
    parser.add_argument('--skip-patterns', nargs='*', default=[
        'intake/gpt_*_agent_policy.yaml',
        'intake/agent_operational_contract.yaml'
    ])
    args = parser.parse_args()

    contract = load_contract()
    required = contract.get('provenance_schema', {}).get('required_fields', [])
    if not args.files:
        print('No files provided; exiting OK')
        return 0
    exit_code = 0
    for f in args.files:
        p = Path(f)
        if not p.exists():
            print(f"Skipped missing file: {f}")
            continue
        # check skip patterns
        skip = False
        for pat in args.skip_patterns:
            if p.match(pat):
                print(f"SKIPPED (pattern): {f}")
                skip = True
                break
        if skip:
            continue
        ok, missing = inspect_file(p, required)
        if ok:
            print(f"OK: {f}")
        else:
            print(f"MISSING_PROVENANCE: {f} -> required keys: {missing}")
            exit_code = 1
    sys.exit(exit_code)

if __name__ == '__main__':
    main()
