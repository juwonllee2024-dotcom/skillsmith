# Trace schema

v0.1 accepts one JSON object per line.

A step:

```json
{"type":"step","payload":{"instruction":"run pytest -q"}}
```

A deterministic test result can bind to a step by source line:

```json
{"type":"test","payload":{"status":"passed","deterministic":true,"step_line":1}}
```

The adapter resolves `step_line` to the canonical content-derived `step_id`. Blank lines are ignored. Malformed JSON, non-object records, invalid step references, and oversized records fail closed with source file/line diagnostics.
