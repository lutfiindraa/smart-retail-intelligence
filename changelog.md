# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.0] - 2026/08/29 - Lutfi Indra

### Added
- **Enterprise Project Directory Architecture:** Inisialisasi arsitektur direktori modular end-to-end (`docs/`, `data/`, `database/`, `etl/`, `analysis/`, `ml/`, `api/`, `dashboard/`, `tests/`) dan konfigurasi manajemen *virtual environment* (`requirements.txt`, `.gitignore`, `.env`).
- **Relational Star-Schema & DDL Definition:** Pembuatan skema basis data relasional di [`schema.sql`] dan indeks optimasi [`indexes.sql`] untuk 9 entitas utama (`categories`, `stores`, `products`, `customers`, `sales_transactions`, `calendar`, `promotions`, `inventory`, `weather`).
- **End-to-End Synthetic Data Generation & ETL Pipelines:**
  - `01_transform_sales.py`: Ekstraksi, pembersihan, normalisasi tipe data, dan pemisahan atribut produk serta transaksi kotor.
  - `02_generate_customers.py`: Pembangkitan dataset profil pelanggan realistis (identitas, demografi, umur, tanggal bergabung, segmentasi awal).
  - `03_assign_customers.py`: Algoritma penugasan transaksi ke pelanggan berdasarkan bobot probabilitas kedatangan dan loyalitas belanja.
  - `04_generate_calendar.py`: Pembangkitan tabel dimensi waktu komprehensif (`year`, `month`, `day_of_week`, `is_weekend`, `week_of_year`).
  - `05_generate_promotions.py`: Simulasi skenario kampanye promosi dan diskon berkala per kategori/toko.
  - `06_generate_inventory.py`: Rekonstruksi pergerakan stok harian (`opening_stock`, `received_stock`, `sold_quantity`, `closing_stock`, `stockout_flag`).
  - `07_generate_weather.py`: Pembangkitan data historis cuaca (`temperature`, `rainfall_mm`, `weather_condition`) per lokasi toko.
  - `db_connection.py`: Abstraksi koneksi database PostgreSQL berbasis *connection pooling* dan SQLAlchemy/psycopg2.
- **Comprehensive Analytics & Intelligence Notebooks:**
  - `01_data_profiling.ipynb`: Verifikasi integritas relasional data, sebaran *missing values*, duplikasi, dan validasi tipe data.
  - `02_sales_analysis.ipynb`: Analisis performa penjualan, revenue trend, *revenue per store/category*, Pareto 80/20 product ranking, dan KPI ritel.
  - `03_customer_analysis.ipynb`: Implementasi segmentasi RFM (Recency, Frequency, Monetary) kuantil dengan visualisasi 3D/2D scatter & radar chart distribusi pelanggan.
  - `04_advanced_retail_analysis.ipynb`: Analisis keranjang belanja (Market Basket Analysis / Association Rules) dan analisis kohort retensi pelanggan (*retention cohort matrix*).
  - `05_demand_forecasting.ipynb`: Analisis dekomposisi deret waktu (Trend, Musiman harian/mingguan), autokorelasi (ACF/PACF), dan eksplorasi *lag/rolling features*.
  - `06_inventory_intelligence.ipynb`: Analisis manajemen rantai pasok ritel, penghitungan *Safety Stock*, *Reorder Point (ROP)*, *Economic Order Quantity (EOQ)*, dan deteksi rasio *Stockout*.
- **Data Validation Suite:** Notebook [`data_processed_validation.ipynb`] dan koleksi query SQL analitik di [`queries.sql`] untuk memastikan konsistensi matematis data hasil transformasi.

### Changed
- **Data Grain & Relational Integrity:** Mengubah relasi transaksi mentah yang bersifat *flat CSV* menjadi relasi multi-tabel berintegritas tinggi dengan *foreign keys*, *check constraints*, dan *not-null checks*.
- **Customer Assignment Strategy:** Menyempurnakan model penugasan pelanggan dari *random uniform* menjadi *weighted distribution* berdasarkan usia, frekuensi transaksi, dan pola waktu kunjungan belanja.
- **Stock Movement Simulation:** Mengadaptasi kalkulasi *closing stock* inventaris dengan mekanisme *lead time restocking* dan *safety buffer threshold* guna merefleksikan kondisi operasional gudang/toko riil.

### Fixed
- **Referential Integrity Mismatches:** Memperbaiki inkonsistensi pemetaan antara ID produk/kategori pada data transaksi dengan tabel referensi master produk.
- **Timestamp & Datetime Alignment:** Menyelaraskan format `transaction_date` dan `transaction_time` lintas *pipeline* pemrosesan data (Pandas v2.x, PostgreSQL DATE/TIME).
- **Zero & Negative Stock Outlier Handling:** Memperbaiki anomali stok negatif pada simulasi pergerakan inventaris harian dengan menambahkan pembatas *stockout flag* dan penyesuaian otomatis stok akhir (*floor-zero boundary*).

---
> **Note:** Versi 1.0.0 menandai selesainya fondasi pipeline data (ETL, Database Modeling, Sintesis Data) serta rangkaian Deep Exploratory & Advanced Analytics (Sales KPI, RFM Customer Segmentation, Basket/Cohort Retail Analytics, Time-Series Demand Forecasting, dan Inventory Intelligence). Pengembangan Machine Learning Modeling, Model Serving API (FastAPI), dan Interactive Dashboard (Streamlit/Dash).
