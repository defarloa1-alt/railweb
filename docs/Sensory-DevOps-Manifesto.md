# Sensory DevOps Manifesto

## 🌀 Sensory DevOps Manifesto

For systems that narrate, visualize, and enrich their own execution.

 
### 1. Narratability Over Silence
Every run should leave a trail—not just logs, but stories.
Audio generation isn’t a gimmick; it’s a cognitive interface.
Let the system speak its state, its choices, its provenance.

 
 
### 2. Visual Modularity
Nodes, toggles, and flows should be visible and inspectable.
Even disabled modules deserve representation—because silence is still a state.
n8n, semantic graphs, and dashboards become the choreography of cognition.

 
 
### 3. Opt-In Activation
Default to restraint.
Let users choose when to speak, when to call APIs, when to enrich.
Flags like `--audio` and `--no-dry-run` are not just switches—they’re permissions.

 
 
### 4. Provenance as First-Class Output
Metadata is memory.
Every run should produce a semantic artifact:
 
- Was audio generated?
- What path did it take?
- What highlights were voiced, skipped, or filtered?

 
 
### 5. Multi-Sensory Debugging
Don’t just read logs—listen to them.
Don’t just trace errors—see them pulse in the graph.
Let the system express its state in ways that match human cognition.

 
 
### 6. Enrichment Pipelines as Living Systems
Emitters, pipelines, filters, and stitchers aren’t just code—they’re semantic organs.
Design them for audit, rollback, and expressive output.
Let them evolve, narrate, and adapt.

---

Implementation checklist (project-specific)

- [x] Preserve provenance metadata for highlights (author, title, doc_url, exported_at, checksum). See `prototype/readwise_audio/fetcher.py` and `run_pipeline.py`.
- [x] Make audio opt-in via flags. See `prototype/readwise_audio/run_pipeline.py` (`--audio`, `--no-dry-run`).
- [x] Provide a local provenance inspector. See `prototype/readwise_audio/debug_ui/provenance_viewer.html`.
- [x] Expose filter-first controls to reduce noise and cost. See `prototype/readwise_audio/fetcher.py` and `run_pipeline.py` (`--filter-tags`, `--filter-keywords`, `--max-highlights`).
- [ ] Document NotebookLM guidance and update README (next step).
- [ ] Add optional Google Docs fetcher for Readwise exports (OAuth required).
- [ ] Add cost/token estimator before enabling audio synthesis.

Rationale: this repository's prototype implements the core of a Sensory DevOps approach: explicit, auditable, and opt-in multimodal enrichment with provenance. Keep modules visible in the orchestration layer and make side-effects explicit.

License & authorship

This manifesto file was added by the repository maintainer. Treat it as guidance; adapt as your project and policies require.
