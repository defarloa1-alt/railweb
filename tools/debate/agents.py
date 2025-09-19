from __future__ import annotations
from typing import Any


class EchoAgent:
    def __init__(self, name: str, prefix: str = "") -> None:
        self.name = name
        self.prefix = prefix

    def propose(self, context: Any) -> str:
        return f"{self.prefix}{context}"
