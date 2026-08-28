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