"""Shim for referencing the existing top-level `tools` package.

This module provides compatibility helpers while we migrate to a proper
`railweb` package layout.
"""
from importlib import import_module


def __getattr__(name: str):
    # Lazy import from the top-level `tools` package if requested as
    # `railweb.tools_shim.<name>`.
    mod = import_module('tools')
    return getattr(mod, name)


def get_tools_module():
    return import_module('tools')
