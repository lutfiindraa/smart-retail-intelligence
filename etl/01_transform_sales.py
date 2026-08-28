from pathlib import Path
import pandas as pd


# ============================================================
# 1. CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "coffee_shop_sales.xlsx"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"


# ============================================================
# 2. UTILITY FUNCTIONS
# ============================================================
def print_section(title: str) -> None:
    """Print a formatted section title."""
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def validate_file_exists(file_path: Path) -> None:
    """Make sure the input file exists."""
    if not file_path.exists():
        raise FileNotFoundError(
            f"Raw dataset tidak ditemukan:\n{file_path}"
        )


# ============================================================
# 3. EXTRACT
# ============================================================
def extract_data(file_path: Path) -> pd.DataFrame:
    """
    Read the raw Excel dataset and return it as a DataFrame.
    """
    print_section("EXTRACT")
    validate_file_exists(file_path)
    print(f"Reading dataset:\n{file_path}")
    df = pd.read_excel(file_path)
    print(f"Rows    : {len(df):,}")
    print(f"Columns : {len(df.columns)}")
    return df

# ============================================================
# 4. VALIDATE RAW DATA
# ============================================================

def validate_raw_data(df: pd.DataFrame) -> None:
    """
    Validate important assumptions about the raw dataset.
    """
    print_section("VALIDATE RAW DATA")

    required_columns = {
        "transaction_id",
        "transaction_date",
        "transaction_time",
        "transaction_qty",
        "store_id",
        "store_location",
        "product_id",
        "unit_price",
        "product_category",
        "product_type",
        "product_detail",
    }

    actual_columns = set(df.columns)
    missing_columns = required_columns - actual_columns
    if missing_columns:
        raise ValueError(
            f"Kolom yang dibutuhkan tidak ditemukan: {missing_columns}"
        )

    print("✓ Required columns tersedia.")

    # Check duplicate transaction ID
    duplicate_transaction_id = df["transaction_id"].duplicated().sum()

    if duplicate_transaction_id > 0:
        raise ValueError(
            f"Ditemukan {duplicate_transaction_id} duplicate transaction_id."
        )

    print("✓ transaction_id unik.")

    # Check missing values
    total_missing = int(df.isna().sum().sum())

    if total_missing > 0:
        print(f"⚠ Ditemukan {total_missing} missing values.")
    else:
        print("✓ Tidak ada missing value.")

    # Check invalid quantity
    invalid_quantity = (df["transaction_qty"] <= 0).sum()

    if invalid_quantity > 0:
        raise ValueError(
            f"Ditemukan {invalid_quantity} transaksi dengan quantity <= 0."
        )

    print("✓ Transaction quantity valid.")

    # Check negative price
    invalid_price = (df["unit_price"] < 0).sum()

    if invalid_price > 0:
        raise ValueError(
            f"Ditemukan {invalid_price} transaksi dengan unit_price negatif."
        )

    print("✓ Unit price valid.")

    # Check product consistency
    product_consistency = (
        df.groupby("product_id")
        .agg(
            product_type_nunique=("product_type", "nunique"),
            product_detail_nunique=("product_detail", "nunique"),
            category_nunique=("product_category", "nunique"),
        )
    )

    inconsistent_products = product_consistency[
        (product_consistency["product_type_nunique"] > 1)
        | (product_consistency["product_detail_nunique"] > 1)
        | (product_consistency["category_nunique"] > 1)
    ]

    if not inconsistent_products.empty:
        raise ValueError(
            "Ditemukan product_id yang tidak konsisten."
        )

    print("✓ Product master konsisten.")

    # Check store consistency
    store_consistency = (
        df.groupby("store_id")["store_location"]
        .nunique()
    )

    inconsistent_stores = store_consistency[
        store_consistency > 1
    ]

    if not inconsistent_stores.empty:
        raise ValueError(
            "Ditemukan store_id dengan lokasi berbeda."
        )

    print("✓ Store master konsisten.")


# ============================================================
# 5. TRANSFORM - CATEGORIES
# ============================================================

