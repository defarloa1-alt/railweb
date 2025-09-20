# Helper PowerShell script to run repo venv python or fall back to py -3
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Join-Path $scriptDir '..'
$venvPy = Join-Path $repoRoot '.venv\Scripts\python.exe'
if (Test-Path $venvPy) {
    & $venvPy @args
} else {
    & py -3 @args
}
