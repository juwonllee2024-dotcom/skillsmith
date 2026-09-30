# SkillSmith Design

## Product
SkillSmith is a local-first CLI that compiles evidence-backed successful coding-agent behavior into portable skills, deterministic evals, and provenance artifacts.

Tagline: **Turn proven agent work into reusable skills.**

## v0.1 Scope
Input agent-session traces, normalize them into canonical events, score only objective evidence, identify repeated successful workflows, and compile reusable artifacts.

The v0.1 pipeline is:

`trace -> adapter -> canonical events -> evidence scoring -> workflow mining -> compiler -> SKILL.md + provenance.json + eval -> verification`

Out of scope for v0.1: cloud services, marketplace, autonomous self-modification, arbitrary historical-command replay, and GUI.

## Core Invariants
1. Agent self-claims such as `DONE` are not evidence by themselves and score 0.
2. Failed sessions must not contaminate a generated skill.
3. Every generated instruction must be traceable to source evidence through provenance.
4. Semantically identical canonical input must produce byte-identical deterministic artifacts.
5. Historical shell commands are data only and are never executed automatically.
6. Output paths must be confined to the requested output directory; path traversal, symlink escape, and overwrite attacks must be rejected.
7. Evidence must be bound to the workflow and exact source context rather than merely coexisting in the same session.
8. Provenance must support integrity verification against canonical source-event hashes.

## Golden Demo
Use three traces for the same goal:
- Trace A: successful workflow with deterministic test evidence.
- Trace B: repeated successful workflow with deterministic test evidence.
- Trace C: agent says it completed the task, but its test fails.

Expected result: only the repeated evidence-backed workflow from A/B becomes a skill; C contributes no promoted instruction. Every generated instruction has source provenance.

## Architecture

### Adapters
Provider-specific trace adapters convert supported JSONL/event formats into one canonical event schema. Unknown or malformed records fail closed with file/line diagnostics.

### Canonical Model
Canonical events include stable content-derived IDs, event type, normalized payload, source location, session ID, and integrity hash. Ordering is normalized deterministically.

### Evidence
Evidence classes are explicit and conservative. Objective test/build/assertion success may support a workflow. Agent prose claims alone never do. Evidence records bind to specific canonical events and workflow steps.

### Mining
Workflow mining finds repeated, evidence-backed step sequences across successful sessions. A sequence that occurs only in failed sessions or lacks bound evidence is excluded.

### Compiler
The compiler produces deterministic `SKILL.md`, `provenance.json`, and an eval fixture/spec. Generated instructions are derived only from promoted workflow steps.

### Verification
Verification checks determinism, provenance completeness/integrity, contamination resistance, output confinement, and non-execution of historical commands.

## CLI
Initial CLI surface:

- `skillsmith compile <trace...> --out <dir>`
- `skillsmith inspect <trace...>`

`compile` writes new artifacts only into the requested output directory and refuses destructive overwrite unless a future explicit safe flag is designed. `inspect` is read-only.

## Repository Structure

```text
skillsmith/
├── pyproject.toml
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── SECURITY.md
├── src/skillsmith/
│   ├── __init__.py
│   ├── cli.py
│   ├── model.py
│   ├── canonical.py
│   ├── adapters/
│   │   ├── __init__.py
│   │   └── jsonl.py
│   ├── evidence.py
│   ├── mining.py
│   ├── compiler.py
│   ├── provenance.py
│   └── verify.py
├── tests/
│   ├── fixtures/
│   ├── test_canonical.py
│   ├── test_evidence.py
│   ├── test_mining.py
│   ├── test_compiler.py
│   ├── test_cli.py
│   ├── test_security.py
│   └── test_golden.py
├── examples/golden/
├── docs/
│   ├── architecture.md
│   ├── schema.md
│   ├── evidence-model.md
│   └── threat-model.md
└── .github/
    ├── workflows/ci.yml
    └── ISSUE_TEMPLATE/
```

## Release Gates
SkillSmith v0.1 must not be called COMPLETE until all of these are verified on the GitHub repository:

1. Clean virtual-environment install from built wheel.
2. Deterministic golden pipeline.
3. Failed-trace contamination resistance.
4. 100% provenance coverage for generated instructions, with integrity verification.
5. Full test suite and CI pass.
6. README commands verified from a clean checkout.
7. Fixture/output secret scan.
8. Historical-command non-execution tests.
9. Path traversal/symlink/output-overwrite defenses.
10. Evidence-to-workflow binding tests, including unrelated-green-test rejection.

## License
Apache-2.0 is the planned license for v0.1 unless changed before release.
