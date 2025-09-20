# Intake folder conventions for railweb

## Purpose

This folder contains the canonical intake artifacts used to create requirements, milestones, risks, and other project planning inputs. Files here are considered the source of truth for initial planning runs and automated ingestion.

Required intake file types (v1 expectations)

- `assumptions.yaml` — project assumptions and modeling constraints
- `scope.yml` — feature in-scope / out-of-scope definitions
- `milestones.csv` — milestone id, title, window, DoD notes
- `risks.csv` — risk id, description, owner
- `success_criteria.yaml` — measurable success criteria / NFRs
- `backlog.csv` — (recommended) backlog placeholder; if missing, automated tools will flag as "gap"

Front-matter and provenance conventions

When intake items are generated or synchronized (for example, from Obsidian), include YAML front-matter at the top of the file with these recommended fields:

- `uid`: stable unique id (policy: kebab-case, prefixed with `rail/railweb/` when applicable)
- `source`: path or URL of the original note (e.g., `obsidian://...` or `git@github.com:.../path`)
- `source_commit`: optional short SHA when the source is a git commit
- `run_id`: id of the ingestion run (optional but recommended)
- `date_synced`: ISO 8601 timestamp when the file was added/updated by automation

Example front-matter (Obsidian-compatible):

```yaml
uid: req-scale-converter
source: obsidian://vault/notes/scale-converter.md
source_commit: 8ad06a3
run_id: run-2025-09-17-railweb-8ad06a3
date_synced: 2025-09-17T00:00:00-04:00
```

Id and naming policy

- Use kebab-case and human-readable prefixes: `req:rail/railweb/...`, `nfr:rail/railweb/...`, `ms:rail/railweb/...`.
- Keep ids stable. Automation uses `uid` or front-matter `id` to avoid creating duplicates.

Safety & gating notes

- Any intake that references live/hardware control must include a `safety_ack` field and explicit notes about required manual testing and local-only constraints. Automation should never enable hardware without an explicit human acknowledgement gate.

Contact / provenance

- When in doubt, include the original source URL and commit SHA in the front-matter so reviewers can trace back the origin of a requirement.
