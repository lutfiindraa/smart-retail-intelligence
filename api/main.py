from fastapi import FastAPI, HTTPException
from sqlalchemy import text
from etl.db_connection import get_engine

from api.schemas import DemandForecastRequest
from api.services.forecast_service import (
    predict_next_day,
    predict_next_7_days,
)
from api.services.inventory_forecast_service import (
    get_inventory_forecast,
)

# Inisialisasi Aplikasi FastAPI
app = FastAPI(
    title="Smart Retail Intelligence API",
    description="Retail analytics, forecasting, and inventory intelligence API",
    version="1.0.0",
)

# Inisialisasi Database Engine
engine = get_engine()


# 1. Base / Root Endpoints
@app.get("/")
def root():
    return {
        "name": "Smart Retail Intelligence API",
        "status": "running",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }


# 2. Endpoint Sales Summary & Store Performance
@app.get("/sales/summary")
def sales_summary():
    query = text("""
        SELECT
            ROUND(SUM(transaction_qty * unit_price), 2)
                AS total_revenue,
            COUNT(DISTINCT transaction_id)
                AS total_transactions,
            SUM(transaction_qty)
                AS total_items,
            ROUND(
                SUM(transaction_qty * unit_price)
                / COUNT(DISTINCT transaction_id),
                2
            ) AS average_order_value
        FROM sales_transactions;
    """)

    with engine.connect() as connection:
        result = connection.execute(query).mappings().one()

    return dict(result)


@app.get("/sales/stores")
def store_performance():
    query = text("""
        SELECT
            st.store_id,
            st.store_location,
            COUNT(DISTINCT s.transaction_id)
                AS transactions,
            ROUND(
                SUM(s.transaction_qty * s.unit_price),
                2
            ) AS revenue,
            ROUND(
                SUM(s.transaction_qty * s.unit_price)
                / COUNT(DISTINCT s.transaction_id),
                2
            ) AS aov
        FROM sales_transactions s
        JOIN stores st
            ON s.store_id = st.store_id
        GROUP BY
            st.store_id,
            st.store_location
        ORDER BY revenue DESC;
    """)

    with engine.connect() as connection:
        result = connection.execute(query).mappings().all()

    return [dict(row) for row in result]


# 3. Endpoint Analytics & Customer RFM
@app.get("/analytics/sales-detail")
def sales_detail():
    query = text("""
        SELECT
            s.transaction_id,
            s.transaction_date,
            s.transaction_time,
            s.transaction_qty,
            s.store_id,
            st.store_location,
            s.product_id,
            p.product_detail,
            c.category_name,
            s.unit_price,
            s.transaction_qty * s.unit_price AS revenue
        FROM sales_transactions s
        JOIN stores st
            ON s.store_id = st.store_id
        JOIN products p
            ON s.product_id = p.product_id
        JOIN categories c
            ON p.category_id = c.category_id
        ORDER BY s.transaction_date, s.transaction_id;
    """)

    with engine.connect() as connection:
        result = connection.execute(query).mappings().all()

    return [dict(row) for row in result]


@app.get("/customers/{customer_id}/rfm")
def customer_rfm(customer_id: int):
    query = text("""
        SELECT
            c.customer_id,
            c.customer_name,
            c.gender,
            c.city,
            c.customer_segment,
            (
                CURRENT_DATE
                - MAX(s.transaction_date)
            ) AS recency,
            COUNT(DISTINCT s.transaction_id)
                AS frequency,
            ROUND(
                SUM(
                    s.transaction_qty
                    * s.unit_price
                ),
                2
            ) AS monetary
        FROM customers c
        JOIN sales_transactions s
            ON c.customer_id = s.customer_id
        WHERE c.customer_id = :customer_id
        GROUP BY
            c.customer_id,
            c.customer_name,
            c.gender,
            c.city,
            c.customer_segment;
    """)

    with engine.connect() as connection:
        result = connection.execute(
            query,
            {"customer_id": customer_id}
        ).mappings().first()

    if not result:
        raise HTTPException(
            status_code=404,
            detail="Customer tidak ditemukan."
        )

    return dict(result)


