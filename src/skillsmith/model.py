from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class CanonicalEvent:
    event_id: str
    event_type: str
    payload: Mapping[str, Any]
    session_id: str
    source: str
    line: int
