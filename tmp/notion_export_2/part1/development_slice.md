# Pilot exports — Development slice (staging)

### Instructions

- Use the sections below to generate machine-readable artifacts for the pilot (A–E).
- Copy each code block to files under docs/framework/ in your repo.

---

### A) Canonical hierarchy CSV (Development slice)

- Prompt to run in your outline page:
    - Create a table with columns node_id, parent_id, title, stage_owner, summary. Capture every heading in this document (H1‑H14) as one row and keep the numbering (e.g., 3.1.2) as node_id.
    - Verify parent_id matches the immediate parent (e.g., 3.1 for node 3.1.2).

Sample CSV (edit to match your outline):

```
node_id,parent_id,title,stage_owner,summary
3, ,Development Capability hub,Product Manager,"Lifecycle hub for Stage: Development"
3.1,3,Minimum Viable Product Development,Product Manager,"Anchor capability for Development"
3.1.1,3.1,MVP Feature Prioritization,Product Manager,"Prioritize features for MVP"
3.1.2,3.1,Baseline Functionality,Tech Lead,"Checklist of must-have behaviors"
3.1.3,3.1,Core Feature Identification,Tech Lead,"Identify core features for primary flows"
3.1.4,3.1,Must-Have Feature Analysis,Product Manager,"Must-have vs nice-to-have criteria"
```

---

### B) Stage page (Markdown with YAML front matter)

Target file: docs/framework/stage_[3.md](http://3.md)

```markdown
---
stage_id: "3"
title: "Development"
owner: "Product Manager"
summary: "Decide scope and entry criteria; execute MVP slice; prepare for launch."
prerequisites: ["2"]
deliverables: ["MVP scope & priorities","Baseline Functionality checklist","Prototype validation report"]
---

# Development

- See hub: <mention-page url="[https://www.notion.so/6640713c709642398082264aff69843a"/](https://www.notion.so/6640713c709642398082264aff69843a"/)>
- Key practices: <mention-page url="[https://www.notion.so/a8bf19555dab4a32917794e5baff86bb"/](https://www.notion.so/a8bf19555dab4a32917794e5baff86bb"/)>, <mention-page url="[https://www.notion.so/c944d92bf76e451398d66e5a9529c5b4"/](https://www.notion.so/c944d92bf76e451398d66e5a9529c5b4"/)>, <mention-page url="[https://www.notion.so/d41b926916a4419985707f05a4d07e24"/](https://www.notion.so/d41b926916a4419985707f05a4d07e24"/)>, <mention-page url="[https://www.notion.so/47c7bfd0be7e40ccbc70aef8e7b33aa3"/](https://www.notion.so/47c7bfd0be7e40ccbc70aef8e7b33aa3"/)>
```

---

### C) Tool matrix (CSV)

Target file: docs/framework/tool_matrix.csv

```
tool_name,purpose,primary_artifacts,rationale
VS Code,Code authoring & reviews,Source code; PRs,"Developer IDE and reviews"
LangGraph Studio,Workflow design & testing,Graphs; pipelines,"Design and validate agent workflows"
GitHub Actions,CI/CD,Builds; test reports; release tags,"Automate builds and releases"
Notion,Planning & taxonomy,Practices; checklists; hubs,"Curated human interface and lineage"
LangSmith,Observability,Runs; traces; logs,"Trace and debug LLM/agent runs"
```

---

### D) Stage JSON (Development)

Target file: docs/framework/stage_3.json

```json
{
  "stage_id": "3",
  "title": "Development",
  "description": "Decide scope and entry criteria; implement MVP slice; validate and prepare for launch.",
  "inputs": ["Prioritized requirements","Designs","Environment readiness"],
  "outputs": ["MVP scope & priorities","Baseline Functionality checklist","Validated prototype"],
  "success_metrics": ["Critical flows implemented","Prototype validated with target users","Readiness criteria met"]
}
```

---

### E) LangGraph node spec (YAML)

Target file: docs/framework/langgraph_nodes.yaml

```yaml
- node_id: "3"
  type: langgraph_node
  title: Development
  entry_conditions:
    - Stage "Validation" complete
  exit_conditions:
    - MVP scope locked
    - Prototype validated
  responsible_role: Product Manager
  downstream_nodes: ["4"]
- node_id: "3.1"
  type: langgraph_node
  title: Minimum Viable Product Development
  entry_conditions:
    - Development started
  exit_conditions:
    - Baseline functionality checklist approved
  responsible_role: Tech Lead
  downstream_nodes: ["3.2","4"]
```

---

Checklist

- [ ]  Validate CSV node_ids against your outline
- [ ]  Commit all files under docs/framework/
- [ ]  Share PR link for review