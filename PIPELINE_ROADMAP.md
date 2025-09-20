Railweb Intake → Production pipeline roadmap

This document maps the end-to-end pipeline from intake artifacts (YAML/KerML/JSON) through validation, parsing, enrichment, and production of Markdown/requirements/trace outputs. It is intended to be a detailed playbook for implementing the pipeline to reach production-ready MDSE artifacts.

Overview
--------
Goals:
- Ingest intake files (from GPT-based intake tools) and validate provenance and schema.
- Parse and normalize requirement bundles (KerML → JSON + trace CSV).
- Generate production Markdown with provenance front matter and auxiliary artifacts.
- Enforce CI gates and provenance policies to prevent regressions.

Core design principles:
- Provenance-first: every produced artifact must carry source metadata and a reproducible link to the input.
- Safety-first for any live-control features: explicit opt-ins, local defaults, and documented manual tests.
- Small, testable modules for parsing, validation, and rendering.

Roadmap tasks (detailed)
------------------------
1) Define input/output contracts & schemas
   - Deliverables:
     - `schema/intake.schema.json` — JSON Schema for intake YAML/JSON files (required fields and provenance keys).
     - `schema/output_provenance.schema.json` — schema for generated provenance JSON files.
     - Example sample intake files in `intake/samples/` for use in tests.
   - Acceptance criteria:
     - Schemas validate existing intake files in `intake/` without false negatives.
     - Tests cover missing required fields and invalid types.
   - Estimated effort: 1-2 days

2) Enhance parsers & validators
   - Deliverables:
     - Improvements to `tools/parse_kerml.py` with better error messages and CLI flags.
     - Improvements to `tools/validate_provenance.py` to return machine-readable errors and an exit code map.
   - Acceptance criteria:
     - Parsers must produce `requirements_<sha>.json` and trace CSV with consistent fields.
     - Validator must fail on missing `source.*` or missing `rounding_rule`.
   - Estimated effort: 2-3 days

3) Implement ingest pipeline scaffold
   - Deliverables:
     - `tools/ingest_pipeline.py` CLI with modes: `discover`, `validate`, `parse`, `emit`, and `dry-run`.
     - Writes outputs to `exports/` with a run manifest (`exports/run_<sha>.json`).
   - Behavior:
     - Discover intake files (patterns: `intake/**/*.yaml`, `.kerml`, `intake/exports/*.kerml`).
     - Validate each file against `schema/intake.schema.json` and provenance checks.
     - Parse KerML files to JSON and CSV via `tools/parse_kerml.py`.
     - Generate Markdown via `tools/yaml_to_md.py` for human review.
   - Acceptance criteria:
     - `tools/ingest_pipeline.py --dry-run` runs without mutating repo and prints planned actions.
     - `tools/ingest_pipeline.py --emit` generates artifacts into `exports/` and a run manifest.
   - Estimated effort: 3-5 days

4) Tests (unit/integration/smoke)
   - Deliverables:
     - `tests/test_parse_kerml.py` (improve coverage), `tests/test_validate_provenance.py`.
     - `tests/test_ingest_pipeline_smoke.py` that runs pipeline against `intake/samples`.
   - Acceptance criteria:
     - Unit tests run locally and in CI; smoke test runs under time limit (e.g., <30s in CI).
   - Estimated effort: 2-3 days

5) CI gating & workflows
   - Deliverables:
     - Add `conflict-check.yml` (done) and `requirements-check.yml` for fast scanning.
     - Add `ingest-pipeline.yml` workflow to run smoke pipeline generation in CI and upload artifacts.
   - Acceptance criteria:
     - PRs touching `intake/**` must pass importer/validator steps before merge.
   - Estimated effort: 1-2 days

6) Provenance enforcement & PR templates
   - Deliverables:
     - Update `.github/PULL_REQUEST_TEMPLATE.md` to include provenance checklist.
     - Add `tools/check_provenance.py` that checks staged intake files in PR contexts.
   - Acceptance criteria:
     - PRs missing required provenance fields are flagged by CI with clear remediation steps.
   - Estimated effort: 1 day

7) Packaging & code layout
   - Deliverables:
     - Add `src/railweb/` with core modules: `railweb.parsers`, `railweb.validators`, `railweb.renderers`.
     - Migrate stable utilities from `tools/` into the package with tests.
   - Acceptance criteria:
     - Tests import modules from `railweb.*` and no longer rely on `PYTHONPATH` hacks.
   - Estimated effort: 2-4 days

8) Safety & staging for live-control features
   - Deliverables:
     - Documented opt-in gating rules, a `SAFETY.md`, and a standard manual test procedure for device code.
   - Acceptance criteria:
     - Any PR that enables device network access must include a manual test plan and safety acknowledgement.
   - Estimated effort: 1-2 days

9) Docs and runbook
   - Deliverables:
     - `PIPELINE_RUNBOOK.md` with run steps, troubleshooting, expected artifacts, and audit log format.
   - Acceptance criteria:
     - A developer can run the pipeline successfully following the runbook.
   - Estimated effort: 1-2 days

10) Monitoring, reproducibility, and artifact provenance
   - Deliverables:
     - Run manifests that include git SHA, tool versions, Python version, and input file list.
     - Store artifacts under `exports/<run_sha>/` with `manifest.json` and `provenance.json`.
   - Acceptance criteria:
     - Every artifact in `exports/` is traceable to an input file and run manifest.
   - Estimated effort: 1-2 days

11) Performance & scalability
   - Deliverables:
     - Benchmarks for parsing large KerML bundles and a plan for partitioned processing if needed.
   - Acceptance criteria:
     - Pipeline can parse a realistic load in acceptable time; document limits.
   - Estimated effort: 1-3 days

12) Release & publishing
   - Deliverables:
     - Decide on artifact publishing (GH releases, GitHub Pages for markdown, or object storage).
     - CI job to publish artifacts when a release tag is created.
   - Acceptance criteria:
     - Released artifacts are discoverable and include provenance metadata.
   - Estimated effort: 1-2 days

13) Follow-ups
   - Add more converters, localized outputs, UI for browsing specs, and DCC/CAD adapters.

Appendix: Acceptance criteria checklist for an intake PR
-------------------------------------------------------
- [ ] Intake file compiles against `schema/intake.schema.json`.
- [ ] `tools/validate_provenance.py` passes for all non-policy files.
- [ ] Any generated artifacts from the sample intake run in `tools/ingest_pipeline.py --dry-run`.
- [ ] PR description includes source citations and a short rationale.



