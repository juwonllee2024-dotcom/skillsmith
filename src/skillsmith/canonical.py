from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from typing import Any, Iterable

from .model import CanonicalEvent


def _stable_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def canonicalize_event(raw: dict[str, Any], *, session_id: str, source: str, line: int) -> CanonicalEvent:
    normalized = {
        "session_id": session_id,
        "source": source,
        "line": line,
        "kind": str(raw.get("kind", "event")),
        "name": str(raw.get("name", "")),
        "status": None if raw.get("status") is None else str(raw["status"]),
        "payload": raw.get("payload", {}),
    }
    event_id = hashlib.sha256(_stable_bytes(normalized)).hexdigest()
    return CanonicalEvent(event_id=event_id, **normalized)


def canonical_event_hash(event: CanonicalEvent) -> str:
    return hashlib.sha256(_stable_bytes(asdict(event))).hexdigest()


def canonical_json(events: Iterable[CanonicalEvent]) -> bytes:
    records = [asdict(event) for event in events]
    records.sort(key=lambda item: item["event_id"])
    return _stable_bytes(records) + b"\n"
