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
    rows: list[tuple[int, dict[str, Any]]] = []
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
            rows.append((line_number, record))

    provisional: list[CanonicalEvent] = [
        canonicalize_event(record, session_id=session_id, source=str(source), line=line_number)
        for line_number, record in rows
    ]
    step_by_line = {
        event.line: event.event_id for event in provisional if event.event_type == "step"
    }

    events: list[CanonicalEvent] = []
    for (line_number, record), event in zip(rows, provisional, strict=True):
        payload = record.get("payload")
        if isinstance(payload, dict) and "step_id" not in payload and "step_line" in payload:
            step_line = payload.get("step_line")
            if not isinstance(step_line, int) or step_line not in step_by_line:
                raise JSONLLoadError(f"{source.name}:{line_number}: invalid step_line reference")
            rewritten = dict(record)
            rewritten_payload = dict(payload)
            rewritten_payload["step_id"] = step_by_line[step_line]
            rewritten["payload"] = rewritten_payload
            event = canonicalize_event(
                rewritten,
                session_id=session_id,
                source=str(source),
                line=line_number,
            )
        events.append(event)
    return events
