# Copilot Coding Agent Pilot


This document describes a small pilot for using GitHub Copilot coding agent safely with the `railweb` repository. It assumes organization owners enable the Copilot coding agent and that repository maintainers will follow the steps below.

## Goals

- Evaluate productivity gains for routine tasks (docs, tests, small refactors).
- Verify provenance, CI checks, and human review provide adequate safety.

## Minimal prerequisites

- GitHub Copilot coding agent enabled at the org or account level (Pro+, Business, or Enterprise).
- Branch protection: require reviews and required status checks (including provenance validator).
- `tools/validate_provenance.py` and `tools/check_push_authorization.py` active in CI and configured as required checks.

## Pilot rules (operational)

- Only repository maintainers may assign issues to Copilot.
- Label an issue `copilot-eligible` before assigning it to Copilot.
- Copilot may only create branches prefixed with `copilot/` (GitHub restriction).
- Copilot PRs require at least one independent reviewer and human approval to run workflows.

## Reviewer checklist for Copilot PRs

1. Confirm the PR branch name starts with `copilot/`.
2. Run/enable CI checks and ensure `tools/validate_provenance.py` passes.
3. Verify the provenance block exists and is accurate for the change (source, confidence, citation where appropriate).
4. Run the test suite and confirm there are no regressions.
5. Check for accidental inclusion of secrets or sensitive files.
6. If satisfied, approve and click "Approve and run workflows" to allow any required Actions to execute.

## Data collection (for pilot evaluation)

- Track time-to-completion for issues assigned to Copilot vs. human-only tasks.
- Count tests added and coverage delta.
- Record iteration count required to reach approved PR.

## Rollout decision

- After 2–4 weeks of the pilot, review metrics and decide whether to broaden Copilot usage, add additional safeguards, or disable the feature.

## Contact & governance

- For questions or incidents, add an issue labeled `copilot-incident` and notify repository maintainers.
