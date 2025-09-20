Create Run API

- POST /internal/create_run
  - Requires Authorization Bearer token matching env `RAILWEB_API_TOKEN`
  - Body JSON: { run_id?: string, meta?: object }
  - Returns 202 with `status_url` while the run is processed in background

- GET /internal/create_run/<run_id>
  - Returns status and results path (if available)

Notes:
- Status is persisted in `runs/.runs_status.db` (SQLite) so status survives restarts.
- Example n8n workflow available at `tools/n8n/create_run_example.json`.
