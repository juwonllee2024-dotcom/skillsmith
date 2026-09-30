from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class CanonicalEvent:
    event_id: str
    session_id: str
    source: str
    line: int
    kind: str
    name: str
    status: str | None
    payload: dict[str, Any]