def transform_categories(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create category master table.
    """

    categories = (
        df[["product_category"]]
        .drop_duplicates()
        .sort_values("product_category")
        .reset_index(drop=True)
    )

    categories.insert(
        0,
        "category_id",
        range(1, len(categories) + 1),
    )

    categories = categories.rename(
        columns={
            "product_category": "category_name"
        }
    )

    return categories


# ============================================================
# 6. TRANSFORM - STORES
# ============================================================

def transform_stores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create store master table.
    """

    stores = (
        df[["store_id", "store_location"]]
        .drop_duplicates()
        .sort_values("store_id")
        .reset_index(drop=True)
    )

    return stores


# ============================================================
# 7. TRANSFORM - PRODUCTS
# ============================================================

def transform_products(
    df: pd.DataFrame,
    categories: pd.DataFrame,
) -> pd.DataFrame:
    """
    Create product master table and replace
    product_category with category_id.
    """

    products = (
        df[
            [
                "product_id",
                "product_category",
                "product_type",
                "product_detail",
            ]
        ]
        .drop_duplicates()
        .copy()
    )

    # Create category mapping:
    # category_name -> category_id
    category_mapping = categories.set_index(
        "category_name"
    )["category_id"]

    products["category_id"] = (
        products["product_category"]
        .map(category_mapping)
    )

    # Make sure every product has a valid category_id
    if products["category_id"].isna().any():
        raise ValueError(
            "Ada product yang tidak memiliki category_id."
        )

    products["category_id"] = (
        products["category_id"]
        .astype(int)
    )

    products = products[
        [
            "product_id",
            "category_id",
            "product_type",
            "product_detail",
        ]
    ]

    products = (
        products
        .sort_values("product_id")
        .reset_index(drop=True)
    )

    return products


# ============================================================
# 8. TRANSFORM - SALES TRANSACTIONS
# ============================================================

def transform_sales_transactions(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Create the sales transaction fact table.
    """

    sales_columns = [
        "transaction_id",
        "transaction_date",
        "transaction_time",
        "transaction_qty",
        "store_id",
        "product_id",
        "unit_price",
    ]

    sales = df[sales_columns].copy()

    # Ensure correct data types
    sales["transaction_id"] = (
        sales["transaction_id"]
        .astype(int)
    )

    sales["transaction_date"] = pd.to_datetime(
        sales["transaction_date"]
    ).dt.date

    sales["transaction_time"] = pd.to_datetime(
        sales["transaction_time"],
        format="%H:%M:%S",
    ).dt.time

    sales["transaction_qty"] = (
        sales["transaction_qty"]
        .astype(int)
    )

    sales["store_id"] = (
        sales["store_id"]
        .astype(int)
    )

    sales["product_id"] = (
        sales["product_id"]
        .astype(int)
    )

    sales["unit_price"] = (
        sales["unit_price"]
        .astype(float)
    )

    sales = (
        sales
        .sort_values("transaction_id")
        .reset_index(drop=True)
    )

    return sales


# ============================================================
# 9. SAVE PROCESSED DATA
# ============================================================

def save_processed_data(
    categories: pd.DataFrame,
    products: pd.DataFrame,
    stores: pd.DataFrame,
    sales_transactions: pd.DataFrame,
    output_dir: Path,
) -> None:
    """
    Save transformed tables as CSV files.
    """

    print_section("LOAD TO PROCESSED FILES")

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_files = {
        "categories.csv": categories,
        "products.csv": products,
        "stores.csv": stores,
        "sales_transactions.csv": sales_transactions,
    }

    for filename, dataframe in output_files.items():

        output_path = output_dir / filename

        dataframe.to_csv(
            output_path,
            index=False,
        )

        print(
            f"✓ {filename:<25} "
            f"{len(dataframe):>8,} rows"
        )


# ============================================================
# 10. SUMMARY
# ============================================================

def print_summary(
    categories: pd.DataFrame,
    products: pd.DataFrame,
    stores: pd.DataFrame,
    sales_transactions: pd.DataFrame,
) -> None:
    """
    Print a summary of transformed datasets.
    """

    print_section("ETL SUMMARY")

    print(
        f"Categories          : {len(categories):,}"
    )

    print(
        f"Products            : {len(products):,}"
    )

    print(
        f"Stores              : {len(stores):,}"
    )

    print(
        f"Sales Transactions  : "
        f"{len(sales_transactions):,}"
    )

    print(
        "\nTransaction period:"
    )

    print(
        f"Start : "
        f"{sales_transactions['transaction_date'].min()}"
    )

    print(
        f"End   : "
        f"{sales_transactions['transaction_date'].max()}"
    )


# ============================================================
# 11. MAIN PIPELINE
# ============================================================

def main() -> None:
    """
    Execute the complete ETL pipeline.
    """

    print_section(
        "SMART RETAIL INTELLIGENCE - ETL PIPELINE"
    )

    # -------------------------
    # EXTRACT
    # -------------------------

    df = extract_data(
        RAW_DATA_PATH
    )

    # -------------------------
    # VALIDATE
    # -------------------------

    validate_raw_data(df)

    # -------------------------
    # TRANSFORM
    # -------------------------

    print_section("TRANSFORM")

    categories = transform_categories(df)

    print(
        f"✓ Categories created: "
        f"{len(categories):,}"
    )

    stores = transform_stores(df)

    print(
        f"✓ Stores created: "
        f"{len(stores):,}"
    )

    products = transform_products(
        df,
        categories,
    )

    print(
        f"✓ Products created: "
        f"{len(products):,}"
    )

    sales_transactions = (
        transform_sales_transactions(df)
    )

    print(
        f"✓ Sales transactions created: "
        f"{len(sales_transactions):,}"
    )

    # -------------------------
    # LOAD
    # -------------------------

    save_processed_data(
        categories=categories,
        products=products,
        stores=stores,
        sales_transactions=sales_transactions,
        output_dir=PROCESSED_DATA_DIR,
    )

    # -------------------------
    # SUMMARY
    # -------------------------

    print_summary(
        categories=categories,
        products=products,
        stores=stores,
        sales_transactions=sales_transactions,
    )

    print_section("ETL COMPLETED SUCCESSFULLY")

    print(
        "Raw dataset berhasil ditransformasi "
        "menjadi relational datasets."
    )


# ============================================================
# 12. ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()