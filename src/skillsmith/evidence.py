from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .model import CanonicalEvent


@dataclass(frozen=True, slots=True)
class Evidence:
    source_event_id: str
    target_step_id: str
    kind: str
    score: int


def score_evidence(event: CanonicalEvent) -> int:
    payload = event.payload
    if event.event_type == "test":
        if payload.get("status") == "passed" and payload.get("deterministic") is True:
            return 100
        return 0
    if event.event_type == "assertion":
        if payload.get("status") == "passed" and payload.get("deterministic") is True:
            return 100
        return 0
    return 0


def bind_evidence(events: Iterable[CanonicalEvent]) -> list[Evidence]:
    bound: list[Evidence] = []
    for event in events:
        score = score_evidence(event)
        target = event.payload.get("step_id") if hasattr(event.payload, "get") else None
        if score <= 0 or not isinstance(target, str) or not target:
            continue
        bound.append(
            Evidence(
                source_event_id=event.event_id,
                target_step_id=target,
                kind=event.event_type,
                score=score,
            )
        )
    return bound


def is_proven(step: CanonicalEvent, evidence: Iterable[Evidence]) -> bool:
    return any(item.target_step_id == step.event_id and item.score > 0 for item in evidence)