# 4. Endpoint Inventory Recommendations (Rule-based)
@app.get("/inventory/recommendations")
def inventory_recommendations():
    query = text("""
        WITH daily_demand AS (
            SELECT 
                i.store_id,
                i.product_id,
                i.inventory_date,
                i.closing_stock,
                COALESCE(SUM(s.transaction_qty), 0) AS demand
            FROM inventory i
            LEFT JOIN sales_transactions s 
                ON i.inventory_date = s.transaction_date 
                AND i.store_id = s.store_id 
                AND i.product_id = s.product_id
            GROUP BY 
                i.store_id, 
                i.product_id, 
                i.inventory_date, 
                i.closing_stock
        ),
        rolling_calc AS (
            SELECT 
                store_id,
                product_id,
                inventory_date,
                closing_stock,
                AVG(demand) OVER (
                    PARTITION BY store_id, product_id 
                    ORDER BY inventory_date 
                    ROWS BETWEEN 7 PRECEDING AND 1 PRECEDING
                ) AS avg_daily_demand_7d
            FROM daily_demand
        ),
        latest_status AS (
            SELECT 
                store_id,
                product_id,
                closing_stock AS current_stock,
                ROUND((COALESCE(avg_daily_demand_7d, 0) * 7)::numeric, 0) AS forecast_7d,
                GREATEST(0, ROUND((COALESCE(avg_daily_demand_7d, 0) * 7 * 1.20 - closing_stock)::numeric, 0)) AS reorder_quantity,
                CASE 
                    WHEN avg_daily_demand_7d IS NULL OR avg_daily_demand_7d = 0 THEN 'No Demand History'
                    WHEN (closing_stock / avg_daily_demand_7d) <= 2 THEN 'Critical'
                    WHEN (closing_stock / avg_daily_demand_7d) <= 5 THEN 'High'
                    WHEN (closing_stock / avg_daily_demand_7d) <= 10 THEN 'Medium'
                    ELSE 'Low'
                END AS risk
            FROM rolling_calc
            WHERE inventory_date = (SELECT MAX(inventory_date) FROM inventory)
        )
        SELECT 
            store_id,
            product_id,
            risk,
            current_stock,
            forecast_7d,
            reorder_quantity
        FROM latest_status
        WHERE reorder_quantity > 0
        ORDER BY reorder_quantity DESC;
    """)

    with engine.connect() as connection:
        result = connection.execute(query).mappings().all()

    return [dict(row) for row in result]


