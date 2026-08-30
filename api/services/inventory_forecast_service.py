from sqlalchemy import text

from api.services.forecast_service import predict_next_7_days
from etl.db_connection import get_engine


engine = get_engine()


def get_inventory_forecast(
    store_id: int,
    product_id: int,
) -> dict:

    forecast_result = predict_next_7_days(
        store_id,
        product_id,
    )

    forecast_demand = (
        forecast_result["total_forecast_demand"]
    )

    query = text("""
        SELECT
            i.closing_stock,
            i.stockout_flag,
            p.product_detail
        FROM inventory i
        JOIN products p
            ON i.product_id = p.product_id
        WHERE i.store_id = :store_id
          AND i.product_id = :product_id
          AND i.inventory_date = (
              SELECT MAX(inventory_date)
              FROM inventory
          );
    """)

    with engine.connect() as connection:
        result = connection.execute(
            query,
            {
                "store_id": store_id,
                "product_id": product_id,
            },
        ).mappings().first()

    if not result:
        raise ValueError(
            "Inventory tidak ditemukan."
        )

    current_stock = float(
        result["closing_stock"]
    )

    safety_stock = round(
        forecast_demand * 0.20,
        2,
    )

    recommended_stock = round(
        forecast_demand + safety_stock,
        2,
    )

    reorder_quantity = round(
        max(
            0,
            recommended_stock - current_stock,
        ),
        2,
    )

    # Risk berdasarkan days of inventory
    if forecast_demand <= 0:
        risk = "No Demand"

    else:
        days_of_inventory = (
            current_stock
            / (forecast_demand / 7)
        )

        if days_of_inventory <= 2:
            risk = "Critical"
        elif days_of_inventory <= 5:
            risk = "High"
        elif days_of_inventory <= 10:
            risk = "Medium"
        else:
            risk = "Low"

    return {
        "store_id": store_id,
        "product_id": product_id,
        "product_detail": result["product_detail"],
        "current_stock": current_stock,
        "forecast_7d_demand": forecast_demand,
        "safety_stock": safety_stock,
        "recommended_stock": recommended_stock,
        "reorder_quantity": reorder_quantity,
        "risk": risk,
    }