# Tools README — railweb

This folder contains small tooling utilities used to inspect and transform intake exports. The README below documents the small scripts and shows example Windows `cmd` commands to run them.

Sensory DevOps

This repository follows the Sensory DevOps principles (see `docs/Sensory-DevOps-Manifesto.md`). Key guidance for contributors:

- Represent modules in orchestration even when disabled (opt-in behavior).
- Produce provenance metadata for generated artifacts (see `prototype/readwise_audio`).
- When opening a PR that adds observable outputs (audio, dashboards, persistent artifacts), include a short note in the PR description referencing the Sensory DevOps checklist in `.github/pull_request_template.md`.


Available tools

- `tools/parse_kerml.py`

  Small KerML extractor that converts KerML-style requirement bundles into a JSON list and a trace CSV.

  Example usage (Windows cmd):

  ```cmd
  python tools\parse_kerml.py intake\exports\requirements_8ad06a3.kerml --out-dir intake\exports
  ```

  Output: `requirements_<sha>.json` and `requirements_<sha>_trace.csv` in the chosen out-dir.

- `tools/yaml_to_md.py`

  Render YAML files to a simple Markdown representation for human review.

  Example usage (Windows cmd):

  ```cmd
  python tools\yaml_to_md.py intake\assumptions.yaml > tmp_assumptions.md
  type tmp_assumptions.md
  ```

Running locally (Windows cmd)

```cmd
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
# run a tool
python tools\parse_kerml.py intake\exports\requirements_8ad06a3.kerml --out-dir intake\exports
```

Notes

- These utilities are intentionally small and conservative. They help reviewers and simple automation. For more complex parsing (nested blocks, full SysML support) we can replace the current regex-based extractor with a small parser or a library.
