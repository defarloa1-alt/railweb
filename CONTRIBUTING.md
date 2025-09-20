# Contributing to railweb

Thanks for contributing! A few quick guidelines:

- Read `docs/Sensory-DevOps-Manifesto.md` to understand project principles.
- Open a PR and reference a milestone from `intake/milestones.csv` where appropriate.
- Include tests for new behavior where possible. See `tests/` for examples.
- If adding observable outputs (audio, dashboards), follow the Sensory DevOps checklist in the PR template.

Development environment

```cmd
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Submitting changes

- Use feature branches and open a PR against `main`.
- Maintainers will review for safety gating, provenance, and citations when applicable.
