"""Simple ingest pipeline scaffold.

Discover intake/*.yaml or *.yml files, validate against schema, and emit artifacts.
Provides a dry-run mode and simple audit logging.
"""
from __future__ import annotations

import argparse
import glob
import json
import logging
import os
import sys
from datetime import datetime

from jsonschema import validate, ValidationError

LOG = logging.getLogger("ingest")


def discover_intake(path="."):
    pattern = os.path.join(path, "intake", "**", "*.yml")
    files = glob.glob(pattern, recursive=True)
    pattern2 = os.path.join(path, "intake", "**", "*.yaml")
    files += glob.glob(pattern2, recursive=True)
    return sorted(files)


def load_json_schema(schema_name: str):
    base = os.path.join(os.path.dirname(__file__), "..", "schema")
    path = os.path.abspath(os.path.join(base, schema_name))
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def read_file(path: str):
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def validate_intake(path: str, schema: dict):
    import yaml

    content = yaml.safe_load(read_file(path))
    try:
        validate(instance=content, schema=schema)
        return True, content
    except ValidationError as e:
        return False, str(e)


def emit_artifact(out_dir: str, basename: str, content: dict):
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"{basename}.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(content, fh, indent=2, sort_keys=True)
    return path


def make_provenance(run_id: str):
    return {
        "run_id": run_id,
        "git_sha": os.environ.get("GIT_SHA", "local"),
        "created_at": datetime.utcnow().isoformat() + "Z",
        "tool_versions": {"ingest_pipeline": "0.1.0"},
    }


def main(argv=None):
    parser = argparse.ArgumentParser(prog="ingest_pipeline")
    parser.add_argument("--path", default=".")
    parser.add_argument("--schema", default="intake.schema.json")
    parser.add_argument("--out", default="exports")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    files = discover_intake(args.path)
    LOG.info("Discovered %d intake files", len(files))

    schema = load_json_schema(args.schema)

    run_id = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    provenance = make_provenance(run_id)

    audit = {"run_id": run_id, "files": [], "errors": []}

    for p in files:
        ok, result = validate_intake(p, schema)
        entry = {"path": p, "ok": bool(ok)}
        if ok:
            entry["summary"] = {"title": result.get("title", "")}
            if not args.dry_run:
                basename = os.path.splitext(os.path.basename(p))[0]
                outpath = emit_artifact(args.out, basename, {"intake": result, "provenance": provenance})
                entry["emitted"] = outpath
        else:
            entry["error"] = result
            audit["errors"].append({"path": p, "error": result})
        audit["files"].append(entry)

    # always emit audit in dry-run and normal
    if not args.dry_run:
        emit_artifact(args.out, f"audit-{run_id}", audit)
        emit_artifact(args.out, f"provenance-{run_id}", provenance)
    else:
        LOG.info("Dry-run: audit summary: %s", json.dumps(audit, indent=2)[:1000])

    if audit["errors"]:
        LOG.error("Errors found during ingest: %d", len(audit["errors"]))
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
