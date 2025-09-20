"""Validate out_audio.metadata.json files against the schema.

Usage:
  python scripts/validate_metadata.py path/to/out_audio.metadata.json
"""
import json
import sys
from jsonschema import validate, ValidationError
from pathlib import Path


def load_schema():
    p = Path(__file__).resolve().parents[1] / 'schema' / 'out_audio.metadata.schema.json'
    return json.loads(p.read_text(encoding='utf-8'))


def validate_file(path):
    schema = load_schema()
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    try:
        validate(instance=data, schema=schema)
        print(f'VALID: {path}')
        return 0
    except ValidationError as e:
        print(f'INVALID: {path}')
        print(e)
        return 2


def main():
    if len(sys.argv) < 2:
        print('Usage: python scripts/validate_metadata.py <file1.json> [file2.json ...]')
        return 1
    rc = 0
    for arg in sys.argv[1:]:
        if not Path(arg).exists():
            print(f'NOT FOUND: {arg}')
            rc = 3
            continue
        r = validate_file(arg)
        if r != 0:
            rc = r
    return rc


if __name__ == '__main__':
    raise SystemExit(main())
