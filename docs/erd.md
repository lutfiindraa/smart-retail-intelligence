erDiagram

    CATEGORIES {
        INT category_id PK
        VARCHAR category_name
    }

    PRODUCTS {
        INT product_id PK
        INT category_id FK
        VARCHAR product_type
        VARCHAR product_detail
    }

    STORES {
        INT store_id PK
        VARCHAR store_location
    }

    SALES_TRANSACTIONS {
        INT transaction_id PK
        DATE transaction_date
        TIME transaction_time
        INT transaction_qty
        INT store_id FK
        INT product_id FK
        DECIMAL unit_price
    }

    CATEGORIES ||--o{ PRODUCTS : contains
    STORES ||--o{ SALES_TRANSACTIONS : records
    PRODUCTS ||--o{ SALES_TRANSACTIONS : sold_in