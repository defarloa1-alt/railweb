# Pull Request Template for railweb

Summary

-------

Provide a one-line summary of the change and reference the relevant milestone from `intake/milestones.csv` (e.g., "M3 Scale Converters MVP").

GPT Preview Reminder
--------------------

- If this PR includes changes to GPT or automation-related files (see `handoff/`, `mirror/`, `intake/`, `tools/`), attach or update `handoff/GPT-preview-checklist.md` with the last session context before merging.

PR Summary

- [ ] **Three-line architecture summary included**
- [ ] **List of new/updated commands provided**
- [ ] **Citations/sources for any new spec values**
- [ ] **Safety gating for any live-control changes**
- [ ] **Manual test procedure for hardware-related PRs**

## Details

**Architecture/Design Change:**

<!-- 3-line summary here -->

**Commands Added/Updated:**

<!-- List commands or interfaces -->

**Citations/Source Docs:**

<!-- Reference intake docs, spec files, or other sources -->

**Test Procedure/Safety Notes:**

<!-- Manual test steps or safety validation (for hardware or live systems) -->

What I changed

-------

- Short bullet list of files/areas touched.

Why this change is needed

-------

- Brief rationale and link to intake artifact (e.g., `intake/scope.yml`, `intake/assumptions.yaml`, or a milestone id).

Checklist (required)

-------

- [ ] Citation metadata included for any published/spec values added or modified. Add the source and version/date inline as YAML front-matter or a nearby CODE comment. Example:

  ```yaml
  # source: NMRA RP-##
  # source_url: https://example.org/nmra-rp-##
  # source_version: 2021-05-01
  value: 2.54
  ```

- [ ] Safety gating reviewed for any live-control, DCC programming, or automation changes.

  - If the change affects hardware control: include an explicit opt-in/default-off behavior and a short text warning shown in the UI (or the code comment where the activation happens).

- [ ] Manual hardware test checklist included (if relevant). Minimum items:

  - Hardware tested: model/command-station used (make/model/firmware).

  - Steps to reproduce (one-line summary).

  - Expected safe behavior and rollback steps.

- [ ] Milestone referenced (e.g., `M4A Real-time Control MVP`) if the change is part of a milestone.

Sensory DevOps (non-blocking, recommended)

- [ ] If this PR adds or changes observable outputs (audio, visual nodes, persistent artifacts), confirm:
  - [ ] The feature is opt-in / disabled by default where appropriate (e.g., `--audio` or a disabled node in the flow).
  - [ ] Provenance metadata is produced for generated artifacts (see `prototype/readwise_audio` for an example).
  - [ ] A brief cost/impact note is included if external APIs or paid TTS services will be called.
  - [ ] A debug or inspection path is available (e.g., `debug_ui/provenance_viewer.html`) or noted.

Testing notes

-------

- Describe quick local test steps taken (or "N/A" if not applicable). For code touching converters, include at least one hand-checked example and expected output.

Additional notes

-------

- If this PR touches licensing or published standards text, prefer linking to the authoritative source and include a short attribution note.
