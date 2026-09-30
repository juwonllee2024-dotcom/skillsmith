import json

from skillsmith.canonical import canonical_event_hash, canonicalize_event
from skillsmith.compiler import compile_artifacts
from skillsmith.mining import mine_workflows


def make_session(session_id: str):
    source = f"{session_id}.jsonl"
    step = canonicalize_event(
        {"type": "step", "payload": {"instruction": "run pytest"}},
        session_id=session_id,
        source=source,
        line=1,
    )
    passed = canonicalize_event(
        {"type": "test", "payload": {"status": "passed", "deterministic": True, "step_id": step.event_id}},
        session_id=session_id,
        source=source,
        line=2,
    )
    return [step, passed]


def test_compiler_gives_every_instruction_integrity_checked_provenance():
    sessions = {"a": make_session("a"), "b": make_session("b")}
    workflows = mine_workflows(sessions)
    source_events = {event.event_id: event for events in sessions.values() for event in events}
    artifacts = compile_artifacts(workflows, source_events)

    assert set(artifacts) == {"SKILL.md", "provenance.json", "eval.json"}
    provenance = json.loads(artifacts["provenance.json"])
    skill_lines = [line for line in artifacts["SKILL.md"].decode().splitlines() if line.startswith("1. ")]
    assert len(skill_lines) == 1
    assert len(provenance["instructions"]) == len(skill_lines)
    record = provenance["instructions"][0]
    assert record["instruction"] == "run pytest"
    assert len(record["sources"]) == 2
    for source in record["sources"]:
        assert source["event_hash"] == canonical_event_hash(source_events[source["event_id"]])


def test_compiler_is_byte_identical_for_equivalent_input_orderings():
    sessions = {"a": make_session("a"), "b": make_session("b")}
    source_events = {event.event_id: event for events in sessions.values() for event in events}
    workflows = mine_workflows(sessions)
    forward = compile_artifacts(workflows, source_events)
    reverse = compile_artifacts(list(reversed(workflows)), dict(reversed(list(source_events.items()))))
    assert forward == reverse
