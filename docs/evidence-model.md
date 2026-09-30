# Evidence model

SkillSmith is deliberately conservative.

- `claim` events, including `DONE`, score 0.
- Failed tests score 0.
- A deterministic passing `test` or `assertion` scores as objective evidence in v0.1.
- Evidence must reference the exact workflow step; a passing test for another step cannot prove it.
- A workflow is promoted only when the same sequence is proven in at least two sessions by default.
- Failed traces cannot contribute source steps to a promoted workflow.
