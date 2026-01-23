# Pandas to Polars Migration Command for Claude Code

**Automatically benchmark, migrate, and optimize your pandas code to Polars.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Polars](https://img.shields.io/badge/polars-1.0.0+-orange.svg)](https://pola.rs/)

---

## What This Does

This Claude Code command automatically:

1. **Benchmarks** your current pandas code
2. **Migrates** to Polars with performance optimizations
3. **Re-benchmarks** and shows exact speedup improvements

All in one command.

### Results Observed

- **8.2x faster** on data aggregations
- **50% lower** API latency
- **10-12x faster** on large CSV ETL (observed in the included smoke tests)

#### What 10-12x Means For Cloud Cost

If your pipeline is primarily compute-bound and billed roughly proportional to runtime (EC2/VMs, Batch jobs, container tasks), a **10-12x speedup** maps to about:

- `10x` -> **~90.0%** less compute time
- `12x` -> **~91.7%** less compute time

Back-of-napkin example (on-demand, 24/7, ~730 hours/month; compute only):

| Provider | Example VM | On-demand $/hour | Approx $/month | $/month @ 10x | $/month @ 12x |
|---|---|---:|---:|---:|---:|
| AWS | EC2 `m7i.xlarge` | $0.2016 | $147.17 | $14.72 | $12.26 |
| Azure | `Standard_D4as_v5` (Linux, East US) | $0.172 | $125.56 | $12.56 | $10.46 |
| GCP | Compute Engine `e2-standard-4` | $0.13402284 | $97.84 | $9.78 | $8.15 |

Pricing sources (as-of 2026-01-21; region/OS/pricing model changes will affect exact numbers):

- AWS EC2 `m7i.xlarge`: https://instances.vantage.sh/aws/ec2/m7i.xlarge
- Azure retail price API (`Standard_D4as_v5`): https://prices.azure.com/api/retail/prices
- GCP `e2-standard-4` pricing table: https://cloud.google.com/compute/all-pricing

Notes:

- These estimates assume you can actually downsize/scale-to-zero or reduce instance-hours. If you are provisioned 24/7 and don’t change instance count, you get latency/headroom, not savings.
- Storage, network egress, managed service fees, and minimum billing granularity can reduce realized savings.

---

## Installation

### Prerequisites

- [Claude Code CLI](https://github.com/anthropics/claude-code) installed
- Python 3.8+
- Polars 1.0.0+

### Install the Command

```bash
# Create commands directory if it doesn't exist
mkdir -p ~/.claude/commands

# Download the command
curl -o ~/.claude/commands/pandas-polars-migration.md \
  https://raw.githubusercontent.com/tommcrojo/pandas-polars-migration-claude/main/.claude/commands/pandas-polars-migration.md

# Install polars
pip install "polars>=1.0.0"
```

### Install Router + Mode-Specific Agents (Recommended)

The command works by itself, but for the best UX (and to better handle different pipeline architectures), install the bundled Claude Code agents too:

```bash
git clone https://github.com/tommcrojo/polars-migration.git
cd polars-migration/pandas-polars-migration-claude
./install.sh
```

This installs:

- `~/.claude/commands/pandas-polars-migration.md`
- `~/.claude/agents/pandas-polars-*.md` (router + in-memory/batch/sql specialists)

That's it! The command is now available in Claude Code.

---

## Quick Start

### Basic Usage

```bash
# Navigate to your project
cd your-project

# Run the migration command
claude /pandas-polars-migration your_script.py
```

### OpenCode Usage (Recommended If You Hit Claude Limits)

This repo also ships an OpenCode subagent at `pandas-polars-migration-claude/.opencode/agent/pandas-polars-migration.md`.

Run it with the Z.ai Coding Plan GLM 4.7 model:

```bash
opencode run \
  --model zai-coding-plan/glm-4.7 \
  --agent pandas-polars-migration \
  "Migrate this path in-place: your_script.py"
```

Notes:

- The agent rewrites the target file in-place to Polars and creates a single pandas backup file.
- It benchmarks before/after and reports the measured numbers (no placeholder speedup claims).

### Migrate Multiple Files

```bash
# Migrate entire directory
claude /pandas-polars-migration src/data/

# Migrate specific files
claude /pandas-polars-migration pipeline1.py pipeline2.py
```

---

## Example

### Before (Pandas)

```python
import pandas as pd

def process_sales_data(file_path: str):
    df = pd.read_csv(file_path)
    df['date'] = pd.to_datetime(df['date'])
    df_filtered = df[df['amount'] > 100]

    top_products = df.groupby('product')['amount'].sum().sort_values(ascending=False).head(10)
    df['amount_normalized'] = df.groupby('region')['amount'].transform(
        lambda x: (x - x.mean()) / x.std()
    )
    return df
```

### After (Polars - Optimized)

```python
import polars as pl

def process_sales_data(file_path: str):
    df = (
        pl.scan_csv(file_path)
        .with_columns(
            pl.col('date').str.strptime(pl.Date, format='%Y-%m-%d')
        )
        .filter(pl.col('amount') > 100)
    )

    top_products = (
        df.group_by('product')
        .agg(pl.col('amount').sum())
        .sort('amount', descending=True)
        .head(10)
        .collect()
    )

    df_normalized = df.with_columns(
        ((pl.col('amount') - pl.col('amount').mean().over('region')) /
         pl.col('amount').std().over('region')).alias('amount_normalized')
    ).collect()

    return df_normalized
```

### Performance Comparison

```
═══════════════════════════════════════════════════════════════
🚀 PANDAS → POLARS MIGRATION RESULTS
═══════════════════════════════════════════════════════════════

Files Migrated: 1
Total Lines Changed: 23

PERFORMANCE COMPARISON
───────────────────────────────────────────────────────────────
Metric              Pandas        Polars        Speedup
───────────────────────────────────────────────────────────────
Read CSV            245.50ms      89.20ms       2.75x
Type Conversion     123.80ms      12.40ms       9.98x
Aggregations        892.30ms      108.70ms      8.21x
───────────────────────────────────────────────────────────────
TOTAL               1261.60ms     210.30ms      6.00x
═══════════════════════════════════════════════════════════════

OPTIMIZATIONS APPLIED:
- Lazy evaluation with scan_csv() + collect()
- Parallel expression execution (3 operations combined)
- Window functions with .over() (1 replacement)
- Removed index operations (0 instances)

FILES MODIFIED:
- demo_pandas_pipeline.py (23 lines changed)

Next steps:
1. Review migrated code in demo_pandas_pipeline.py
2. Run your test suite to verify correctness
3. Update requirements.txt: remove pandas, add polars
```

---

## What Makes This Different

We write **OPTIMIZED** Polars code:

### Optimizations Applied

| Optimization | Description |
|--------------|-------------|
| **Lazy Evaluation** | Uses `scan_csv()` + `collect()` for query optimization |
| **Parallel Execution** | Combines operations in single `with_columns()` |
| **Window Functions** | Replaces `groupby().transform()` with `.over()` |
| **No Index Operations** | Removes pandas index overhead |
| **Streaming Mode** | Enables streaming for large datasets (>1GB) |
| **Strict Typing** | Explicit type conversions for better performance |

All following official [Polars best practices](https://docs.pola.rs/user-guide/misc/performance/).

---

## Perfect For

- **ETL pipelines** - Speed up data transformations
- **ML preprocessing** - Faster feature engineering
- **API data processing** - Reduce latency
- **Log analytics** - Handle larger datasets
- **Any pandas code > 10K rows** - Significant speedup gains

---

## How It Works

The command follows a 6-phase workflow:

1. **DISCOVER & ANALYZE** - Find pandas usage patterns
2. **BENCHMARK BASELINE** - Measure current performance
3. **MIGRATE TO POLARS** - Apply optimization rules
4. **BENCHMARK OPTIMIZED** - Measure new performance
5. **REPORT RESULTS** - Show detailed comparison
6. **VERIFICATION** - Provide next steps

---

## Requirements

- **Python**: 3.8+
- **Polars**: >= 1.0.0 (tested with 1.0.0)
- **Pandas**: (for the original code being migrated)
- **Claude Code**: Latest version

The command was built using Polars 1.0.0 documentation and best practices.

---

## Examples

Check out the [`examples/`](examples/) directory for:

- **`demo_pandas_pipeline.py`** - Before: pandas implementation
- **`demo_polars_pipeline.py`** - After: optimized Polars implementation (generated)
- **`sales_data.csv`** - Sample dataset (50K rows)
- **`benchmark_results.md`** - Real benchmark data
- **`generate_data.py`** - Script to generate test data

### Try the Demo

```bash
# Clone the repo
git clone https://github.com/tommcrojo/pandas-polars-migration-claude.git
cd pandas-polars-migration-claude/examples

# Generate sample data
python3 generate_data.py

# Run the pandas version
python3 demo_pandas_pipeline.py

# Run the migration command
claude /pandas-polars-migration demo_pandas_pipeline.py

# Compare results!
```

### CLI Smoke Test (Jan 2026)

Ran a clean-room smoke test in a standalone folder (`polars-migration-smoke-test/`) that:

1. Generates synthetic CSVs (50K + 500K rows)
2. Runs a pandas ETL pipeline + pytest
3. Benchmarks baseline performance
4. Runs Claude Code migration (`/pandas-polars-migration`)
5. Re-runs pytest and benchmarks again

Environment:

- Claude Code: `2.1.14`
- Python: `3.12.3`
- pandas: `3.0.0`
- polars: `1.37.1`

Command used (non-interactive approvals):

```bash
claude --permission-mode bypassPermissions /pandas-polars-migration etl_pipeline.py
```

Also tested alternative CLIs/models to avoid hitting Claude usage limits:

- OpenCode + `zai-coding-plan/glm-4.7` (attempted; agent wiring needs follow-up)
- Gemini CLI + `gemini-3-flash-preview` (successful in-place migration; ~10x on 500k rows)

Benchmark dataset: `transactions_big.csv` (500,000 rows), 7 runs, 2 warmups:

| Version | Mean (ms) | Stdev (ms) | Speedup |
|--------|----------:|-----------:|--------:|
| Pandas baseline | 734.40 | 22.07 | 1.00x |
| Polars (after Claude) | 60.34 | 3.47 | **12.17x** |

Optimizations included in the command (only applied when safe/useful for large CSV pipelines):

- Avoided datetime parsing by extracting `month` via string slice (`YYYY-MM`) when timestamps are ISO-like and only month is needed
- Added explicit CSV schemas (skip type inference)
- Projected only used columns (less I/O)
- Removed intermediate `gross` column; computed `revenue` in one expression
- Reused `mean/std` window stats to avoid recomputing
- Used `.collect(engine="streaming")` when the plan supports streaming

Artifacts produced by the command in the smoke-test folder:

- `etl_pipeline_pandas_original.py` (auto-backup of original pandas file)
- `MIGRATION_REPORT.md` (detailed notes)
- `validate_migration.py` (output equivalence check)

---

## Important Notes

- Always **backup your code** or work in a git branch
- Polars syntax is **stricter than pandas** - type errors will surface
- Run your **test suite** after migration to verify correctness
- The command focuses on **common pandas operations**; complex edge cases may require manual review
- Update `requirements.txt`: remove pandas, add polars

---

## Contributing

Contributions are welcome! Here's how you can help:

1. **Report bugs** - Open an issue with details
2. **Suggest features** - What pandas patterns should we support?
3. **Submit PRs** - Improve migration rules or add optimizations
4. **Share results** - Post your benchmark improvements!

---

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

## Links

- [Polars Documentation](https://docs.pola.rs/)
- [Claude Code](https://github.com/anthropics/claude-code)
- [LinkedIn Post](LINKEDIN_POST.md) - Announcement & discussion
- [Blog Post](#) - Coming soon: detailed technical deep dive

---

## Show Your Support

If this command helped you, please:

- Star this repo
- Share on social media
- Share your benchmark results in Issues
- Contribute improvements

---

## Contact

Questions or feedback? Open an issue or reach out on [LinkedIn](https://linkedin.com/in/tommcrojo).

---

**Built by [tommcrojo](https://github.com/tommcrojo)**

*Try it before scaling infrastructure. You might not need that bigger instance.*
