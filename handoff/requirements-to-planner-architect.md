---
title: Handoff Packet — Requirements Engineer (SysML v2)
generated: 2025-09-18
---

## 1. Current Contract Snapshot

- **Inputs**: `intake/` folder with
  - Required: `backlog.csv`, `risks.csv`, `milestones.csv`, `scope_capacity.yaml`
  - Optional: `assumptions.yaml`, `success_criteria.yaml`

- **Outputs**: `runs/<run_id>/` with
  - `requirements.md`, `architecture-brief.md`, `nodes.csv`, `edges.csv`, `cypher.cypher`, `index.json`, `README.md`

- **ID Policy**: Stable kebab-case IDs (`req:<domain>/<area>/<slug>`).

- **Hand-offs**:
  - Planner → backlog CSV, risks, milestones.
  - Architect → architecture brief (quality scenarios, NFRs, interface constraints).

- **Validation**: ISO/IEC/IEEE 29148; traceability enforced.

## 2. Intake README (Railweb) Changes

- Intake v1 defines:
  - `assumptions.yaml`, `scope.yml`, `milestones.csv`, `risks.csv`, `success_criteria.yaml`, `backlog.csv` (recommended).

- Front-matter conventions required:
  - `uid`, `source`, `source_commit`, `run_id`, `date_synced`.

- ID prefixes mandated:
  - `req:rail/railweb/...`, `nfr:rail/railweb/...`, `ms:rail/railweb/...`.

- Safety gating:
  - Any intake referencing hardware requires `safety_ack`.

**Impact**: Requirements Engineer must adapt to `scope.yml`, optional `backlog.csv`, and propagate provenance metadata.

## 3. Metadata JSON Template (Prototype/Readwise Audio)

Example (`out_audio.metadata.json`):

```json
{
  "run_id": "local-sample",
  "generated_at": "2025-09-18T00:00:00Z",
  "llm": {"model": "gpt-4o"},
  "tts_provider": "elevenlabs",
  "audio_generated": false,
  "audio_path": null,
  "highlights_provenance": []
}
```

Derived Requirements

- Ingest saved highlights → must preserve provenance (author, source_title, exported_at, checksum).
- Dry-run gating → no network calls, `audio_generated=false`.
- Audio toggle → disabled by default, operator must enable.
- No auto-uploads → prevent accidental publish.
- NFRs → segment→source traceability, provenance completeness.

Artifacts

- `out_audio.metadata.json` (artifact, verification anchor).
- `debug_ui/provenance_viewer.html` (inspection tool).

## 4. New Requirements & Risks from `llm_prompt.py`

Constraints

- LLM model selection — "The system SHALL accept `OPENAI_MODEL` env var to configure model (default `gpt-4o`)."
- JSON output contract — "LLM responses SHALL be valid JSON with keys: `script`, `show_notes`."

Nonfunctional

- Retry/backoff resilience — "The system SHALL retry LLM API calls up to 3 times with exponential backoff starting at 0.5s."

Risks

- LLM JSON fragility — "Malformed JSON responses may break pipeline. Mitigation: regex extraction fallback; test coverage required."

## 5. Collaboration Hooks

Planner

- Reflect optional backlog presence.
- Add risks: accidental publish, API key exposure, JSON fragility.
- Add tasks: enable real-run mode, configure supported models (`OPENAI_MODEL`), tune retry/backoff policy.
- Milestones: demo-ready dry-run; gated real-run.

Architect

- Define interface contracts:
  - `OPENAI_API_KEY`, `OPENAI_MODEL`, retry/backoff policy.
  - `audio_enabled` flag.
  - `ELEVENLABS_API_KEY`, ffmpeg input/output contract.
  - Enforce JSON schema (`script`, `show_notes`) in downstream components.
  - Extend metadata schema to include segment arrays for full trace coverage.

Instruction for Planner & Architect editors:
Please align backlog/brief parsing with:

- Intake v1 schema changes (`scope.yml`, provenance front-matter).
- Metadata JSON ingestion (`out_audio.metadata.json`).
- New constraints (LLM model selection, JSON output contract).
- New NFR (retry/backoff resilience).
- New risk (LLM JSON fragility).
