#!/usr/bin/env python3
"""Validate handoff JSON/YAML against the schema.

Usage: python scripts/validate_handoff.py handoff/requirements-to-planner-architect.example.json
"""
import sys
import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator, exceptions


def load(path: Path):
    text = path.read_text(encoding="utf-8")
    if path.suffix in (".yaml", ".yml"):
        return yaml.safe_load(text)
    return json.loads(text)


def main():
    if len(sys.argv) < 2:
        print("Usage: validate_handoff.py <file.json|yaml>")
        return 2
    target = Path(sys.argv[1])
    schema_path = Path(__file__).resolve().parents[1] / "handoff" / "requirements-to-planner-architect.schema.json"
    if not schema_path.exists():
        print("Schema not found:", schema_path)
        return 2
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    data = load(target)
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(data), key=lambda e: e.path)
    if errors:
        print(f"Validation failed: {len(errors)} error(s)")
        for e in errors:
            print("-", ".".join(map(str, e.path)) or "<root>", e.message)
        return 1
    print("Validation OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
