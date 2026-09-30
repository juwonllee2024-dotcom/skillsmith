import json

from skillsmith.canonical import canonical_event_hash, canonical_json, canonicalize_event


def test_stable_content_derived_ids_and_canonical_json():
    raw_a = {"type": "message", "payload": {"b": 2, "a": 1}}
    raw_b = {"payload": {"a": 1, "b": 2}, "type": "message"}

    event_a = canonicalize_event(raw_a, session_id="s1", source="trace.jsonl", line=1)
    event_b = canonicalize_event(raw_b, session_id="s1", source="trace.jsonl", line=1)

    assert event_a.event_id == event_b.event_id
    assert canonical_event_hash(event_a) == canonical_event_hash(event_b)
    assert canonical_json([event_a]) == canonical_json([event_b])


def test_canonical_json_sorts_events_deterministically():
    e1 = canonicalize_event({"type": "z", "payload": {"x": 1}}, session_id="s", source="f", line=2)
    e2 = canonicalize_event({"type": "a", "payload": {"x": 2}}, session_id="s", source="f", line=1)

    first = canonical_json([e1, e2])
    second = canonical_json([e2, e1])

    assert first == second
    decoded = json.loads(first)
    assert [item["event_id"] for item in decoded] == sorted(item["event_id"] for item in decoded)
