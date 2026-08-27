# Data Dictionary

## stores

| Column | Type | Description | Key |
|---|---|---|---|
| store_id | INTEGER | Unique identifier for store | PK |
| store_location | VARCHAR | Store location name | |

## categories

| Column | Type | Description | Key |
|---|---|---|---|
| category_id | INTEGER | Unique category identifier | PK |
| category_name | VARCHAR | Product category name | |

## products

| Column | Type | Description | Key |
|---|---|---|---|
| product_id | INTEGER | Unique product identifier | PK |
| category_id | INTEGER | Reference to category | FK |
| product_type | VARCHAR | Product type | |
| product_detail | VARCHAR | Product detail/name | |

## sales_transactions

| Column | Type | Description | Key |
|---|---|---|---|
| transaction_id | INTEGER | Unique transaction identifier | PK |
| transaction_date | DATE | Transaction date | |
| transaction_time | TIME | Transaction time | |
| store_id | INTEGER | Store identifier | FK |
| product_id | INTEGER | Product identifier | FK |
| transaction_qty | INTEGER | Quantity purchased | |
| unit_price | DECIMAL | Unit price at transaction time | |