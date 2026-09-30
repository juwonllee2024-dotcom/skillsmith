# Security Policy

SkillSmith processes agent traces as untrusted data. Historical command text must never be executed automatically. Output traversal, symlink escape, destructive overwrite, malformed trace input, provenance tampering, and unrelated-evidence binding are treated as security-relevant failures.

Please report suspected vulnerabilities privately through GitHub's security reporting features when available rather than opening a public issue. Do not include live credentials or private trace data.
