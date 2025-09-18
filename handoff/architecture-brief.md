---
title: Architecture Brief (railweb - Readwise→Audio prototype)
generated: 2025-09-18
---

## Overview

This brief summarizes the architecture-relevant items required by the Architect to support the Readwise→Audio prototype handoff.

## Capabilities

- Content Ingestion (Readwise highlights)
- Script Synthesis (LLM)
- Audio Synthesis (ElevenLabs, disabled by default)
- Artifact Stitching (ffmpeg)

## Interfaces / Contracts

- OPENAI API
  - Env: `OPENAI_API_KEY`
  - Model: configurable via `OPENAI_MODEL` (default `gpt-4o`)
  - Contract: LLM responses SHALL be valid JSON with keys `script` and `show_notes`.

- ElevenLabs API
  - Env: `ELEVENLABS_API_KEY`
  - Usage gated by `audio_enabled` control.

- Filesystem
  - Prototype working directory: `prototype/readwise_audio`
  - Artifacts: `out_audio.metadata.json`, segment audio files, `out_audio.mp3`

- ffmpeg
  - Required for stitching. Input: list of segment file paths. Output: `out_audio.mp3`.

## Quality Scenarios / NFRs

- Traceability: segment→source traceability stored in `out_audio.metadata.json`.
- Safety: audio synthesis disabled by default; operator must enable.
- Observability: debug UI (`provenance_viewer.html`) for ad-hoc inspection.
- Resilience: retry/backoff for external API calls (LLM, ElevenLabs). Default: 3 attempts, backoff starting at 0.5s.

## Artifacts & Data

- `out_audio.metadata.json` (primary artifact for validation)
- `debug_ui/provenance_viewer.html`

## Gaps & Risks

- No retention policy for generated artifacts.
- No S3/PR publishing contract (future work).
- LLM JSON fragility — need schema enforcement and tests.

## Recommended Next Steps for Architecture

1. Define a small JSON Schema for LLM output and validate at the LLM boundary.
2. Define artifact retention & publishing policy (human gate required).
3. Define rate-limit & retry policy for network calls across the architecture.
