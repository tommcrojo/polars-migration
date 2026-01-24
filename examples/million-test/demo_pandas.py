#!/usr/bin/env python3
"""Simple pandas ETL pipeline for demo.

This is the baseline that gets migrated in-place to Polars.
"""

import time

import pandas as pd


def process_sales_data(file_path: str) -> pd.DataFrame:
    """Process sales data with pandas."""

    df = pd.read_csv(file_path)

    date_series = pd.to_datetime(df["date"])
    df["date"] = date_series
    df = df[df["amount"] >= 100].copy()

    df["month"] = date_series.dt.to_period("M").astype(str)

    region_stats = df.groupby("region")["amount"].agg(["mean", "std"]).reset_index()
    df = df.merge(region_stats, on="region", how="left")
    df["amount_normalized"] = (df["amount"] - df["mean"]) / df["std"].replace(0, 1)

    result = (
        df.groupby(["product", "month"])
        .agg(amount=("amount", "sum"), avg=("amount", "mean"), n=("amount", "count"))
        .reset_index()
        .rename(
            columns={
                "amount": "total_revenue",
                "avg": "avg_revenue",
                "n": "transaction_count",
            }
        )
        .sort_values("total_revenue", ascending=False)
    )

    return result


def benchmark():
    """Run pipeline with timing."""

    print("=" * 60)
    print("Running PANDAS pipeline...")
    print("=" * 60)

    start = time.time()
    result = process_sales_data("sales_data.csv")
    elapsed = time.time() - start

    print(f"\n✓ Pipeline completed in {elapsed * 1000:.2f}ms")
    print(f"✓ Result shape: {result.shape}")
    print("\nTop 5 results:")
    print(result.head(5).to_string(index=False))

    return elapsed


if __name__ == "__main__":
    benchmark()
