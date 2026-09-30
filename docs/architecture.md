# Architecture

SkillSmith's v0.1 pipeline is:

`JSONL trace -> adapter -> canonical events -> evidence binding -> workflow mining -> deterministic compiler -> verification -> safe output`

The adapter converts untrusted JSONL to immutable canonical events. Evidence scoring recognizes only explicit deterministic success signals and binds them to exact step IDs. Mining groups identical proven step sequences across sessions and ignores failed/unproven sessions. The compiler emits deterministic `SKILL.md`, `provenance.json`, and `eval.json`. Verification checks provenance integrity before safe output writing.
