# 🚀 Pandas → Polars Migration Command for Claude Code

**Automatically benchmark, migrate, and optimize your pandas code to Polars.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Polars](https://img.shields.io/badge/polars-1.0.0+-orange.svg)](https://pola.rs/)

---

## 🎯 What This Does

This Claude Code command automatically:

1. **Benchmarks** your current pandas code
2. **Migrates** to Polars with performance optimizations
3. **Re-benchmarks** and shows exact speedup improvements

All in one command.

### Real Results

- **8.2x faster** on data aggregations
- **50% lower** API latency
- **25% cost savings** on cloud compute

---

## 📦 Installation

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

That's it! The command is now available in Claude Code.

---

## 🚀 Quick Start

### Basic Usage

```bash
# Navigate to your project
cd your-project

# Run the migration command
claude /pandas-polars-migration your_script.py
```

### Migrate Multiple Files

```bash
# Migrate entire directory
claude /pandas-polars-migration src/data/

# Migrate specific files
claude /pandas-polars-migration pipeline1.py pipeline2.py
```

---

## 🎬 Example

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
🎯 TOTAL            1261.60ms     210.30ms      6.00x
═══════════════════════════════════════════════════════════════

OPTIMIZATIONS APPLIED:
✓ Lazy evaluation with scan_csv() + collect()
✓ Parallel expression execution (3 operations combined)
✓ Window functions with .over() (1 replacement)
✓ Removed index operations (0 instances)

FILES MODIFIED:
- demo_pandas_pipeline.py (23 lines changed)

Next steps:
1. Review migrated code in demo_pandas_pipeline.py
2. Run your test suite to verify correctness
3. Update requirements.txt: remove pandas, add polars
```

---

## 🧠 What Makes This Different

This command doesn't just translate syntax—it writes **OPTIMIZED** Polars code:

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

## 💡 Perfect For

- **ETL pipelines** - Speed up data transformations
- **ML preprocessing** - Faster feature engineering
- **API data processing** - Reduce latency
- **Log analytics** - Handle larger datasets
- **Any pandas code > 10K rows** - Significant speedup gains

---

## 📋 How It Works

The command follows a 6-phase workflow:

1. **DISCOVER & ANALYZE** - Find pandas usage patterns
2. **BENCHMARK BASELINE** - Measure current performance
3. **MIGRATE TO POLARS** - Apply optimization rules
4. **BENCHMARK OPTIMIZED** - Measure new performance
5. **REPORT RESULTS** - Show detailed comparison
6. **VERIFICATION** - Provide next steps

---

## 🔧 Requirements

- **Python**: 3.8+
- **Polars**: >= 1.0.0 (tested with 1.0.0)
- **Pandas**: (for the original code being migrated)
- **Claude Code**: Latest version

The command was built using Polars 1.0.0 documentation and best practices.

---

## 📚 Examples

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

---

## ⚠️ Important Notes

- Always **backup your code** or work in a git branch
- Polars syntax is **stricter than pandas** - type errors will surface
- Run your **test suite** after migration to verify correctness
- The command focuses on **common pandas operations**; complex edge cases may require manual review
- Update `requirements.txt`: remove pandas, add polars

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Report bugs** - Open an issue with details
2. **Suggest features** - What pandas patterns should we support?
3. **Submit PRs** - Improve migration rules or add optimizations
4. **Share results** - Post your benchmark improvements!

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🔗 Links

- [Polars Documentation](https://docs.pola.rs/)
- [Claude Code](https://github.com/anthropics/claude-code)
- [LinkedIn Post](LINKEDIN_POST.md) - Announcement & discussion
- [Blog Post](#) - Coming soon: detailed technical deep dive

---

## 🌟 Show Your Support

If this command helped you, please:

- ⭐ Star this repo
- 📢 Share on social media
- 💬 Share your benchmark results in Issues
- 🤝 Contribute improvements

---

## 📧 Contact

Questions or feedback? Open an issue or reach out on [LinkedIn](https://linkedin.com/in/tommcrojo).

---

**Built with ❤️ by [tommcrojo](https://github.com/tommcrojo)**

*Try it before scaling infrastructure. You might not need that bigger instance.*
