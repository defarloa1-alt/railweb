# AI Assistant Handover

Date: 2025-09-18

## Purpose

This document captures the work performed by the AI assistant during the planning and governance
session for the `railweb` repository. It summarizes created and modified artifacts, the human-in-the-loop
workflows, validation tooling, and recommended next steps for maintainers.

## Summary of actions

1. Read intake artifacts and repository layout to understand constraints and goals.
2. Created governance and policy artifacts for GPT agents (requirements & planning policies).
3. Added a provenance validator and CI workflow to enforce provenance on intake changes.
4. Produced a SysML run and packaged the outputs as a tracked artifact in `intake/architecture/` (zip + sha256).
5. Snapshot local workspace into a WIP branch and reset the working tree for a clean PR workflow.
6. Designed and added an approval workflow (planner → requirements → architecture) and example metadata for `runs/`.
7. Designed a Neo4j-backed presentation layer and sync strategy for intake/run artifacts.
8. Added documentation and example files to support a n8n/webhook-driven human-in-the-loop approval flow.

## Files added or modified

The following is a non-exhaustive list of files the assistant created or edited during the session. Use
`git log` / `git show` for exact commits.

1. `intake/agent_operational_contract.yaml` (existing but referenced heavily)
2. `intake/gpt_requirements_agent_policy.yaml` (policy for requirements agent)
3. `intake/gpt_planning_agent_policy.yaml` (newly added planning policy)
4. `intake/AGENT_PUSH_WORKFLOW.md` (workflow doc describing approvals, push_authorized_by)
5. `runs/example_run/meta.yaml` (example metadata showing provenance and approvals)
6. `intake/architecture/railweb-20250918-ops01.zip` (tracked run artifact)
7. `intake/architecture/railweb-20250918-ops01.zip.sha256` (checksum)
8. `tools/validate_provenance.py` (provenance validator)
9. `tools/check_push_authorization.py` (CI helper that enforces the push gate)
10. `tools/llm_adapter/` (Express scaffold + OpenAI/Perplexity provider drivers)
11. `.github/workflows/provenance-check.yml` (CI workflow to run validator + push auth check)
12. `.gitignore` (updated to ignore `intake/perplexity.txt`)

## Where to review changes

The WIP snapshot branch `wip/save-current-changes-20250918153850` contains the full working set of local
changes if you need to inspect or cherry-pick files.

## How to run the provenance validator locally

The repository includes `tools/validate_provenance.py`. To validate one or more files locally:

```powershell
python tools/validate_provenance.py intake/gpt_planning_agent_policy.yaml
```

## What changed recently (delta since last handover)

- Added `tools/check_push_authorization.py`: a CI helper that enforces the push gate defined in
	`intake/agent_operational_contract.yaml` (the `push_authorized_by` field by default). The provenance workflow
	now runs this script after validation.
- Scaffolding: `tools/llm_adapter/` was added to prototype an Express-based LLM adapter (OpenAI + placeholder
	Perplexity drivers). See `tools/llm_adapter/README.md` for usage.
- Security: `.gitignore` was updated to ignore `intake/perplexity.txt`. The exposed Perplexity key was removed
	from the working tree; immediate key rotation was recommended.

## How to run the push-authorization check locally

The helper `tools/check_push_authorization.py` enforces the push gate defined in
`intake/agent_operational_contract.yaml` (the `push_authorized_by` field by default). To run it locally:

```powershell
python tools/check_push_authorization.py <changed-file1> [<changed-file2> ...]
```

Behavior summary:

1. If no changed files are under `intake/` or `runs/`, the script skips and exits 0.
2. If there are intake/runs changes, the script searches for `runs/*/meta.yaml` and `intake/*/meta.yaml` (and
	 `intake/meta.yaml`) for the configured authorization field. If none contain the authorization entry the script
	 exits non-zero and CI will fail the PR.

## Security / secret remediation (summary and next steps)

1. A Perplexity API key was briefly present in `intake/perplexity.txt`. Remediation performed in this session:
	 - The file was removed from the working tree (if present) and added to `.gitignore`.
	 - The user rotated the secret immediately (recommended practice).
2. If you require absolute removal from Git history, coordinate with repository admins and schedule a history-rewrite
	 using `git filter-repo` or BFG Repo-Cleaner; note this is disruptive and requires all collaborators to re-clone or rebase.

## How to start a new thread (recommended minimal steps)

If you want to start a new discussion/work thread (for example, a new planning run or an architectural review), follow these steps:

1. Create a new run folder under `runs/` with a short, unique id (timestamp or date-based is fine):

```powershell
mkdir runs\\railweb-<YYYYMMDD>-<shortid>
```

2. Add a `meta.yaml` with required provenance fields and optionally the `push_authorized_by` field if you want to allow
	 pushing changes from this run.

Example `runs/railweb-20250918-ops02/meta.yaml` (minimal):

```yaml
source:
	id: railweb-20250918-ops02
	title: "Architecture run - followup"
	date: 2025-09-18
	url: ""
confidence: high
rounding_rule: "none"
# push_authorized_by: alice@example.com  # add when an authorized reviewer signs off
```

3. Add any outputs (documents, exports, archives) under the run folder and commit the run.

4. Open a pull request that changes `intake/` or `runs/` as needed. The provenance CI and push-authorization check will run on PRs touching those paths.

5. To authorize a push from this run, add a `push_authorized_by` entry to the `meta.yaml` (or use the review UI when one exists). The CI will accept the PR when the meta includes an authorized value.

## Prioritized next steps (recommended)

1. Enable branch-protection on the main branch and make the provenance CI workflow a required status check.
2. Add unit tests for `tools/check_push_authorization.py` and `tools/validate_provenance.py` (sample meta files).
3. Finish the approval UI prototype (Express + static pages) so reviewers can sign off and automatically inject `push_authorized_by` into run meta files via a controlled workflow.
4. If you need the Perplexity key entirely removed from history, schedule a git-history cleanup with the team.
5. Wire the Perplexity provider in `tools/llm_adapter/` using the official API and ensure keys are stored in CI/secret stores (not in files).

## Contact / follow-up

If you'd like, I can:

- Create unit tests for the new CI helpers and wire them into the repository test suite.
- Scaffold the approval UI and demonstrate signing off a run (local dev server + demo flows).
- Draft a small PR template that requires authors to indicate whether runs/intake changes include `push_authorized_by`.

I pushed all active changes to `feature/railweb-mvp`. Tell me which next step you want me to do first and I will mark it in-progress and implement it.
