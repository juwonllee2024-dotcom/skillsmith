# SkillSmith v0.1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a local-first CLI that compiles only evidence-backed repeated agent workflows into deterministic skills with verifiable provenance.

**Architecture:** Provider traces are normalized into immutable canonical events, objective evidence is bound to exact workflow steps, repeated successful workflows are mined, and deterministic artifacts are compiled. Security boundaries treat historical commands as inert data and confine output to a safe directory.

**Tech Stack:** Python 3.11+, stdlib-first, `pytest` for tests, `argparse` for CLI, `dataclasses`/typed structures for the canonical model.

**Spec:** `docs/superpowers/specs/2026-09-30-skillsmith-design.md`

## Global Constraints

- `DONE` or equivalent agent prose alone has evidence score 0.
- Failed sessions never promote instructions.
- Every generated instruction requires source provenance.
- Canonically equivalent inputs produce byte-identical artifacts.
- Historical shell commands are never executed automatically.
- Output traversal, symlink escape, and destructive overwrite fail closed.
- Evidence must bind to the specific workflow step/source context.
- Provenance integrity is verified from canonical source-event hashes.

## Review Focus

- Malformed/hostile JSONL must fail with file and line diagnostics without partial output.
- Reordered equivalent input must not change artifact bytes.
- Unrelated passing tests must not prove an unrelated workflow step.
- Symlink/path traversal attempts must not escape the output directory.
- Historical command text must never reach an execution primitive.

---

### Task 1: Package skeleton + canonical event model

**Files:**
- Create: `pyproject.toml`
- Create: `src/skillsmith/__init__.py`
- Create: `src/skillsmith/model.py`
- Create: `src/skillsmith/canonical.py`
- Test: `tests/test_canonical.py`

**Interfaces:**
- Produces: `CanonicalEvent`, `canonicalize_event(raw, *, session_id, source, line)`, `canonical_event_hash(event)`, `canonical_json(events)`.

- [ ] Write failing tests for stable content-derived IDs, deterministic ordering, and byte-identical canonical JSON.
- [ ] Run `pytest tests/test_canonical.py -q` and verify failure.
- [ ] Implement the minimal canonical model and hashing/serialization.
- [ ] Run `pytest tests/test_canonical.py -q` and verify pass.
- [ ] Commit: `feat: add deterministic canonical event model`.

### Task 2: Safe JSONL adapter

**Files:**
- Create: `src/skillsmith/adapters/__init__.py`
- Create: `src/skillsmith/adapters/jsonl.py`
- Test: `tests/test_adapter_jsonl.py`

**Interfaces:**
- Consumes: canonicalization interfaces from Task 1.
- Produces: `load_jsonl(path, *, session_id) -> list[CanonicalEvent]`.

- [ ] Write failing tests for valid JSONL, malformed line diagnostics, blank lines, and oversized/invalid records failing closed.
- [ ] Run targeted tests and verify failure.
- [ ] Implement read-only JSONL parsing with no command execution.
- [ ] Run targeted tests and verify pass.
- [ ] Commit: `feat: add safe jsonl trace adapter`.

### Task 3: Evidence model and exact binding

**Files:**
- Create: `src/skillsmith/evidence.py`
- Test: `tests/test_evidence.py`

**Interfaces:**
- Consumes: `CanonicalEvent`.
- Produces: `Evidence`, `score_evidence(event)`, `bind_evidence(events)`, `is_proven(step, evidence)`.

- [ ] Write failing tests proving `DONE` = 0, failed tests never prove, successful deterministic assertions can prove, wrong/unrelated evidence cannot prove.
- [ ] Run tests and verify failure.
- [ ] Implement explicit evidence classes and source/event binding.
- [ ] Run tests and verify pass.
- [ ] Commit: `feat: bind objective evidence to workflow steps`.

### Task 4: Workflow mining with contamination resistance

**Files:**
- Create: `src/skillsmith/mining.py`
- Test: `tests/test_mining.py`

**Interfaces:**
- Consumes: canonical events plus bound evidence.
- Produces: `WorkflowStep`, `Workflow`, `mine_workflows(sessions, *, min_successes=2)`.

- [ ] Write failing tests for repeated successful workflow extraction and failed-session contamination resistance.
- [ ] Add metamorphic test: adding many failed traces must not change promoted workflow.
- [ ] Run tests and verify failure.
- [ ] Implement minimal deterministic mining based on normalized step signatures and evidence-backed success.
- [ ] Run tests and verify pass.
- [ ] Commit: `feat: mine repeated proven workflows`.

