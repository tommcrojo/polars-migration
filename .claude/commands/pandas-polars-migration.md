---
name: pandas-polars-migration
description: Benchmarks pandas code, migrates to Polars with optimizations, re-benchmarks, and shows performance improvements. Use when user wants to optimize pandas pipelines.
argument-hint: [file_path or directory]
model: sonnet
---

# Pandas → Polars Migration with Benchmarking

You are running the **pandas-polars-migration** workflow to automatically optimize data processing code.

## Target
Migrate: $ARGUMENTS

If no path provided, search for Python files with pandas imports in current directory.

## Prerequisites Check
Before starting migration:
1. Verify polars is installed: `python -c "import polars; print(polars.__version__)"`
2. Required version: polars >= 1.0.0 (tested with 1.0.0)
3. If not installed: `pip install "polars>=1.0.0"`

## Git Branch Setup (if in git repo)
**IMPORTANT: Always work in a separate branch for safety**

1. **Check if in git repository:**
   - Run: `git rev-parse --git-dir 2>/dev/null`
   - If exit code is 0, we're in a git repo
   - If not in git repo, skip this section and proceed to Phase 1

2. **If in git repo, create migration branch:**
   - Check current branch: `git branch --show-current`
   - Check for uncommitted changes: `git status --porcelain`

3. **Handle uncommitted changes:**
   - If uncommitted changes exist:
     - **STOP and warn user**: "WARNING: You have uncommitted changes. Please commit or stash them before migration."
     - Show: `git status`
     - Recommend: "Run `git add . && git commit -m 'Pre-migration snapshot'` or `git stash`"
     - **DO NOT PROCEED** until working directory is clean

4. **Create and switch to migration branch:**
   - Check if `polars-migration` branch already exists: `git branch --list polars-migration`
   - If exists:
     - Warn: "Branch 'polars-migration' already exists. Switch to it or use different name?"
     - Options:
       1. Switch to existing branch: `git checkout polars-migration`
       2. Create timestamped branch: `polars-migration-YYYYMMDD-HHMMSS`
   - If doesn't exist:
     - Create and switch: `git checkout -b polars-migration`
     - Confirm: "Created branch 'polars-migration' from [base_branch]"

5. **Success message:**
   ```
   Git setup complete
   - Working in branch: polars-migration
   - Base branch: [original_branch]
   - All changes will be isolated in this branch
   ```

## Reference Documentation
Use these official Polars resources for accurate syntax and best practices:

**Core Documentation:**
- Polars User Guide: https://docs.pola.rs/
- API Reference: https://docs.pola.rs/api/python/stable/reference/index.html
- Lazy API: https://docs.pola.rs/api/python/stable/reference/lazyframe/index.html

**Migration & Optimization Guides:**
- Coming from Pandas: https://docs.pola.rs/user-guide/migration/pandas/
- Lazy/Eager API: https://docs.pola.rs/user-guide/concepts/lazy-vs-eager/
- Performance: https://docs.pola.rs/user-guide/misc/performance/

**Key Operations:**
- Expressions: https://docs.pola.rs/user-guide/expressions/
- Window Functions: https://docs.pola.rs/user-guide/expressions/window-functions/
- Group By: https://docs.pola.rs/user-guide/transformations/group-by/
- Streaming: https://docs.pola.rs/user-guide/concepts/streaming/

**When in doubt, use WebFetch to read these documentation pages for accurate, up-to-date syntax.**

## Phase 1: DISCOVER & ANALYZE
1. Find all Python files using pandas:
   - Use Grep to find `import pandas` or `import pandas as pd`
   - Read each file to understand data operations
   - Identify: CSV I/O, filtering, groupby, aggregations, type conversions

2. Extract the data pipeline operations:
   - Read operations (read_csv, read_excel, etc.)
   - Transformations (assign, loc, iloc, merge, join)
   - Aggregations (groupby, value_counts, mean, sum)
   - Output operations (to_csv, to_parquet, etc.)

3. Create benchmark harness:
   - Write benchmark script that measures current pandas performance
   - Measure: read time, transformation time, aggregation time, total time
   - Use `time.perf_counter()` for microsecond precision

### Choose The Right ETL Mode (Router)

Before rewriting code, classify the pipeline into one primary mode and optimize accordingly.

Modes:

1. **In-memory (returns a DataFrame)**
   - Used by downstream Python code (APIs/notebooks); final result is materialized.
