# railweb

## Overview

**railweb** is an open-source web system for model railroaders. It provides authoritative, source-cited reference data, smart converters, beginner through advanced guides, and modern control and planning tools for the global model railroading community.

## Goals

- **Comprehensive Standards**: NMRA/NEM/other specs, with clear citations.
- **Cross-scale Tools**: Converters, calculators, control, and programming utilities for all major scales.
- **Platform Agnostic**: Works on desktop and mobile, no required cloud account for v1.
- **Open for All**: Guides for hobbyists, clubs, educators—founded on community and accuracy.

<!--TABLE:START-->

| Name   | Status      | Notes          |
| ------ | ----------- | -------------- |
| Task A | Done        | Completed work |
| Task B | In Progress | Work ongoing   |

<!--TABLE:END-->

## Features

- **Reference Library**: Specs and how-tos, tightly sourced and date/version stamped.
- **Converters/Calculators**: Seamless, flexible tools for scale conversion, voltage, current, etc.
- **Control & Programming**: Modern DCC, real-time controls, and CAD/CAM links.
- **Integrated Guides**: From beginner scenery to advanced automation.
- **Simulation Ready**: (v1): CAD/CAM I/O, import/export, and scenario planners.

## Project Milestones

See `intake/milestones.csv` for the canonical milestone list and definitions of done.

## What’s In Scope (v1)

- Spec lookup/search (≤3 clicks to any reference)
- Multi-format converters (e.g., scale, DCC, voltage)
- Real-time device control (local / no cloud required)
- DCC/CAD/CAM compatible import/export
- Comprehensive, source-cited guides

## What’s Out of Scope (for v1)

- Online marketplace
- Forums/social features
- Remote operation via cloud

## Success Criteria

- **Quantitative**: ≥20 published specs, converter/calc test coverage, guides are actionable
- **Qualitative**: All content source-cited; discoverable in ≤3 clicks

## Assumptions

- English-only v1; other languages future-scope
- NMRA “first,” others post-MVP
- Must work well on both desktop and mobile
- Licensing, safety, reliability are core constraints

## Risks & Mitigations

See `intake/risks.csv` for the current list of risks, mitigations and owners.

## Contributing

Contributions, feedback, and new guide submissions are welcome! See `CONTRIBUTING.md` for details on how to open issues, run the test suite, and submit PRs.

## Developer setup (Windows - cmd.exe)

1. Create a Python 3.12 environment (recommended):

```cmd
python -m venv .venv
.venv\Scripts\activate
```

1. Install project dependencies:

```cmd
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pytest jsonschema
```

1. Run the test suite:

```cmd
python -m pytest -q
```

1. Optional: install pre-commit hooks (if you have git installed locally):

```cmd
python -m pip install pre-commit
pre-commit install
pre-commit run --all-files
```

## Quickstart - Run Readwise→Audio prototype (dry-run)

```cmd
cd prototype\readwise_audio
python run_pipeline.py --no-dry-run --audio
```

Notes:
- The prototype is opt-in for external API calls. Use `--no-dry-run` to allow real calls, and set `ELEVENLABS_API_KEY` (and other keys) via environment variables.
- Provenance metadata is written to `out_audio.metadata.json` when the prototype runs.

## License

MIT (see `LICENSE`)

## Contact

Project owner: Tony DeFarlo
File an issue or open a discussion for questions.
# railweb

Railweb is a collection of reference material, converters, and prototypes for model-railroad hobbyists and tooling.

This repository includes a small prototype for Readwise→Audio enrichment and a Sensory DevOps manifesto describing principles for observable, auditable multi-sensory pipelines.

- Sensory DevOps Manifesto: `docs/Sensory-DevOps-Manifesto.md`
- Prototype: `prototype/readwise_audio/`

See `tools/README.md` for utilities and `.github/pull_request_template.md` for PR guidance.
