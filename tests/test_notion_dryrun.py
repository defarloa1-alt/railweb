import subprocess
import sys
from pathlib import Path


def test_notion_dry_run_writes_table(tmp_path):
    out = tmp_path / "notion_out.md"
    # create the file first — the script expects the output path to exist in dry-run
    out.write_text("", encoding="utf-8")
    py = sys.executable
    script = Path(".github/scripts/notion_to_md.py")
    assert script.exists(), "Notion script not found"
    cmd = [py, str(script), "--dry-run", "--out", str(out)]
    res = subprocess.run(cmd, capture_output=True)
    assert res.returncode == 0, f"notion script failed: {res.stderr.decode()}"
    text = out.read_text(encoding="utf-8")
    assert "<!--TABLE:START-->" in text and "<!--TABLE:END-->" in text
    assert "|" in text, "Expected markdown table pipe characters in output"