2. **Batch ETL (writes datasets)**
   - Terminal step writes CSV/NDJSON/IPC/Parquet and the job ends.
3. **SQL-first**
   - Pipeline is primarily expressed as SQL strings and execution is SQL-driven.

Detection heuristics:

- Terminal `to_parquet/to_csv/to_json/to_feather` or storage writes -> Batch ETL.
- Returning a DataFrame to callers -> In-memory.
- Large SQL strings / SQL engine as the primary representation -> SQL-first.

If custom agents are installed (recommended), delegate via the Task tool:

- `pandas-polars-router` (orchestrator)
- `pandas-polars-inmemory`
- `pandas-polars-batch`
- `pandas-polars-sql`

## Phase 2: TEST VERIFICATION (PRE-MIGRATION)
**CRITICAL: Verify business logic correctness before and after migration**

1. **Detect existing tests:**
   - Search for test files: `test_*.py`, `*_test.py`, or `tests/` directory
   - Look for pytest, unittest, or other test frameworks
   - Check for test functions related to the code being migrated

2. **Run existing tests (if found):**
   - Execute test suite: `pytest -v` or `python -m unittest discover`
   - Capture baseline test results (all tests should pass)
   - Store test output for comparison after migration
   - **If tests fail before migration, STOP and inform user to fix tests first**

3. **If no tests exist - CREATE VALIDATION TEST:**
   - **WARN the user**: "WARNING: No tests detected. Creating automatic validation test to verify correctness."
   - **Generate a comparison test script** that:
     1. Runs the original pandas code on sample/test data
     2. Captures the output (dataframes, aggregations, values)
     3. Saves this as the "expected output"
     4. Will be used to validate the Polars version produces identical results

   **Create `_migration_validation_test.py`:**
   ```python
   """
   Automatic validation test for pandas-to-polars migration.
   This test compares outputs from original pandas code vs migrated polars code.
   """
   import pandas as pd
   import polars as pl
   import numpy as np

   def compare_dataframes(df_pandas, df_polars, name="DataFrame"):
       """Compare pandas and polars dataframes for equality."""
       # Convert Polars to pandas for comparison
       df_polars_as_pandas = df_polars.to_pandas()

       # Sort both by all columns to handle order differences
       df_pandas_sorted = df_pandas.sort_values(by=list(df_pandas.columns)).reset_index(drop=True)
       df_polars_sorted = df_polars_as_pandas.sort_values(by=list(df_polars_as_pandas.columns)).reset_index(drop=True)

       # Compare shapes
       assert df_pandas_sorted.shape == df_polars_sorted.shape, \
           f"{name} shape mismatch: pandas {df_pandas_sorted.shape} vs polars {df_polars_sorted.shape}"

       # Compare values (with tolerance for floating point)
       pd.testing.assert_frame_equal(
           df_pandas_sorted,
           df_polars_sorted,
           check_dtype=False,  # Allow type differences
           atol=1e-6,  # Floating point tolerance
           rtol=1e-6
       )
       print(f"{name} outputs match!")

   def test_original_vs_migrated():
       # [Insert actual test code that runs both versions and compares]
       pass
   ```

4. **Test strategy guidance:**
   - If tests exist: "Found X test files. Running pre-migration tests..."
   - If no tests: "WARNING: No tests found. Creating automatic validation test to compare pandas vs polars outputs..."

## Phase 3: BENCHMARK BASELINE
1. Run benchmark on original pandas code
2. Capture metrics:
   - Read time (ms)
   - Type conversion time (ms)
   - Transformation/aggregation time (ms)
   - Total time (ms)
   - Memory usage (if possible via memory_profiler)
3. Store baseline results

## Phase 4: MIGRATE TO POLARS
Apply these optimization rules during migration:

### In-Place Migration (IMPORTANT)

When the target is a file path (e.g. `some_pipeline.py`), you MUST:

1. Rewrite the original file in-place to the final Polars implementation.
2. Create exactly one backup of the original pandas file (recommended name pattern: `<original_stem>_pandas_backup.py`) unless the user already has git.
3. Avoid leaving multiple alternative implementations around (do NOT create both `*_polars.py` and `*_polars_optimized.py`).

The goal is that the user runs their original entrypoint filename and immediately experiences the performance improvement.

### Choose The Right Pipeline Mode (IMPORTANT)

Before rewriting code, classify the pipeline into one primary mode and optimize accordingly:

