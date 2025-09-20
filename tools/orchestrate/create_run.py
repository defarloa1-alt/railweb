from pathlib import Path
import shutil
import uuid
import subprocess
import yaml
import sys

REPO = Path(__file__).resolve().parents[2]
RUNS = REPO / 'runs'
EXAMPLE = REPO / 'runs' / 'example_run' / 'meta.example.yaml'


def create_run(run_id: str | None = None) -> int:
    run_id = run_id or f"run-{uuid.uuid4().hex[:8]}"
    dest = RUNS / run_id
    dest.mkdir(parents=True, exist_ok=False)
    # copy example meta
    if EXAMPLE.exists():
        shutil.copy(EXAMPLE, dest / 'meta.yaml')
    else:
        (dest / 'meta.yaml').write_text('run_id: '+run_id)

    # run debate (inproc runner ensures sys.path)
    runner = REPO / 'tools' / 'debate' / 'run_real_debate_inproc.py'
    try:
        proc = subprocess.run([sys.executable, str(runner)], capture_output=True, text=True, timeout=20)
        out = proc.stdout + proc.stderr
        (dest / 'results.txt').write_text(out)
        return 0
    except Exception as e:
        (dest / 'results.txt').write_text(str(e))
        return 2


if __name__ == '__main__':
    rid = sys.argv[1] if len(sys.argv) > 1 else None
    rc = create_run(rid)
    print(f"create_run returned {rc}")
    sys.exit(rc)
