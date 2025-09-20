import subprocess
import sys
import time
from pathlib import Path

here = Path(__file__).resolve().parents[2]
python = str(Path(here) / '.venv' / 'Scripts' / 'python.exe')
log = Path(here) / 'mock_adapter_run.log'
with open(log, 'wb') as f:
    proc = subprocess.Popen([python, str(Path(here) / 'tools' / 'debate' / 'mock_adapter.py')], stdout=f, stderr=f)
    time.sleep(1.0)
    f.flush()
print('started pid=', proc.pid)
print('log size=', log.stat().st_size)
print('log head:')
with open(log, 'r', encoding='utf-8', errors='ignore') as f:
    for _ in range(20):
        line = f.readline()
        if not line:
            break
        print(line.rstrip())
print('done')