1. **In-memory (returns a DataFrame)**
   - The function returns a DataFrame to Python or is used by downstream in-process code (APIs/notebooks).
2. **Batch ETL (writes datasets)**
   - The pipeline's terminal step writes CSV/NDJSON/IPC/Parquet (local or object storage) and the job ends.
3. **SQL-driven**
   - The pipeline is primarily expressed as SQL strings and execution is SQL-first.

Detection heuristics:

- Terminal `to_parquet/to_csv/to_json/to_feather` (or writing to S3/GCS/Azure) -> Batch ETL.
- Returning a DataFrame to callers -> In-memory.
- Large SQL strings as the main execution path -> SQL-driven.

Mode-specific optimization:

- **In-memory**: `scan_*` + lazy transforms + one final `.collect()` (prefer `engine="streaming"` for large data).
- **Batch ETL**: prefer end-to-end lazy + `sink_*` so Polars can stream without materializing.
  - Use `LazyFrame.sink_parquet/sink_csv/sink_ndjson/sink_ipc` instead of `collect() + write_*` when possible.
  - For partitioned outputs, prefer partitioning APIs (e.g. `pl.PartitionBy` / sink partition args) over manual Python loops.
- **SQL-driven**: if the pipeline is already SQL-first, consider Polars SQL (`SQLContext`/`.sql()`).
  - Polars 1.37 includes significant SQL ORDER BY speedups; do not force a rewrite to SQL if code is not SQL-first.

### Core Polars Optimization Rules:
1. **Use lazy evaluation**: Replace `pl.read_csv()` with `pl.scan_csv()` + `.collect()`
2. **Parallelize expressions**: Combine operations in single `with_columns(expr1, expr2, expr3)`
3. **Window functions**: Replace `groupby().transform()` with `.with_columns(...over())`
4. **No index operations**: Remove all `.loc`, `.iloc`, `reset_index()` calls
5. **Strict typing**: Explicit type conversions (no auto float casting)
6. **Schema + projection pushdown** (big CSVs): provide explicit `schema`/`schema_overrides` and select only used columns early
7. **Avoid expensive parsing when unnecessary**: if a timestamp string is only used to derive `YYYY-MM`, slice the string instead of parsing datetime
8. **Streaming for large data**: Use `.collect(engine="streaming")` when the plan supports streaming and the dataset is large
9. **Avoid redundant work**: don't compute the same expression twice; avoid creating intermediate columns that are never used downstream

### When To Apply The “Big Dataset” Optimizations

Apply rules (6)-(8) when any of the following are true:

- Input is a CSV and `scan_csv(...)` is used AND the file is "large" (recommend heuristics: >= 50MB on disk OR >= 500k rows OR the pipeline is known to be production-scale).
- The pipeline performs heavy operations that benefit from reduced IO and memory pressure (joins + group_by aggregations + window expressions).

Do NOT apply these if they would change semantics or you cannot prove they are safe from the code/tests.

**Schema + projection pushdown conditions:**

- You can infer stable dtypes from:
  - pandas `read_csv(..., dtype=...)` arguments, OR
  - explicit casts in code (`astype`, `to_numeric`), OR
  - usage patterns (IDs only compared/joined => integer; prices/amounts used in arithmetic => float; categorical strings => Utf8).
- If you are unsure about a dtype, do not force it; prefer leaving inference on for that column.
- Prefer `schema_overrides={...}` for a partial, safer schema when you can only confidently type a subset of columns (especially numeric/join-key columns).
- Always project (`select(...)`) only the columns referenced downstream (filters/joins/aggs/outputs).

**Avoid datetime parsing conditions:**

- The source timestamp column is a string that appears ISO-like (`YYYY-MM-...`) AND the code only needs a month key like `YYYY-MM`.
- Safe replacement patterns:
  - pandas: `pd.to_datetime(df["ts"]).dt.to_period("M").astype(str)`
  - polars (fast path): `pl.col("ts").str.slice(0, 7).alias("month")`
- If the code uses timezone-aware logic, day-level filters, date arithmetic, or anything beyond extracting month, DO parse to a datetime.

**Streaming collect conditions:**

- Prefer: `.collect(engine="streaming")` (NOT `streaming=True`, which is deprecated in recent Polars).
- Use only when the query plan is streaming-compatible; if streaming errors or regresses performance, fall back to `.collect()`.

