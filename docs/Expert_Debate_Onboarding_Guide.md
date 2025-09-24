# Expert Debate System Onboarding Guide

## Purpose
- Give incoming technical leads a high-level map of the Expert Debate stack
- Clarify how the Python-only path and the optional Node adapter relate
- Provide first-week actions so the architect and developer can build momentum quickly

## Current State Snapshot (2025-09)
- Python-only debate stack is functional per `docs/Expert_Debate_Minimum_Stack_Ready.md`
- Expert personas (5) and core SysML artifacts are curated under `intake/` and `docs/`
- Infrastructure tests succeed locally without hitting the OpenAI API
- Live OpenAI calls require a valid API key and an accessible model (current scripts default to `gpt-4`)

## Architecture Overview
- **Personas & Artifacts**: Markdown personas live in `intake/ai_experts/`; primary debate artifact is `docs/Chrystallum_SysML_Block_Definitions.md`, with scope and milestone inputs in `intake/scope.yml` and `intake/milestones.csv`
- **Python Expert Path**: `tools/python_expert_debate.py` provides `PythonExpertAgent` and `PythonDebateOrchestrator` for direct OpenAI usage; `tools/test_expert_system.py` exercises personas, artifacts, and import sanity without API calls
- **Adapter-Based Path**: `tools/minimal_expert_debate.py` integrates with `tools/llm_adapter` (Node/Express) via HTTP; `tools/start_expert_debate.py` orchestrates prerequisite checks, adapter startup, and smoke tests
- **Shared Contracts**: Both paths expect experts to emit JSON with `analysis`, `key_concerns`, `recommendations`, `compliance_notes`, and `confidence`; debate rounds build consensus scores and aggregate recommendations

## Intake Structuring Agent Persona
- Reference persona: `intake/ai_experts/intake_structuring_agent.md`
- Handles structured updates across `intake/` artifacts while enforcing policy constraints and provenance fields.
- Coordinates with Requirements Engineer, Project Planner, and System Architect experts to stage debate-ready inputs and trigger downstream actions.

## Alignment with AI Expert SDLC Project Plan
- **Phase 1 - Foundation (Weeks 1-2)**: Ensure personas, debate orchestrator, and validation schemas in `intake/`, `tools/`, and `schema/` stay aligned; confirm consensus outputs pass automated checks.
- **Phase 2 - Knowledge Integration (Weeks 3-4)**: Prioritize the enrichment hooks outlined in `docs/AI_Expert_SDLC_Project_Plan.md` by wiring experts into Neo4j ingestion, Perplexity or Wikidata lookups, and confidence-weighted relationships; vet the `tools/neo4j/` pipeline and graph schema against live debates.
- **Phase 3 - Advanced Workflows (Weeks 5-6)**: Coordinate with UI and orchestration owners to add human review surfaces, CI/CD automation for personas, and production deployment runbooks once Phases 1-2 stabilize.
- Track deliverable status in `docs/AI_Expert_SDLC_Project_Plan.md` and reflect updates in debate summaries to keep artifacts synchronized.

## Repository Topography (key folders)
- `tools/`: Python utilities, expert debate orchestration, adapters, diagnostics
- `intake/`: Structured project inputs (personas, scope, milestones, context)
- `docs/`: Generated and hand-authored documentation, including SysML deliverables
- `tests/`: Pytest suites for adapters, enrichment, intake validation, and debate utilities
- `exports/`: CSV snapshots of broader Chrystallum planning artifacts

## Local Setup Checklist
1. Install Python 3.12+ (3.13 recommended by current scripts)
2. `python -m venv .venv` and activate (`.venv\Scripts\activate` on Windows or `source .venv/bin/activate` on Unix)
3. `python -m pip install --upgrade pip`
4. `python -m pip install -r requirements.txt` and `python -m pip install openai`
5. Export `OPENAI_API_KEY` (PowerShell: `setx OPENAI_API_KEY <key>`; for session only use `$env:OPENAI_API_KEY = '<key>'`)
6. Optional: if using the HTTP adapter, install Node 18+ and run `npm install` in `tools/llm_adapter/`

## Verification Flow
- Dry-run infrastructure check: `python tools/test_expert_system.py`
- Python-only demo (direct OpenAI): `python tools/python_expert_debate.py`
- Adapter smoke: `python tools/start_expert_debate.py` (starts adapter, initializes experts, executes a debate round)
- Run the broader pytest suite when modifying shared libraries: `python -m pytest -q`

## Role-Specific First Week Actions
### System Architect
- Review personas under `intake/ai_experts/` (especially `intake_structuring_agent.md`) to confirm responsibilities and gaps
- Deep-read `docs/Chrystallum_SysML_Block_Definitions.md` and align debate prompts with current architecture decisions
- Validate that scope, milestones, and risks stay synchronized with generated debate outputs; update `docs/SDLC_Expert_Debate_Summary.md` once the API model issue is resolved
- Draft an architecture change log capturing assumptions, open interface questions, and SysML v2 modeling priorities

### Lead Developer
- Stand up the Python-only debate flow; confirm experts return valid JSON and note any schema drift
- Validate the guardrails and automation commands in `intake/ai_experts/intake_structuring_agent.md` so intake updates stay policy-compliant
- Resolve the `model_not_found` (HTTP 403) errors logged in `docs/SDLC_Expert_Debate_Summary.md` by switching to an accessible model (e.g., `gpt-4o-mini` or your organization's provisioned model ID) inside `tools/python_expert_debate.py` and `tools/minimal_expert_debate.py`
- Normalize console glyphs (the current decorative characters render as mojibake on Windows) to keep logs legible
- Expand automated coverage around debate consensus logic (`tools/minimal_expert_debate.py`) and add fixtures for new artifacts as they appear in `intake/`

## Known Risks & Follow-Ups
- **Model Access**: OpenAI project `proj_zsBBVeSxc1MunoV5yGAVAgih` cannot reach `gpt-4`; update configuration to a permitted model or request access
- **Persona Drift**: Personas are Markdown only; consider extracting structured metadata (YAML front matter) to support validation and tooling
- **Adapter Maintenance**: Node adapter is optional but untested recently; schedule a combined Python + adapter integration test before relying on it for production debates
- **Data Volume**: SysML block definitions exceed 18 KB; monitor token usage and chunking strategy when feeding large artifacts to models

## Communication & Documentation
- Keep this guide, `docs/Expert_Debate_Minimum_Stack_Ready.md`, and `handoff/chrystallum_session_handoff_v20250920_final.md` updated as ownership transfers
- Record debate outcomes or consensus exports in `docs/` or `exports/` with timestamps to preserve traceability
- Use repository discussions or issues to log model configuration changes, persona revisions, and debate workflow adjustments
