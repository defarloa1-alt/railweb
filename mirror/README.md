Railweb Automation Mirror (minimal)
=================================

This is a tiny FastAPI-based mirror that implements the minimal automation surface for handoff validation and run indexing.

Quickstart (Windows cmd.exe)

1. Create a venv and install deps

```cmd
python -m venv .venv
.\.venv\Scripts\activate
pip install -r mirror/requirements.txt
```

2. Run the server

```cmd
python -m mirror.main
# or
uvicorn mirror.main:APP --reload --port 8080
```

3. Validate the example handoff

```cmd
curl -s -X POST http://localhost:8080/validate_handoff -H "Content-Type: application/json" -d @handoff/requirements-to-planner-architect.example.json | jq .
```

Auth & non-dry-run operations

- The server supports a bearer token controlled by the `MIRROR_BEARER_TOKEN` env var.
- Non-dry-run operations (`dry_run=false`) require a valid bearer token in `Authorization: Bearer <token>`.

Example (ingest with token):

```cmd
curl -s -X POST http://localhost:8080/ingest_handoff -H "Content-Type: application/json" -H "Authorization: Bearer $MIRROR_TOKEN" -d @handoff/requirements-to-planner-architect.example.json | jq .
```

Notes
- This is intentionally minimal. For production, add auth, rate limiting, robust schema validation, and logging.

Environment variables

- `MIRROR_BEARER_TOKEN` → required for non-dry-run operations (set this in CI as a secret).
- `PORT` → optional, defaults to `8080`.
- `RUNS_DIR` → optional, defaults to `runs/`.

Example run index

When ingesting a handoff the mirror writes `runs/{run_id}/index.json`. Example:

```json
{
  "run_id": "run-20250918-abc123",
  "validated": true,
  "errors": [],
  "dry_run": true,
  "source_commit": "abc1234",
  "date_synced": "2025-09-18T00:00:00Z",
  "artifacts": ["runs/run-20250918-abc123/index.json"]
}
```

CI hint

- Use the mirror in CI to validate `handoff/*.yaml|json` with `/validate_handoff` before merging.
- Optionally call `/ingest_handoff` in a gated workflow to generate `runs/` artifacts for Planner/Architect consumption.

Security note

- `dry_run=true` by default. CI workflows should leave `dry_run` enabled unless an explicit approval step flips it to false. This prevents accidental external API calls from PRs.

Local testing with token (cmd.exe)

```cmd
set MIRROR_BEARER_TOKEN=replace-me
set MIRROR_TOKEN=replace-me
python -m mirror.main
```
