# Agent Push Workflow (human-in-the-loop)

This document describes the recommended safe workflow for using GPT agents (local, hosted, or orchestrated via n8n/webhooks) to produce planning, requirements, and architecture artifacts for the `railweb` repository.

High-level flow

1. Planner run: An agent (orchestrated via n8n or run locally) produces a proposed planning artifact and writes a run bundle under `runs/<run-id>/` (or uploads a proposal to a PR). The run bundle MUST include provenance metadata (see `provenance_schema` in `intake/agent_operational_contract.yaml`).
2. Planner review: A human planner reviews the proposal and, if acceptable, adds an approval block to the run metadata (`push_authorized_by`). Approval can be recorded in the run metadata file or in the PR description. The planner may also make small edits in `intake/` directly in VS Code.
3. Requirements stage: If the planner approves, the run or PR is forwarded to Requirements (via n8n webhook or manual hand-off). The Requirements reviewer inspects the proposed requirement rows, provenance, and conflict reports. If acceptable, Requirements may also add their approval block.
4. Architecture stage: The combined approved planning+requirements artifacts are forwarded to Architecture. The architect reviews and may request changes, or add an approval block.
5. Final human push: After the necessary approvals (planner, requirements, architect) are recorded in `runs/<run-id>/meta.yaml` or PR front-matter (see example below), a human operator using VS Code (or an approved automation with a short-lived token) performs the final commit and push to `feature/railweb-mvp`.

Example approval metadata (place under `runs/<run-id>/meta.yaml` or in PR front-matter):

```yaml
run_id: example_run_20250918
provenance:
  source:
    id: example_agent_run_20250918
    title: "Example planning run"
    date: 2025-09-18
    url: "runs/example_run/meta.yaml"
  confidence: 0.8
  rounding_rule: "N/A"

approvals:
  planner:
    name: "alice@example.com"
    timestamp: "2025-09-18T16:20:00Z"
    note: "Reviewed planning updates; OK to proceed to requirements."
  requirements:
    name: "bob@example.com"
    timestamp: "2025-09-18T16:40:00Z"
    note: "Reviewed requirement rows; no conflicts."
  architecture:
    name: "carol@example.com"
    timestamp: "2025-09-18T17:00:00Z"
    note: "Architecture review complete."

push_authorized_by:
  name: "dave@example.com"
  timestamp: "2025-09-18T17:05:00Z"
  reason: "Final review passed — ready to commit to feature/railweb-mvp"
```

Notes on n8n/webhook integration

- Orchestrate runs using n8n flows that call your agent endpoint, place outputs into `runs/<run-id>/`, then send a webhook to the assigned reviewer.
- Reviewers receive the webhook and can either:
  - Click a secure link to approve in a simple web UI (which writes the approval into the run metadata), or
  - Manually edit `runs/<run-id>/meta.yaml` in the repo and add the approval block (then open a PR).
- Do NOT grant broad long-lived tokens to the agent. Use short-lived tokens for automated steps and a GitHub App with minimal scopes for any automation that must push.

Minimal checklist before pushing to `feature/railweb-mvp`

- [ ] `runs/<run-id>/meta.yaml` exists
- [ ] `provenance.source.*` fields are present
- [ ] `approvals` includes required signoffs (planner, requirements, architecture) per project policy
- [ ] `push_authorized_by` is present and valid
- [ ] CI provenance check passes (provenance fields validated)

If any step fails, the run should remain unmerged and the reviewer should request changes from the agent or make manual edits.

Maintainers may adapt the required approvers list and the minimal checklist to match changes in the intake contract.


Here’s a clear, novice-friendly summary of the **Agent Push Workflow (Human-in-the-Loop)** for the `railweb` repository:

---

### 🧠 What It Is:

A safe, structured process for using GPT agents to generate planning, requirements, and architecture documents — with human reviewers at each step to ensure quality and traceability.

---

### 🔄 High-Level Workflow:

1. **Agent Proposal (Planner Run):**
    
    - An agent creates a planning artifact.
    - It saves the output in `runs/<run-id>/` or uploads it to a pull request (PR).
    - Must include **provenance metadata** (source info, confidence, etc.).
2. **Planner Review:**
    
    - A human planner checks the agent’s proposal.
    - If approved, they add an approval block (`push_authorized_by`) in the metadata or PR.
    - Minor edits can be made directly in VS Code.
3. **Requirements Review:**
    
    - The approved plan is sent to the Requirements reviewer.
    - They inspect requirement rows, provenance, and conflict reports.
    - If satisfied, they add their approval block.
4. **Architecture Review:**
    
    - The combined planning + requirements are reviewed by the architect.
    - They may request changes or approve the bundle.
5. **Final Push:**
    
    - Once all approvals are recorded in `meta.yaml` or PR front-matter,
    - A human (or approved automation with a short-lived token) pushes the commit to `feature/railweb-mvp`.

---

### ✅ Approval Metadata Example:

Stored in `meta.yaml` or PR description:

```yaml
approvals:
  planner: { name, timestamp, note }
  requirements: { name, timestamp, note }
  architecture: { name, timestamp, note }

push_authorized_by: { name, timestamp, reason }
```

---

### 🔗 n8n/Webhook Integration:

- Use **n8n** to run agents and notify reviewers via webhook.
- Reviewers can:
    - Approve via a secure web UI, or
    - Manually edit `meta.yaml` and open a PR.
- Use **short-lived tokens** for automation — never give agents long-term access.

---

### 🧾 Final Push Checklist:

Before merging to `feature/railweb-mvp`, confirm:

- [ ] `meta.yaml` exists
- [ ] Provenance fields are filled
- [ ] Planner, Requirements, and Architecture approvals are present
- [ ] `push_authorized_by` is valid
- [ ] CI provenance check passes

If anything’s missing, the run stays unmerged until fixed.

---

Want this turned into a visual storyboard or YAML onboarding doc? I can modularize it for your intake pipeline.