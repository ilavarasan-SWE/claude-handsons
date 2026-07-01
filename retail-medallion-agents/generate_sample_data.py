"""Generate a realistic retail sales CSV with intentional data quality issues."""
from __future__ import annotations

import random
import string
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

CATEGORIES = ["Electronics", "Clothing", "Home & Garden", "Sports", "Toys", "Food & Beverage", "Books", "Beauty"]
REGIONS = ["North", "South", "East", "West", "Central"]
STORES = [f"Store_{i:03d}" for i in range(1, 21)]
PRODUCTS = [
    "Laptop Pro 15", "Wireless Earbuds", "4K Smart TV", "Coffee Maker", "Running Shoes",
    "Winter Jacket", "Yoga Mat", "Board Game Deluxe", "Cookbook Collection", "Face Moisturizer",
    "Gaming Controller", "Desk Lamp", "Water Bottle", "Backpack XL", "Smartwatch",
    "Bluetooth Speaker", "Electric Toothbrush", "Protein Powder", "Sunglasses", "Tablet Stand",
    "USB Hub", "Mechanical Keyboard", "Webcam HD", "Air Purifier", "Standing Desk Mat",
    "Garden Hose", "Plant Pot Set", "Dog Food Premium", "Cat Toy Set", "Baby Monitor",
]
DATE_FORMATS = ["%Y-%m-%d", "%m/%d/%Y", "%d-%m-%Y", "%B %d, %Y", "%Y%m%d"]


def random_date(start: date, end: date) -> date:
    return start + timedelta(days=random.randint(0, (end - start).days))


def random_date_str(d: date) -> str:
    fmt = random.choice(DATE_FORMATS)
    return d.strftime(fmt)


def generate_order_id() -> str:
    return "ORD-" + "".join(random.choices(string.digits, k=8))


def generate_sample_csv(
    n_rows: int = 5000,
    output_path: str | Path = "data/raw/sample_retail_sales.csv",
) -> Path:
    random.seed(42)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    start_date = date(2023, 1, 1)
    end_date = date(2024, 12, 31)

    rows = []
    for i in range(n_rows):
        d = random_date(start_date, end_date)

        order_id = generate_order_id()
        product = random.choice(PRODUCTS)
        category = random.choice(CATEGORIES)
        region = random.choice(REGIONS)
        store = random.choice(STORES)
        quantity = random.randint(1, 20)
        unit_price = round(random.uniform(5.0, 999.99), 2)
        customer_age = random.randint(18, 75)
        payment_method = random.choice(["Credit Card", "Debit Card", "Cash", "Online", "Gift Card"])

        row = {
            "Order ID": order_id,
            "Order Date": random_date_str(d),
            "Product Name": product,
            "Category": category,
            "Region": region,
            "Store": store,
            "Quantity": quantity,
            "Unit Price": unit_price,
            "Customer Age": customer_age,
            "Payment Method": payment_method,
        }

        # Introduce intentional data quality issues
        r = random.random()
        if r < 0.04:
            row["Order ID"] = None          # null ID
        elif r < 0.07:
            row["Order Date"] = None        # null date
        elif r < 0.10:
            row["Category"] = None          # null category
        elif r < 0.13:
            row["Region"] = None            # null region
        elif r < 0.15:
            row["Customer Age"] = None      # null numeric
        elif r < 0.17:
            row["Quantity"] = -random.randint(1, 10)   # negative quantity (anomaly)
        elif r < 0.18:
            row["Unit Price"] = -round(random.uniform(1, 100), 2)  # negative price

        # Mixed types in category column
        if random.random() < 0.01:
            row["Category"] = random.randint(1, 8)

        rows.append(row)

    # Introduce ~150 duplicates
    duplicates = random.sample(rows[:1000], 150)
    rows.extend(duplicates)
    random.shuffle(rows)

    df = pd.DataFrame(rows)
    df.to_csv(output_path, index=False)
    print(f"Generated {len(df)} rows ({n_rows} original + ~150 duplicates) → {output_path}")
    return output_path


if __name__ == "__main__":
    generate_sample_csv()
