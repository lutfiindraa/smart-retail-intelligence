-- ===================================================
-- SMART RETAIL INTELLIGENCE - SQL BUSINESS ANALYTICS
-- ===================================================

-- Challenge 1: Total Revenue per Store
SELECT 
    st.store_id,
    st.store_location,
    SUM(s.transaction_qty * s.unit_price) AS total_revenue
FROM sales_transactions s
JOIN stores st ON s.store_id = st.store_id
GROUP BY st.store_id, st.store_location
ORDER BY total_revenue DESC;

-- Challenge 2: Top 10 Produk Berdasarkan Revenue
SELECT 
    p.product_id,
    p.product_detail,
    SUM(s.transaction_qty) AS total_quantity,
    SUM(s.transaction_qty * s.unit_price) AS total_revenue
FROM sales_transactions s
JOIN products p ON s.product_id = p.product_id
GROUP BY p.product_id, p.product_detail
ORDER BY total_revenue DESC
LIMIT 10;

-- Challenge 3: Revenue Bulanan (Januari–Juni 2023)
SELECT 
    TO_CHAR(s.transaction_date, 'YYYY-MM') AS month,
    SUM(s.transaction_qty * s.unit_price) AS total_revenue
FROM sales_transactions s
WHERE s.transaction_date >= '2023-01-01' 
  AND s.transaction_date < '2023-07-01'
GROUP BY TO_CHAR(s.transaction_date, 'YYYY-MM')
ORDER BY month ASC;

-- Challenge 4: Revenue Berdasarkan Kategori Produk
SELECT 
    c.category_id,
    c.category_name,
    SUM(s.transaction_qty * s.unit_price) AS total_revenue
FROM sales_transactions s
JOIN products p ON s.product_id = p.product_id
JOIN categories c ON p.category_id = c.category_id
GROUP BY c.category_id, c.category_name
ORDER BY total_revenue DESC;

-- Challenge 5: Jam Paling Ramai Berdasarkan Jumlah Transaksi
SELECT 
    EXTRACT(HOUR FROM s.transaction_time) AS transaction_hour,
    COUNT(DISTINCT s.transaction_id) AS total_transactions,
    SUM(s.transaction_qty) AS total_items_sold
FROM sales_transactions s
GROUP BY EXTRACT(HOUR FROM s.transaction_time)
ORDER BY total_transactions DESC;

-- Challenge 6: AOV (Average Order Value) per Store
SELECT 
    st.store_id,
    st.store_location,
    COUNT(DISTINCT s.transaction_id) AS total_transactions,
    ROUND(SUM(s.transaction_qty * s.unit_price), 2) AS total_revenue,
    ROUND(SUM(s.transaction_qty * s.unit_price) / COUNT(DISTINCT s.transaction_id), 2) AS average_order_value
FROM sales_transactions s
JOIN stores st ON s.store_id = st.store_id
GROUP BY st.store_id, st.store_location
ORDER BY average_order_value DESC;

-- Challenge 7: Monthly Revenue Growth Percentage (WoW)
WITH monthly_sales AS (
    SELECT 
        TO_CHAR(transaction_date, 'YYYY-MM') AS month,
        SUM(transaction_qty * unit_price) AS revenue
    FROM sales_transactions
    GROUP BY TO_CHAR(transaction_date, 'YYYY-MM')
)
SELECT 
    month,
    ROUND(revenue, 2) AS revenue,
    ROUND(LAG(revenue) OVER (ORDER BY month), 2) AS previous_month_revenue,
    ROUND(
        ((revenue - LAG(revenue) OVER (ORDER BY month)) / LAG(revenue) OVER (ORDER BY month)) * 100, 
        2
    ) || '%' AS growth_percentage
FROM monthly_sales
ORDER BY month ASC;


-- Challenge 8: Best-Selling Product per Store
WITH product_store_revenue AS (
    SELECT 
        st.store_location,
        p.product_id,
        p.product_detail,
        SUM(s.transaction_qty * s.unit_price) AS revenue,
        ROW_NUMBER() OVER (
            PARTITION BY st.store_id 
            ORDER BY SUM(s.transaction_qty * s.unit_price) DESC
        ) AS rank
    FROM sales_transactions s
    JOIN stores st ON s.store_id = st.store_id
    JOIN products p ON s.product_id = p.product_id
    GROUP BY st.store_id, st.store_location, p.product_id, p.product_detail
)
SELECT 
    store_location,
    product_id,
    product_detail,
    ROUND(revenue, 2) AS revenue,
    rank
FROM product_store_revenue
WHERE rank = 1
ORDER BY store_location;

-- Challenge 9: Revenue by Day of Week (Most to Least Busy)
SELECT 
    TO_CHAR(transaction_date, 'Day') AS day_of_week,
    COUNT(DISTINCT transaction_id) AS transactions,
    SUM(transaction_qty) AS quantity,
    ROUND(SUM(transaction_qty * unit_price), 2) AS revenue
FROM sales_transactions
GROUP BY 
    EXTRACT(DOW FROM transaction_date),
    TO_CHAR(transaction_date, 'Day')
ORDER BY revenue DESC;

-- Challenge 10: Peak Hour per Category (Category × Hour)
WITH category_hourly_revenue AS (
    SELECT 
        c.category_name AS category,
        EXTRACT(HOUR FROM s.transaction_time) AS hour,
        SUM(s.transaction_qty * s.unit_price) AS revenue,
        ROW_NUMBER() OVER (
            PARTITION BY c.category_id 
            ORDER BY SUM(s.transaction_qty * s.unit_price) DESC
        ) AS rank
    FROM sales_transactions s
    JOIN products p ON s.product_id = p.product_id
    JOIN categories c ON p.category_id = c.category_id
    GROUP BY c.category_id, c.category_name, EXTRACT(HOUR FROM s.transaction_time)
)
SELECT 
    category,
    hour,
    ROUND(revenue, 2) AS revenue,
    rank
FROM category_hourly_revenue
WHERE rank = 1
ORDER BY revenue DESC;