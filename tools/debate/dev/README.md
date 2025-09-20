Development helpers for `tools/debate`.

This folder contains demo and integration helper scripts used during local development and testing. Files here are not required for production and can be moved or removed as needed.

Included helpers (dev versions):
- `mock_adapter.py` (copy or run original from `tools/debate/mock_adapter.py`)
- `run_real_debate_inproc.py` (run the example debate runner in-process)

How to run locally:
1. Activate venv
   - Windows: `C:/dev/railweb/.venv/Scripts/activate`
2. Start mock adapter (if needed):
   - `C:/dev/railweb/.venv/Scripts/python.exe tools/debate/mock_adapter.py`
3. Run the inproc runner:
   - `C:/dev/railweb/.venv/Scripts/python.exe tools/debate/run_real_debate_inproc.py`
