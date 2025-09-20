# Development guide

Quick steps to run debate demos and tests locally.

1. Activate the repository venv (Windows):

```powershell
C:/dev/railweb/.venv/Scripts/Activate.ps1
```

2. Install dependencies (if not done):

```powershell
C:/dev/railweb/.venv/Scripts/python.exe -m pip install -r requirements.txt -r test-requirements.txt
```

3. Start mock adapter (in separate terminal):

```powershell
C:/dev/railweb/.venv/Scripts/python.exe tools/debate/mock_adapter.py
```

4. Run the in-process demo runner:

```powershell
C:/dev/railweb/.venv/Scripts/python.exe tools/debate/run_real_debate_inproc.py
```

5. Run tests (includes integration test that starts mock adapter in-process):

```powershell
C:/dev/railweb/.venv/Scripts/python.exe -m pytest -q -s
```

Notes
- Use `tools/debate/dev/` for local helper scripts and experimental runners. Keep production code in `tools/debate/`.