### Migration Mappings:
| Pandas | Polars |
|--------|--------|
| `pd.read_csv()` | `pl.scan_csv()` (lazy) |
| `df["col"]` | `df.select("col")` |
| `df[df["a"] > 10]` | `df.filter(pl.col("a") > 10)` |
| `df.assign()` | `df.with_columns()` |
| `df.groupby("col").sum()` | `df.group_by("col").agg(pl.col().sum())` |
| `pd.to_datetime()` | `pl.col().str.strptime(pl.Datetime)` |
| `value_counts()` | `group_by().len().sort("len", descending=True)` |
| `.isin()` | `.is_in()` |
| `.mean()` on Series | `select(pl.col().mean()).item()` |

### Migration Steps:
1. Replace pandas imports: `import polars as pl`
2. Convert read operations to lazy: `scan_csv()` instead of `read_csv()`
3. If migrating CSV reads for large datasets:
   - Add `schema`/`schema_overrides` where safe
   - Add early `.select(...)` to keep only referenced columns
4. Rewrite filtering with `pl.col()` expressions and filter early to reduce volume
5. Combine sequential operations into parallel expressions
6. Replace groupby+transform with `.over()` patterns
   - IMPORTANT: avoid recomputing window stats; compute mean/std once (temp cols) and reuse
7. Drop columns as soon as they are no longer needed (e.g. raw timestamp after `month` derived)
   - Also drop unused intermediate columns (e.g. `gross`) if they are not referenced later
8. Add `.collect()` at the end of lazy chains
   - For large datasets, prefer `.collect(engine="streaming")` if supported
9. Ensure proper type handling (no auto-coercion assumptions)

### Output File Rules

- If migrating a single file, the final Polars code MUST be written back to that same file path.
- If you create a backup, ensure the backup is not imported by the rest of the project (it is only for reference).
- Only create extra helper scripts (benchmarks/validation) if needed for benchmarking/correctness; keep them minimal.

## Phase 5: BENCHMARK OPTIMIZED CODE
1. Run same benchmark on Polars code
2. Capture same metrics
3. Calculate speedup ratios:
   - `speedup = pandas_time / polars_time`
4. Generate comparison report

## Phase 6: TEST VERIFICATION (POST-MIGRATION)
**CRITICAL: Verify business logic is preserved after migration**

WARNING:**NEVER MODIFY TEST FILES** - Tests are the source of truth. Only fix the migrated code.

1. **Run tests again (if they existed):**
   - Execute the same test suite: `pytest -v` or `python -m unittest discover`
   - Compare results with pre-migration baseline
   - **All tests that passed before MUST pass now**

2. **Test result comparison:**
   - **All tests pass**: "All X tests passed! Business logic preserved." → Continue to Phase 7
   - ✗ **Tests fail**: Proceed to iterative fixing (step 3)

