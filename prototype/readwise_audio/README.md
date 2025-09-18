Readwise → Audio prototype

This prototype demonstrates a minimal pipeline to fetch highlights from Readwise (or other saved highlights), generate a concise host script using an LLM, synthesize audio using a TTS provider, and stitch segments with ffmpeg.

It is intentionally small and meant for local/dry-run testing. It does not automatically upload artifacts or create PRs.

Environment variables

- READWISE_TOKEN (optional) - to fetch Readwise highlights via API
- OPENAI_API_KEY - required for LLM prompt (or set DRY_RUN=1 to skip LLM API calls)
- ELEVENLABS_API_KEY (optional) - for ElevenLabs TTS
- AWS_* envs (optional) - if you enable S3 upload in future
- DRY_RUN=1 - skip network calls and generate local sample outputs

Files

- fetcher.py - fetches sample highlights (or uses Readwise API when configured)
- llm_prompt.py - builds a prompt and calls the LLM (OpenAI)
- tts.py - wrapper that calls TTS provider (ElevenLabs mock in DRY_RUN)
- stitcher.py - creates ffmpeg commands to stitch audio files
- run_pipeline.py - small CLI to run the prototype end-to-end in dry-run mode
- requirements.txt - python deps (requests, openai)

Debug UI

- debug_ui/provenance_viewer.html - small local HTML page to inspect `out_audio.metadata.json`. Open it in a browser and load the JSON file produced by the run to view segment → source mappings.

Mission-control UX notes

- The visual n8n flow should keep the audio module visible but disabled by default. Operators must explicitly enable audio synthesis.
- Add a "filter-first" step so operators can prune highlights before any LLM or TTS calls.
- The debug UI above is useful during demos: it helps map segments back to source highlights and shows checksums and exported dates.

How to run (DRY RUN recommended):

1. Install deps

```powershell
python -m pip install -r prototype/readwise_audio/requirements.txt
```

2. Run dry-run

```powershell
set DRY_RUN=1
python prototype\readwise_audio\run_pipeline.py
```

To run with real APIs, unset DRY_RUN and provide OPENAI_API_KEY and a TTS API key. Review the code before enabling real requests.
