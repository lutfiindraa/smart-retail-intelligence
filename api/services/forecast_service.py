from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sqlalchemy import text
from etl.db_connection import get_engine

PROJECT_ROOT = Path(__file__).resolve().parents[2]

MODEL_PATH = (
    PROJECT_ROOT
    / "ml"
    / "models"
    / "demand_forecast_rf.joblib"
)

FEATURES_PATH = (
    PROJECT_ROOT
    / "ml"
    / "models"
    / "demand_forecast_features.joblib"
)

model = joblib.load(MODEL_PATH)
feature_columns = joblib.load(FEATURES_PATH)
engine = get_engine()


def get_product_category(product_id: int) -> str:
    query = text("""
        SELECT c.category_name
        FROM products p
        JOIN categories c
            ON p.category_id = c.category_id
        WHERE p.product_id = :product_id
    """)

    with engine.connect() as connection:
        result = connection.execute(
            query,
            {"product_id": product_id}
        ).mappings().first()

    if not result:
        raise ValueError(
            f"Product {product_id} tidak ditemukan."
        )

    return result["category_name"]


def build_forecast_features(
    store_id: int,
    product_id: int,
) -> tuple[pd.DataFrame, pd.Timestamp]:

    query = text("""
        SELECT
            s.transaction_date,
            s.transaction_qty AS demand
        FROM sales_transactions s
        WHERE s.store_id = :store_id
          AND s.product_id = :product_id
        ORDER BY s.transaction_date
    """)

    with engine.connect() as connection:
        history = pd.read_sql(
            query,
            connection,
            params={
                "store_id": store_id,
                "product_id": product_id,
            },
        )

    if history.empty:
        raise ValueError(
            "Tidak ditemukan histori penjualan."
        )

    history["transaction_date"] = pd.to_datetime(
        history["transaction_date"]
    )

    # Lengkapi tanggal yang tidak memiliki transaksi
    date_range = pd.date_range(
        history["transaction_date"].min(),
        history["transaction_date"].max(),
        freq="D"
    )

    history = (
        history
        .groupby("transaction_date", as_index=False)["demand"]
        .sum()
        .set_index("transaction_date")
        .reindex(date_range, fill_value=0)
        .rename_axis("transaction_date")
        .reset_index()
    )

    latest_date = history["transaction_date"].max()
    forecast_date = latest_date + pd.Timedelta(days=1)

    stores_query = text("""
        SELECT store_location
        FROM stores
        WHERE store_id = :store_id
    """)

    with engine.connect() as connection:
        store_result = connection.execute(
            stores_query,
            {"store_id": store_id}
        ).mappings().first()

    if not store_result:
        raise ValueError(
            f"Store {store_id} tidak ditemukan."
        )

    store_location = store_result["store_location"]

    category_name = get_product_category(
        product_id
    )

    calendar_query = text("""
        SELECT *
        FROM calendar
        WHERE date = :forecast_date
    """)

    weather_query = text("""
        SELECT *
        FROM weather
        WHERE date = :forecast_date
          AND location = :location
    """)

    with engine.connect() as connection:

        calendar_result = connection.execute(
            calendar_query,
            {"forecast_date": forecast_date.date()}
        ).mappings().first()

        weather_result = connection.execute(
            weather_query,
            {
                "forecast_date": forecast_date.date(),
                "location": store_location,
            }
        ).mappings().first()

    if not calendar_result:
        raise ValueError(
            f"Calendar untuk {forecast_date.date()} tidak tersedia."
        )

    if not weather_result:
        raise ValueError(
            f"Weather untuk {forecast_date.date()} "
            f"di {store_location} tidak tersedia."
        )

    # Menghitung Fitur Lag & Rolling Mean secara presisi untuk Hari Esok (forecast_date)
    lag_1 = history["demand"].iloc[-1]
    lag_7 = history["demand"].iloc[-7] if len(history) >= 7 else 0
    lag_14 = history["demand"].iloc[-14] if len(history) >= 14 else 0
    lag_28 = history["demand"].iloc[-28] if len(history) >= 28 else 0

    rolling_mean_7 = history["demand"].tail(7).mean()
    rolling_mean_28 = history["demand"].tail(28).mean()

    features = {
        "store_id": store_id,
        "product_id": product_id,
        "category_name": category_name,
        "temperature": weather_result["temperature"],
        "rainfall_mm": weather_result["rainfall_mm"],
        "is_weekend": calendar_result["is_weekend"],
        "month": calendar_result["month"],
        "day_of_week": calendar_result["day_of_week"],
        "week_of_year": calendar_result["week_of_year"],
        "is_month_start": int(
            calendar_result["date"].day == 1
        ),
        "is_month_end": int(
            (
                pd.Timestamp(calendar_result["date"])
                + pd.offsets.MonthEnd(0)
            ).date()
            == calendar_result["date"]
        ),
        "lag_1": lag_1,
        "lag_7": lag_7,
        "lag_14": lag_14,
        "lag_28": lag_28,
        "rolling_mean_7": rolling_mean_7,
        "rolling_mean_28": rolling_mean_28,
    }

    return pd.DataFrame([features]), forecast_date


def predict_next_day(
    store_id: int,
    product_id: int,
) -> dict:

    features, forecast_date = build_forecast_features(
        store_id,
        product_id,
    )

    encoded = pd.get_dummies(
        features,
        columns=["category_name"]
    )

    encoded = encoded.reindex(
        columns=feature_columns,
        fill_value=0
    )

    prediction = model.predict(encoded)[0]

    return {
        "store_id": store_id,
        "product_id": product_id,
        "forecast_date": forecast_date.date().isoformat(),
        "predicted_demand": round(
            max(0, float(prediction)),
            2
        ),
        "forecast_horizon": "1 day",
    }

