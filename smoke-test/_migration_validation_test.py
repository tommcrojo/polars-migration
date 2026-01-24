#!/usr/bin/env python3
"""
Automatic validation test for pandas-to-polars migration.
This test compares outputs from original pandas code vs migrated polars code.
"""
import sys
import pandas as pd
import polars as pl


def compare_dataframes(df_pandas, df_polars, name="DataFrame"):
    """Compare pandas and polars dataframes for equality."""
    # Convert Polars to pandas for comparison
    df_polars_as_pandas = df_polars.to_pandas()

    # Sort both by all columns to handle order differences
    sort_cols = list(df_pandas.columns)
    df_pandas_sorted = df_pandas.sort_values(by=sort_cols).reset_index(drop=True)
    df_polars_sorted = df_polars_as_pandas.sort_values(by=sort_cols).reset_index(drop=True)

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
    print(f"✓ {name} outputs match!")
    return True


def test_original_vs_migrated():
    """Test that pandas and polars implementations produce identical results."""
    print("=" * 70)
    print("VALIDATION TEST: Pandas Baseline vs Polars Migrated Output")
    print("=" * 70)

    try:
        # Load pandas baseline
        print("\n[1/2] Loading pandas baseline from CSV...")
        result_pandas = pd.read_csv("_validation_baseline.csv")
        print(f"      Pandas baseline shape: {result_pandas.shape}")

        # Polars version (migrated)
        import demo_pandas
        print("\n[2/2] Running polars migrated version...")
        result_polars = demo_pandas.process_sales_data("sales_data.csv")
        print(f"      Polars result shape: {result_polars.shape}")

        # Compare outputs
        print("\n" + "=" * 70)
        print("COMPARING OUTPUTS")
        print("=" * 70)

        success = compare_dataframes(result_pandas, result_polars, "Sales Data Results")

        if success:
            print("\n" + "=" * 70)
            print("✓ VALIDATION PASSED - Outputs match!")
            print("=" * 70)
            print("\nSample comparison (top 3 rows):")
            print("\nPandas (baseline):")
            print(result_pandas.head(3).to_string(index=False))
            print("\nPolars (migrated):")
            print(result_polars.head(3))

        return success

    except Exception as e:
        print(f"\n✗ Validation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_original_vs_migrated()
    sys.exit(0 if success else 1)
