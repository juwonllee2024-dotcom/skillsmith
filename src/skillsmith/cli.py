from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from .adapters.jsonl import JSONLLoadError, load_jsonl
from .compiler import compile_artifacts
from .mining import mine_workflows
from .verify import ArtifactVerificationError, OutputSafetyError, verify_artifacts, write_artifacts_safely


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="skillsmith")
    subparsers = parser.add_subparsers(dest="command", required=True)

    inspect = subparsers.add_parser("inspect")
    inspect.add_argument("traces", nargs="+")

    compile_cmd = subparsers.add_parser("compile")
    compile_cmd.add_argument("traces", nargs="+")
    compile_cmd.add_argument("--out", required=True)
    return parser


def _load_sessions(trace_paths: Sequence[str]):
    sessions = {}
    source_events = {}
    seen_session_ids: set[str] = set()
    for raw_path in trace_paths:
        path = Path(raw_path)
        base_id = path.stem or "trace"
        session_id = base_id
        suffix = 2
        while session_id in seen_session_ids:
            session_id = f"{base_id}-{suffix}"
            suffix += 1
        seen_session_ids.add(session_id)
        events = load_jsonl(path, session_id=session_id)
        sessions[session_id] = events
        for event in events:
            source_events[event.event_id] = event
    return sessions, source_events


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    try:
        sessions, source_events = _load_sessions(args.traces)
        workflows = mine_workflows(sessions)
        if args.command == "inspect":
            summary = {
                "session_count": len(sessions),
                "workflow_count": len(workflows),
                "workflows": [
                    [step.instruction for step in workflow.steps]
                    for workflow in workflows
                ],
            }
            print(json.dumps(summary, indent=2, sort_keys=True))
            return 0

        artifacts = compile_artifacts(workflows, source_events)
        verify_artifacts(artifacts, source_events)
        write_artifacts_safely(args.out, artifacts)
        return 0
    except (OSError, JSONLLoadError, OutputSafetyError, ArtifactVerificationError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2


def entrypoint() -> None:
    raise SystemExit(main())
