from skillsmith.canonical import canonicalize_event
from skillsmith.evidence import bind_evidence, is_proven, score_evidence


def ev(raw, line=1):
    return canonicalize_event(raw, session_id="s1", source="trace.jsonl", line=line)


def test_done_claim_alone_scores_zero_and_does_not_prove_step():
    step = ev({"type": "step", "payload": {"instruction": "run tests"}}, 1)
    done = ev({"type": "claim", "payload": {"text": "DONE", "step_id": step.event_id}}, 2)
    assert score_evidence(done) == 0
    assert not is_proven(step, bind_evidence([step, done]))


def test_failed_test_never_proves_step():
    step = ev({"type": "step", "payload": {"instruction": "run tests"}}, 1)
    failed = ev({"type": "test", "payload": {"status": "failed", "step_id": step.event_id}}, 2)
    assert score_evidence(failed) == 0
    assert not is_proven(step, bind_evidence([step, failed]))


def test_successful_deterministic_test_can_prove_exact_step():
    step = ev({"type": "step", "payload": {"instruction": "run tests"}}, 1)
    passed = ev({"type": "test", "payload": {"status": "passed", "deterministic": True, "step_id": step.event_id}}, 2)
    evidence = bind_evidence([step, passed])
    assert score_evidence(passed) == 100
    assert is_proven(step, evidence)


def test_unrelated_passing_test_cannot_prove_another_step():
    step_a = ev({"type": "step", "payload": {"instruction": "format"}}, 1)
    step_b = ev({"type": "step", "payload": {"instruction": "run tests"}}, 2)
    passed = ev({"type": "test", "payload": {"status": "passed", "deterministic": True, "step_id": step_b.event_id}}, 3)
    evidence = bind_evidence([step_a, step_b, passed])
    assert not is_proven(step_a, evidence)
    assert is_proven(step_b, evidence)
