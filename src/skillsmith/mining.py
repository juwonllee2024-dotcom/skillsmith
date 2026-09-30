from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

from .evidence import bind_evidence, is_proven
from .model import CanonicalEvent


@dataclass(frozen=True, slots=True)
class WorkflowStep:
    instruction: str
    source_step_ids: tuple[str, ...]
    source_session_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class Workflow:
    steps: tuple[WorkflowStep, ...]
    support_sessions: tuple[str, ...]


def _proven_sequence(events: Sequence[CanonicalEvent]) -> tuple[list[CanonicalEvent], tuple[str, ...]]:
    evidence = bind_evidence(events)
    steps = [event for event in events if event.event_type == "step" and is_proven(event, evidence)]
    steps.sort(key=lambda event: event.line)
    signature = tuple(str(step.payload.get("instruction", "")).strip() for step in steps)
    if not signature or any(not item for item in signature):
        return [], ()
    return steps, signature


def mine_workflows(
    sessions: Mapping[str, Sequence[CanonicalEvent]], *, min_successes: int = 2
) -> list[Workflow]:
    grouped: dict[tuple[str, ...], list[tuple[str, list[CanonicalEvent]]]] = {}
    for session_id in sorted(sessions):
        steps, signature = _proven_sequence(sessions[session_id])
        if signature:
            grouped.setdefault(signature, []).append((session_id, steps))

    workflows: list[Workflow] = []
    for signature in sorted(grouped):
        supporters = grouped[signature]
        if len(supporters) < min_successes:
            continue
        workflow_steps: list[WorkflowStep] = []
        for index, instruction in enumerate(signature):
            source_step_ids = tuple(sorted(steps[index].event_id for _, steps in supporters))
            source_session_ids = tuple(sorted(session_id for session_id, _ in supporters))
            workflow_steps.append(
                WorkflowStep(
                    instruction=instruction,
                    source_step_ids=source_step_ids,
                    source_session_ids=source_session_ids,
                )
            )
        workflows.append(
            Workflow(
                steps=tuple(workflow_steps),
                support_sessions=tuple(sorted(session_id for session_id, _ in supporters)),
            )
        )
    return workflows
