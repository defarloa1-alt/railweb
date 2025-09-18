Assistants API mirror spec (minimal)
===================================

Purpose
-------

This document describes a minimal Assistants API mirror that reproduces the behavior of the Requirements Engineer MyGPT. Use this when you need an external service API that automates Planner/Architect ingestion, validations, and artifact generation.

Design
------

- Use the same model family and distilled prompts from the handoff packet.
- Expose thin endpoints for: `ingest_handoff`, `validate_handoff`, `generate_index`.
- Keep side-effects gated: require `dry_run=false` and `api_key` in request to perform artifact writes.

Endpoints
---------

1. POST /ingest_handoff
   - Body: `{ "path": "handoff/requirements-to-planner-architect.yaml", "run_id": "...", "dry_run": true|false }`
   - Behavior: loads the YAML, validates against schema, returns parsed object and validation report. If `dry_run=false` and validation passes, write generated artifacts to `runs/{run_id}/`.

2. POST /validate_handoff
   - Body: `{ "file": "path or content" }`
   - Behavior: validates the handoff file and returns AJV/yq validated output and errors.

3. POST /generate_index
   - Body: `{ "run_id": "...", "artifacts": ["path1","path2"], "validation": { ... } }`
   - Behavior: produce `runs/{run_id}/index.json` with artifact pointers and validation status.

Security & Safety
-----------------

- Require API auth for non-dry-run operations.
- Log only hashed run IDs and redact secrets.
- Default `dry_run=true`.

Usage
-----

This mirror can be run as a small Flask/FastAPI service, or executed via GitHub Actions (CI-driven ingestion). It lets Planner/Architect GPTs trigger automated validations without needing direct MyGPT access.
