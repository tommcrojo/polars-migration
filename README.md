# Pandas → Polars Migration Command for Claude Code

Automatically benchmark, migrate, and optimize your pandas code to Polars.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Polars](https://img.shields.io/badge/polars-1.0.0+-orange.svg)](https://pola.rs/)

---

## What This Does

```bash
claude /pandas-polars-migration your_script.py
```

One command. That's it.

The command benchmarks your current pandas code, migrates it to Polars with optimizations, then re-benchmarks to show you exactly what changed. No guessing, no manual translation, no hoping you didn't break something.

---

## Real Results

I've been testing this on real projects:

| Metric | Result |
|--------|--------|
| Data aggregations | **8.2x faster** |
| API latency | **50% lower** |
| Large CSV ETL (500K rows) | **12.17x faster** |

A 10x speedup on compute-bound pipelines means roughly **90% less compute time**. Before you scale infrastructure, see if the code itself is the bottleneck.

---

## What Actually Changes

This isn't a naive syntax swap. The command writes optimized Polars code.

**Before (Pandas):**
```python
import pandas as pd

df = pd.read_csv(file_path)
df['date'] = pd.to_datetime(df['date'])
df_filtered = df[df['amount'] > 100]
df['norm'] = df.groupby('region')['amount'].transform(lambda x: (x - x.mean()) / x.std())
```

**After (Polars - Optimized):**
```python
import polars as pl

df = (
    pl.scan_csv(file_path)
    .with_columns(pl.col('date').str.strptime(pl.Date, format='%Y-%m-%d'))
    .filter(pl.col('amount') > 100)
    .with_columns(
        ((pl.col('amount') - pl.col('amount').mean().over('region')) /
         pl.col('amount').std().over('region')).alias('norm')
    ).collect()
)
```

The differences matter:

| Optimization | What It Does |
|--------------|--------------|
| **Lazy Evaluation** | Uses `scan_csv()` + `collect()` for query optimization |
| **Parallel Execution** | Combines operations in single `with_columns()` |
| **Window Functions** | Replaces `groupby().transform()` with `.over()` |
| **Streaming Mode** | Enables streaming for large datasets (>1GB) |
| **Type Safety** | Explicit conversions for better performance |

All following official [Polars best practices](https://docs.pola.rs/user-guide/misc/performance/).

---

## Installation

```bash
# Install the command
curl -o ~/.claude/commands/pandas-polars-migration.md \
  https://raw.githubusercontent.com/tommcrojo/pandas-polars-migration-claude/main/.claude/commands/pandas-polars-migration.md

# Install polars if needed
pip install "polars>=1.0.0"

# Run migration
claude /pandas-polars-migration your_script.py
```

That's it. The command is now available in Claude Code.

---

## Example Output

```
╔══════════════════════════════════════════════════════════╗
║  🚀 PANDAS → POLARS MIGRATION RESULTS                         ║
╠══════════════════════════════════════════════════════════╣
║  Files Migrated: 1                                             ║
║  Total Lines Changed: 23                                        ║
║                                                               ║
║  PERFORMANCE COMPARISON                                         ║
║  ─────────────────────────────────────────────────────────────────  ║
║  Metric              Pandas        Polars        Speedup          ║
║  ─────────────────────────────────────────────────────────────────  ║
║  Read CSV            245.50ms      89.20ms       2.75x        ║
║  Type Conversion     123.80ms      12.40ms       9.98x        ║
║  Aggregations        892.30ms      108.70ms      8.21x        ║
║  ─────────────────────────────────────────────────────────────────  ║
║  TOTAL               1261.60ms     210.30ms      **6.00x**    ║
╚══════════════════════════════════════════════════════════╝
```

---

## What This Is Good For

- **ETL pipelines** - Speed up batch transformations
- **ML preprocessing** - Faster feature engineering
- **API data processing** - Reduce latency
- **Log analytics** - Handle larger datasets
- **Any pandas code > 10K rows** - Significant gains

---

## Try the Demo

### Quick Demo (for recording/testing)
```bash
git clone https://github.com/tommcrojo/pandas-polars-migration-claude.git
cd pandas-polars-migration-claude/smoke-test

# Generate 500K test data + run migration
python3 generate_data.py
python3 demo_pandas.py
claude /pandas-polars-migration demo_pandas.py
```

Uses 500K rows to show **10-12x speedup**. See [`smoke-test/`](smoke-test/) for video script and recording tips.

### Full Example
```bash
git clone https://github.com/tommcrojo/pandas-polars-migration-claude.git
cd pandas-polars-migration-claude/examples

# Generate sample data
python3 generate_data.py

# Run migration
claude /pandas-polars-migration demo_pandas_pipeline.py
```

---

## Requirements

- **Python**: 3.8+
- **Polars**: >= 1.0.0 (tested with 1.37.1)
- **Claude Code**: Latest version
- **Pandas**: Only needed for code you're migrating

---

## Important Notes

- Always **backup your code** or work in a git branch
- Run your **test suite** after migration to verify correctness
- Polars syntax is stricter—type errors will surface immediately
- The command handles common pandas patterns; complex edge cases may need manual review

---

## License

MIT License - see [LICENSE](LICENSE) file.

---

## Links

- [Polars Documentation](https://docs.pola.rs/)
- [Claude Code](https://github.com/anthropics/claude-code)
- [LinkedIn](https://linkedin.com/in/tommcrojo)

---

**Built by [tommcrojo](https://github.com/tommcrojo)**

*Try it before scaling infrastructure. You might not need that bigger instance.*
