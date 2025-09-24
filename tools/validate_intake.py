#!/usr/bin/env python3
"""Validate an intake artifact (YAML or JSON) against the intake JSON Schema.

Usage: tools/validate_intake.py path/to/artifact.yaml
"""
import sys
import json
from pathlib import Path

import yaml
from jsonschema import validate, Draft7Validator

SCHEMA_PATH = Path(__file__).resolve().parents[1] / 'schema' / 'intake_artifact.schema.json'


def load_schema(path=SCHEMA_PATH):
    with open(path, 'r', encoding='utf8') as f:
        return json.load(f)


def load_artifact(path: Path):
    with open(path, 'r', encoding='utf8') as f:
        text = f.read()
    # Try YAML first (front-matter + body or full YAML)
    try:
        doc = yaml.safe_load(text)
        if isinstance(doc, dict):
            return doc
    except Exception:
        pass
    # Fallback: try JSON
    try:
        return json.loads(text)
    except Exception as e:
        raise ValueError(f'Could not parse {path}: {e}')


def main():
    if len(sys.argv) < 2:
        print('Usage: validate_intake.py path/to/artifact.yaml')
        sys.exit(2)
    p = Path(sys.argv[1])
    artifact = load_artifact(p)
    schema = load_schema()
    validator = Draft7Validator(schema)
    errors = sorted(validator.iter_errors(artifact), key=lambda e: e.path)
    if errors:
        print('Validation failed:')
        for e in errors:
            print('-', '/'.join(map(str, e.path)) or '<root>', e.message)
        sys.exit(1)
    print('OK')


if __name__ == '__main__':
    main()
