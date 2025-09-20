```markdown
# Railweb Agent Handoff v20250920

This handoff documents the latest changes landed on 2025-09-20 and provides pointers to
new/updated tooling introduced by the assistant.

Summary of changes
------------------
- Orchestrator: added `tools/orchestrate/github_integration.py` (GitHub Issues fallback)
  and updated `tools/orchestrate/linear_integration.py` to use the fallback when `LINEAR_API_KEY`
  is not present.
- Notion materializer: `.github/scripts/notion_to_md.py` and `.github/workflows/update-table.yml` were
  added to support materializing a Notion database into `README.md` (dry-run + debug logging).
- Tests: unit tests added/updated to cover orchestrator flows and the fallback behavior (`tests/test_linear_integration.py`).

How to run/verify
-----------------
1. Linear path (requires env vars):
   - Set `LINEAR_API_KEY` and optionally `LINEAR_TEAM_ID`.
   - Call `tools/orchestrate/linear_integration.create_issue_for_run(run_id, meta)` from a script or REPL.

2. GitHub fallback (no Linear key):
   - Set `GITHUB_TOKEN` and `GITHUB_REPOSITORY` (or pass `repo` and `token` explicitly).
   - Call the same entrypoint; when `LINEAR_API_KEY` is absent the code will create a GitHub issue and return an id like `GH#123`.

3. Notion materializer (dry-run):
   - Run `.github/scripts/notion_to_md.py --dry-run --out sample.md --sample .github/scripts/sample_notion_response.json`
   - To run live, set `NOTION_TOKEN` and `NOTION_DB_ID` and run without `--dry-run` (note: environment gating and safety rules apply).

Notes & provenance
------------------
- The changes were merged via PR #2 on 2025-09-19/20 and include merge-conflict resolutions that preserved existing workflows.
- For any run that creates issues, ensure the meta includes provenance information. See `tools/orchestrate/meta_schema.json` for schema.

Contact
-------
Reach the repository maintainer via the repo issues or the `intake/contacts` entry for questions about handoff details.

```
