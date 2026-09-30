import json
from pathlib import Path

import pytest

from skillsmith.canonical import canonicalize_event
from skillsmith.compiler import compile_artifacts
from skillsmith.mining import mine_workflows
from skillsmith.verify import ArtifactVerificationError, OutputSafetyError, safe_output_path, verify_artifacts, write_artifacts_safely


def make_artifacts():
    sessions = {}
    for session_id in ("a", "b"):
        step = canonicalize_event({"type":"step","payload":{"instruction":"run pytest"}}, session_id=session_id, source=f"{session_id}.jsonl", line=1)
        evidence = canonicalize_event({"type":"test","payload":{"status":"passed","deterministic":True,"step_id":step.event_id}}, session_id=session_id, source=f"{session_id}.jsonl", line=2)
        sessions[session_id] = [step, evidence]
    workflows = mine_workflows(sessions)
    source_events = {event.event_id:event for events in sessions.values() for event in events}
    return compile_artifacts(workflows, source_events), source_events


@pytest.mark.parametrize("relative", ["../escape.txt", "/tmp/escape.txt"])
def test_safe_output_path_rejects_traversal_and_absolute_paths(tmp_path: Path, relative: str):
    with pytest.raises(OutputSafetyError):
        safe_output_path(tmp_path, relative)


def test_safe_output_path_rejects_symlink_escape(tmp_path: Path):
    outside = tmp_path / "outside"
    outside.mkdir()
    root = tmp_path / "out"
    root.mkdir()
    (root / "link").symlink_to(outside, target_is_directory=True)
    with pytest.raises(OutputSafetyError):
        safe_output_path(root, "link/escape.txt")


def test_write_artifacts_refuses_existing_output_without_partial_write(tmp_path: Path):
    root = tmp_path / "out"
    root.mkdir()
    (root / "provenance.json").write_text("occupied", encoding="utf-8")
    artifacts = {"SKILL.md": b"skill\n", "provenance.json": b"{}\n"}
    with pytest.raises(OutputSafetyError, match="already exists"):
        write_artifacts_safely(root, artifacts)
    assert not (root / "SKILL.md").exists()


def test_verify_artifacts_detects_provenance_tampering():
    artifacts, source_events = make_artifacts()
    parsed = json.loads(artifacts["provenance.json"])
    parsed["instructions"][0]["sources"][0]["event_hash"] = "0" * 64
    tampered = dict(artifacts)
    tampered["provenance.json"] = (json.dumps(parsed, sort_keys=True, separators=(",", ":")) + "\n").encode()
    with pytest.raises(ArtifactVerificationError, match="hash mismatch"):
        verify_artifacts(tampered, source_events)


def test_verify_artifacts_accepts_valid_compiler_output():
    artifacts, source_events = make_artifacts()
    verify_artifacts(artifacts, source_events)
