from pathlib import Path

from skillsmith.cli import main


def write_trace(path: Path, instruction: str = "pytest -q", *, passed: bool = True):
    status = "passed" if passed else "failed"
    path.write_text(
        '{"type":"step","payload":{"instruction":' + repr(instruction).replace("'", '"') + '}}\n'
        '{"type":"test","payload":{"status":"' + status + '","deterministic":true,"step_line":1}}\n',
        encoding="utf-8",
    )


def test_compile_cli_writes_expected_artifacts(tmp_path: Path):
    a = tmp_path / "a.jsonl"
    b = tmp_path / "b.jsonl"
    write_trace(a)
    write_trace(b)
    out = tmp_path / "out"
    code = main(["compile", str(a), str(b), "--out", str(out)])
    assert code == 0
    assert sorted(path.name for path in out.iterdir()) == ["SKILL.md", "eval.json", "provenance.json"]


def test_inspect_cli_is_read_only_and_reports_workflow_count(tmp_path: Path, capsys):
    a = tmp_path / "a.jsonl"
    b = tmp_path / "b.jsonl"
    write_trace(a)
    write_trace(b)
    code = main(["inspect", str(a), str(b)])
    assert code == 0
    output = capsys.readouterr().out
    assert '"workflow_count": 1' in output
    assert not (tmp_path / "out").exists()


def test_compile_cli_malformed_input_returns_nonzero_without_output(tmp_path: Path, capsys):
    bad = tmp_path / "bad.jsonl"
    bad.write_text("not-json\n", encoding="utf-8")
    out = tmp_path / "out"
    code = main(["compile", str(bad), "--out", str(out)])
    assert code != 0
    assert "bad.jsonl:1" in capsys.readouterr().err
    assert not out.exists()


def test_compile_cli_refuses_collision(tmp_path: Path, capsys):
    a = tmp_path / "a.jsonl"
    b = tmp_path / "b.jsonl"
    write_trace(a)
    write_trace(b)
    out = tmp_path / "out"
    out.mkdir()
    (out / "SKILL.md").write_text("occupied", encoding="utf-8")
    code = main(["compile", str(a), str(b), "--out", str(out)])
    assert code != 0
    assert "already exists" in capsys.readouterr().err


def test_historical_command_text_is_never_executed(tmp_path: Path):
    marker = tmp_path / "SHOULD_NOT_EXIST"
    command = f"touch {marker}"
    a = tmp_path / "a.jsonl"
    b = tmp_path / "b.jsonl"
    write_trace(a, command)
    write_trace(b, command)
    code = main(["compile", str(a), str(b), "--out", str(tmp_path / "out")])
    assert code == 0
    assert not marker.exists()
