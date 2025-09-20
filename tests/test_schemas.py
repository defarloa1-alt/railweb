import json
import os
from jsonschema import validate


HERE = os.path.dirname(__file__)
SCHEMA_DIR = os.path.join(HERE, "..", "schema")


def load_schema(name):
    path = os.path.join(SCHEMA_DIR, name)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def test_intake_schema_valid_sample():
    schema = load_schema("intake.schema.json")
    sample = {
        "id": "req-001",
        "title": "Scale converter requirement",
        "source": {"name": "NEM", "url": "https://example.org/specs/nem", "version": "2025-01"},
        "items": [{"type": "requirement", "value": "Convert mm to inches"}],
    }
    validate(instance=sample, schema=schema)


def test_provenance_schema_valid_sample():
    schema = load_schema("provenance.schema.json")
    sample = {
        "run_id": "20250920-01",
        "git_sha": "abcdef0",
        "created_at": "2025-09-20T12:00:00Z",
        "tool_versions": {"ingest_pipeline": "0.1.0", "railweb": "0.1.0", "python": "3.13.7"},
    }
    validate(instance=sample, schema=schema)


def test_requirements_schema_valid_sample():
    schema = load_schema("requirements.schema.json")
    sample = {"requirements": [{"id": "R1", "text": "Support HO scale"}]}
    validate(instance=sample, schema=schema)


def test_intake_schema_rejects_missing_fields():
    schema = load_schema("intake.schema.json")
    bad = {"title": "missing id and source"}
    try:
        validate(instance=bad, schema=schema)
        assert False, "schema should have rejected missing required fields"
    except Exception:
        pass


def test_provenance_schema_rejects_missing_tool_versions():
    schema = load_schema("provenance.schema.json")
    bad = {"run_id": "x", "git_sha": "abc1234", "created_at": "2025-09-20T12:00:00Z", "tool_versions": {}}
    try:
        validate(instance=bad, schema=schema)
        assert False, "schema should have rejected missing required tool_versions keys"
    except Exception:
        pass