3. **If tests failed - ITERATIVE FIX LOOP:**

   **IMPORTANT RULES:**
   - **NEVER modify test files** unless explicitly told by the user
   - **Only fix the migrated code** to match expected behavior
   - **Run tests after each fix** until all tests pass
   - **Maximum 5 fix iterations** - if still failing, report to user for manual review

   **For each failing test:**

   a. **Analyze the failure:**
      - Read the test file to understand expected behavior
      - Compare test output with error message
      - Identify root cause in migrated code

   b. **Common migration issues to check:**
      - Type handling differences (int vs float with nulls)
      - Column ordering changes (Polars doesn't preserve arbitrary order)
      - Precision differences in floating point operations
      - Missing null handling (Polars strict nulls vs pandas NaN)
      - DataFrame vs LazyFrame (forgot `.collect()`)
      - Index operations removed incorrectly
      - Date/datetime parsing format issues
      - Aggregation result structure differences

   c. **Fix the migrated code:**
      - Make targeted fixes to address the specific test failure
      - DO NOT modify tests - they define the expected behavior
      - Preserve the Polars optimizations where possible
      - If optimization conflicts with correctness, prioritize correctness

   d. **Re-run tests:**
      - Execute test suite again: `pytest -v` or `python -m unittest discover`
      - Check if this fix resolved the issue
      - Document what was fixed

   e. **Iterate until all tests pass:**
      - Repeat steps a-d for each remaining failure
      - Track number of iterations (max 5)
      - After each iteration, report progress: "Fixed X issues, Y tests still failing"

   f. **If max iterations reached (5) and tests still fail:**
      - Document all remaining failures clearly
      - Explain what was attempted and why it didn't work
      - Provide the best-effort migrated code
      - Recommend: "Manual review required. Consider these approaches:
        1. Review failing test expectations vs migrated code output
        2. Check if Polars behavior fundamentally differs from pandas
        3. May need to adjust migration strategy for specific operations"

4. **Success criteria:**
   - All tests that passed pre-migration now pass post-migration
   - No test files were modified
   - Business logic is preserved

5. **If no tests existed but validation test was created:**

   **Run the auto-generated validation test:**

   a. **Execute the validation test:**
      - The test compares pandas output (baseline) with polars output (migrated)
      - Run: `python _migration_validation_test.py`
      - This validates correctness even without formal test suite

   b. **If validation test passes:**
      - "Validation successful! Pandas and Polars outputs match."
      - Proceed to Phase 7

   c. **If validation test fails - ITERATIVE FIX LOOP:**
      - Follow the same iterative fix process as step 3 above
      - Analyze differences between pandas and polars outputs
      - Fix the migrated code (not the validation test)
      - Re-run validation test
      - Iterate up to 5 times until outputs match

   d. **Common issues when outputs don't match:**
      - Column order differs (Polars doesn't preserve arbitrary order)
      - Floating point precision differences
      - Null handling (NaN vs null)
      - Type differences (int64 vs int32, etc.)
      - Index included in pandas output but not polars
      - Aggregation result structure (Series vs DataFrame)

   e. **If validation fails after 5 iterations:**
      - Provide detailed comparison of outputs
      - Show what's different and why
      - Recommend manual review
      - Keep the validation test for user to debug further

   f. **Cleanup:**
      - Ask user: "Keep validation test for future reference? (y/n)"
      - If no, delete `_migration_validation_test.py`
      - If yes, document that it can be used for regression testing

## Phase 7: ATOMIC COMMITS (if in git repo)
**If working in a git repository, make atomic commits throughout the process**

WARNING:**Make commits after each major phase for clear history and easy rollback**

### Commit 1: After Phase 2 - Add validation test (if created)
**When:** After creating `_migration_validation_test.py` (if no tests existed)

```bash
git add _migration_validation_test.py
git commit -m "Add pandas baseline validation test for migration

- Created automatic validation test to compare outputs
- Captures expected behavior before Polars migration
- Will be used to verify correctness after migration"
```

### Commit 2: After Phase 4 - Migrate code to Polars
**When:** After completing the migration but before running tests

```bash
git add [migrated_file1.py] [migrated_file2.py]
git commit -m "Migrate pandas code to Polars with optimizations

Optimizations applied:
- Lazy evaluation with scan_csv() + collect()
- Parallel expression execution ([X] operations combined)
- Window functions with .over() ([Y] replacements)
- Removed index operations ([Z] instances)

Files migrated:
- file1.py: [brief description]
- file2.py: [brief description]

Performance (preliminary):
- [X]x faster read operations
- [Y]x faster aggregations"
```

### Commit 3: After Phase 6 - Fix test failures (if any)
**When:** After fixing failing tests (create one commit per fix iteration or batch related fixes)

```bash
# If tests failed and were fixed
git add [fixed_files]
git commit -m "Fix Polars migration issues to pass tests

Fixed issues:
- [Issue 1]: [Description of fix]
- [Issue 2]: [Description of fix]

Tests now passing: [X/Y]"
```

**Repeat for each fix iteration if needed (up to 5 times)**

### Commit 4: Final summary commit (optional)
**When:** After all tests pass and migration is complete

```bash
git commit --allow-empty -m "Migration complete: pandas to Polars

Summary:
- Files migrated: [X]
- Lines changed: [Y]
- Performance improvement: [Z]x speedup
- Tests: [All passing / N/A]
- Validation: [Passed / Manual review required]

Ready for review and merge to [base_branch]"
```

**Commit Strategy:**
- **DO**: Make atomic commits for each logical change
- **DO**: Include performance metrics in commit messages
- **DO**: Reference which tests were fixed in each commit
- **DON'T**: Make one big commit with all changes
- **DON'T**: Commit broken/failing code (unless max iterations reached)

## Phase 8: REPORT RESULTS
Output format:
```
═══════════════════════════════════════════════════════════════
PANDAS TO POLARS MIGRATION RESULTS
═══════════════════════════════════════════════════════════════

Files Migrated: X
Total Lines Changed: Y

PERFORMANCE COMPARISON
───────────────────────────────────────────────────────────────
Metric              Pandas        Polars        Speedup
───────────────────────────────────────────────────────────────
Read CSV            XXX.XXms      XX.XXms       X.Xx
Type Conversion     XXX.XXms      XX.XXms       X.Xx
Aggregations        XXX.XXms      XX.XXms       X.Xx
───────────────────────────────────────────────────────────────
TOTAL               XXX.XXms      XX.XXms       X.Xx
═══════════════════════════════════════════════════════════════

OPTIMIZATIONS APPLIED:
- Lazy evaluation with scan_csv() + collect()
- Parallel expression execution (X operations combined)
- Window functions with .over() (X replacements)
- Removed index operations (X instances)
- [Other specific optimizations]

MEMORY SAVINGS: X% reduction (if measured)

TEST VERIFICATION:
[If tests existed and all passed]
All X tests passed - Business logic preserved!

[If tests existed and some failed after 5 iterations]
WARNING: Y tests still failing after fixes - Manual review required
    Failed tests: [list test names]

[If no tests existed, but validation test was created]
Validation test passed - Pandas and Polars outputs match!
    (Validation test saved as: _migration_validation_test.py)

[If no tests existed and validation failed]
WARNING: Validation test shows differences - Manual review recommended
    See _migration_validation_test.py for details

FILES MODIFIED:
- path/to/file1.py (X lines changed)
- path/to/file2.py (Y lines changed)

[If validation test was created]
FILES CREATED:
- _migration_validation_test.py (automatic validation)

[If in git repo]
GIT STATUS:
All changes committed to branch: polars-migration
  Base branch: [original_branch]

Next steps:
1. Review migrated code in [file paths]
2. [If tests passed] Tests verified - ready for production!
3. [If no tests] Run the validation test: python _migration_validation_test.py
4. Update requirements.txt: remove pandas, add polars>=1.0.0
5. [If in git repo] Review changes: git diff [base_branch]
6. [If in git repo] Merge when ready: git checkout [base_branch] && git merge polars-migration
7. Consider performance testing with larger datasets
```

## Phase 8: CLEANUP & RECOMMENDATIONS

1. **Git workflow (if in git repo):**
   - Inform user they're in branch `polars-migration`
   - Suggest reviewing changes: `git diff [base_branch]...polars-migration`
   - Provide merge instructions:
     ```bash
     # Review changes
     git log --oneline [base_branch]..polars-migration

     # When satisfied, merge to base branch
     git checkout [base_branch]
     git merge polars-migration

     # Or create a pull request if using GitHub/GitLab
     git push origin polars-migration
     ```
   - If tests failed, warn: "WARNING: Do not merge until all tests pass!"

2. **Additional verification steps:**
   - Test with production-like data volumes
   - Verify edge cases (nulls, empty datasets, large files)
   - Check memory usage improvements
   - Profile performance on actual workloads

3. **Dependencies update:**
   - Update `requirements.txt` or `pyproject.toml`:
     - Remove: `pandas`
     - Add: `polars>=1.0.0`
   - Update any documentation mentioning pandas
   - Update CI/CD pipelines if needed

4. **Documentation and resources:**
   - Link to Polars docs: https://docs.pola.rs/
   - Performance tuning: https://docs.pola.rs/user-guide/misc/performance/
   - Migration guide: https://docs.pola.rs/user-guide/migration/pandas/

5. **Edge cases requiring manual review:**
   - MultiIndex usage (not supported in Polars)
   - Pandas plotting functions (`.plot()`)
   - Pandas-specific datetime operations
   - Complex custom apply functions
   - Integration with pandas-only libraries

## Important Notes:
- Always maintain a backup or work in git branch
- Polars syntax is stricter than pandas - type errors will surface
- Large datasets (>RAM) benefit from streaming: `.collect(engine="streaming")`
- If code uses pandas-specific features (MultiIndex, plotting), flag for manual review
- Update imports: `polars` should be in requirements.txt
- The command focuses on common pandas operations; complex edge cases may require manual review
- Always run your existing test suite after migration to verify correctness

## Error Handling:
- If polars is not installed, provide installation instructions
- If input file doesn't use pandas, inform user and exit gracefully
- If migration encounters unsupported pandas features, document them clearly
- If benchmarking fails, still provide the migrated code with a note
