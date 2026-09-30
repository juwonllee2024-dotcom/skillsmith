# Contributing

1. Create a focused branch.
2. Add or update a failing test before changing production behavior.
3. Implement the smallest change that makes the test pass.
4. Run `pytest -q` before opening a pull request.
5. Preserve SkillSmith's fail-closed trust model: agent prose is not evidence, command text is inert, provenance is mandatory, and output must remain confined.

Bug reports should include a minimal sanitized trace when possible. Never post secrets, credentials, private prompts, or proprietary source data in public issues.
