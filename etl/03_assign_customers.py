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

CUSTOMERS_PATH = (
    PROJECT_ROOT
    / "data"
    / "synthetic"
    / "customers.csv"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "sales_transactions_with_customer.csv"
)

RANDOM_SEED = 42


STORE_CITY_MAP = {
    3: "Astoria",
    5: "Lower Manhattan",
    8: "Hell's Kitchen",
}


# ============================================================
# LOAD DATA
# ============================================================

def load_data():
    sales = pd.read_csv(
        SALES_PATH,
        parse_dates=["transaction_date"],
    )

    customers = pd.read_csv(
        CUSTOMERS_PATH,
        parse_dates=["join_date"],
    )

    return sales, customers


# ============================================================
# VALIDATE INPUT
# ============================================================

def validate_input(
    sales: pd.DataFrame,
    customers: pd.DataFrame,
) -> None:

    required_sales = {
        "transaction_id",
        "transaction_date",
        "store_id",
    }

    required_customers = {
        "customer_id",
        "city",
        "join_date",
    }

    missing_sales = required_sales - set(sales.columns)
    missing_customers = (
        required_customers - set(customers.columns)
    )

    if missing_sales:
        raise ValueError(
            f"Kolom sales tidak lengkap: {missing_sales}"
        )

    if missing_customers:
        raise ValueError(
            f"Kolom customer tidak lengkap: {missing_customers}"
        )

    if sales["transaction_id"].duplicated().any():
        raise ValueError(
            "Duplicate transaction_id ditemukan."
        )

    if customers["customer_id"].duplicated().any():
        raise ValueError(
            "Duplicate customer_id ditemukan."
        )

    unknown_stores = set(
        sales["store_id"].unique()
    ) - set(STORE_CITY_MAP)

    if unknown_stores:
        raise ValueError(
            f"Store ID tidak dikenal: {unknown_stores}"
        )


# ============================================================
# ASSIGN CUSTOMER
# ============================================================

def assign_customers(
    sales: pd.DataFrame,
    customers: pd.DataFrame,
) -> pd.DataFrame:

    rng = np.random.default_rng(RANDOM_SEED)

    sales = sales.copy()

    # Set activity score agar distribusi customer
    # tidak sepenuhnya uniform.
    activity_score = rng.lognormal(
        mean=0.0,
        sigma=1.0,
        size=len(customers),
    )

    customers = customers.copy()

    customers["activity_score"] = activity_score

    assignments = []

    # Proses per store
    for store_id, store_city in STORE_CITY_MAP.items():

        store_sales = (
            sales[sales["store_id"] == store_id]
            .sort_values("transaction_date")
            .copy()
        )

        store_customers = (
            customers[customers["city"] == store_city]
            .copy()
        )

        if store_customers.empty:
            raise ValueError(
                f"Tidak ada customer untuk store {store_id}."
            )

        # Proses per tanggal agar eligible customer
        # hanya customer yang sudah join.
        for transaction_date, daily_sales in (
            store_sales.groupby("transaction_date")
        ):

            eligible = store_customers[
                store_customers["join_date"]
                <= transaction_date
            ].copy()

            if eligible.empty:
                raise ValueError(
                    f"Tidak ada customer eligible untuk "
                    f"store {store_id} pada "
                    f"{transaction_date.date()}."
                )

            # Customer yang sudah lama join sedikit
            # lebih berpeluang melakukan transaksi.
            tenure_days = (
                transaction_date
                - eligible["join_date"]
            ).dt.days

            tenure_factor = (
                1.0
                + tenure_days.clip(lower=0) / 365
            )

            weights = (
                eligible["activity_score"]
                * tenure_factor
            )

            weights = weights.to_numpy(
                dtype=float
            )

            weights = (
                weights / weights.sum()
            )

            selected_customer_ids = rng.choice(
                eligible["customer_id"].to_numpy(),
                size=len(daily_sales),
                replace=True,
                p=weights,
            )

            daily_result = pd.DataFrame({
                "transaction_id": (
                    daily_sales["transaction_id"]
                    .to_numpy()
                ),
                "customer_id": selected_customer_ids,
            })

            assignments.append(
                daily_result
            )

    assignment_df = pd.concat(
        assignments,
        ignore_index=True,
    )

    return assignment_df


