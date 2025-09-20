
# Railweb Approval UI (prototype)

This is a small prototype reviewer UI used to demonstrate a human-in-the-loop approval flow for runs.


Usage (local demo only):

1. Install dependencies:

```powershell
cd tools\approval_ui
npm install
```

1. Start the server:

```powershell
npm start
```

1. Open the server in your browser (for example, `http://localhost:3002`) and enter a `runId` that exists under `runs/`.

Notes:

- This is a demo-only scaffold. It writes `push_authorized_by` directly into `runs/<runId>/meta.yaml`.
- Do not run this in production without adding authentication and authorization.

