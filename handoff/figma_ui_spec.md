Figma UI spec (placeholder)

Purpose: A minimal UI to review intake PRs, view artifact details (MD + JSON-LD), and approve ingestion to the knowledge graph.

Screens:
- Dashboard: list of pending intake PRs with filters (type, date, author, confidence).
- Artifact detail: shows YAML front-matter, human MD, generated JSON-LD graph preview (node and relations), provenance panel, and raw model output.
- Approve modal: a reviewer can add notes and set `push_authorized_by` before clicking Approve.

Interactions:
- Clicking Approve triggers a GitHub review / adds `approved` label and merges (or signals CI to run ingestion job).
- Graph preview opens a simple node-edge diagram using the JSON-LD sidecar; allow toggling between JSON-LD and graph view.

Design tokens: colors, fonts, and components will be created in Figma proper; this is a short placeholder for dev handoff.
