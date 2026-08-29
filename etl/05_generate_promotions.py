from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

OUTPUT_DIR = PROJECT_ROOT / "data" / "synthetic"
OUTPUT_PATH = OUTPUT_DIR / "promotions.csv"

RANDOM_SEED = 42


def generate_promotions() -> pd.DataFrame:
    rng = np.random.default_rng(RANDOM_SEED)

    products = pd.read_csv(
        PROJECT_ROOT
        / "data"
        / "processed"
        / "products.csv"
    )

    stores = pd.read_csv(
        PROJECT_ROOT
        / "data"
        / "processed"
        / "stores.csv"
    )

    dates = pd.date_range(
        "2023-01-01",
        "2023-06-30",
        freq="7D",
    )

    promotion_types = [
        "Happy Hour",
        "Weekend Promotion",
        "Product Discount",
        "Seasonal Promotion",
    ]

    records = []

    promotion_id = 1

    for start_date in dates:

        promotion_type = rng.choice(
            promotion_types
        )

        duration_days = int(
            rng.integers(2, 8)
        )

        end_date = min(
            start_date
            + pd.Timedelta(days=duration_days),
            pd.Timestamp("2023-06-30"),
        )

        discount = float(
            rng.choice(
                [10, 15, 20, 25]
            )
        )

        # Tentukan store yang terkena promo
        store_id = int(
            rng.choice(stores["store_id"])
        )

        # Weekend promotion berlaku untuk beberapa produk,
        # sedangkan promotion lainnya fokus ke satu produk.
        if promotion_type == "Weekend Promotion":
            selected_products = products.sample(
                n=min(5, len(products)),
                random_state=int(
                    rng.integers(0, 1_000_000)
                ),
            )
        else:
            selected_products = products.sample(
                n=1,
                random_state=int(
                    rng.integers(0, 1_000_000)
                ),
            )

        for _, product in selected_products.iterrows():

            records.append({
                "promotion_id": promotion_id,
                "store_id": store_id,
                "product_id": int(
                    product["product_id"]
                ),
                "promotion_type": promotion_type,
                "discount_percentage": discount,
                "start_date": start_date.date(),
                "end_date": end_date.date(),
            })

            promotion_id += 1

    return pd.DataFrame(records)


def validate_promotions(
    promotions: pd.DataFrame,
) -> None:

    if promotions.empty:
        raise ValueError(
            "Promotion dataset kosong."
        )

    if promotions["promotion_id"].duplicated().any():
        raise ValueError(
            "Duplicate promotion_id ditemukan."
        )

    if promotions.isna().any().any():
        raise ValueError(
            "Missing value ditemukan."
        )

    if (
        promotions["discount_percentage"]
        <= 0
    ).any():
        raise ValueError(
            "Discount harus > 0."
        )

    if (
        promotions["discount_percentage"]
        > 100
    ).any():
        raise ValueError(
            "Discount tidak boleh > 100%."
        )

    if (
        promotions["end_date"]
        < promotions["start_date"]
    ).any():
        raise ValueError(
            "end_date tidak boleh sebelum start_date."
        )


def main():

    print("=" * 60)
    print("GENERATE SYNTHETIC PROMOTION DATA")
    print("=" * 60)

    promotions = generate_promotions()

    validate_promotions(promotions)

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    promotions.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print(
        f"✓ Promotions : {len(promotions):,}"
    )

    print(
        f"✓ Promotion types : "
        f"{promotions['promotion_type'].nunique()}"
    )

    print(
        f"✓ Saved : {OUTPUT_PATH}"
    )

    print("=" * 60)
    print("PROMOTION GENERATION COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()