# ============================================================
# MERGE RESULT
# ============================================================

def build_enriched_sales(
    sales: pd.DataFrame,
    assignments: pd.DataFrame,
) -> pd.DataFrame:

    enriched = sales.merge(
        assignments,
        on="transaction_id",
        how="left",
        validate="one_to_one",
    )

    if enriched["customer_id"].isna().any():
        raise ValueError(
            "Ada transaksi yang tidak mendapatkan customer_id."
        )

    enriched["customer_id"] = (
        enriched["customer_id"]
        .astype(int)
    )

    enriched = (
        enriched
        .sort_values("transaction_id")
        .reset_index(drop=True)
    )

    return enriched


# ============================================================
# VALIDATE RESULT
# ============================================================

def validate_result(
    enriched: pd.DataFrame,
    customers: pd.DataFrame,
) -> None:

    print("\n=== VALIDASI CUSTOMER ASSIGNMENT ===")

    # Jumlah transaksi
    if len(enriched) != 149116:
        raise ValueError(
            "Jumlah transaksi berubah."
        )

    print(
        f"✓ Transactions : {len(enriched):,}"
    )

    # Tidak ada customer null
    null_customer = (
        enriched["customer_id"].isna().sum()
    )

    print(
        f"✓ Missing customer_id : {null_customer}"
    )

    # Semua customer valid
    valid_customer_ids = set(
        customers["customer_id"]
    )

    invalid_customer = (
        ~enriched["customer_id"]
        .isin(valid_customer_ids)
    ).sum()

    print(
        f"✓ Invalid customer_id : "
        f"{invalid_customer}"
    )

    # Join date tidak boleh setelah transaksi
    customer_dates = customers[
        ["customer_id", "join_date"]
    ]

    check = enriched.merge(
        customer_dates,
        on="customer_id",
        how="left",
    )

    invalid_join_date = (
        check["join_date"]
        > check["transaction_date"]
    ).sum()

    print(
        f"✓ Transaction sebelum join_date : "
        f"{invalid_join_date}"
    )

    # Konsistensi store dan customer city
    customer_city = customers[
        ["customer_id", "city"]
    ]

    check_city = enriched.merge(
        customer_city,
        on="customer_id",
        how="left",
    )

    check_city["expected_city"] = (
        check_city["store_id"]
        .map(STORE_CITY_MAP)
    )

    invalid_city = (
        check_city["city"]
        != check_city["expected_city"]
    ).sum()

    print(
        f"✓ Store/customer city mismatch : "
        f"{invalid_city}"
    )

    if (
        null_customer
        or invalid_customer
        or invalid_join_date
        or invalid_city
    ):
        raise ValueError(
            "Customer assignment gagal validasi."
        )


# ============================================================
# SAVE
# ============================================================

def save_result(
    enriched: pd.DataFrame,
) -> None:

    enriched.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print(
        f"\n✓ Saved: {OUTPUT_PATH}"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("ASSIGN CUSTOMERS TO SALES TRANSACTIONS")
    print("=" * 60)

    sales, customers = load_data()

    print(
        f"Sales rows     : {len(sales):,}"
    )

    print(
        f"Customers      : {len(customers):,}"
    )

    validate_input(
        sales,
        customers,
    )

    print(
        "\nAssigning customers..."
    )

    assignments = assign_customers(
        sales,
        customers,
    )

    enriched = build_enriched_sales(
        sales,
        assignments,
    )

    validate_result(
        enriched,
        customers,
    )

    save_result(
        enriched
    )

    print("=" * 60)
    print("CUSTOMER ASSIGNMENT COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()