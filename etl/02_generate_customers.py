from pathlib import Path

import numpy as np
import pandas as pd


# ============================================================
# CONFIG
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

SALES_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "sales_transactions.csv"
)

OUTPUT_DIR = PROJECT_ROOT / "data" / "synthetic"

N_CUSTOMERS = 20_000

RANDOM_SEED = 42


# ============================================================
# GENERATE CUSTOMER MASTER
# ============================================================

def generate_customers(
    n_customers: int,
    sales_df: pd.DataFrame,
) -> pd.DataFrame:

    rng = np.random.default_rng(RANDOM_SEED)

    first_names = [
        "Alex", "Daniel", "Michael", "James", "John",
        "Emily", "Sarah", "Emma", "Olivia", "Sophia",
        "David", "William", "Robert", "Thomas", "Grace",
    ]

    last_names = [
        "Smith", "Johnson", "Williams", "Brown", "Jones",
        "Miller", "Davis", "Wilson", "Taylor", "Anderson",
        "Thomas", "Jackson", "White", "Harris", "Martin",
    ]

    city_by_store = {
        3: "Astoria",
        5: "Lower Manhattan",
        8: "Hell's Kitchen",
    }

    customer_ids = np.arange(1, n_customers + 1)

    customers = pd.DataFrame({
        "customer_id": customer_ids,
        "customer_name": [
            f"{rng.choice(first_names)} "
            f"{rng.choice(last_names)}"
            for _ in customer_ids
        ],
        "gender": rng.choice(
            ["Male", "Female"],
            size=n_customers,
            p=[0.5, 0.5],
        ),
        "birth_year": rng.integers(
            1965,
            2006,
            size=n_customers,
        ),
        "city": rng.choice(
            list(city_by_store.values()),
            size=n_customers,
            p=[0.30, 0.40, 0.30],
        ),
        "join_date": pd.to_datetime(
            rng.choice(
                pd.date_range(
                    "2021-01-01",
                    "2023-06-30",
                ),
                size=n_customers,
                replace=True,
            )
        ),
    })

    customers["age"] = (
        2023 - customers["birth_year"]
    )

    def assign_segment(age: int) -> str:
        if age <= 24:
            return "Student"
        if age <= 34:
            return "Young Professional"
        if age <= 49:
            return "Family"
        return "Mature"

    customers["customer_segment"] = (
        customers["age"]
        .apply(assign_segment)
    )

    return customers


# ============================================================
# VALIDATE
# ============================================================

def validate_customers(
    customers: pd.DataFrame,
) -> None:

    if customers["customer_id"].duplicated().any():
        raise ValueError(
            "Duplicate customer_id ditemukan."
        )

    if customers.isna().any().any():
        raise ValueError(
            "Missing value ditemukan pada customer data."
        )

    print(
        f"✓ Customer count: "
        f"{len(customers):,}"
    )

    print(
        f"✓ Unique customer_id: "
        f"{customers['customer_id'].nunique():,}"
    )


# ============================================================
# SAVE
# ============================================================

def save_customers(
    customers: pd.DataFrame,
) -> None:

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        OUTPUT_DIR
        / "customers.csv"
    )

    customers.to_csv(
        output_path,
        index=False,
    )

    print(
        f"✓ Saved: {output_path}"
    )


# ============================================================
# MAIN
# ============================================================

def main() -> None:

    print("=" * 60)
    print("GENERATE SYNTHETIC CUSTOMER DATA")
    print("=" * 60)

    sales_df = pd.read_csv(
        SALES_PATH
    )

    customers = generate_customers(
        n_customers=N_CUSTOMERS,
        sales_df=sales_df,
    )

    validate_customers(
        customers
    )

    save_customers(
        customers
    )

    print("=" * 60)
    print("CUSTOMER GENERATION COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()