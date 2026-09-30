from skillsmith.canonical import canonical_event_hash, canonical_json, canonicalize_event


def test_canonical_event_id_is_content_derived_and_stable():
    raw = {"kind": "tool", "name": "pytest", "status": "passed", "payload": {"b": 2, "a": 1}}
    first = canonicalize_event(raw, session_id="s1", source="trace.jsonl", line=7)
    second = canonicalize_event(raw, session_id="s1", source="trace.jsonl", line=7)
    assert first.event_id == second.event_id
    assert canonical_event_hash(first) == canonical_event_hash(second)


def test_canonical_json_is_byte_identical_for_equivalent_input_order():
    a = canonicalize_event({"kind": "step", "name": "build", "payload": {"z": 1, "a": 2}}, session_id="s1", source="x", line=1)
    b = canonicalize_event({"payload": {"a": 2, "z": 1}, "name": "build", "kind": "step"}, session_id="s1", source="x", line=1)
    assert canonical_json([a]) == canonical_json([b])


def test_canonical_json_sorts_events_deterministically():
    later = canonicalize_event({"kind": "step", "name": "z"}, session_id="s", source="x", line=2)
    earlier = canonicalize_event({"kind": "step", "name": "a"}, session_id="s", source="x", line=1)
    assert canonical_json([later, earlier]) == canonical_json([earlier, later])
