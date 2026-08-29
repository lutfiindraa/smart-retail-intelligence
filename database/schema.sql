-- 1. KATEGORI PRODUK
CREATE TABLE categories (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL UNIQUE
);

-- 2. TOKO
CREATE TABLE stores (
    store_id INTEGER PRIMARY KEY,
    store_location VARCHAR(100) NOT NULL UNIQUE
);

-- 3. PRODUK
CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    category_id INTEGER NOT NULL,
    product_type VARCHAR(150) NOT NULL,
    product_detail VARCHAR(200) NOT NULL,

    CONSTRAINT fk_products_category
        FOREIGN KEY (category_id)
        REFERENCES categories(category_id)
);

-- 4. PELANGGAN (ENTITAS BARU)
CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    gender VARCHAR(20) NOT NULL,
    birth_year INTEGER NOT NULL,
    city VARCHAR(100) NOT NULL,
    join_date DATE NOT NULL,
    age INTEGER NOT NULL,
    customer_segment VARCHAR(50) NOT NULL
);

-- 5. TRANSAKSI PENJUALAN (DENGAN CUSTOMER_ID)
CREATE TABLE sales_transactions (
    transaction_id INTEGER PRIMARY KEY,
    transaction_date DATE NOT NULL,
    transaction_time TIME NOT NULL,
    transaction_qty INTEGER NOT NULL,
    store_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,

    CONSTRAINT fk_sales_store
        FOREIGN KEY (store_id)
        REFERENCES stores(store_id),

    CONSTRAINT fk_sales_product
        FOREIGN KEY (product_id)
        REFERENCES products(product_id),

    CONSTRAINT fk_sales_customer
        FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id),

    CONSTRAINT chk_transaction_qty
        CHECK (transaction_qty > 0),

    CONSTRAINT chk_unit_price
        CHECK (unit_price >= 0)
);

-- 6. KALENDER / DIMENSI WAKTU
CREATE TABLE calendar (
    date DATE PRIMARY KEY,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    day INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,
    day_name VARCHAR(20) NOT NULL,
    week_of_year INTEGER NOT NULL,
    is_weekend BOOLEAN NOT NULL
);

-- 7. PROMOSI
CREATE TABLE promotions (
    promotion_id INTEGER PRIMARY KEY,
    store_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    promotion_type VARCHAR(50) NOT NULL,
    discount_percentage DECIMAL(5,2) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,

    CONSTRAINT fk_promotion_store
        FOREIGN KEY (store_id)
        REFERENCES stores(store_id),

    CONSTRAINT fk_promotion_product
        FOREIGN KEY (product_id)
        REFERENCES products(product_id),

    CONSTRAINT chk_discount
        CHECK (
            discount_percentage > 0
            AND discount_percentage <= 100
        ),

    CONSTRAINT chk_promotion_dates
        CHECK (end_date >= start_date)
);

-- 8. INVENTARIS / STOK
CREATE TABLE inventory (
    inventory_date DATE NOT NULL,
    store_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    opening_stock INTEGER NOT NULL,
    received_stock INTEGER NOT NULL,
    sold_quantity INTEGER NOT NULL,
    closing_stock INTEGER NOT NULL,
    stockout_flag BOOLEAN NOT NULL,

    PRIMARY KEY (
        inventory_date,
        store_id,
        product_id
    ),

    FOREIGN KEY (store_id)
        REFERENCES stores(store_id),

    FOREIGN KEY (product_id)
        REFERENCES products(product_id),

    CHECK (opening_stock >= 0),
    CHECK (received_stock >= 0),
    CHECK (sold_quantity >= 0),
    CHECK (closing_stock >= 0)
);

-- 9. CUACA
CREATE TABLE weather (
    date DATE NOT NULL,
    location VARCHAR(100) NOT NULL,
    temperature DECIMAL(5,2) NOT NULL,
    rainfall_mm DECIMAL(6,2) NOT NULL,
    weather_condition VARCHAR(20) NOT NULL,

    PRIMARY KEY (date, location),

    CHECK (rainfall_mm >= 0),

    CHECK (
        weather_condition
        IN ('Clear', 'Cloudy', 'Rain')
    )
);