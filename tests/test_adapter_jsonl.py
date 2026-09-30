from pathlib import Path

import pytest

from skillsmith.adapters.jsonl import JSONLLoadError, load_jsonl


def test_load_jsonl_reads_valid_records_and_skips_blank_lines(tmp_path: Path):
    path = tmp_path / "trace.jsonl"
    path.write_text(
        '{"type":"step","payload":{"instruction":"pytest -q"}}\n\n'
        '{"type":"test","payload":{"status":"passed"}}\n',
        encoding="utf-8",
    )
    events = load_jsonl(path, session_id="session-1")
    assert [event.event_type for event in events] == ["step", "test"]
    assert [event.line for event in events] == [1, 3]


def test_load_jsonl_reports_file_and_line_for_malformed_json(tmp_path: Path):
    path = tmp_path / "bad.jsonl"
    path.write_text('{"type":"step"}\nnot-json\n', encoding="utf-8")
    with pytest.raises(JSONLLoadError, match=r"bad\.jsonl:2"):
        load_jsonl(path, session_id="s")


def test_load_jsonl_rejects_non_object_records(tmp_path: Path):
    path = tmp_path / "array.jsonl"
    path.write_text('[1,2,3]\n', encoding="utf-8")
    with pytest.raises(JSONLLoadError, match=r"array\.jsonl:1"):
        load_jsonl(path, session_id="s")


def test_load_jsonl_rejects_oversized_record(tmp_path: Path):
    path = tmp_path / "huge.jsonl"
    path.write_text('{"type":"step","payload":{"x":"' + ('a' * 200) + '"}}\n', encoding="utf-8")
    with pytest.raises(JSONLLoadError, match=r"record exceeds"):
        load_jsonl(path, session_id="s", max_record_bytes=64)


def test_load_jsonl_resolves_step_line_reference_to_canonical_step_id(tmp_path: Path):
    path = tmp_path / "trace.jsonl"
    path.write_text(
        '{"type":"step","payload":{"instruction":"pytest -q"}}\n'
        '{"type":"test","payload":{"status":"passed","deterministic":true,"step_line":1}}\n',
        encoding="utf-8",
    )
    events = load_jsonl(path, session_id="trace")
    assert events[1].payload["step_id"] == events[0].event_id