### Task 5: Provenance + deterministic compiler

**Files:**
- Create: `src/skillsmith/provenance.py`
- Create: `src/skillsmith/compiler.py`
- Test: `tests/test_compiler.py`

**Interfaces:**
- Consumes: promoted `Workflow` objects.
- Produces: deterministic `SKILL.md`, `provenance.json`, and eval artifact bytes.

- [ ] Write failing tests for 100% instruction provenance, integrity hashes, and byte-identical output across equivalent input orderings.
- [ ] Run tests and verify failure.
- [ ] Implement deterministic rendering with sorted keys/records and normalized newlines.
- [ ] Run tests and verify pass.
- [ ] Commit: `feat: compile deterministic skill artifacts with provenance`.

### Task 6: Output safety and verification

**Files:**
- Create: `src/skillsmith/verify.py`
- Test: `tests/test_security.py`

**Interfaces:**
- Produces: `safe_output_path(root, relative)`, `verify_artifacts(...)`, `write_artifacts_safely(...)`.

- [ ] Write failing tests for `../` traversal, absolute paths, symlink escape, existing-output collision, and provenance tampering.
- [ ] Run tests and verify failure.
- [ ] Implement fail-closed path confinement and integrity verification.
- [ ] Run tests and verify pass.
- [ ] Commit: `feat: add fail-closed artifact safety checks`.

### Task 7: CLI and first-user path

**Files:**
- Create: `src/skillsmith/cli.py`
- Test: `tests/test_cli.py`

**Interfaces:**
- Produces commands: `skillsmith inspect <trace...>` and `skillsmith compile <trace...> --out <dir>`.

- [ ] Write failing CLI tests for happy path, malformed input, collision refusal, and nonzero failure exit codes.
- [ ] Run tests and verify failure.
- [ ] Implement CLI orchestration only; do not duplicate domain logic.
- [ ] Run tests and verify pass.
- [ ] Commit: `feat: add inspect and compile cli`.

### Task 8: Golden three-trace E2E demo

**Files:**
- Create: `tests/fixtures/golden/success-a.jsonl`
- Create: `tests/fixtures/golden/success-b.jsonl`
- Create: `tests/fixtures/golden/fail-done.jsonl`
- Create: `tests/test_golden.py`
- Create: `examples/golden/README.md`

**Interfaces:**
- Exercises the whole public pipeline.

- [ ] Write the three fixtures: two objectively successful repeated workflows and one failed `DONE` claim.
- [ ] Write E2E assertions: only A/B workflow promoted; failed shortcut absent; all instructions have valid provenance.
- [ ] Run test and verify failure before final integration wiring.
- [ ] Wire missing integration minimally.
- [ ] Run golden E2E and full suite.
- [ ] Commit: `test: add evidence-backed golden pipeline`.

### Task 9: Docs, license, CI, release gates

**Files:**
- Create: `README.md`
- Create: `LICENSE`
- Create: `CONTRIBUTING.md`
- Create: `SECURITY.md`
- Create: `docs/architecture.md`
- Create: `docs/schema.md`
- Create: `docs/evidence-model.md`
- Create: `docs/threat-model.md`
- Create: `.github/workflows/ci.yml`
- Create: `.github/ISSUE_TEMPLATE/bug_report.md`
- Create: `.github/ISSUE_TEMPLATE/feature_request.md`

**Interfaces:**
- Public install, quick-start, contributor, security and CI surface.

- [ ] Document only commands actually implemented and tested.
- [ ] Add Apache-2.0 license text.
- [ ] Add CI for supported Python versions, install, tests, and wheel build/install smoke test.
- [ ] Run the README quick-start from a clean environment locally where available.
- [ ] Commit: `docs: prepare SkillSmith v0.1 release surface`.

### Task 10: Final verification

**Files:**
- Modify only files required by failures found during verification.

- [ ] Run the complete test suite.
- [ ] Build a wheel and install it into a fresh virtual environment.
- [ ] Run the golden CLI demo from the installed wheel.
- [ ] Verify repeated runs produce byte-identical artifacts.
- [ ] Verify fixtures/output contain no obvious secrets.
- [ ] Check GitHub Actions for the exact commit after push.
- [ ] Do not mark COMPLETE unless every release gate in the spec passes.
- [ ] Commit fixes only if verification finds defects.
