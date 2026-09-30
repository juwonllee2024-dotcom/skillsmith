from __future__ import annotations

import json
from pathlib import Path
from typing import Mapping

from .canonical import canonical_event_hash
from .model import CanonicalEvent


class OutputSafetyError(ValueError):
    pass


class ArtifactVerificationError(ValueError):
    pass


def safe_output_path(root: str | Path, relative: str | Path) -> Path:
    root_path = Path(root)
    rel = Path(relative)
    if rel.is_absolute():
        raise OutputSafetyError(f"absolute output path is not allowed: {relative}")
    root_resolved = root_path.resolve(strict=False)
    candidate = (root_path / rel).resolve(strict=False)
    if not candidate.is_relative_to(root_resolved):
        raise OutputSafetyError(f"output path escapes root: {relative}")
    return candidate


def write_artifacts_safely(root: str | Path, artifacts: Mapping[str, bytes]) -> None:
    root_path = Path(root)
    targets: list[tuple[Path, bytes]] = []
    for relative, content in sorted(artifacts.items()):
        target = safe_output_path(root_path, relative)
        if target.exists() or target.is_symlink():
            raise OutputSafetyError(f"output already exists: {relative}")
        targets.append((target, content))

    root_path.mkdir(parents=True, exist_ok=True)
    for target, content in targets:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)


def verify_artifacts(artifacts: Mapping[str, bytes], source_events: Mapping[str, CanonicalEvent]) -> None:
    required = {"SKILL.md", "provenance.json", "eval.json"}
    missing = required - set(artifacts)
    if missing:
        raise ArtifactVerificationError(f"missing artifacts: {sorted(missing)}")
    try:
        provenance = json.loads(artifacts["provenance.json"])
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ArtifactVerificationError("invalid provenance.json") from exc

    records = provenance.get("instructions")
    if not isinstance(records, list):
        raise ArtifactVerificationError("invalid provenance instructions")

    skill_instructions = [
        line.split(". ", 1)[1]
        for line in artifacts["SKILL.md"].decode("utf-8").splitlines()
        if line and line[0].isdigit() and ". " in line
    ]
    if len(records) != len(skill_instructions):
        raise ArtifactVerificationError("provenance coverage mismatch")

    for expected_instruction, record in zip(skill_instructions, records, strict=True):
        if record.get("instruction") != expected_instruction:
            raise ArtifactVerificationError("provenance instruction mismatch")
        sources = record.get("sources")
        if not isinstance(sources, list) or not sources:
            raise ArtifactVerificationError("instruction missing provenance sources")
        for source in sources:
            event_id = source.get("event_id")
            if event_id not in source_events:
                raise ArtifactVerificationError(f"unknown source event: {event_id}")
            expected_hash = canonical_event_hash(source_events[event_id])
            if source.get("event_hash") != expected_hash:
                raise ArtifactVerificationError(f"hash mismatch for source event: {event_id}")
