CREATE TABLE categories (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE stores (
    store_id INTEGER PRIMARY KEY,
    store_location VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    category_id INTEGER NOT NULL,
    product_type VARCHAR(150) NOT NULL,
    product_detail VARCHAR(200) NOT NULL,

    CONSTRAINT fk_products_category
        FOREIGN KEY (category_id)
        REFERENCES categories(category_id)
);

CREATE TABLE sales_transactions (
    transaction_id INTEGER PRIMARY KEY,
    transaction_date DATE NOT NULL,
    transaction_time TIME NOT NULL,
    transaction_qty INTEGER NOT NULL,
    store_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,

    CONSTRAINT fk_sales_store
        FOREIGN KEY (store_id)
        REFERENCES stores(store_id),

    CONSTRAINT fk_sales_product
        FOREIGN KEY (product_id)
        REFERENCES products(product_id),

    CONSTRAINT chk_transaction_qty
        CHECK (transaction_qty > 0),

    CONSTRAINT chk_unit_price
        CHECK (unit_price >= 0)
);