# 5. Endpoint Machine Learning Demand Forecast & ML Inventory Recommendation
@app.post("/forecast")
def forecast_demand(
    request: DemandForecastRequest
):
    try:
        return predict_next_day(
            store_id=request.store_id,
            product_id=request.product_id,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@app.post("/forecast/7-days")
def forecast_7_days(
    request: DemandForecastRequest
):
    try:
        return predict_next_7_days(
            store_id=request.store_id,
            product_id=request.product_id,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@app.post("/inventory/forecast-recommendation")
def inventory_forecast_recommendation(
    request: DemandForecastRequest
):
    try:
        return get_inventory_forecast(
            store_id=request.store_id,
            product_id=request.product_id,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


# ============================================================
# 6. Advanced Analytics Endpoints
# ============================================================

@app.get("/analytics/daily-sales")
def daily_sales():
    """Daily aggregated sales for heatmaps and trend analysis."""
    query = text("""
        SELECT
            s.transaction_date,
            EXTRACT(DOW FROM s.transaction_date)::int AS day_of_week,
            EXTRACT(WEEK FROM s.transaction_date)::int AS week_of_year,
            EXTRACT(MONTH FROM s.transaction_date)::int AS month,
            COUNT(DISTINCT s.transaction_id) AS transactions,
            SUM(s.transaction_qty) AS quantity,
            ROUND(SUM(s.transaction_qty * s.unit_price)::numeric, 2) AS revenue
        FROM sales_transactions s
        GROUP BY s.transaction_date
        ORDER BY s.transaction_date;
    """)
    with engine.connect() as connection:
        result = connection.execute(query).mappings().all()
    return [dict(row) for row in result]


@app.get("/analytics/customer-segments")
def customer_segments():
    """All customers with RFM metrics and scoring segments."""
    query = text("""
        WITH rfm_base AS (
            SELECT
                c.customer_id,
                c.customer_name,
                c.gender,
                c.city,
                c.customer_segment,
                c.birth_year,
                c.join_date,
                c.age,
                (DATE '2023-07-01' - MAX(s.transaction_date)) AS recency,
                COUNT(DISTINCT s.transaction_id) AS frequency,
                ROUND(SUM(s.transaction_qty * s.unit_price)::numeric, 2) AS monetary,
                COUNT(DISTINCT s.product_id) AS unique_products,
                COUNT(DISTINCT s.store_id) AS stores_visited,
                MIN(s.transaction_date) AS first_purchase,
                MAX(s.transaction_date) AS last_purchase
            FROM customers c
            JOIN sales_transactions s ON c.customer_id = s.customer_id
            GROUP BY
                c.customer_id, c.customer_name, c.gender, c.city,
                c.customer_segment, c.birth_year, c.join_date, c.age
        ),
        scored AS (
            SELECT
                *,
                NTILE(5) OVER (ORDER BY recency DESC) AS r_score,
                NTILE(5) OVER (ORDER BY frequency) AS f_score,
                NTILE(5) OVER (ORDER BY monetary) AS m_score
            FROM rfm_base
        )
        SELECT
            *,
            CASE
                WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
                WHEN r_score >= 4 AND f_score >= 3 THEN 'Loyal Customers'
                WHEN r_score >= 4 AND f_score <= 2 THEN 'New / Promising'
                WHEN r_score <= 2 AND f_score >= 4 AND m_score >= 4 THEN 'At Risk High Value'
                WHEN r_score <= 2 AND f_score >= 3 THEN 'At Risk'
                WHEN r_score <= 2 AND f_score <= 2 THEN 'Lost / Hibernating'
                ELSE 'Potential'
            END AS rfm_segment
        FROM scored
        ORDER BY monetary DESC;
    """)
    with engine.connect() as connection:
        result = connection.execute(query).mappings().all()
    return [dict(row) for row in result]


@app.get("/analytics/product-performance")
def product_performance():
    """Detailed product-level performance metrics."""
    query = text("""
        SELECT
            p.product_id,
            p.product_detail,
            p.product_type,
            c.category_name,
            COUNT(DISTINCT s.transaction_id) AS transactions,
            SUM(s.transaction_qty) AS total_qty,
            ROUND(SUM(s.transaction_qty * s.unit_price)::numeric, 2) AS revenue,
            ROUND(AVG(s.unit_price)::numeric, 2) AS avg_price,
            ROUND(AVG(s.transaction_qty)::numeric, 2) AS avg_qty_per_txn,
            COUNT(DISTINCT s.customer_id) AS unique_customers,
            COUNT(DISTINCT s.store_id) AS stores_selling,
            MIN(s.transaction_date) AS first_sale,
            MAX(s.transaction_date) AS last_sale
        FROM products p
        JOIN categories c ON p.category_id = c.category_id
        JOIN sales_transactions s ON p.product_id = s.product_id
        GROUP BY p.product_id, p.product_detail, p.product_type, c.category_name
        ORDER BY revenue DESC;
    """)
    with engine.connect() as connection:
        result = connection.execute(query).mappings().all()
    return [dict(row) for row in result]


@app.get("/analytics/weather-impact")
def weather_impact():
    """Weather correlated with daily sales per store location."""
    query = text("""
        SELECT
            w.date,
            w.location,
            w.temperature,
            w.rainfall_mm,
            w.weather_condition,
            COALESCE(agg.transactions, 0) AS transactions,
            COALESCE(agg.quantity, 0) AS quantity,
            COALESCE(agg.revenue, 0) AS revenue
        FROM weather w
        LEFT JOIN (
            SELECT
                s.transaction_date,
                st.store_location,
                COUNT(DISTINCT s.transaction_id) AS transactions,
                SUM(s.transaction_qty) AS quantity,
                ROUND(SUM(s.transaction_qty * s.unit_price)::numeric, 2) AS revenue
            FROM sales_transactions s
            JOIN stores st ON s.store_id = st.store_id
            GROUP BY s.transaction_date, st.store_location
        ) agg ON w.date = agg.transaction_date
            AND w.location = agg.store_location
        ORDER BY w.date, w.location;
    """)
    with engine.connect() as connection:
        result = connection.execute(query).mappings().all()
    return [dict(row) for row in result]


@app.get("/analytics/inventory-health")
def inventory_health():
    """Comprehensive inventory health status with product details."""
    query = text("""
        WITH latest AS (
            SELECT
                i.store_id,
                st.store_location,
                i.product_id,
                p.product_detail,
                c.category_name,
                i.opening_stock,
                i.received_stock,
                i.sold_quantity,
                i.closing_stock,
                i.stockout_flag,
                i.inventory_date
            FROM inventory i
            JOIN stores st ON i.store_id = st.store_id
            JOIN products p ON i.product_id = p.product_id
            JOIN categories c ON p.category_id = c.category_id
            WHERE i.inventory_date = (
                SELECT MAX(inventory_date) FROM inventory
            )
        ),
        demand_avg AS (
            SELECT
                store_id,
                product_id,
                ROUND(AVG(sold_quantity)::numeric, 2) AS avg_daily_demand
            FROM inventory
            WHERE inventory_date >= (
                SELECT MAX(inventory_date) - INTERVAL '14 days'
                FROM inventory
            )
            GROUP BY store_id, product_id
        )
        SELECT
            l.*,
            COALESCE(d.avg_daily_demand, 0) AS avg_daily_demand,
            CASE
                WHEN COALESCE(d.avg_daily_demand, 0) = 0 THEN 999
                ELSE ROUND((l.closing_stock / d.avg_daily_demand)::numeric, 1)
            END AS days_of_stock,
            CASE
                WHEN COALESCE(d.avg_daily_demand, 0) = 0 THEN 'No Demand'
                WHEN (l.closing_stock / d.avg_daily_demand) <= 2 THEN 'Critical'
                WHEN (l.closing_stock / d.avg_daily_demand) <= 5 THEN 'High'
                WHEN (l.closing_stock / d.avg_daily_demand) <= 10 THEN 'Medium'
                ELSE 'Low'
            END AS risk_level
        FROM latest l
        LEFT JOIN demand_avg d
            ON l.store_id = d.store_id
            AND l.product_id = d.product_id
        ORDER BY days_of_stock ASC;
    """)
    with engine.connect() as connection:
        result = connection.execute(query).mappings().all()
    return [dict(row) for row in result]


@app.get("/analytics/promotions")
def promotions():
    """Promotion data with effectiveness metrics."""
    query = text("""
        SELECT
            p.promotion_id,
            p.store_id,
            st.store_location,
            p.product_id,
            pr.product_detail,
            p.promotion_type,
            p.discount_percentage,
            p.start_date,
            p.end_date,
            COUNT(DISTINCT s.transaction_id) AS transactions,
            COALESCE(SUM(s.transaction_qty), 0) AS quantity,
            ROUND(COALESCE(SUM(s.transaction_qty * s.unit_price), 0)::numeric, 2) AS revenue
        FROM promotions p
        JOIN stores st ON p.store_id = st.store_id
        JOIN products pr ON p.product_id = pr.product_id
        LEFT JOIN sales_transactions s
            ON s.store_id = p.store_id
            AND s.product_id = p.product_id
            AND s.transaction_date BETWEEN p.start_date AND p.end_date
        GROUP BY
            p.promotion_id, p.store_id, st.store_location,
            p.product_id, pr.product_detail, p.promotion_type,
            p.discount_percentage, p.start_date, p.end_date
        ORDER BY p.start_date DESC;
    """)
    with engine.connect() as connection:
        result = connection.execute(query).mappings().all()
    return [dict(row) for row in result]