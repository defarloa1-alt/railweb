"""Scan repository files for git merge conflict markers and exit with non-zero status if any are found.

Usage: python tools/check_conflicts.py [path1 path2 ...]
If no paths are provided the script scans the repository root recursively.
"""
import sys
from pathlib import Path

CONFLICT_MARKERS = ["<" * 7, "=" * 7, ">" * 7]


def scan_paths(paths):
    repo = Path(__file__).resolve().parents[1]
    targets = [Path(p) for p in (paths or [str(repo)])]
    issues = []
    for t in targets:
        if t.is_file():
            for i in scan_file(t):
                issues.append((t, i))
        else:
            for p in t.rglob("*"):
                if p.is_file():
                    for i in scan_file(p):
                        issues.append((p, i))
    return issues


def scan_file(path):
    out = []
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return out
    for n, line in enumerate(text.splitlines(), start=1):
        for m in CONFLICT_MARKERS:
            if m in line:
                out.append((n, line.strip()))
    return out


if __name__ == "__main__":
    paths = sys.argv[1:]
    issues = scan_paths(paths)
    if issues:
        print("Merge conflict markers found:")
        for p, (ln, txt) in issues:
            print(f"{p}:{ln}: {txt}")
        sys.exit(2)
    print("No merge conflict markers found.")
    sys.exit(0)
