@echo off
REM Helper to run the repository venv Python if present, else fall back to py -3
SET REPO_ROOT=%~dp0\..
SET VENV_PY=%REPO_ROOT%\.venv\Scripts\python.exe
IF EXIST "%VENV_PY%" (
  "%VENV_PY%" %*
) ELSE (
  py -3 %*
)
