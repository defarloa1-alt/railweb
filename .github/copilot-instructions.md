## Copilot / AI Agent Instructions for railweb

Purpose: Help an AI coding agent become immediately productive in this repository by listing the discoverable architecture, data flows, developer signals, and project constraints the agent must respect.

1. What is present (source of truth)
- The repo currently contains planning and intake artifacts under `intake/` (see `intake/scope.yml`, `assumptions.yaml`, `success_criteria.yaml`, `milestones.csv`, `risks.csv`). Use these files as the primary source of project goals, constraints and acceptance criteria.

2. Big-picture summary (from `intake/scope.yml`)
- Project goal: a web-based reference and tooling site for model railroad hobbyists: spec corpus, scale conversion calculators, guidance, real-time layout control (throttle/turnout), DCC programming utilities, and simulation/CAD integration.
- v1 constraints: no e-commerce, no social features, live control constrained to local/network-limited usage (safety-first).

3. Immediate agent priorities (actionable)
- Read `intake/scope.yml` and `assumptions.yaml` before making feature decisions. They define in-scope features and constraints (safety/licensing).
- When adding or modifying code, always include a citation/source/version metadata for any published spec values (intake requires this).
- Preserve safety constraints for any live-control or DCC features: require explicit acknowledgement gates and local-only defaults unless maintainers indicate otherwise.

4. What to look for next (where architecture will appear)
- When source code appears, expect one of these patterns. Search for these files/dirs to find the project architecture quickly:
  - `package.json`, `yarn.lock`, `pnpm-lock.yaml` → Node/JS web app (frontend and possibly server).
  - `pyproject.toml`, `requirements.txt` → Python services or tooling.
  - `Dockerfile`, `docker-compose.yml` → container-based services.
  - `src/`, `web/`, `server/`, `cmd/` → service boundaries and entry points.

5. Project-specific conventions and notes (discoverable)
- Data provenance: every spec/value shown to users must carry a source and version/date (see `assumptions.yaml`).
- Rounding/units: conversions must follow documented rounding rules; tests should include hand-checked canonical examples (see `success_criteria.yaml`).
- Safety and gating: features that control real hardware must include explicit UI/UX warnings and require opt-in confirmations (see `assumptions.yaml` and `risks.csv`).

6. Integration points and dependencies (from intake)
- Expected external integrations: command stations / DCC decoder interfaces and simulator/CAD file formats. The intake prioritizes a small, documented set of supported interfaces (see `milestones.csv` item M2A).
- Licensing: some standards may be restricted; prefer summarizing with citation and linking to authoritative documents rather than reproducing copyrighted text (see `risks.csv` R1).

7. If you cannot find build/test/deploy scripts
- The repository currently has no source or build config files in the root; before making assumptions, ask the maintainers for the preferred stack and CI/build commands. If asked to proceed without guidance, implement changes that are easy to revert (feature branches) and include a README note explaining how you tested locally.

8. Helpful searches/examples (explicit)
- To find where converters live: search for keywords `convert`, `scale`, `units`, `rounding`.
- To find live-control code: search for `throttle`, `turnout`, `DCC`, `command station`, `CV read`, `CV write`.
- To find data files: look under `data/`, `specs/`, `corpus/`, or `intake/`.

9. Safety, tests and deliverables
- Small changes: include a one-paragraph rationale referencing the relevant intake file (e.g., "matches M3 Scale Converters MVP in intake/milestones.csv").
- Any DCC/control change must include a non-hardware-breaking default (no automatic activation) and a documented manual test procedure in the PR.

10. When in doubt
- Prefer asking: this repo currently exposes planning artifacts but no runtime code. If something isn't discoverable in the repo, ask the repository owner or open an issue referencing the intake file that motivated the question.

----
If you'd like I can (1) merge this into an existing copilot-instructions file if you have one elsewhere, (2) extend these notes once source code is added (I will re-scan `src/`, `package.json`, etc.), or (3) create short PR templates and checklists that enforce the citation and safety rules above.

## Auto-extension: when code appears

When an AI agent detects source code, build manifests, or CI config in the repository, auto-extend these instructions with a short, focused section describing the discovered architecture and workflows. Follow this minimal, repeatable workflow:

1. Detect files using these patterns (stop at first match of each group):
  - Language & package manifests: `package.json`, `pyproject.toml`, `requirements.txt`, `Gemfile`, `go.mod`.
  - Build/CI/container: `Dockerfile`, `docker-compose.yml`, `.github/workflows/*.yml`, `Makefile`.
  - Source roots: `src/`, `web/`, `server/`, `cmd/`, `app/`.
  - Test frameworks: `jest.config.js`, `pytest.ini`, `tox.ini`, `tests/`.

2. Summarize discovered architecture in 3 lines: runtime (Node/Python/etc.), entry points (files/dirs), and test command.

3. Add concrete developer commands to the instructions (examples):
  - Node: `npm install` + `npm test` (or `pnpm install && pnpm test` if `pnpm-lock.yaml` exists).
  - Python: `python -m venv .venv && .\.venv\Scripts\activate && pip install -r requirements.txt && pytest` (Windows examples included).
  - Docker: `docker build -t railweb .` and `docker-compose up --build`.

4. Cite any discovered policy or config snippets (CI checks, linters) and note any safety gates found (e.g., workflows that deploy or run hardware tests).

5. Commit the small augmentation as an edit to `.github/copilot-instructions.md` and include a one-line rationale referencing the detected files.

Rules and limits:
- Keep auto-extensions concise (<= 12 lines) and strictly factual — only include commands and references present in the repo.
- Do not add security-sensitive automation (e.g., remote control activation) without explicit maintainer approval.
- When in doubt about build/run commands, include them as suggestions and mark them "suggested" (not authoritative).
