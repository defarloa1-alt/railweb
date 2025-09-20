# conftest.py
# Ensure the repository root is on sys.path so tests can import `tools.*` when run in CI
import os
import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))
