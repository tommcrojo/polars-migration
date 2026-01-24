# Million-Row Demo

Quick, clean demo of pandas → Polars migration for video/recording.

This generates a ~1,000,000 row CSV so the benchmark has enough signal to show a **dramatic speedup**.

Perfect for:
- Recording 60-second video demos
- Showing command in real-time
- Live streaming demos
- Testing the command works in fresh environment

---

## Quick Start (For Demo Recording)

```bash
# 1. Generate test data (~1M rows)
python3 generate_data.py

# 2. Run Claude Code migration
claude /pandas-polars-migration demo_pandas.py
```

That's it. 2 commands.

The command automatically:
- Benchmarks the pandas version
- Migrates to Polars
- Re-benchmarks the Polars version
- Shows exact speedup

You don't need to run the script manually—the command handles benchmarking.

---

## What This Demo Shows

**Pandas pipeline does:**
1. Reads ~1,000,000 rows CSV
2. Parses dates
3. Filters high-value transactions (≥100€)
4. Computes normalized amount per region
5. Aggregates by product and month
6. Sorts by total revenue

**After migration:**
Same operations, but in optimized Polars.

---

## Expected Output

The command prints a before/after benchmark table plus the speedup.

For a clean recording, focus the camera on:

- The baseline runtime (pandas)
- The post-migration runtime (Polars)
- The reported speedup

---

## Video Script (60 seconds)

**[0-10s] Hook:**
> "I built a tool that migrates pandas to Polars automatically. Watch this."

**[10-20s] Show baseline:**
> Mention: "It benchmarks the pandas version first." Show the baseline row in the results table.

**[20-35s] Run migration:**
> "Now I run `/pandas-polars-migration demo_pandas.py` in Claude Code."
> Show command executing, file being rewritten.

**[35-50s] Show speedup:**
> Show the Polars row + the speedup line.
> "Same output. Big speedup. One command."

**[50-60s] CTA:**
> "Link in comments. Free. Open source. Try it before scaling infra."

---

## Tips for Recording

1. **Clean terminal** - Clear before starting demo
2. **Large font** - Make terminal readable in video
3. **Speed** - Don't rush, but don't pause awkwardly
4. **Zoom** - Highlight the milliseconds in output
5. **Voiceover** - Clear, concise explanation

---

## Cleanup

```bash
# Remove generated files
rm -f sales_data.csv
git checkout demo_pandas.py  # Restore original pandas version (if you want to re-run the demo)
```
