#!/usr/bin/env python3
"""Generate synthetic sales data for demo purposes.

Fast, simple, produces ~1,000,000 rows CSV.
"""

import csv
import random
from datetime import datetime, timedelta
import time


def generate_data():
    """Generate synthetic sales data."""

    # Config - 1M rows for a dramatic speedup demo
    num_rows = 1_000_000
    products = [
        "laptop",
        "phone",
        "tablet",
        "monitor",
        "keyboard",
        "mouse",
        "headphones",
    ]
    regions = ["madrid", "barcelona", "valencia", "sevilla", "bilbao"]
    categories = ["electronics", "accessories", "peripherals"]

    # Base date
    start_date = datetime(2024, 1, 1)

    print(f"Generating {num_rows:,} rows...")
    start = time.time()

    with open("sales_data.csv", "w", newline="") as f:
        writer = csv.writer(f)
        # Header
        writer.writerow(["date", "product", "amount", "region", "category"])

        for i in range(num_rows):
            # Generate realistic-looking data
            date = start_date + timedelta(days=random.randint(0, 364))
            product = random.choice(products)
            amount = random.uniform(10, 2000)  # 10€ to 2000€
            region = random.choice(regions)
            category = random.choice(categories)

            writer.writerow(
                [date.strftime("%Y-%m-%d"), product, f"{amount:.2f}", region, category]
            )

            # Progress indicator
            if (i + 1) % 100_000 == 0:
                print(f"  {(i + 1) // 1000}K rows generated...")

    elapsed = time.time() - start
    print(f"Done! Generated {num_rows:,} rows in {elapsed:.2f}s")
    print(f"File: sales_data.csv ({(num_rows * 0.1):.1f} MB approx)")


if __name__ == "__main__":
    generate_data()
