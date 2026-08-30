# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026/08/30 - Lutfi Indra

### Added
- **Machine Learning Demand Forecasting & Serving Pipeline:**
  - Integrasi model machine learning *Random Forest Regressor* (`ml/models/demand_forecast_rf.joblib` & `demand_forecast_features.joblib`) untuk peramalan permintaan produk harian (*daily product demand forecasting*).
  - Layanan inferensi peramalan cerdas (`api/services/forecast_service.py`): prediksi permintaan *Next-Day* (`predict_next_day`), rolling autoregresif multi-hari (`predict_next_7_days`), ekstraksi fitur kalender, lag demand, dan rolling statistics.
  - Layanan rekomendasi rantai pasok cerdas (`api/services/inventory_forecast_service.py`): kalkulasi otomatis *Safety Stock* dinamis (buffer 20%), *Recommended Stock*, *Reorder Quantity*, serta klasifikasi tingkat urgensi stok (*Days of Inventory Risk*: Critical, High, Medium, Low, No Demand).
- **Enterprise Model Serving & Analytics Backend (FastAPI):**
  - Pembuatan backend REST API berkinerja tinggi terintegrasi PostgreSQL (`api/main.py`, `api/schemas.py`, `api/database.py`).
  - **Core & Health Endpoints:** `GET /`, `GET /health`.
  - **Sales & Store Endpoints:** `GET /sales/summary`, `GET /sales/stores`.
  - **Deep Analytics Endpoints:** `GET /analytics/sales-detail`, `GET /analytics/daily-sales`, `GET /analytics/product-performance`, `GET /analytics/weather-impact`, `GET /analytics/promotions`.
  - **Customer Intelligence Endpoints:** `GET /customers/{customer_id}/rfm`, `GET /analytics/customer-segments` (kuantil NTILE-5 scoring: Champions, Loyal Customers, Potential, At Risk, Lost/Hibernating).
  - **Inventory Health Endpoints:** `GET /inventory/recommendations`, `GET /analytics/inventory-health` (monitoring *Days of Stock*, *Stockout Alerts*, dan kuantitas *Restock*).
  - **Machine Learning Inference Endpoints:** `POST /forecast`, `POST /forecast/7-days`, `POST /inventory/forecast-recommendation`.
- **Interactive Multi-Page Streamlit Intelligence Platform (`dashboard/app.py`):**
  - Desain antarmuka modern *Cyber & Dark Premium Glassmorphism Theme* dengan font Google Inter, palet warna HSL kontras tinggi, dan *custom animated UI components*.
  - **7 Modul Halaman Interaktif Terintegrasi:**
    - `🏠 Executive Overview`: Metrik KPI eksekutif (Total Revenue, Total Transactions, Total Items Sold, Average Order Value), komparasi pendapatan per toko, dan *Performance Matrix*.
    - `📊 Sales Deep Analytics`: Analisis tren penjualan harian/mingguan/bulanan, kalender visual heatmap transaksi, Pareto 80/20 breakdown, performa kategori, dan distribusi penjualan.
    - `👥 Customer Intelligence`: Visualisasi interaktif segmentasi RFM (2D/3D scatter plot, radar chart), demografi pelanggan (usia, gender, kota), dan pencarian profil pelanggan individual.
    - `📦 Inventory Intelligence`: Pemantauan stok real-time, evaluasi *Days of Stock*, deteksi dini stok kritis/kehabisan stok (*out-of-stock*), dan rekomendasi pemesanan ulang (*reorder*).
    - `🔮 Demand Forecast`: Peramalan permintaan produk 1 hingga 7 hari ke depan dengan perbandingan aktual vs prediksi dan rekomendasi inventaris berbasis model ML.
    - `🌦️ Weather & External`: Analisis korelasi dampak parameter cuaca (suhu, curah hujan) terhadap volume dan nilai transaksi toko.
    - `📋 Data Explorer`: Eksplorasi tabel interaktif data transaksi, produk, pelanggan, promosi, dan inventaris dengan filter dinamis dan fungsi unduh CSV.
  - Implementasi *caching layer* client-side (`@st.cache_data(ttl=300)`) untuk optimasi latensi data.

### Changed
- **API & Analytics Integration:** Menghubungkan seluruh visualisasi dashboard langsung ke REST API FastAPI untuk arsitektur terdesentralisasi dan skalabel.
- **Calendar & Weather Generators:** Memperbarui parameter pembangkitan kalender (`etl/04_generate_calendar.py`) dan cuaca (`etl/07_generate_weather.py`) untuk sinkronisasi fitur waktu pada model *demand forecasting*.

### Fixed
- **Pipeline Data Leakage Prevention:** Memperbaiki mekanisme lag feature dan rolling window pada layanan inferensi ML agar tidak terjadi *look-ahead bias* saat inferensi masa depan.
- **Inventory Zero-Demand Edge Cases:** Menangani kondisi pembagian nol (*division-by-zero*) pada perhitungan *Days of Inventory* untuk produk yang tidak memiliki riwayat permintaan terbaru.

---

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

> **Note:** Versi **1.0.0** menandai penyelesaian menyeluruh platform *End-to-End Smart Retail Intelligence*: mulai dari fondasi Data Engineering & ETL PostgreSQL, Deep Retail & Customer Analytics (RFM, Market Basket, Cohort), Time-Series Demand Forecasting Machine Learning Model (*Random Forest*), Model Serving Backend API berkinerja tinggi (*FastAPI*), hingga *Interactive Multi-Page Streamlit Dashboard* bertema premium.
