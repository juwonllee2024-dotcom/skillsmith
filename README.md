# SkillSmith

**Turn proven agent work into reusable skills.**

SkillSmith is a local-first CLI that compiles repeated, evidence-backed agent workflows into deterministic skill artifacts with source provenance. Agent prose such as `DONE` is never evidence by itself, failed sessions do not promote instructions, and historical command text is treated as inert data.

## Quick start

Requires Python 3.11+.

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install .

skillsmith inspect \
  tests/fixtures/golden/success-a.jsonl \
  tests/fixtures/golden/success-b.jsonl \
  tests/fixtures/golden/fail-done.jsonl

skillsmith compile \
  tests/fixtures/golden/success-a.jsonl \
  tests/fixtures/golden/success-b.jsonl \
  tests/fixtures/golden/fail-done.jsonl \
  --out compiled-skill
```

The golden demo produces:

```text
compiled-skill/
├── SKILL.md
├── provenance.json
└── eval.json
```

`SKILL.md` contains only the repeated workflow backed by deterministic passing-test evidence from the two successful traces. The failed `DONE` trace contributes no promoted instruction.

## Commands

```text
skillsmith inspect <trace...>
skillsmith compile <trace...> --out <dir>
```

`inspect` is read-only. `compile` refuses destructive overwrite and confines generated files to the requested output directory.

## Trust model

- Agent claims alone score zero.
- Only explicitly supported objective evidence can prove a step.
- Evidence is bound to the exact canonical step it proves.
- Every emitted instruction has source-event provenance and integrity hashes.
- Historical shell commands are never automatically executed.
- Path traversal, symlink escape, and output collision fail closed.

See [`docs/evidence-model.md`](docs/evidence-model.md) and [`docs/threat-model.md`](docs/threat-model.md).

## Development

```bash
python -m pip install -e '.[dev]'
pytest -q
```

## Status

SkillSmith v0.1 is under active verification. A release is not considered complete until the repository release gates, including clean wheel installation and CI for the exact commit, pass.

## License

Apache-2.0. See [`LICENSE`](LICENSE).
