# railweb LLM adapter

Small Express adapter to route UI requests to OpenAI / Perplexity (mock-capable).

Usage

1. Install dependencies:

```powershell
cd tools/llm_adapter
npm install
```

1. Create `.env` file (see `.env.example`) and set keys for providers you want to use.

1. Start the adapter:

```powershell
npm start
```

Endpoints

- POST /api/llm/summarizeRun
- POST /api/llm/explainChange

Provider selection

Use `DEFAULT_PROVIDER` env var or pass `?provider=openai` or `?provider=perplexity` on the endpoint call.

Notes

- This is a prototype scaffold. The Perplexity provider is a placeholder and requires exact API docs/keys to wire production calls.
- Responses include `provenance_suggestions` and `citations` so the UI can pre-fill `runs/<run-id>/meta.yaml`.