def predict_next_7_days(
    store_id: int,
    product_id: int,
) -> dict:

    query = text("""
        SELECT
            transaction_date,
            transaction_qty AS demand
        FROM sales_transactions
        WHERE store_id = :store_id
          AND product_id = :product_id
        ORDER BY transaction_date;
    """)

    with engine.connect() as connection:
        history = pd.read_sql(
            query,
            connection,
            params={
                "store_id": store_id,
                "product_id": product_id,
            },
        )

    if history.empty:
        raise ValueError(
            "Tidak ditemukan histori penjualan."
        )

    history["transaction_date"] = pd.to_datetime(
        history["transaction_date"]
    )

    # Lengkapi tanggal yang tidak memiliki transaksi
    date_range = pd.date_range(
        history["transaction_date"].min(),
        history["transaction_date"].max(),
        freq="D",
    )

    history = (
        history
        .groupby("transaction_date", as_index=False)["demand"]
        .sum()
        .set_index("transaction_date")
        .reindex(date_range, fill_value=0)
        .rename_axis("transaction_date")
        .reset_index()
    )

    store_query = text("""
        SELECT store_location
        FROM stores
        WHERE store_id = :store_id;
    """)

    product_query = text("""
        SELECT c.category_name
        FROM products p
        JOIN categories c
            ON p.category_id = c.category_id
        WHERE p.product_id = :product_id;
    """)

    with engine.connect() as connection:

        store_result = connection.execute(
            store_query,
            {"store_id": store_id},
        ).mappings().first()

        product_result = connection.execute(
            product_query,
            {"product_id": product_id},
        ).mappings().first()

    if not store_result:
        raise ValueError(
            f"Store {store_id} tidak ditemukan."
        )

    if not product_result:
        raise ValueError(
            f"Product {product_id} tidak ditemukan."
        )

    store_location = store_result["store_location"]
    category_name = product_result["category_name"]

    last_history_date = history["transaction_date"].max()

    forecasts = []

    for _ in range(7):

        forecast_date = (
            last_history_date
            + pd.Timedelta(days=1)
        )

        # -----------------------------
        # Historical features
        # -----------------------------

        lag_1 = history["demand"].iloc[-1]
        lag_7 = history["demand"].iloc[-7]
        lag_14 = history["demand"].iloc[-14]
        lag_28 = history["demand"].iloc[-28]

        rolling_mean_7 = (
            history["demand"]
            .iloc[-7:]
            .mean()
        )

        rolling_mean_28 = (
            history["demand"]
            .iloc[-28:]
            .mean()
        )

        # -----------------------------
        # Calendar
        # -----------------------------

        calendar_query = text("""
            SELECT
                year,
                month,
                day_of_week,
                week_of_year,
                is_weekend
            FROM calendar
            WHERE date = :forecast_date;
        """)

        weather_query = text("""
            SELECT
                temperature,
                rainfall_mm,
                weather_condition
            FROM weather
            WHERE date = :forecast_date
              AND location = :location;
        """)

        with engine.connect() as connection:

            calendar_result = connection.execute(
                calendar_query,
                {
                    "forecast_date": forecast_date.date()
                },
            ).mappings().first()

            weather_result = connection.execute(
                weather_query,
                {
                    "forecast_date": forecast_date.date(),
                    "location": store_location,
                },
            ).mappings().first()

        if not calendar_result:
            raise ValueError(
                f"Calendar {forecast_date.date()} tidak tersedia."
            )

        if not weather_result:
            raise ValueError(
                f"Weather {forecast_date.date()} "
                f"untuk {store_location} tidak tersedia."
            )

        # -----------------------------
        # Feature construction
        # -----------------------------

        features = pd.DataFrame([{
            "store_id": store_id,
            "product_id": product_id,
            "category_name": category_name,
            "temperature": weather_result["temperature"],
            "rainfall_mm": weather_result["rainfall_mm"],
            "is_weekend": calendar_result["is_weekend"],
            "month": calendar_result["month"],
            "day_of_week": calendar_result["day_of_week"],
            "week_of_year": calendar_result["week_of_year"],
            "is_month_start": int(
                forecast_date.day == 1
            ),
            "is_month_end": int(
                forecast_date.is_month_end
            ),
            "lag_1": lag_1,
            "lag_7": lag_7,
            "lag_14": lag_14,
            "lag_28": lag_28,
            "rolling_mean_7": rolling_mean_7,
            "rolling_mean_28": rolling_mean_28,
        }])

        encoded = pd.get_dummies(
            features,
            columns=["category_name"],
        )

        encoded = encoded.reindex(
            columns=feature_columns,
            fill_value=0,
        )

        prediction = model.predict(
            encoded
        )[0]

        prediction = max(
            0,
            float(prediction),
        )

        prediction = round(
            prediction,
            2,
        )

        forecasts.append({
            "date": forecast_date.date().isoformat(),
            "predicted_demand": prediction,
        })

        # --------------------------------
        # Recursive step
        # --------------------------------

        history.loc[
            forecast_date,
            "demand"
        ] = prediction

        last_history_date = forecast_date

    total_forecast = round(
        sum(
            item["predicted_demand"]
            for item in forecasts
        ),
        2,
    )

    return {
        "store_id": store_id,
        "product_id": product_id,
        "forecast_horizon": "7 days",
        "forecasts": forecasts,
        "total_forecast_demand": total_forecast,
    }