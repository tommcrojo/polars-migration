#!/usr/bin/env python3
"""
Simple Polars ETL pipeline for demo.
Reads sales_data.csv, transforms, aggregates.
Migrated from pandas with optimizations.
"""

import polars as pl
import time


def process_sales_data(file_path: str):
    """Process sales data with Polars (lazy evaluation)."""

    # Lazy read CSV with early projection
    df = (
        pl.scan_csv(file_path)
        # Filter high-value transactions early to reduce volume
        .filter(pl.col("amount") >= 100)
        # Derive month from date string (avoid full datetime parse)
        # Extract YYYY-MM directly from ISO date string
        .with_columns(
            pl.col("date").str.slice(0, 7).alias("month")
        )
        # Select only columns we need
        .select(["amount", "region", "product", "month"])
    )

    # Compute region-level statistics using window functions
    df_normalized = df.with_columns(
        [
            # Compute mean and std per region using window functions
            pl.col("amount").mean().over("region").alias("mean"),
            pl.col("amount").std().over("region").alias("std"),
        ]
    ).with_columns(
        # Compute z-score normalization
        ((pl.col("amount") - pl.col("mean")) / pl.col("std").fill_null(1.0).replace(0, 1.0))
        .alias("amount_normalized")
    )

    # Aggregations by product and month
    result = (
        df_normalized
        .group_by(["product", "month"])
        .agg(
            [
                pl.col("amount").sum().alias("total_revenue"),
                pl.col("amount").mean().alias("avg_revenue"),
                pl.col("amount").count().alias("transaction_count"),
            ]
        )
        # Sort by total revenue descending
        .sort("total_revenue", descending=True)
        # Collect with streaming for large datasets
        .collect(engine="streaming")
    )

    return result


def benchmark():
    """Run pipeline with timing."""

    print("=" * 60)
    print("Running POLARS pipeline...")
    print("=" * 60)

    start = time.time()
    result = process_sales_data("sales_data.csv")
    elapsed = time.time() - start

    print(f"\n✓ Pipeline completed in {elapsed * 1000:.2f}ms")
    print(f"✓ Result shape: {result.shape}")
    print(f"\nTop 5 results:")
    print(result.head(5))

    return elapsed


if __name__ == "__main__":
    benchmark()
