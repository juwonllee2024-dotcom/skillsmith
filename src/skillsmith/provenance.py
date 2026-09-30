from __future__ import annotations

from typing import Mapping

from .canonical import canonical_event_hash
from .mining import Workflow
from .model import CanonicalEvent


def build_provenance(workflows: list[Workflow] | tuple[Workflow, ...], source_events: Mapping[str, CanonicalEvent]) -> dict:
    instructions = []
    ordered_workflows = sorted(workflows, key=lambda workflow: tuple(step.instruction for step in workflow.steps))
    for workflow in ordered_workflows:
        for step in workflow.steps:
            sources = []
            for event_id in sorted(step.source_step_ids):
                event = source_events[event_id]
                sources.append(
                    {
                        "event_id": event_id,
                        "event_hash": canonical_event_hash(event),
                        "session_id": event.session_id,
                        "source": event.source,
                        "line": event.line,
                    }
                )
            instructions.append({"instruction": step.instruction, "sources": sources})
    return {"version": 1, "instructions": instructions}
