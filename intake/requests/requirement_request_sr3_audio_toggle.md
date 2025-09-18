---
uid: d2f9e7b2-3a4e-4f3f-a8b6-1a2b3c4d5e6f
type: block
block_type: requirement_request
system: railweb
author: AD
block_name: SR-3 Audio toggle
in_port: User
out_port: Requirements Manager
priority: high
impact: important
source: intake
source_path: "intake/requests/requirement_request_sr3_audio_toggle.md"
date: 2025-09-18
---

# Use case: Audio generation is opt-in

## Summary

Mission control SHALL present a control named `audio_enabled` whose default value is false. This control enables or disables audio synthesis at runtime and must be persisted with the session preferences.

## Primary flow (happy path)

1. The operator opens Mission Control.
2. The operator sees an `audio_enabled` control (checkbox or toggle) defaulted to `false`.
3. The operator enables audio by toggling `audio_enabled` to `true`.
4. The operator confirms any additional gating prompts required for hardware or external API calls.

## Non-goals / constraints

- This requirement does not mandate a particular UI framework or storage backend for preferences.
- Enabling audio does not imply automatic publishing of artifacts; publishing must be gated separately.

## Acceptance criteria

- `audio_enabled` control exists in Mission Control and defaults to `false`.
- Enabling the control is required before any real audio provider calls are made.
- The control state is persisted across the operator session.

## Implementation notes / suggestions

- Map `audio_enabled` to the prototype `--audio` flag and to `ELEVENLABS_API_KEY` presence checks in the runner.
- Ensure UI shows safety and provenance reminders when enabling audio.

## Provenance

- Created from advisor note (author: AD) on 2025-09-18.
