#!/usr/bin/env python3
"""Schema-based provenance and intake validator.

Supports validating YAML/JSON/Markdown front-matter against JSON Schema
files stored in `schema/`.

Usage: python tools/validate_provenance.py --schema provenance.schema.json file1.md file2.yml
Exits 0 if all files validate, non-zero otherwise.
"""
import argparse
import json
import sys
from pathlib import Path

import yaml
from jsonschema import validate, ValidationError


def load_schema(schema_name: str) -> dict:
    base = Path(__file__).resolve().parents[1] / "schema"
    path = base / schema_name
    if not path.exists():
        raise SystemExit(f"Schema not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def extract_candidate_data(path: Path):
    text = path.read_text(encoding="utf-8")
    if path.suffix in (".yml", ".yaml", ".json"):
        try:
            return yaml.safe_load(text)
        except Exception:
            return None
    if path.suffix in (".md", ".markdown"):
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                try:
                    return yaml.safe_load(parts[1])
                except Exception:
                    return None
    return None


def validate_file(path: Path, schema: dict):
    data = extract_candidate_data(path)
    if data is None:
        return False, "no YAML/JSON content found"
    try:
        validate(instance=data, schema=schema)
        return True, None
    except ValidationError as e:
        return False, str(e)


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--schema", required=True, help="Schema filename in schema/ (e.g. provenance.schema.json)")
    p.add_argument("files", nargs="+", help="Files to validate")
    args = p.parse_args(argv)

    schema = load_schema(args.schema)
    exit_code = 0
    for f in args.files:
        path = Path(f)
        if not path.exists():
            print(f"MISSING: {f}")
            exit_code = 2
            continue
        ok, msg = validate_file(path, schema)
        if ok:
            print(f"OK: {f}")
        else:
            print(f"INVALID: {f} -> {msg}")
            exit_code = 1
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
