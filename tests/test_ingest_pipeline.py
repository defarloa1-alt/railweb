import os
import subprocess
import sys


def test_ingest_dry_run_no_files(tmp_path):
    # Run ingest pipeline in dry-run mode against an empty temp path. It should succeed (exit 0).
    py = sys.executable
    cmd = [py, "-m", "tools.ingest_pipeline", "--dry-run", "--path", str(tmp_path)]
    res = subprocess.run(cmd, capture_output=True)
    assert res.returncode == 0, f"ingest pipeline failed: {res.stderr.decode()}"


def test_discover_intake_folder_exists():
    # The repo should have an 'intake' folder per project layout
    assert os.path.isdir(os.path.join(os.getcwd(), "intake"))
