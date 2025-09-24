import os
import sys
from pathlib import Path


def pytest_configure(config):
    """Ensure the repository root is on sys.path so tests can import `tools`.

    This keeps the lightweight `tools/` directory importable during pytest runs
    without needing to install the package.
    """
    repo_root = Path(__file__).resolve().parents[1]
    repo_root_str = str(repo_root)
    if repo_root_str not in sys.path:
        sys.path.insert(0, repo_root_str)