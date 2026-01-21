"""Generate sample sales data for benchmarking."""
import csv
import random
from datetime import datetime, timedelta

# Sample data
PRODUCTS = [
    'Laptop', 'Mouse', 'Keyboard', 'Monitor', 'Headphones',
    'Webcam', 'USB Cable', 'External Drive', 'RAM', 'SSD',
    'Graphics Card', 'Processor', 'Motherboard', 'Power Supply',
    'Case', 'Cooling Fan', 'Desk', 'Chair', 'Microphone', 'Speaker'
]

REGIONS = ['North', 'South', 'East', 'West', 'Central']

def generate_sales_data(num_rows=50000):
    """Generate sample sales data."""
    start_date = datetime(2023, 1, 1)

    with open('sales_data.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['date', 'product', 'region', 'amount', 'quantity'])

        for _ in range(num_rows):
            # Random date in 2023-2024
            date = start_date + timedelta(days=random.randint(0, 730))
            product = random.choice(PRODUCTS)
            region = random.choice(REGIONS)

            # Amount between $10 and $2000
            amount = round(random.uniform(10, 2000), 2)

            # Quantity between 1 and 50
            quantity = random.randint(1, 50)

            writer.writerow([
                date.strftime('%Y-%m-%d'),
                product,
                region,
                amount,
                quantity
            ])

    print(f"Generated {num_rows} rows of sales data in sales_data.csv")

if __name__ == '__main__':
    generate_sales_data(50000)
