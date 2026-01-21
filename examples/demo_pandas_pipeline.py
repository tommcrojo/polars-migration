"""
Demo Pandas Pipeline - Sales Data Analysis
This script demonstrates common pandas operations that can be optimized with Polars.
"""
import pandas as pd
import time

def process_sales_data(file_path: str):
    """Process sales data with pandas operations."""

    # Read data
    start_read = time.perf_counter()
    df = pd.read_csv(file_path)
    read_time = (time.perf_counter() - start_read) * 1000

    # Type conversion
    start_convert = time.perf_counter()
    df['date'] = pd.to_datetime(df['date'])
    df['amount'] = df['amount'].astype(float)
    convert_time = (time.perf_counter() - start_convert) * 1000

    # Filtering
    start_transform = time.perf_counter()
    df_filtered = df[df['amount'] > 100]

    # Aggregations
    top_products = df.groupby('product')['amount'].sum().sort_values(ascending=False).head(10)
    avg_by_region = df.groupby('region')['amount'].mean()

    # Transform pattern (window function)
    df['amount_normalized'] = df.groupby('region')['amount'].transform(
        lambda x: (x - x.mean()) / x.std()
    )

    # Value counts
    region_counts = df['region'].value_counts()

    # Multiple aggregations
    summary = df.groupby('region').agg({
        'amount': ['sum', 'mean', 'count'],
        'quantity': 'sum'
    })

    transform_time = (time.perf_counter() - start_transform) * 1000

    return {
        'df': df,
        'top_products': top_products,
        'avg_by_region': avg_by_region,
        'region_counts': region_counts,
        'summary': summary,
        'metrics': {
            'read_time': read_time,
            'convert_time': convert_time,
            'transform_time': transform_time,
            'total_time': read_time + convert_time + transform_time
        }
    }


def main():
    """Run the benchmark."""
    file_path = 'sales_data.csv'

    print("=" * 70)
    print("PANDAS BENCHMARK - Sales Data Analysis")
    print("=" * 70)

    start_total = time.perf_counter()
    result = process_sales_data(file_path)
    total_time = (time.perf_counter() - start_total) * 1000

    metrics = result['metrics']

    print(f"\n{'Operation':<25} {'Time (ms)':<15}")
    print("-" * 40)
    print(f"{'Read CSV':<25} {metrics['read_time']:>10.2f}ms")
    print(f"{'Type Conversion':<25} {metrics['convert_time']:>10.2f}ms")
    print(f"{'Transformations/Agg':<25} {metrics['transform_time']:>10.2f}ms")
    print("-" * 40)
    print(f"{'TOTAL':<25} {total_time:>10.2f}ms")
    print("=" * 70)

    print(f"\nDataset size: {len(result['df'])} rows")
    print(f"Top product: {result['top_products'].index[0]} (${result['top_products'].iloc[0]:.2f})")
    print(f"Regions analyzed: {len(result['region_counts'])}")


if __name__ == '__main__':
    main()
