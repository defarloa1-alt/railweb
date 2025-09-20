# Railweb — Developer Onboarding

This short onboarding helps new contributors get productive quickly.

## Project summary

Railweb is a web-focused reference and tooling project for model-railroading hobbyists. It provides a source-cited specification library, scale converters, guides, and prototypes (eg. Readwise→Audio). The repo includes small tooling utilities (`tools/`) and prototypes under `prototype/`.

Key constraints from `intake/`:
- NMRA-first authoritative sources; provenance metadata required for published spec values.
- Live-control features must be opt-in and include explicit safety acknowledgement.
- v1 excludes e-commerce and remote cloud control.

## Quick dev setup (Windows, cmd.exe)

1. Create and activate a virtual environment (Python 3.11+ recommended):

```cmd
python -m venv .venv
.venv\Scripts\activate
```

2. Install dependencies:

```cmd
python -m pip install --upgrade pip
python -m pip install -r requirements.txt -r test-requirements.txt
```

3. Run tests:

```cmd
python -m pytest -q
```

Notes:
- CI workflows use Python 3.11; README mentions 3.12 for local envs. Either 3.11 or 3.12 should work for most development tasks.
- Some tests start a Flask mock adapter on port 3001 (tools/debate/mock_adapter). Tests set `PYTHONPATH` to the repo root in CI; when running locally, run tests from the repo root or set `PYTHONPATH` accordingly.

## What I fixed during onboarding

- Cleaned `requirements.txt` (removed merge conflict markers and duplicate entries).
- Removed merge conflict markers from `tools/debate/generate_debate_insights.py` so tests can import the module.
- Ran the test suite; tests completed with expected warnings and outputs.

## How tests are organized

- `tests/` contains unit and integration tests. They import local utilities from `tools/` and `prototype/`.
- To avoid `ModuleNotFoundError` for `tools`, run pytest from repo root or set `PYTHONPATH` to the repository root.

## CI notes

- GitHub Actions workflows in `.github/workflows/` run pytest on pushes and PRs.
- There are additional workflows for provenance checks which run `tools/validate_provenance.py` on intake changes.

## Suggested next tasks

- Add a small `pre-commit` configuration to catch merge-conflict markers in staged files.
- Add a CI check that scans for `<<<<<<<` conflict markers to prevent bad commits (low-risk automated guard).
- Create a checklist for adding new spec entries that enforces provenance metadata (source.id, source.title, source.date, source.url, confidence, rounding_rule).
- Expand `ONBOARDING.md` with links to architecture areas (where converters will live) once source code modules are added.

If you'd like, I can open a small PR that adds the conflict-marker CI check and a `pre-commit` hook configuration.
