from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from datetime import datetime, timezone
import json
import os
import uuid
from pathlib import Path
from typing import Tuple, List, Dict, Any
import logging

try:
    import yaml
except Exception:  # pragma: no cover - optional dependency helper
    yaml = None
    logger.warning("PyYAML not available; YAML files will not be supported in this runtime")
from jsonschema import Draft202012Validator

logger = logging.getLogger("mirror")
logging.basicConfig(level=logging.INFO)

APP = FastAPI(title="Railweb Automation Mirror API", version="0.1.0")

RUNS = Path("runs")
RUNS.mkdir(exist_ok=True)

SCHEMA_PATH = Path(__file__).resolve().parents[1] / "handoff" / "requirements-to-planner-architect.schema.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_handoff_obj(path_or_obj: Any) -> dict:
    if isinstance(path_or_obj, dict):
        return path_or_obj
    p = Path(path_or_obj)
    text = p.read_text(encoding="utf-8")
    if p.suffix in (".yaml", ".yml"):
        return yaml.safe_load(text)
    return json.loads(text)


def validate_handoff_obj(h: dict) -> Tuple[bool, List[Dict[str, Any]]]:
    if not SCHEMA_PATH.exists():
        # Fallback: basic checks
        errs = []
        if "requirements" not in h:
            errs.append({"path": "$.requirements", "message": "Missing requirements"})
        if "title" not in h:
            errs.append({"path": "$.title", "message": "Missing title"})
        return (len(errs) == 0, errs)

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    errors = []
    for e in validator.iter_errors(h):
        path = "." + ".".join([str(x) for x in e.path]) if e.path else "$"
        errors.append({"path": path, "message": e.message})
    return (len(errors) == 0, errors)


def ingest_handoff_obj(h: dict, dry_run: bool = True, run_id: str | None = None, source_commit: str | None = None):
    validated, errors = validate_handoff_obj(h)
    run_id = run_id or f"run-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}"
    run_dir = RUNS / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    index = {
        "run_id": run_id,
        "validated": validated,
        "errors": errors,
        "dry_run": dry_run,
        "source_commit": source_commit or h.get("provenance", {}).get("source_commit"),
        "date_synced": now_iso(),
        "artifacts": [],
    }
    (run_dir / "index.json").write_text(json.dumps(index, indent=2), encoding="utf-8")
    logger.info("Wrote run index: %s", run_dir / "index.json")
    return index


def generate_index_obj(run_id: str, dry_run: bool = True, source_commit: str | None = None):
    run_dir = RUNS / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    status = "updated" if (run_dir / "index.json").exists() else "created"
    index = {
        "run_id": run_id,
        "validated": True,
        "errors": [],
        "dry_run": dry_run,
        "source_commit": source_commit,
        "date_synced": now_iso(),
        "artifacts": [],
    }
    (run_dir / "index.json").write_text(json.dumps(index, indent=2), encoding="utf-8")
    return {"run_id": run_id, "path": str(run_dir / "index.json"), "status": status, "date_synced": index["date_synced"]}


class ValidateReq(BaseModel):
    dry_run: bool = True
    handoff: dict


class IngestReq(BaseModel):
    dry_run: bool = True
    run_id: str | None = None
    source_commit: str | None = None
    handoff: dict


class IndexReq(BaseModel):
    dry_run: bool = True
    run_id: str
    source_commit: str | None = None


@APP.post("/validate_handoff")
async def validate_handoff(request: Request):
    # Accept either {"handoff": {...}} or a raw handoff object (CI posts raw example JSON)
    payload = await request.json()
    handoff_obj = payload.get("handoff") if isinstance(payload, dict) and "handoff" in payload else payload
    ok, errors = validate_handoff_obj(handoff_obj)
    return {"validated": ok, "errors": errors, "run_id": f"validation-{uuid.uuid4().hex[:8]}", "source_commit": handoff_obj.get("provenance", {}).get("source_commit"), "date_synced": now_iso()}


@APP.post("/ingest_handoff")
def _require_token(request: Request):
    token_env = os.getenv("MIRROR_BEARER_TOKEN")
    if not token_env:
        raise HTTPException(status_code=500, detail="Server misconfigured: MIRROR_BEARER_TOKEN not set")
    auth = request.headers.get("authorization") or request.headers.get("Authorization")
    if not auth or not auth.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    token = auth.split(None, 1)[1]
    if token != token_env:
        raise HTTPException(status_code=403, detail="Invalid token")


@APP.post("/ingest_handoff")
async def ingest_handoff(request: Request):
    # Accept either a wrapper payload or a raw handoff object. Default dry_run is True.
    payload = await request.json()
    # support both {"handoff": {...}, "dry_run": false, ...} and raw handoff object
    if isinstance(payload, dict) and ("handoff" in payload or "dry_run" in payload or "run_id" in payload):
        dry_run = payload.get("dry_run", True)
        run_id = payload.get("run_id")
        source_commit = payload.get("source_commit")
        handoff_obj = payload.get("handoff") if "handoff" in payload else payload
    else:
        # raw handoff object posted
        dry_run = True
        run_id = None
        source_commit = None
        handoff_obj = payload

    # enforce auth for non-dry-run operations
    if not dry_run:
        _require_token(request)

    idx = ingest_handoff_obj(handoff_obj, dry_run=dry_run, run_id=run_id, source_commit=source_commit)
    return {"run_id": idx["run_id"], "validated": idx["validated"], "errors": idx["errors"], "artifacts": [f"runs/{idx['run_id']}/index.json"], "date_synced": idx["date_synced"], "dry_run": idx["dry_run"]}


@APP.post("/generate_index")
def generate_index(req: IndexReq, request: Request):
    # enforce auth for non-dry-run operations
    if not req.dry_run:
        _require_token(request)
    res = generate_index_obj(req.run_id, dry_run=req.dry_run, source_commit=req.source_commit)
    return {"run_id": res["run_id"], "path": res["path"], "status": res["status"], "date_synced": res["date_synced"]}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("mirror.main:APP", host="0.0.0.0", port=8080, reload=True)
