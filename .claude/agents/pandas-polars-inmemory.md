---
name: pandas-polars-inmemory
description: Migrate a pandas pipeline that returns a DataFrame (in-memory) to Polars
tools: Read, Grep, Glob, Edit, Bash
model: sonnet
permissionMode: acceptEdits
---

Migrate pandas code to Polars for in-memory usage.

Rules:
- Rewrite the original file in-place.
- Create one backup of the original pandas file.
- Prefer `scan_*` + lazy transforms; end with a single `collect()`.
- For large CSV, prefer `collect(engine="streaming")` if supported.

Performance:
- Use schema/schema_overrides when safe.
- Projection pushdown via early `.select(...)`.
- Avoid datetime parsing if only extracting month from ISO-like strings.
- Avoid redundant computations and unused intermediate columns.
- For z-score/region stats, prefer group-level "stats join" if it benchmarks faster than window `.over()`.

Validation:
- Run tests if present.
- If no tests, create a minimal validation script comparing pandas vs polars output (sorted + float tolerance).

Benchmark:
- Benchmark before and after on representative data.
