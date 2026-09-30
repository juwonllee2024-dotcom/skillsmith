# Threat model

SkillSmith assumes trace data may be hostile.

## Defenses

- Historical command text is data only; v0.1 has no command-execution primitive.
- JSONL record size is bounded and malformed records fail closed.
- Output paths are resolved beneath the requested root; traversal and symlink escape are rejected.
- Existing output files are not overwritten.
- All target paths are preflighted before writing to avoid partial output on collision.
- Provenance hashes are recomputed from canonical source events and tampering is rejected.
- Evidence is bound to exact step IDs, preventing unrelated green tests from proving a workflow.

## Out of scope

v0.1 does not execute historical traces, provide a cloud service, or autonomously modify itself.
