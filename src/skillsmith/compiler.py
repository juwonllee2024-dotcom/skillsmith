from __future__ import annotations

import json
from typing import Mapping, Sequence

from .mining import Workflow
from .model import CanonicalEvent
from .provenance import build_provenance


def _json_bytes(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")


def compile_artifacts(workflows: Sequence[Workflow], source_events: Mapping[str, CanonicalEvent]) -> dict[str, bytes]:
    ordered = sorted(workflows, key=lambda workflow: tuple(step.instruction for step in workflow.steps))
    provenance = build_provenance(list(ordered), source_events)
    lines = ["# Generated Skill", "", "## Instructions", ""]
    index = 1
    for workflow in ordered:
        for step in workflow.steps:
            lines.append(f"{index}. {step.instruction}")
            index += 1
    skill = ("\n".join(lines).rstrip() + "\n").encode("utf-8")
    evaluation = {
        "version": 1,
        "workflow_count": len(ordered),
        "instructions": [
            step.instruction
            for workflow in ordered
            for step in workflow.steps
        ],
    }
    return {
        "SKILL.md": skill,
        "provenance.json": _json_bytes(provenance),
        "eval.json": _json_bytes(evaluation),
    }
