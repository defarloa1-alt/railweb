# GPT Preview Checklist

Use this checklist when hitting **Preview** in the GPT editor before applying a patch.  
Copy relevant sections into a scratch file to preserve the last session state.

---

## 1. Context / Instructions

- [ ] Copy the full **context block**.
- [ ] Note operational mode (intake/runs folders, schema rules).
- [ ] Note handoff contracts (Planner / Architect).
- [ ] Note custom parsing rules or compliance checks.

---

## 2. UI Shortcuts

- [ ] List all shortcuts currently recognized (e.g., `New run`, `Display requirements`, `Show backlog`, `Planner handoff`, `Architect handoff`, `Show diagram`).
- [ ] Note any export options (`Export table`, `Export backlog`).

---

## 3. Special Modes

- [ ] Record **Display requirements mode** columns.
- [ ] Record **Show backlog mode** columns.
- [ ] Note if CSV export is supported.

---

## 4. Operational Mode

- [ ] Confirm required intake files.
- [ ] Confirm optional intake files.
- [ ] Confirm run folder outputs (`requirements.md`, `nodes.csv`, `edges.csv`, etc.).
- [ ] Check if `latest/` pointer is supported.

---

## 5. Contracts

- [ ] Planner handoff rules (backlog CSV, risks, milestones).
- [ ] Architect handoff rules (architecture brief, NFRs, constraints).

---

## 6. Compliance & Validation

- [ ] ISO/IEC/IEEE 29148 validation rules (clarity, traceability, feasibility).
- [ ] Safety/provenance enforcement (`safety_ack`, provenance front-matter).

---

## 7. New Additions (Patch Delta)

- [ ] Highlight what the new patch will add/change.
- [ ] Compare to previous context after patch is applied.

---

### Notes

Keep a scratch file of each context block before patching. This ensures you always have a rollback point if a patch introduces errors.
