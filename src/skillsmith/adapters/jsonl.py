from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..canonical import canonicalize_event
from ..model import CanonicalEvent


class JSONLLoadError(ValueError):
    pass


def load_jsonl(path: str | Path, *, session_id: str, max_record_bytes: int = 1_048_576) -> list[CanonicalEvent]:
    source = Path(path)
    events: list[CanonicalEvent] = []
    with source.open("r", encoding="utf-8", newline="") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            if not raw_line.strip():
                continue
            if len(raw_line.encode("utf-8")) > max_record_bytes:
                raise JSONLLoadError(f"{source.name}:{line_number}: record exceeds {max_record_bytes} bytes")
            try:
                record: Any = json.loads(raw_line)
            except json.JSONDecodeError as exc:
                raise JSONLLoadError(f"{source.name}:{line_number}: malformed JSON: {exc.msg}") from exc
            if not isinstance(record, dict):
                raise JSONLLoadError(f"{source.name}:{line_number}: expected JSON object")
            events.append(
                canonicalize_event(
                    record,
                    session_id=session_id,
                    source=str(source),
                    line=line_number,
                )
            )
    return events
