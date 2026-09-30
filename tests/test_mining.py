from skillsmith.canonical import canonicalize_event
from skillsmith.mining import mine_workflows


def make_session(session_id: str, *, passed: bool = True):
    source = f"{session_id}.jsonl"
    step1 = canonicalize_event(
        {"type": "step", "payload": {"instruction": "run pytest"}},
        session_id=session_id,
        source=source,
        line=1,
    )
    step2 = canonicalize_event(
        {"type": "step", "payload": {"instruction": "run ruff"}},
        session_id=session_id,
        source=source,
        line=2,
    )
    status = "passed" if passed else "failed"
    e1 = canonicalize_event(
        {"type": "test", "payload": {"status": status, "deterministic": True, "step_id": step1.event_id}},
        session_id=session_id,
        source=source,
        line=3,
    )
    e2 = canonicalize_event(
        {"type": "test", "payload": {"status": status, "deterministic": True, "step_id": step2.event_id}},
        session_id=session_id,
        source=source,
        line=4,
    )
    return [step1, step2, e1, e2]


def test_mines_repeated_proven_workflow_across_successful_sessions():
    workflows = mine_workflows({"a": make_session("a"), "b": make_session("b")})
    assert len(workflows) == 1
    workflow = workflows[0]
    assert [step.instruction for step in workflow.steps] == ["run pytest", "run ruff"]
    assert workflow.support_sessions == ("a", "b")


def test_failed_session_does_not_promote_or_contaminate_workflow():
    sessions = {
        "a": make_session("a"),
        "b": make_session("b"),
        "failed": make_session("failed", passed=False),
    }
    workflow = mine_workflows(sessions)[0]
    assert workflow.support_sessions == ("a", "b")
    assert all("failed" not in step.source_session_ids for step in workflow.steps)


def test_adding_many_failed_traces_does_not_change_promoted_workflow():
    base = {"a": make_session("a"), "b": make_session("b")}
    baseline = mine_workflows(base)
    noisy = dict(base)
    for index in range(100):
        noisy[f"failed-{index}"] = make_session(f"failed-{index}", passed=False)
    assert mine_workflows(noisy) == baseline
