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