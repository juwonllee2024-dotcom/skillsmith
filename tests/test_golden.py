import json
from pathlib import Path

from skillsmith.cli import main


FIXTURES = Path(__file__).parent / "fixtures" / "golden"


def test_golden_three_trace_pipeline_promotes_only_proven_repeated_workflow(tmp_path: Path):
    out = tmp_path / "compiled"
    code = main(
        [
            "compile",
            str(FIXTURES / "success-a.jsonl"),
            str(FIXTURES / "success-b.jsonl"),
            str(FIXTURES / "fail-done.jsonl"),
            "--out",
            str(out),
        ]
    )
    assert code == 0
    skill = (out / "SKILL.md").read_text(encoding="utf-8")
    assert "run pytest -q" in skill
    assert "skip verification and declare done" not in skill
    assert "DONE" not in skill

    provenance = json.loads((out / "provenance.json").read_text(encoding="utf-8"))
    assert len(provenance["instructions"]) == 1
    assert provenance["instructions"][0]["instruction"] == "run pytest -q"
    assert len(provenance["instructions"][0]["sources"]) == 2
    assert {src["session_id"] for src in provenance["instructions"][0]["sources"]} == {"success-a", "success-b"}
