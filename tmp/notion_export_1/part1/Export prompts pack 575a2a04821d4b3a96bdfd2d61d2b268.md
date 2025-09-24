# Export prompts pack

### Purpose

Reusable prompts to regenerate CSV/Markdown/JSON/YAML artifacts from Notion.

---

### 1) Canonical hierarchy table

“Create a table with columns node_id, parent_id, title, stage_owner, summary. Capture every heading in this document (H1‑H14) as one row and keep the numbering (e.g. 3.1.2) as the node_id. Verify parent_id is the immediate parent (e.g. 3.1 for 3.1.2).”

### 2) Slice a stage page with YAML front matter

“Split the current section into a standalone page with front matter and save it.”

Front matter template:

```yaml
---
stage_id: "<id>"
title: "<Stage name>"
owner: "<Role>"
summary: "<One-paragraph summary>"
prerequisites: ["<parent ids>"]
deliverables: ["<deliverable A>","<deliverable B>"]
---
```

### 3) Footnotes lookup table

“Extract every footnote into a table with columns node_id, footnote_text, reference_type.”

### 4) Tool matrix

“Produce a table where each row is a tool with columns tool_name, purpose, primary_artifacts, rationale. Include one row for each tool mentioned.”

### 5) Stage JSON

“Emit the key data above as a JSON object with stage_id, title, description, inputs, outputs, success_metrics.”

### 6) LangGraph node specs (YAML)

“Write a YAML snippet for each major stage showing node_id, type: langgraph_node, entry_conditions, exit_conditions, responsible_role, downstream_nodes.”

---

Notes

- After generation, export as CSV/MD/JSON/YAML and commit under docs/framework/ in your repo.
- Keep Notion as the curation layer; Git as the system of record for exported artifacts.