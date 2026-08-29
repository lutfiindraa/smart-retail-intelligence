from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

SALES_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "sales_transactions_with_customer.csv"
)

PRODUCTS_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "products.csv"
)

STORES_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "stores.csv"
)

OUTPUT_DIR = PROJECT_ROOT / "data" / "synthetic"
OUTPUT_PATH = OUTPUT_DIR / "inventory.csv"

RANDOM_SEED = 42


def generate_inventory() -> pd.DataFrame:

    rng = np.random.default_rng(RANDOM_SEED)

    sales = pd.read_csv(
        SALES_PATH,
        parse_dates=["transaction_date"],
    )

    products = pd.read_csv(
        PRODUCTS_PATH
    )

    stores = pd.read_csv(
        STORES_PATH
    )

    daily_sales = (
        sales.groupby(
            [
                "transaction_date",
                "store_id",
                "product_id",
            ]
        )["transaction_qty"]
        .sum()
        .reset_index()
    )

    dates = pd.date_range(
        sales["transaction_date"].min(),
        sales["transaction_date"].max(),
        freq="D",
    )

    # Gabungkan seluruh kombinasi
    # date × store × product
    calendar = pd.MultiIndex.from_product(
        [
            dates,
            stores["store_id"],
            products["product_id"],
        ],
        names=[
            "inventory_date",
            "store_id",
            "product_id",
        ],
    ).to_frame(index=False)

    daily_sales = daily_sales.rename(
        columns={
            "transaction_date": "inventory_date",
            "transaction_qty": "sold_quantity",
        }
    )

    inventory = calendar.merge(
        daily_sales,
        on=[
            "inventory_date",
            "store_id",
            "product_id",
        ],
        how="left",
    )

    inventory["sold_quantity"] = (
        inventory["sold_quantity"]
        .fillna(0)
        .astype(int)
    )

    # Base stock per product
    product_base_stock = {
        product_id: int(
            rng.integers(30, 150)
        )
        for product_id in products["product_id"]
    }

    inventory["base_stock"] = (
        inventory["product_id"]
        .map(product_base_stock)
    )

    # Opening stock dibuat berdasarkan kebutuhan
    inventory["opening_stock"] = (
        inventory["base_stock"]
        + inventory["sold_quantity"] * 2
        + rng.integers(
            0,
            30,
            size=len(inventory),
        )
    )

    inventory["received_stock"] = (
        rng.binomial(
            n=1,
            p=0.20,
            size=len(inventory),
        )
        * rng.integers(
            20,
            100,
            size=len(inventory),
        )
    )

    inventory["available_stock"] = (
        inventory["opening_stock"]
        + inventory["received_stock"]
    )

    inventory["closing_stock"] = (
        inventory["available_stock"]
        - inventory["sold_quantity"]
    ).clip(lower=0)

    inventory["stockout_flag"] = (
        inventory["closing_stock"] == 0
    )

    inventory = inventory[
        [
            "inventory_date",
            "store_id",
            "product_id",
            "opening_stock",
            "received_stock",
            "sold_quantity",
            "closing_stock",
            "stockout_flag",
        ]
    ]

    return inventory


def validate_inventory(
    inventory: pd.DataFrame,
) -> None:

    if inventory.empty:
        raise ValueError(
            "Inventory dataset kosong."
        )

    if inventory.isna().any().any():
        raise ValueError(
            "Missing value ditemukan."
        )

    numeric_columns = [
        "opening_stock",
        "received_stock",
        "sold_quantity",
        "closing_stock",
    ]

    for column in numeric_columns:
        if (inventory[column] < 0).any():
            raise ValueError(
                f"Nilai negatif pada {column}."
            )

    expected_closing = (
        inventory["opening_stock"]
        + inventory["received_stock"]
        - inventory["sold_quantity"]
    ).clip(lower=0)

    mismatch = (
        inventory["closing_stock"]
        != expected_closing
    ).sum()

    if mismatch:
        raise ValueError(
            f"Closing stock mismatch: {mismatch}"
        )


def main():

    print("=" * 60)
    print("GENERATE SYNTHETIC INVENTORY DATA")
    print("=" * 60)

    inventory = generate_inventory()

    validate_inventory(
        inventory
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    inventory.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print(
        f"✓ Inventory rows : "
        f"{len(inventory):,}"
    )

    print(
        f"✓ Stockout records : "
        f"{inventory['stockout_flag'].sum():,}"
    )

    print(
        f"✓ Saved : {OUTPUT_PATH}"
    )

    print("=" * 60)
    print("INVENTORY GENERATION COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()