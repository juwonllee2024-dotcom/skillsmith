from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from typing import Any, Iterable, Mapping

from .model import CanonicalEvent


def _normalize(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(k): _normalize(value[k]) for k in sorted(value, key=str)}
    if isinstance(value, list):
        return [_normalize(v) for v in value]
    return value


def _stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def canonicalize_event(raw: Mapping[str, Any], *, session_id: str, source: str, line: int) -> CanonicalEvent:
    event_type = str(raw.get("type", "unknown"))
    payload = _normalize(raw.get("payload", {}))
    basis = {
        "event_type": event_type,
        "payload": payload,
        "session_id": session_id,
        "source": source,
        "line": int(line),
    }
    event_id = hashlib.sha256(_stable_json(basis).encode("utf-8")).hexdigest()[:24]
    return CanonicalEvent(
        event_id=event_id,
        event_type=event_type,
        payload=payload,
        session_id=session_id,
        source=source,
        line=int(line),
    )


def canonical_event_hash(event: CanonicalEvent) -> str:
    return hashlib.sha256(_stable_json(asdict(event)).encode("utf-8")).hexdigest()


def canonical_json(events: Iterable[CanonicalEvent]) -> bytes:
    rows = [asdict(event) for event in events]
    rows.sort(key=lambda item: item["event_id"])
    return (_stable_json(rows) + "\n").encode("utf-8")
