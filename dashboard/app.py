import math
from datetime import date, timedelta
import os

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import streamlit as st


# ╔══════════════════════════════════════════════════════════════╗
# ║  CONFIG                                                      ║
# ╚══════════════════════════════════════════════════════════════╝

API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "http://127.0.0.1:8000",
)

st.set_page_config(
    page_title="Smart Retail Intelligence",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ╔══════════════════════════════════════════════════════════════╗
# ║  PREMIUM CSS THEME                                           ║
# ╚══════════════════════════════════════════════════════════════╝

st.markdown("""
<style>
/* ── Import Font ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

/* ── Global ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* ── Main background ── */
.stApp {
    background: linear-gradient(135deg, #0a0e1a 0%, #0d1525 30%, #111d35 60%, #0a0e1a 100%);
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1525 0%, #111d35 50%, #0a1628 100%);
    border-right: 1px solid rgba(56, 189, 248, 0.08);
}

section[data-testid="stSidebar"] .stRadio > label {
    color: rgba(255,255,255,0.5) !important;
    font-size: 0.7rem !important;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    font-weight: 600;
}

section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(56, 189, 248, 0.06);
    border-radius: 12px;
    padding: 10px 16px !important;
    margin-bottom: 4px;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    color: rgba(255,255,255,0.7) !important;
    font-weight: 500;
}

section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label:hover {
    background: rgba(56, 189, 248, 0.08);
    border-color: rgba(56, 189, 248, 0.2);
    transform: translateX(4px);
}

section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label[data-checked="true"] {
    background: linear-gradient(135deg, rgba(56, 189, 248, 0.15), rgba(168, 85, 247, 0.10));
    border-color: rgba(56, 189, 248, 0.3);
    color: #38bdf8 !important;
}

/* ── Headers ── */
h1, h2, h3 {
    color: #f1f5f9 !important;
}

h1 {
    font-weight: 800 !important;
    background: linear-gradient(135deg, #38bdf8, #818cf8, #a78bfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

h2 {
    font-weight: 700 !important;
    color: #e2e8f0 !important;
    border-bottom: 2px solid rgba(56, 189, 248, 0.15);
    padding-bottom: 8px;
}

h3 {
    font-weight: 600 !important;
    color: #cbd5e1 !important;
}

/* ── Metric Cards ── */
[data-testid="stMetric"] {
    background: rgba(255, 255, 255, 0.03);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(56, 189, 248, 0.10);
    border-radius: 16px;
    padding: 20px 24px;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.15);
}

[data-testid="stMetric"]:hover {
    border-color: rgba(56, 189, 248, 0.25);
    box-shadow: 0 8px 32px rgba(56, 189, 248, 0.08);
    transform: translateY(-2px);
}

[data-testid="stMetric"] label {
    color: rgba(148, 163, 184, 0.9) !important;
    font-size: 0.75rem !important;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    font-weight: 600 !important;
}

[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: #f1f5f9 !important;
    font-weight: 700 !important;
}

[data-testid="stMetricDelta"] > div {
    font-weight: 600 !important;
}

/* ── Containers / expanders ── */
[data-testid="stExpander"] {
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(56, 189, 248, 0.08);
    border-radius: 16px;
    overflow: hidden;
}

[data-testid="stExpander"] summary {
    color: #94a3b8 !important;
    font-weight: 600;
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid rgba(56, 189, 248, 0.08);
}

/* ── Buttons ── */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #38bdf8, #818cf8) !important;
    border: none;
    border-radius: 12px;
    font-weight: 600;
    letter-spacing: 0.5px;
    transition: all 0.3s;
    box-shadow: 0 4px 16px rgba(56, 189, 248, 0.2);
}

.stButton > button[kind="primary"]:hover {
    box-shadow: 0 8px 24px rgba(56, 189, 248, 0.35);
    transform: translateY(-1px);
}

/* ── Info / Warning / Error Boxes ── */
.stAlert {
    border-radius: 12px !important;
    backdrop-filter: blur(8px);
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: rgba(255,255,255,0.02);
    border-radius: 12px;
    padding: 4px;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 10px;
    color: #94a3b8;
    font-weight: 600;
    padding: 8px 20px;
}

.stTabs [data-baseweb="tab"][aria-selected="true"] {
    background: rgba(56, 189, 248, 0.12);
    color: #38bdf8;
}

/* ── Divider ── */
hr {
    border-color: rgba(56, 189, 248, 0.08) !important;
}

/* ── Caption ── */
.stCaption, [data-testid="stCaptionContainer"] {
    color: rgba(148, 163, 184, 0.6) !important;
}

/* ── Selectbox / Number Input ── */
.stSelectbox, .stNumberInput {
    color: #e2e8f0;
}

/* ── Plotly chart containers ── */
[data-testid="stPlotlyChart"] {
    border-radius: 16px;
    overflow: hidden;
    background: rgba(255,255,255,0.01);
    border: 1px solid rgba(56, 189, 248, 0.05);
}

/* ── Custom insight card ── */
.insight-card {
    background: linear-gradient(135deg, rgba(56, 189, 248, 0.06), rgba(168, 85, 247, 0.04));
    border: 1px solid rgba(56, 189, 248, 0.12);
    border-radius: 16px;
    padding: 20px 24px;
    margin: 12px 0;
    color: #cbd5e1;
    line-height: 1.7;
}

.insight-card strong {
    color: #38bdf8;
}

.insight-card em {
    color: #a78bfa;
}

.insight-header {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.85rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #38bdf8;
    margin-bottom: 10px;
}

/* ── Logo area ── */
.logo-container {
    text-align: center;
    padding: 24px 16px 16px;
    margin-bottom: 8px;
}

.logo-text {
    font-size: 1.3rem;
    font-weight: 800;
    background: linear-gradient(135deg, #38bdf8, #818cf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.5px;
}

.logo-subtitle {
    font-size: 0.65rem;
    color: rgba(148, 163, 184, 0.5);
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-top: 4px;
}

/* ── Page Header badge ── */
.page-badge {
    display: inline-block;
    background: linear-gradient(135deg, rgba(56, 189, 248, 0.15), rgba(168, 85, 247, 0.10));
    border: 1px solid rgba(56, 189, 248, 0.2);
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 0.7rem;
    color: #38bdf8;
    font-weight: 600;
    letter-spacing: 0.5px;
    margin-bottom: 8px;
}
</style>
""", unsafe_allow_html=True)


# ╔══════════════════════════════════════════════════════════════╗
# ║  PLOTLY THEME                                                ║
# ╚══════════════════════════════════════════════════════════════╝

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color="#94a3b8", size=12),
    title_font=dict(size=16, color="#e2e8f0", family="Inter"),
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        font=dict(color="#94a3b8", size=11),
    ),
    xaxis=dict(
        gridcolor="rgba(56, 189, 248, 0.06)",
        zerolinecolor="rgba(56, 189, 248, 0.06)",
    ),
    yaxis=dict(
        gridcolor="rgba(56, 189, 248, 0.06)",
        zerolinecolor="rgba(56, 189, 248, 0.06)",
    ),
    margin=dict(l=40, r=40, t=50, b=40),
    hoverlabel=dict(
        bgcolor="#1e293b",
        font_size=12,
        font_family="Inter",
        font_color="#f1f5f9",
        bordercolor="rgba(56, 189, 248, 0.3)",
    ),
)

COLOR_SEQUENCE = [
    "#38bdf8", "#818cf8", "#a78bfa", "#f472b6",
    "#34d399", "#fbbf24", "#fb923c", "#f87171",
    "#22d3ee", "#c084fc",
]

COLOR_RISK = {
    "Critical": "#ef4444",
    "High": "#f97316",
    "Medium": "#fbbf24",
    "Low": "#22c55e",
    "No Demand": "#64748b",
    "No Demand History": "#64748b",
}


# ╔══════════════════════════════════════════════════════════════╗
# ║  API HELPERS                                                 ║
# ╚══════════════════════════════════════════════════════════════╝

def api_get(endpoint: str):
    resp = requests.get(f"{API_BASE_URL}{endpoint}", timeout=30)
    resp.raise_for_status()
    return resp.json()


def api_post(endpoint: str, payload: dict):
    resp = requests.post(f"{API_BASE_URL}{endpoint}", json=payload, timeout=60)
    resp.raise_for_status()
    return resp.json()


# ╔══════════════════════════════════════════════════════════════╗
# ║  DATA LOADERS (cached)                                       ║
# ╚══════════════════════════════════════════════════════════════╝

@st.cache_data(ttl=300)
def load_sales_summary():
    return api_get("/sales/summary")


@st.cache_data(ttl=300)
def load_stores():
    return pd.DataFrame(api_get("/sales/stores"))


@st.cache_data(ttl=300)
def load_sales_detail():
    return pd.DataFrame(api_get("/analytics/sales-detail"))


@st.cache_data(ttl=300)
def load_daily_sales():
    return pd.DataFrame(api_get("/analytics/daily-sales"))


@st.cache_data(ttl=300)
def load_customer_segments():
    return pd.DataFrame(api_get("/analytics/customer-segments"))


@st.cache_data(ttl=300)
def load_product_performance():
    return pd.DataFrame(api_get("/analytics/product-performance"))


@st.cache_data(ttl=300)
def load_weather_impact():
    return pd.DataFrame(api_get("/analytics/weather-impact"))


@st.cache_data(ttl=300)
def load_inventory_health():
    return pd.DataFrame(api_get("/analytics/inventory-health"))


@st.cache_data(ttl=300)
def load_inventory_recommendations():
    return pd.DataFrame(api_get("/inventory/recommendations"))


@st.cache_data(ttl=300)
def load_promotions():
    return pd.DataFrame(api_get("/analytics/promotions"))


# ╔══════════════════════════════════════════════════════════════╗
# ║  FORMATTING HELPERS                                          ║
# ╚══════════════════════════════════════════════════════════════╝

def fmt_currency(v):
    if abs(v) >= 1_000_000:
        return f"Rp {v/1_000_000:,.1f}M"
    if abs(v) >= 1_000:
        return f"Rp {v/1_000:,.1f}K"
    return f"Rp {v:,.0f}"


def fmt_number(v):
    if abs(v) >= 1_000_000:
        return f"{v/1_000_000:,.1f}M"
    if abs(v) >= 1_000:
        return f"{v/1_000:,.1f}K"
    return f"{v:,.0f}"


def fmt_full_currency(v):
    return f"Rp {v:,.2f}"


def insight_card(icon, title, body):
    """Render a styled insight card."""
    st.markdown(
        f"""<div class="insight-card">
        <div class="insight-header">{icon} {title}</div>
        {body}
        </div>""",
        unsafe_allow_html=True,
    )


def apply_plotly_theme(fig):
    """Apply the dark premium theme to a plotly figure."""
    fig.update_layout(**PLOTLY_LAYOUT)
    return fig


# ╔══════════════════════════════════════════════════════════════╗
# ║  SIDEBAR                                                     ║
# ╚══════════════════════════════════════════════════════════════╝

with st.sidebar:
    st.markdown(
        """<div class="logo-container">
            <div class="logo-text">🧠 Smart Retail</div>
            <div class="logo-subtitle">Intelligence Platform</div>
        </div>""",
        unsafe_allow_html=True,
    )

    page = st.radio(
        "NAVIGATION",
        [
            "🏠  Executive Overview",
            "📊  Sales Deep Analytics",
            "👥  Customer Intelligence",
            "📦  Inventory Intelligence",
            "🔮  Demand Forecast",
            "🌦️  Weather & External",
            "📋  Data Explorer",
        ],
        index=0,
    )

    st.divider()

    st.markdown(
        """<div style="padding: 12px 16px; background: rgba(56,189,248,0.04);
        border: 1px solid rgba(56,189,248,0.08); border-radius: 12px;
        font-size: 0.72rem; color: #64748b; line-height: 1.8;">
        <strong style="color:#94a3b8;">Data Pipeline</strong><br>
        PostgreSQL → FastAPI → Streamlit<br><br>
        <strong style="color:#94a3b8;">ML Model</strong><br>
        Random Forest Regressor<br><br>
        <strong style="color:#94a3b8;">Data Refresh</strong><br>
        Cache TTL: 5 minutes
        </div>""",
        unsafe_allow_html=True,
    )


# ╔══════════════════════════════════════════════════════════════╗
# ║  LOAD CORE DATA                                              ║
# ╚══════════════════════════════════════════════════════════════╝

try:
    summary = load_sales_summary()
    stores_df = load_stores()
except requests.RequestException:
    st.error(
        "⚠️ **FastAPI tidak dapat diakses.** "
        "Pastikan server berjalan pada `http://127.0.0.1:8000`"
    )
    st.stop()


# ╔══════════════════════════════════════════════════════════════╗
# ║  PAGE 1 — EXECUTIVE OVERVIEW                                ║
# ╚══════════════════════════════════════════════════════════════╝

if page == "🏠  Executive Overview":

    st.markdown('<div class="page-badge">EXECUTIVE DASHBOARD</div>', unsafe_allow_html=True)
    st.title("Executive Overview")
    st.caption("Ringkasan menyeluruh kondisi bisnis retail — revenue, transaksi, performa toko, dan temuan strategis.")

    # ── KPI Row ──
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Revenue", fmt_currency(summary["total_revenue"]))
    c2.metric("Total Transactions", fmt_number(summary["total_transactions"]))
    c3.metric("Items Sold", fmt_number(summary["total_items"]))
    c4.metric("Avg Order Value", fmt_currency(summary["average_order_value"]))

    st.divider()

    # ── Store Performance ──
    st.subheader("🏪 Store Performance Comparison")

    col_chart, col_table = st.columns([3, 2])

    with col_chart:
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=stores_df["store_location"],
            y=stores_df["revenue"],
            name="Revenue",
            marker=dict(
                color=stores_df["revenue"],
                colorscale=[[0, "#1e3a5f"], [0.5, "#38bdf8"], [1, "#818cf8"]],
                cornerradius=6,
            ),
            text=[fmt_currency(v) for v in stores_df["revenue"]],
            textposition="outside",
            textfont=dict(color="#94a3b8", size=11),
        ))
        fig.update_layout(
            title="Revenue by Store Location",
            showlegend=False,
            yaxis_title="Revenue (Rp)",
        )
        apply_plotly_theme(fig)
        st.plotly_chart(fig, use_container_width=True)

    with col_table:
        st.markdown("##### 📊 Performance Matrix")
        display_stores = stores_df.copy()
        display_stores["revenue_fmt"] = display_stores["revenue"].apply(fmt_full_currency)
        display_stores["aov_fmt"] = display_stores["aov"].apply(fmt_full_currency)
        display_stores["txn_fmt"] = display_stores["transactions"].apply(lambda x: f"{x:,}")
        st.dataframe(
            display_stores[["store_location", "revenue_fmt", "txn_fmt", "aov_fmt"]].rename(
                columns={
                    "store_location": "Store",
                    "revenue_fmt": "Revenue",
                    "txn_fmt": "Transactions",
                    "aov_fmt": "AOV",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )

    # ── AOV Comparison ──
    st.subheader("💰 Average Order Value Comparison")
    fig_aov = go.Figure()
    fig_aov.add_trace(go.Bar(
        x=stores_df["store_location"],
        y=stores_df["aov"],
        marker=dict(
            color=stores_df["aov"],
            colorscale=[[0, "#1e3a5f"], [0.5, "#a78bfa"], [1, "#f472b6"]],
            cornerradius=6,
        ),
        text=[fmt_currency(v) for v in stores_df["aov"]],
        textposition="outside",
        textfont=dict(color="#94a3b8", size=11),
    ))
    fig_aov.update_layout(title="AOV by Store", showlegend=False, yaxis_title="AOV (Rp)")
    apply_plotly_theme(fig_aov)
    st.plotly_chart(fig_aov, use_container_width=True)

    st.divider()

    # ── Key Findings ──
    st.subheader("🔍 Key Business Findings")
    best = stores_df.sort_values("revenue", ascending=False).iloc[0]
    worst = stores_df.sort_values("revenue", ascending=True).iloc[0]
    best_aov = stores_df.sort_values("aov", ascending=False).iloc[0]
    avg_rev = stores_df["revenue"].mean()
    total_rev = stores_df["revenue"].sum()
    best_pct = (best["revenue"] / total_rev) * 100

    c1, c2 = st.columns(2)
    with c1:
        insight_card("🏆", "Revenue Leader",
            f"<strong>{best['store_location']}</strong> memimpin dengan total revenue "
            f"<strong>{fmt_full_currency(best['revenue'])}</strong>, menyumbang "
            f"<em>{best_pct:.1f}%</em> dari total revenue semua toko. "
            f"Ini menunjukkan bahwa lokasi tersebut memiliki traffic pelanggan tertinggi "
            f"atau basket size yang lebih besar dibanding toko lainnya."
        )
    with c2:
        insight_card("💎", "Highest AOV",
            f"<strong>{best_aov['store_location']}</strong> memiliki AOV tertinggi sebesar "
            f"<strong>{fmt_full_currency(best_aov['aov'])}</strong>. "
            f"Ini mengindikasikan pelanggan di lokasi ini cenderung membeli produk dengan "
            f"harga lebih tinggi atau membeli lebih banyak item per transaksi — "
            f"strategi upselling/cross-selling di toko ini sangat efektif."
        )

    revenue_gap = best["revenue"] - worst["revenue"]
    insight_card("📈", "Revenue Gap Analysis",
        f"Terdapat gap revenue sebesar <strong>{fmt_full_currency(revenue_gap)}</strong> "
        f"antara toko terbaik (<strong>{best['store_location']}</strong>) dan terlemah "
        f"(<strong>{worst['store_location']}</strong>). "
        f"Rata-rata revenue per toko adalah <strong>{fmt_full_currency(avg_rev)}</strong>. "
        f"Toko yang berada di bawah rata-rata perlu dievaluasi dari sisi lokasi strategis, "
        f"product mix, dan strategi pemasaran lokal."
    )

    # ── Top Products ──
    try:
        products_df = load_product_performance()
        st.divider()
        st.subheader("🥇 Top 10 Products by Revenue")
        top10 = products_df.head(10)
        fig_top = go.Figure(go.Bar(
            y=top10["product_detail"],
            x=top10["revenue"],
            orientation="h",
            marker=dict(
                color=top10["revenue"],
                colorscale=[[0, "#1e3a5f"], [0.5, "#38bdf8"], [1, "#818cf8"]],
                cornerradius=4,
            ),
            text=[fmt_currency(v) for v in top10["revenue"]],
            textposition="outside",
            textfont=dict(color="#94a3b8", size=10),
        ))
        fig_top.update_layout(
            title="Top 10 Products — Revenue",
            yaxis=dict(autorange="reversed"),
            showlegend=False,
            height=450,
        )
        apply_plotly_theme(fig_top)
        st.plotly_chart(fig_top, use_container_width=True)

        top1 = top10.iloc[0]
        insight_card("🏅", "Best Seller",
            f"Produk <strong>{top1['product_detail']}</strong> (kategori: {top1['category_name']}) "
            f"menjadi produk dengan revenue tertinggi sebesar <strong>{fmt_full_currency(top1['revenue'])}</strong> "
            f"dari <strong>{top1['transactions']:,}</strong> transaksi. "
            f"Produk ini terjual di <strong>{top1['stores_selling']}</strong> toko dan "
            f"dibeli oleh <strong>{top1['unique_customers']:,}</strong> pelanggan unik."
        )
    except Exception:
        pass


# ╔══════════════════════════════════════════════════════════════╗
# ║  PAGE 2 — SALES DEEP ANALYTICS                              ║
# ╚══════════════════════════════════════════════════════════════╝

elif page == "📊  Sales Deep Analytics":

    st.markdown('<div class="page-badge">SALES ANALYTICS</div>', unsafe_allow_html=True)
    st.title("Sales Deep Analytics")
    st.caption(
        "Analisis mendalam pola penjualan — tren bulanan, distribusi kategori, "
        "pola jam sibuk, dan performa produk secara granular."
    )

    try:
        sales_df = load_sales_detail()
    except requests.RequestException:
        st.warning("Endpoint `/analytics/sales-detail` belum tersedia.")
        st.stop()

    sales_df["transaction_date"] = pd.to_datetime(sales_df["transaction_date"])

    # ── Monthly Revenue Trend ──
    st.subheader("📈 Monthly Revenue Trend")

    monthly = (
        sales_df
        .assign(month=sales_df["transaction_date"].dt.to_period("M").astype(str))
        .groupby("month")
        .agg(
            revenue=("revenue", "sum"),
            transactions=("transaction_id", "nunique"),
            quantity=("transaction_qty", "sum"),
        )
        .reset_index()
    )

    monthly["revenue_change"] = monthly["revenue"].pct_change() * 100

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=monthly["month"], y=monthly["revenue"],
        mode="lines+markers",
        name="Revenue",
        line=dict(color="#38bdf8", width=3),
        marker=dict(size=8, color="#38bdf8"),
        fill="tozeroy",
        fillcolor="rgba(56, 189, 248, 0.08)",
    ))
    fig.update_layout(title="Monthly Revenue Trend", yaxis_title="Revenue (Rp)")
    apply_plotly_theme(fig)
    st.plotly_chart(fig, use_container_width=True)

    # Monthly metrics
    best_month = monthly.loc[monthly["revenue"].idxmax()]
    worst_month = monthly.loc[monthly["revenue"].idxmin()]
    avg_monthly = monthly["revenue"].mean()

    insight_card("📅", "Monthly Revenue Analysis",
        f"Bulan dengan revenue tertinggi: <strong>{best_month['month']}</strong> "
        f"({fmt_full_currency(best_month['revenue'])}). "
        f"Bulan terendah: <strong>{worst_month['month']}</strong> "
        f"({fmt_full_currency(worst_month['revenue'])}). "
        f"Rata-rata revenue bulanan: <strong>{fmt_full_currency(avg_monthly)}</strong>. "
        f"Perhatikan tren kenaikan/penurunan untuk mengoptimalkan strategi seasonal campaign."
    )

    st.divider()

    # ── Category Analysis ──
    st.subheader("🏷️ Category Performance")

    category = (
        sales_df
        .groupby("category_name")
        .agg(
            revenue=("revenue", "sum"),
            quantity=("transaction_qty", "sum"),
            transactions=("transaction_id", "nunique"),
            avg_price=("unit_price", "mean"),
        )
        .reset_index()
        .sort_values("revenue", ascending=False)
    )
    category["aov"] = category["revenue"] / category["transactions"]
    total_cat_rev = category["revenue"].sum()
    category["share_pct"] = (category["revenue"] / total_cat_rev * 100).round(1)

    col1, col2 = st.columns(2)

    with col1:
        fig_bar = go.Figure(go.Bar(
            x=category["category_name"],
            y=category["revenue"],
            marker=dict(color=COLOR_SEQUENCE[:len(category)], cornerradius=6),
            text=[f"{s}%" for s in category["share_pct"]],
            textposition="outside",
            textfont=dict(color="#94a3b8", size=11),
        ))
        fig_bar.update_layout(title="Revenue by Category", xaxis_tickangle=45)
        apply_plotly_theme(fig_bar)
        st.plotly_chart(fig_bar, use_container_width=True)

    with col2:
        fig_pie = px.pie(
            category, names="category_name", values="revenue",
            color_discrete_sequence=COLOR_SEQUENCE,
            hole=0.55,
        )
        fig_pie.update_traces(
            textposition="outside",
            textinfo="label+percent",
            textfont=dict(color="#94a3b8"),
        )
        fig_pie.update_layout(
            title="Revenue Share by Category",
            showlegend=False,
        )
        apply_plotly_theme(fig_pie)
        st.plotly_chart(fig_pie, use_container_width=True)

    top_cat = category.iloc[0]
    insight_card("🏷️", "Category Insight",
        f"Kategori <strong>{top_cat['category_name']}</strong> mendominasi dengan "
        f"<strong>{top_cat['share_pct']}%</strong> total revenue "
        f"({fmt_full_currency(top_cat['revenue'])}). "
        f"Rata-rata harga di kategori ini: <strong>{fmt_full_currency(top_cat['avg_price'])}</strong> "
        f"dengan <strong>{top_cat['transactions']:,.0f}</strong> transaksi. "
        f"Fokus promosi dan stock allocation ke kategori ini untuk maximize ROI."
    )

    st.divider()

    # ── Sunburst: Store → Category ──
    st.subheader("🎯 Revenue Composition — Store × Category")

    store_cat = (
        sales_df
        .groupby(["store_location", "category_name"])
        .agg(revenue=("revenue", "sum"))
        .reset_index()
    )

    fig_sun = px.sunburst(
        store_cat,
        path=["store_location", "category_name"],
        values="revenue",
        color_discrete_sequence=COLOR_SEQUENCE,
    )
    fig_sun.update_layout(title="Hierarchical Revenue — Store → Category", height=550)
    fig_sun.update_traces(
        textinfo="label+percent parent",
        insidetextfont=dict(color="white"),
    )
    apply_plotly_theme(fig_sun)
    st.plotly_chart(fig_sun, use_container_width=True)

    insight_card("🎯", "Komposisi Revenue",
        "Sunburst chart menunjukkan kontribusi setiap kategori di masing-masing toko. "
        "Klik segmen untuk drill-down. Ini membantu mengidentifikasi "
        "<strong>kategori unggulan per toko</strong> sehingga keputusan product mix "
        "dan space allocation bisa dibuat berdasarkan data, bukan asumsi."
    )

    st.divider()

    # ── Hourly Activity ──
    st.subheader("⏰ Hourly Transaction Activity")

    sales_df["hour"] = pd.to_datetime(sales_df["transaction_time"]).dt.hour

    hourly = (
        sales_df.groupby("hour")
        .agg(
            transactions=("transaction_id", "nunique"),
            revenue=("revenue", "sum"),
        )
        .reset_index()
    )

    fig_hr = go.Figure()
    fig_hr.add_trace(go.Bar(
        x=hourly["hour"], y=hourly["transactions"],
        name="Transactions",
        marker=dict(
            color=hourly["transactions"],
            colorscale=[[0, "#1e3a5f"], [0.5, "#38bdf8"], [1, "#818cf8"]],
            cornerradius=6,
        ),
    ))
    fig_hr.update_layout(
        title="Transactions by Hour of Day",
        xaxis_title="Hour (24h)",
        yaxis_title="Transactions",
    )
    apply_plotly_theme(fig_hr)
    st.plotly_chart(fig_hr, use_container_width=True)

    peak_hour = hourly.loc[hourly["transactions"].idxmax()]
    off_hour = hourly.loc[hourly["transactions"].idxmin()]

    insight_card("⏰", "Peak Hours Analysis",
        f"Jam tersibuk: <strong>{int(peak_hour['hour']):02d}:00</strong> "
        f"dengan <strong>{peak_hour['transactions']:,.0f}</strong> transaksi. "
        f"Jam paling sepi: <strong>{int(off_hour['hour']):02d}:00</strong> "
        f"({off_hour['transactions']:,.0f} transaksi). "
        f"Alokasikan lebih banyak staf dan pastikan stok prima pada jam sibuk. "
        f"Pertimbangkan flash promotion di jam sepi untuk meratakan traffic."
    )

    st.divider()

    # ── Day of Week ──
    st.subheader("📆 Day-of-Week Pattern")

    sales_df["day_name"] = sales_df["transaction_date"].dt.day_name()
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    dow = (
        sales_df.groupby("day_name")
        .agg(
            revenue=("revenue", "sum"),
            transactions=("transaction_id", "nunique"),
        )
        .reindex(day_order)
        .reset_index()
    )

    fig_dow = go.Figure()
    fig_dow.add_trace(go.Bar(
        x=dow["day_name"], y=dow["revenue"],
        marker=dict(
            color=["#818cf8" if d in ["Saturday", "Sunday"] else "#38bdf8" for d in dow["day_name"]],
            cornerradius=6,
        ),
        text=[fmt_currency(v) for v in dow["revenue"]],
        textposition="outside",
        textfont=dict(color="#94a3b8", size=10),
    ))
    fig_dow.update_layout(title="Revenue by Day of Week", yaxis_title="Revenue (Rp)")
    apply_plotly_theme(fig_dow)
    st.plotly_chart(fig_dow, use_container_width=True)

    weekend_rev = dow[dow["day_name"].isin(["Saturday", "Sunday"])]["revenue"].sum()
    weekday_rev = dow[~dow["day_name"].isin(["Saturday", "Sunday"])]["revenue"].sum()
    we_pct = weekend_rev / (weekend_rev + weekday_rev) * 100

    insight_card("📆", "Weekday vs Weekend",
        f"Revenue weekend (Sab-Min): <strong>{fmt_full_currency(weekend_rev)}</strong> "
        f"(<em>{we_pct:.1f}%</em>). "
        f"Revenue weekday (Sen-Jum): <strong>{fmt_full_currency(weekday_rev)}</strong> "
        f"(<em>{100-we_pct:.1f}%</em>). "
        f"{'Weekend mendominasi — fokus promosi dan event di hari libur.' if we_pct > 50 else 'Weekday mendominasi — pelanggan cenderung berbelanja di hari kerja, pertimbangkan loyalty program untuk weekend.'}"
    )


# ╔══════════════════════════════════════════════════════════════╗
# ║  PAGE 3 — CUSTOMER INTELLIGENCE                             ║
# ╚══════════════════════════════════════════════════════════════╝

elif page == "👥  Customer Intelligence":

    st.markdown('<div class="page-badge">CUSTOMER ANALYTICS</div>', unsafe_allow_html=True)
    st.title("Customer Intelligence")
    st.caption(
        "Analisis pelanggan berbasis RFM (Recency, Frequency, Monetary) — "
        "segmentasi, profil demografis, dan estimasi customer lifetime value."
    )

    try:
        cust_df = load_customer_segments()
    except requests.RequestException:
        st.error("Customer segments API tidak tersedia.")
        st.stop()

    if "recency" in cust_df.columns:
        cust_df["recency"] = pd.to_numeric(cust_df["recency"], errors="coerce").fillna(0).astype(int)

    # ── RFM Overview ──
    st.subheader("📊 RFM Segmentation Overview")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Customers", fmt_number(len(cust_df)))
    c2.metric("Avg Recency", f"{cust_df['recency'].mean():.0f} days")
    c3.metric("Avg Frequency", f"{cust_df['frequency'].mean():.1f} txn")
    c4.metric("Avg Monetary", fmt_currency(cust_df["monetary"].mean()))

    st.divider()

    # ── Segment Distribution ──
    st.subheader("🎯 Customer Segment Distribution")
    seg_counts = cust_df["customer_segment"].value_counts().reset_index()
    seg_counts.columns = ["segment", "count"]
    seg_counts["pct"] = (seg_counts["count"] / seg_counts["count"].sum() * 100).round(1)

    col1, col2 = st.columns([2, 3])

    with col1:
        fig_seg = px.pie(
            seg_counts, names="segment", values="count",
            color_discrete_sequence=COLOR_SEQUENCE,
            hole=0.6,
        )
        fig_seg.update_traces(
            textposition="outside",
            textinfo="label+percent",
            textfont=dict(color="#94a3b8", size=11),
        )
        fig_seg.update_layout(title="Segment Distribution", showlegend=False, height=400)
        apply_plotly_theme(fig_seg)
        st.plotly_chart(fig_seg, use_container_width=True)

    with col2:
        seg_metrics = (
            cust_df.groupby("customer_segment")
            .agg(
                customers=("customer_id", "count"),
                avg_recency=("recency", "mean"),
                avg_frequency=("frequency", "mean"),
                avg_monetary=("monetary", "mean"),
                total_revenue=("monetary", "sum"),
            )
            .reset_index()
            .sort_values("total_revenue", ascending=False)
        )
        seg_metrics["avg_recency"] = seg_metrics["avg_recency"].round(0).astype(int)
        seg_metrics["avg_frequency"] = seg_metrics["avg_frequency"].round(1)
        seg_metrics["avg_monetary"] = seg_metrics["avg_monetary"].apply(fmt_currency)
        seg_metrics["total_revenue"] = seg_metrics["total_revenue"].apply(fmt_currency)

        st.markdown("##### 📋 Segment Performance Summary")
        st.dataframe(
            seg_metrics.rename(columns={
                "customer_segment": "Segment",
                "customers": "Customers",
                "avg_recency": "Avg Recency (days)",
                "avg_frequency": "Avg Freq",
                "avg_monetary": "Avg Monetary",
                "total_revenue": "Total Revenue",
            }),
            use_container_width=True,
            hide_index=True,
        )

    top_seg = seg_counts.iloc[0]
    insight_card("🎯", "Segmentation Insight",
        f"Segment terbesar: <strong>{top_seg['segment']}</strong> "
        f"dengan <strong>{top_seg['count']:,}</strong> pelanggan ({top_seg['pct']}%). "
        f"Gunakan strategi retention yang berbeda untuk setiap segment: "
        f"<em>Champions</em> → exclusive rewards, "
        f"<em>At Risk</em> → win-back campaign, "
        f"<em>New Customers</em> → onboarding program."
    )

    st.divider()

    # ── RFM 3D Scatter ──
    st.subheader("🔬 RFM 3D Visualization")

    st.markdown(
        "> Scatter 3D menampilkan setiap pelanggan dalam ruang **Recency × Frequency × Monetary**. "
        "Warna menunjukkan segment. Hover untuk detail."
    )

    fig_3d = px.scatter_3d(
        cust_df,
        x="recency",
        y="frequency",
        z="monetary",
        color="customer_segment",
        hover_name="customer_name",
        hover_data=["city", "gender", "monetary"],
        color_discrete_sequence=COLOR_SEQUENCE,
        opacity=0.8,
    )
    fig_3d.update_layout(
        title="3D RFM Customer Map",
        height=600,
        scene=dict(
            xaxis_title="Recency (days)",
            yaxis_title="Frequency (txn)",
            zaxis_title="Monetary (Rp)",
            bgcolor="rgba(0,0,0,0)",
        ),
    )
    apply_plotly_theme(fig_3d)
    st.plotly_chart(fig_3d, use_container_width=True)

    insight_card("🔬", "RFM 3D Interpretation",
        "Pelanggan di <strong>sudut kiri-atas-depan</strong> (recency rendah, frequency tinggi, monetary tinggi) "
        "adalah <em>Champions</em> — pelanggan paling berharga. "
        "Pelanggan di <strong>sudut kanan-bawah-belakang</strong> adalah yang berisiko churn. "
        "Fokus retensi pada cluster yang mulai bergeser ke arah recency tinggi."
    )

    st.divider()

    # ── Demographics ──
    st.subheader("👤 Customer Demographics")

    col1, col2 = st.columns(2)

    with col1:
        gender_rev = cust_df.groupby("gender").agg(
            count=("customer_id", "count"),
            revenue=("monetary", "sum"),
        ).reset_index()

        fig_g = px.bar(
            gender_rev, x="gender", y="revenue",
            color="gender", color_discrete_sequence=["#38bdf8", "#f472b6", "#a78bfa"],
            text=[fmt_currency(v) for v in gender_rev["revenue"]],
        )
        fig_g.update_traces(textposition="outside", textfont=dict(color="#94a3b8"))
        fig_g.update_layout(title="Revenue by Gender", showlegend=False)
        apply_plotly_theme(fig_g)
        st.plotly_chart(fig_g, use_container_width=True)

    with col2:
        city_rev = (
            cust_df.groupby("city")
            .agg(count=("customer_id", "count"), revenue=("monetary", "sum"))
            .reset_index()
            .sort_values("revenue", ascending=False)
            .head(10)
        )

        fig_c = go.Figure(go.Bar(
            y=city_rev["city"], x=city_rev["revenue"],
            orientation="h",
            marker=dict(
                color=city_rev["revenue"],
                colorscale=[[0, "#1e3a5f"], [0.5, "#a78bfa"], [1, "#f472b6"]],
                cornerradius=4,
            ),
            text=[fmt_currency(v) for v in city_rev["revenue"]],
            textposition="outside",
            textfont=dict(color="#94a3b8", size=10),
        ))
        fig_c.update_layout(
            title="Top 10 Cities by Revenue",
            yaxis=dict(autorange="reversed"),
            showlegend=False,
        )
        apply_plotly_theme(fig_c)
        st.plotly_chart(fig_c, use_container_width=True)

    st.divider()

    # ── Individual Customer Lookup ──
    st.subheader("🔎 Individual Customer Deep Dive")

    customer_id = st.number_input("Customer ID", min_value=1, value=1, step=1)

    if st.button("🔍 Analyze Customer", type="primary"):
        try:
            cdata = api_get(f"/customers/{customer_id}/rfm")

            st.markdown("---")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Recency", f"{cdata['recency']} days")
            c2.metric("Frequency", f"{cdata['frequency']} txn")
            c3.metric("Monetary", fmt_full_currency(cdata["monetary"]))
            c4.metric("Segment", cdata.get("customer_segment", "N/A"))

            info_cols = {k: v for k, v in cdata.items()
                         if k not in ["recency", "frequency", "monetary", "customer_segment"]}

            insight_card("👤", f"Customer #{customer_id} Profile",
                f"<strong>{cdata.get('customer_name', 'Unknown')}</strong> "
                f"dari <em>{cdata.get('city', 'N/A')}</em> ({cdata.get('gender', 'N/A')}). "
                f"Segment: <strong>{cdata.get('customer_segment', 'N/A')}</strong>. "
                f"Total spending: <strong>{fmt_full_currency(cdata['monetary'])}</strong> "
                f"dalam <strong>{cdata['frequency']}</strong> transaksi. "
                f"Terakhir berbelanja <strong>{cdata['recency']}</strong> hari yang lalu."
            )

            with st.expander("📄 Raw Customer Data"):
                st.json(cdata)

        except requests.HTTPError:
            st.error(f"Customer ID {customer_id} tidak ditemukan.")


# ╔══════════════════════════════════════════════════════════════╗
# ║  PAGE 4 — INVENTORY INTELLIGENCE                            ║
# ╚══════════════════════════════════════════════════════════════╝

elif page == "📦  Inventory Intelligence":

    st.markdown('<div class="page-badge">INVENTORY ANALYTICS</div>', unsafe_allow_html=True)
    st.title("Inventory Intelligence")
    st.caption(
        "Monitoring kesehatan inventaris, analisis risiko stockout, "
        "dan rekomendasi reorder berbasis demand forecasting."
    )

    try:
        inv_health = load_inventory_health()
        inv_reorder = load_inventory_recommendations()
    except requests.RequestException:
        st.error("Inventory API tidak tersedia.")
        st.stop()

    # ── Health Summary ──
    st.subheader("🏥 Inventory Health Summary")

    if "risk_level" in inv_health.columns:
        risk_col = "risk_level"
    else:
        risk_col = "risk"

    risk_summary = inv_health[risk_col].value_counts().reset_index()
    risk_summary.columns = ["risk", "count"]

    total_items = len(inv_health)
    critical = int(risk_summary.loc[risk_summary["risk"] == "Critical", "count"].sum())
    high = int(risk_summary.loc[risk_summary["risk"] == "High", "count"].sum())
    medium = int(risk_summary.loc[risk_summary["risk"] == "Medium", "count"].sum())
    low = int(risk_summary.loc[risk_summary["risk"] == "Low", "count"].sum())

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total SKUs Tracked", fmt_number(total_items))
    c2.metric("🔴 Critical", critical)
    c3.metric("🟠 High Risk", high)
    c4.metric("🟡 Medium Risk", medium)
    c5.metric("🟢 Low Risk", low)

    st.divider()

    # ── Risk Distribution ──
    st.subheader("⚠️ Risk Distribution")

    col1, col2 = st.columns(2)

    with col1:
        risk_order = ["Critical", "High", "Medium", "Low", "No Demand"]
        risk_display = risk_summary[risk_summary["risk"].isin(risk_order)].copy()
        risk_display["color"] = risk_display["risk"].map(COLOR_RISK)

        fig_risk = go.Figure(go.Bar(
            x=risk_display["risk"],
            y=risk_display["count"],
            marker=dict(
                color=[COLOR_RISK.get(r, "#64748b") for r in risk_display["risk"]],
                cornerradius=6,
            ),
            text=risk_display["count"],
            textposition="outside",
            textfont=dict(color="#94a3b8", size=12, weight="bold"),
        ))
        fig_risk.update_layout(title="Items by Risk Level", yaxis_title="Count")
        apply_plotly_theme(fig_risk)
        st.plotly_chart(fig_risk, use_container_width=True)

    with col2:
        fig_pie_risk = px.pie(
            risk_display, names="risk", values="count",
            color="risk",
            color_discrete_map=COLOR_RISK,
            hole=0.6,
        )
        fig_pie_risk.update_traces(
            textposition="outside",
            textinfo="label+percent",
            textfont=dict(color="#94a3b8"),
        )
        fig_pie_risk.update_layout(title="Risk Proportion", showlegend=False)
        apply_plotly_theme(fig_pie_risk)
        st.plotly_chart(fig_pie_risk, use_container_width=True)

    health_pct_critical = (critical / max(total_items, 1)) * 100
    insight_card("⚠️", "Inventory Risk Assessment",
        f"Dari <strong>{total_items:,}</strong> SKU yang dimonitor, "
        f"<strong>{critical}</strong> ({health_pct_critical:.1f}%) berada di level <em>Critical</em> "
        f"(sisa stock ≤ 2 hari) dan <strong>{high}</strong> di level <em>High</em> (≤ 5 hari). "
        f"SKU Critical memerlukan <strong>immediate reorder</strong> untuk menghindari lost sales. "
        f"Disarankan untuk mengaktifkan auto-reorder trigger untuk item-item Critical."
    )

    st.divider()

    # ── Stock Coverage Days ──
    if "days_of_stock" in inv_health.columns:
        st.subheader("📊 Stock Coverage Days Distribution")

        valid_dos = inv_health[inv_health["days_of_stock"] < 999].copy()

        if not valid_dos.empty:
            fig_dos = px.histogram(
                valid_dos, x="days_of_stock",
                nbins=30,
                color_discrete_sequence=["#38bdf8"],
            )
            fig_dos.update_layout(
                title="Distribution of Stock Coverage (Days)",
                xaxis_title="Days of Stock Remaining",
                yaxis_title="Number of SKUs",
            )
            # Add reference lines
            fig_dos.add_vline(x=2, line_dash="dash", line_color="#ef4444",
                              annotation_text="Critical (2 days)")
            fig_dos.add_vline(x=5, line_dash="dash", line_color="#f97316",
                              annotation_text="High (5 days)")
            fig_dos.add_vline(x=10, line_dash="dash", line_color="#fbbf24",
                              annotation_text="Medium (10 days)")
            apply_plotly_theme(fig_dos)
            st.plotly_chart(fig_dos, use_container_width=True)

            med_dos = valid_dos["days_of_stock"].median()
            insight_card("📊", "Stock Coverage Analysis",
                f"Median coverage: <strong>{med_dos:.1f} hari</strong>. "
                f"SKU dengan coverage &lt;2 hari harus di-reorder segera. "
                f"Target optimal: minimal 7-10 hari stock coverage untuk menghindari "
                f"gangguan supply chain dan mempertahankan service level."
            )

            st.divider()

    # ── Store-wise Inventory ──
    if "store_location" in inv_health.columns:
        st.subheader("🏪 Store-wise Inventory Status")

        store_inv = (
            inv_health.groupby("store_location")
            .agg(
                total_skus=("product_id", "count"),
                avg_stock=("closing_stock", "mean"),
                critical_count=(risk_col, lambda x: (x == "Critical").sum()),
                stockout_count=("stockout_flag", "sum"),
            )
            .reset_index()
            .sort_values("critical_count", ascending=False)
        )

        fig_store_inv = go.Figure()
        fig_store_inv.add_trace(go.Bar(
            x=store_inv["store_location"],
            y=store_inv["critical_count"],
            name="Critical",
            marker_color="#ef4444",
        ))
        fig_store_inv.add_trace(go.Bar(
            x=store_inv["store_location"],
            y=store_inv["stockout_count"],
            name="Stockout",
            marker_color="#f97316",
        ))
        fig_store_inv.update_layout(
            title="Critical Items & Stockouts by Store",
            barmode="group",
            yaxis_title="Count",
        )
        apply_plotly_theme(fig_store_inv)
        st.plotly_chart(fig_store_inv, use_container_width=True)

    st.divider()

    # ── Reorder Priority Table ──
    st.subheader("📋 Reorder Priority List")

    if inv_reorder.empty:
        st.success("✅ Tidak ada produk yang membutuhkan reorder saat ini.")
    else:
        total_reorder_units = inv_reorder["reorder_quantity"].sum()

        st.metric("Total Units to Reorder", f"{total_reorder_units:,.0f} units")

        display_inv = inv_reorder.head(25).copy()

        def color_risk_fn(val):
            colors = {
                "Critical": "background-color: rgba(239,68,68,0.2); color: #ef4444;",
                "High": "background-color: rgba(249,115,22,0.2); color: #f97316;",
                "Medium": "background-color: rgba(251,191,36,0.2); color: #fbbf24;",
                "Low": "background-color: rgba(34,197,94,0.2); color: #22c55e;",
            }
            return colors.get(val, "")

        st.dataframe(display_inv, use_container_width=True, hide_index=True)

        insight_card("📋", "Reorder Recommendation",
            f"Total <strong>{len(inv_reorder):,}</strong> SKU memerlukan reorder "
            f"dengan total <strong>{total_reorder_units:,.0f} unit</strong>. "
            f"Prioritaskan item dengan risk <em>Critical</em> terlebih dahulu. "
            f"Reorder quantity sudah termasuk <strong>safety stock 20%</strong> "
            f"di atas forecast demand 7 hari."
        )


# ╔══════════════════════════════════════════════════════════════╗
# ║  PAGE 5 — DEMAND FORECAST                                   ║
# ╚══════════════════════════════════════════════════════════════╝

elif page == "🔮  Demand Forecast":

    st.markdown('<div class="page-badge">ML-POWERED FORECAST</div>', unsafe_allow_html=True)
    st.title("Demand Forecast")
    st.caption(
        "Prediksi demand 7 hari ke depan menggunakan Random Forest Regressor "
        "berbasis histori penjualan, kalender, dan data cuaca."
    )

    insight_card("🤖", "Model Information",
        "Model: <strong>Random Forest Regressor</strong> | "
        "Features: lag demand (1,7,14,28 hari), rolling mean (7,28), "
        "calendar features (day of week, weekend, month), weather (temperature, rainfall), "
        "store & product encoding. "
        "Prediksi bersifat <em>recursive</em> — output hari ke-N menjadi input hari ke-(N+1)."
    )

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        store_id = st.number_input("Store ID", min_value=1, value=8, step=1)

    with col2:
        product_id = st.number_input("Product ID", min_value=1, value=87, step=1)

    if st.button("🔮 Generate 7-Day Forecast", type="primary", use_container_width=True):

        try:
            with st.spinner("Running ML forecast model..."):
                result = api_post(
                    "/forecast/7-days",
                    {"store_id": int(store_id), "product_id": int(product_id)},
                )

            forecasts = pd.DataFrame(result["forecasts"])
            forecasts["date"] = pd.to_datetime(forecasts["date"])

            st.divider()
            st.subheader("📈 7-Day Demand Forecast")

            c1, c2, c3 = st.columns(3)
            c1.metric("Total Forecast Demand", f"{result['total_forecast_demand']:.2f} units")
            c2.metric("Avg Daily Demand", f"{result['total_forecast_demand']/7:.2f} units")
            c3.metric("Forecast Horizon", "7 Days")

            # Forecast chart
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=forecasts["date"], y=forecasts["predicted_demand"],
                mode="lines+markers+text",
                line=dict(color="#38bdf8", width=3),
                marker=dict(size=10, color="#38bdf8", line=dict(color="#818cf8", width=2)),
                text=[f"{v:.1f}" for v in forecasts["predicted_demand"]],
                textposition="top center",
                textfont=dict(color="#94a3b8", size=11),
                fill="tozeroy",
                fillcolor="rgba(56, 189, 248, 0.08)",
                name="Predicted Demand",
            ))
            fig.update_layout(
                title=f"7-Day Demand Forecast — Store {store_id}, Product {product_id}",
                xaxis_title="Date",
                yaxis_title="Predicted Demand (units)",
                height=400,
            )
            apply_plotly_theme(fig)
            st.plotly_chart(fig, use_container_width=True)

            # Forecast data table
            with st.expander("📊 Forecast Data Table"):
                forecasts_display = forecasts.copy()
                forecasts_display["date"] = forecasts_display["date"].dt.strftime("%Y-%m-%d (%A)")
                st.dataframe(forecasts_display, use_container_width=True, hide_index=True)

            # Analyze pattern
            max_day = forecasts.loc[forecasts["predicted_demand"].idxmax()]
            min_day = forecasts.loc[forecasts["predicted_demand"].idxmin()]
            trend_direction = "naik" if forecasts["predicted_demand"].iloc[-1] > forecasts["predicted_demand"].iloc[0] else "turun"

            insight_card("📈", "Forecast Interpretation",
                f"Prediksi demand tertinggi: <strong>{max_day['date'].strftime('%A, %d %b')}</strong> "
                f"({max_day['predicted_demand']:.2f} units). "
                f"Terendah: <strong>{min_day['date'].strftime('%A, %d %b')}</strong> "
                f"({min_day['predicted_demand']:.2f} units). "
                f"Tren keseluruhan <strong>{trend_direction}</strong>. "
                f"Total demand 7 hari: <strong>{result['total_forecast_demand']:.2f} units</strong>."
            )

            st.divider()

            # ── Auto Inventory Recommendation ──
            st.subheader("📦 Automatic Inventory Recommendation")

            try:
                rec = api_post(
                    "/inventory/forecast-recommendation",
                    {"store_id": int(store_id), "product_id": int(product_id)},
                )

                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Current Stock", f"{rec['current_stock']:.0f} units")
                c2.metric("7-Day Forecast", f"{rec['forecast_7d_demand']:.0f} units")
                c3.metric("Reorder Qty", f"{rec['reorder_quantity']:.0f} units")

                risk_emoji = {"Critical": "🔴", "High": "🟠", "Medium": "🟡", "Low": "🟢", "No Demand": "⚪"}
                c4.metric("Risk Level", f"{risk_emoji.get(rec['risk'], '⚪')} {rec['risk']}")

                stock_gap = rec["current_stock"] - rec["forecast_7d_demand"]
                if stock_gap < 0:
                    insight_card("🚨", "Stock Alert",
                        f"<strong>{rec['product_detail']}</strong> memiliki "
                        f"<strong>defisit stock {abs(stock_gap):.0f} unit</strong>. "
                        f"Stock saat ini ({rec['current_stock']:.0f}) tidak cukup untuk memenuhi "
                        f"forecast demand 7 hari ({rec['forecast_7d_demand']:.0f}). "
                        f"Segera lakukan reorder sebanyak <strong>{rec['reorder_quantity']:.0f} unit</strong> "
                        f"(sudah termasuk safety stock 20%)."
                    )
                else:
                    insight_card("✅", "Stock Status",
                        f"<strong>{rec['product_detail']}</strong> memiliki "
                        f"stock yang {'memadai' if rec['risk'] in ['Low', 'Medium'] else 'perlu dimonitor'}. "
                        f"Current stock: <strong>{rec['current_stock']:.0f} unit</strong>, "
                        f"forecast 7 hari: <strong>{rec['forecast_7d_demand']:.0f} unit</strong>. "
                        f"Surplus: <strong>{stock_gap:.0f} unit</strong>."
                    )

            except requests.RequestException:
                st.warning("Inventory recommendation tidak tersedia untuk produk ini.")

        except requests.RequestException as exc:
            st.error(f"Forecast gagal: {exc}")


# ╔══════════════════════════════════════════════════════════════╗
# ║  PAGE 6 — WEATHER & EXTERNAL FACTORS                        ║
# ╚══════════════════════════════════════════════════════════════╝

elif page == "🌦️  Weather & External":

    st.markdown('<div class="page-badge">EXTERNAL FACTORS</div>', unsafe_allow_html=True)
    st.title("Weather & External Factors")
    st.caption(
        "Analisis pengaruh cuaca (suhu, curah hujan, kondisi cuaca) "
        "terhadap pola penjualan di setiap lokasi toko."
    )

    try:
        weather_df = load_weather_impact()
    except requests.RequestException:
        st.error("Weather API tidak tersedia.")
        st.stop()

    weather_df["date"] = pd.to_datetime(weather_df["date"])

    # ── Overview ──
    st.subheader("🌡️ Weather Overview")

    c1, c2, c3 = st.columns(3)
    c1.metric("Avg Temperature", f"{weather_df['temperature'].mean():.1f}°C")
    c2.metric("Avg Rainfall", f"{weather_df['rainfall_mm'].mean():.1f} mm")

    condition_counts = weather_df["weather_condition"].value_counts()
    most_common = condition_counts.index[0]
    c3.metric("Most Common Weather", most_common)

    st.divider()

    # ── Temperature vs Revenue ──
    st.subheader("🌡️ Temperature vs Revenue")

    weather_sales = weather_df[weather_df["revenue"] > 0].copy()

    if not weather_sales.empty:
        fig_temp = px.scatter(
            weather_sales,
            x="temperature", y="revenue",
            color="location",
            color_discrete_sequence=COLOR_SEQUENCE,
            opacity=0.7,
        )

        # Overall trendline with numpy (tanpa dependency statsmodels)
        if len(weather_sales) > 1:
            try:
                x_vals = weather_sales["temperature"].astype(float).values
                y_vals = weather_sales["revenue"].astype(float).values
                valid_mask = ~np.isnan(x_vals) & ~np.isnan(y_vals)
                if np.sum(valid_mask) > 1:
                    slope, intercept = np.polyfit(x_vals[valid_mask], y_vals[valid_mask], 1)
                    x_line = np.linspace(x_vals[valid_mask].min(), x_vals[valid_mask].max(), 50)
                    y_line = slope * x_line + intercept
                    fig_temp.add_trace(go.Scatter(
                        x=x_line, y=y_line,
                        mode="lines",
                        name=f"Trend (Slope: {slope:+.1f})",
                        line=dict(color="#f43f5e", width=2.5, dash="dash"),
                    ))
            except Exception:
                pass

        fig_temp.update_layout(
            title="Temperature vs Daily Revenue (per Store)",
            xaxis_title="Temperature (°C)",
            yaxis_title="Revenue (Rp)",
            height=500,
        )
        apply_plotly_theme(fig_temp)
        st.plotly_chart(fig_temp, use_container_width=True)

        # Correlation
        corr_temp = weather_sales[["temperature", "revenue"]].corr().iloc[0, 1]
        corr_strength = "kuat" if abs(corr_temp) > 0.5 else ("sedang" if abs(corr_temp) > 0.3 else "lemah")
        corr_dir = "positif" if corr_temp > 0 else "negatif"

        insight_card("🌡️", "Temperature-Revenue Correlation",
            f"Korelasi: <strong>r = {corr_temp:.3f}</strong> ({corr_strength}, {corr_dir}). "
            f"{'Suhu yang lebih tinggi berkorelasi dengan penjualan lebih tinggi — kemungkinan produk minuman dingin/es lebih laku di cuaca panas.' if corr_temp > 0 else 'Suhu yang lebih rendah berkorelasi dengan penjualan lebih tinggi — pelanggan mungkin lebih sering berbelanja di cuaca sejuk.'} "
            f"Gunakan informasi ini untuk <strong>menyesuaikan stock</strong> berdasarkan forecast cuaca."
        )

    st.divider()

    # ── Rainfall Impact ──
    st.subheader("🌧️ Rainfall Impact Analysis")

    if not weather_sales.empty:
        fig_rain = px.scatter(
            weather_sales,
            x="rainfall_mm", y="revenue",
            color="location",
            color_discrete_sequence=COLOR_SEQUENCE,
            opacity=0.7,
        )

        # Overall trendline with numpy (tanpa dependency statsmodels)
        if len(weather_sales) > 1:
            try:
                x_vals = weather_sales["rainfall_mm"].astype(float).values
                y_vals = weather_sales["revenue"].astype(float).values
                valid_mask = ~np.isnan(x_vals) & ~np.isnan(y_vals)
                if np.sum(valid_mask) > 1:
                    slope, intercept = np.polyfit(x_vals[valid_mask], y_vals[valid_mask], 1)
                    x_line = np.linspace(x_vals[valid_mask].min(), x_vals[valid_mask].max(), 50)
                    y_line = slope * x_line + intercept
                    fig_rain.add_trace(go.Scatter(
                        x=x_line, y=y_line,
                        mode="lines",
                        name=f"Trend (Slope: {slope:+.1f})",
                        line=dict(color="#f43f5e", width=2.5, dash="dash"),
                    ))
            except Exception:
                pass

        fig_rain.update_layout(
            title="Rainfall vs Daily Revenue",
            xaxis_title="Rainfall (mm)",
            yaxis_title="Revenue (Rp)",
        )
        apply_plotly_theme(fig_rain)
        st.plotly_chart(fig_rain, use_container_width=True)

        corr_rain = weather_sales[["rainfall_mm", "revenue"]].corr().iloc[0, 1]
        insight_card("🌧️", "Rainfall-Revenue Correlation",
            f"Korelasi curah hujan-revenue: <strong>r = {corr_rain:.3f}</strong>. "
            f"{'Hujan berdampak negatif terhadap penjualan — pertimbangkan delivery service atau promosi online di hari hujan.' if corr_rain < 0 else 'Hujan tidak mengurangi penjualan secara signifikan — pelanggan tetap berbelanja meskipun hujan.'}"
        )

    st.divider()

    # ── Weather Condition Comparison ──
    st.subheader("☀️ Sales by Weather Condition")

    cond_agg = (
        weather_sales.groupby("weather_condition")
        .agg(
            avg_revenue=("revenue", "mean"),
            avg_qty=("quantity", "mean"),
            avg_txn=("transactions", "mean"),
            days=("date", "count"),
        )
        .reset_index()
    )

    weather_colors = {"Clear": "#fbbf24", "Cloudy": "#94a3b8", "Rain": "#38bdf8"}

    fig_cond = go.Figure()
    fig_cond.add_trace(go.Bar(
        x=cond_agg["weather_condition"],
        y=cond_agg["avg_revenue"],
        marker=dict(
            color=[weather_colors.get(c, "#64748b") for c in cond_agg["weather_condition"]],
            cornerradius=6,
        ),
        text=[fmt_currency(v) for v in cond_agg["avg_revenue"]],
        textposition="outside",
        textfont=dict(color="#94a3b8", size=12),
    ))
    fig_cond.update_layout(
        title="Average Daily Revenue by Weather Condition",
        yaxis_title="Avg Revenue (Rp)",
    )
    apply_plotly_theme(fig_cond)
    st.plotly_chart(fig_cond, use_container_width=True)

    if len(cond_agg) > 1:
        best_weather = cond_agg.loc[cond_agg["avg_revenue"].idxmax()]
        worst_weather = cond_agg.loc[cond_agg["avg_revenue"].idxmin()]
        diff_pct = ((best_weather["avg_revenue"] - worst_weather["avg_revenue"]) / worst_weather["avg_revenue"]) * 100

        insight_card("☀️", "Weather Condition Impact",
            f"Cuaca <strong>{best_weather['weather_condition']}</strong> menghasilkan rata-rata revenue harian tertinggi "
            f"(<strong>{fmt_currency(best_weather['avg_revenue'])}</strong>), "
            f"<strong>{diff_pct:.1f}%</strong> lebih tinggi dibanding "
            f"<strong>{worst_weather['weather_condition']}</strong> "
            f"({fmt_currency(worst_weather['avg_revenue'])}). "
            f"Optimalkan staffing dan stock berdasarkan weather forecast."
        )

    st.divider()

    # ── Store Weather Sensitivity ──
    st.subheader("🏪 Store Weather Sensitivity")

    store_weather = (
        weather_sales.groupby("location")
        .apply(lambda g: g[["temperature", "revenue"]].corr().iloc[0, 1], include_groups=False)
        .reset_index()
    )
    store_weather.columns = ["location", "temp_corr"]
    store_weather["abs_corr"] = store_weather["temp_corr"].abs()
    store_weather = store_weather.sort_values("abs_corr", ascending=False)

    fig_sens = go.Figure(go.Bar(
        x=store_weather["location"],
        y=store_weather["temp_corr"],
        marker=dict(
            color=["#ef4444" if c < 0 else "#22c55e" for c in store_weather["temp_corr"]],
            cornerradius=6,
        ),
        text=[f"{v:.3f}" for v in store_weather["temp_corr"]],
        textposition="outside",
        textfont=dict(color="#94a3b8", size=11),
    ))
    fig_sens.update_layout(
        title="Temperature-Revenue Correlation by Store",
        yaxis_title="Correlation (r)",
        yaxis_range=[-1, 1],
    )
    fig_sens.add_hline(y=0, line_dash="dash", line_color="rgba(148,163,184,0.3)")
    apply_plotly_theme(fig_sens)
    st.plotly_chart(fig_sens, use_container_width=True)

    most_sensitive = store_weather.iloc[0]
    insight_card("🏪", "Store Sensitivity Analysis",
        f"Toko yang paling sensitif terhadap perubahan suhu: <strong>{most_sensitive['location']}</strong> "
        f"(r = {most_sensitive['temp_corr']:.3f}). "
        f"Toko dengan korelasi positif tinggi akan mengalami peningkatan penjualan saat cuaca panas, "
        f"sedangkan toko dengan korelasi negatif akan lebih ramai saat cuaca dingin. "
        f"Sesuaikan product mix dan kampanye promosi per toko berdasarkan pola ini."
    )


# ╔══════════════════════════════════════════════════════════════╗
# ║  PAGE 7 — DATA EXPLORER                                     ║
# ╚══════════════════════════════════════════════════════════════╝

elif page == "📋  Data Explorer":

    st.markdown('<div class="page-badge">DATA EXPLORER</div>', unsafe_allow_html=True)
    st.title("Data Explorer")
    st.caption(
        "Eksplorasi data mentah dengan filter interaktif. "
        "Browsing, filtering, statistik, dan download data."
    )

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🛒 Sales Data",
        "👥 Customers",
        "📦 Products",
        "📊 Inventory",
        "🌦️ Weather",
    ])

    # ── Tab 1: Sales ──
    with tab1:
        st.subheader("🛒 Sales Transactions Explorer")

        try:
            sales_raw = load_sales_detail()
            sales_raw["transaction_date"] = pd.to_datetime(sales_raw["transaction_date"])

            # Filters
            col1, col2, col3 = st.columns(3)
            with col1:
                stores_list = ["All"] + sorted(sales_raw["store_location"].unique().tolist())
                sel_store = st.selectbox("Store", stores_list, key="exp_store")
            with col2:
                cats_list = ["All"] + sorted(sales_raw["category_name"].unique().tolist())
                sel_cat = st.selectbox("Category", cats_list, key="exp_cat")
            with col3:
                date_range = st.date_input(
                    "Date Range",
                    value=(
                        sales_raw["transaction_date"].min().date(),
                        sales_raw["transaction_date"].max().date(),
                    ),
                    key="exp_dates",
                )

            filtered = sales_raw.copy()
            if sel_store != "All":
                filtered = filtered[filtered["store_location"] == sel_store]
            if sel_cat != "All":
                filtered = filtered[filtered["category_name"] == sel_cat]
            if len(date_range) == 2:
                filtered = filtered[
                    (filtered["transaction_date"].dt.date >= date_range[0])
                    & (filtered["transaction_date"].dt.date <= date_range[1])
                ]

            st.markdown(f"**{len(filtered):,}** records found")

            st.dataframe(filtered.head(500), use_container_width=True, hide_index=True)

            # Quick stats
            with st.expander("📊 Quick Statistics"):
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Total Revenue", fmt_full_currency(filtered["revenue"].sum()))
                c2.metric("Unique Transactions", fmt_number(filtered["transaction_id"].nunique()))
                c3.metric("Avg Unit Price", fmt_full_currency(filtered["unit_price"].mean()))
                c4.metric("Avg Qty/Txn", f"{filtered['transaction_qty'].mean():.2f}")

            # Download
            csv_data = filtered.to_csv(index=False)
            st.download_button(
                "📥 Download Filtered Data (CSV)",
                csv_data,
                "sales_data_filtered.csv",
                "text/csv",
            )

        except requests.RequestException:
            st.warning("Sales data not available.")

    # ── Tab 2: Customers ──
    with tab2:
        st.subheader("👥 Customer Database")

        try:
            cust_raw = load_customer_segments()

            col1, col2 = st.columns(2)
            with col1:
                segs = ["All"] + sorted(cust_raw["customer_segment"].unique().tolist())
                sel_seg = st.selectbox("Segment", segs, key="exp_seg")
            with col2:
                cities = ["All"] + sorted(cust_raw["city"].unique().tolist())
                sel_city = st.selectbox("City", cities, key="exp_city")

            cust_filt = cust_raw.copy()
            if sel_seg != "All":
                cust_filt = cust_filt[cust_filt["customer_segment"] == sel_seg]
            if sel_city != "All":
                cust_filt = cust_filt[cust_filt["city"] == sel_city]

            st.markdown(f"**{len(cust_filt):,}** customers found")
            st.dataframe(cust_filt.head(500), use_container_width=True, hide_index=True)

            csv_cust = cust_filt.to_csv(index=False)
            st.download_button("📥 Download Customer Data", csv_cust, "customers_filtered.csv", "text/csv")

        except requests.RequestException:
            st.warning("Customer data not available.")

    # ── Tab 3: Products ──
    with tab3:
        st.subheader("📦 Product Performance")

        try:
            prod_raw = load_product_performance()

            cat_filter = ["All"] + sorted(prod_raw["category_name"].unique().tolist())
            sel_pcat = st.selectbox("Category", cat_filter, key="exp_pcat")

            prod_filt = prod_raw.copy()
            if sel_pcat != "All":
                prod_filt = prod_filt[prod_filt["category_name"] == sel_pcat]

            st.markdown(f"**{len(prod_filt):,}** products found")
            st.dataframe(prod_filt.head(500), use_container_width=True, hide_index=True)

            csv_prod = prod_filt.to_csv(index=False)
            st.download_button("📥 Download Product Data", csv_prod, "products_filtered.csv", "text/csv")

        except requests.RequestException:
            st.warning("Product data not available.")

    # ── Tab 4: Inventory ──
    with tab4:
        st.subheader("📊 Inventory Health Data")

        try:
            inv_raw = load_inventory_health()

            risk_filter = ["All"] + sorted(inv_raw.get("risk_level", inv_raw.get("risk", pd.Series())).unique().tolist())
            sel_risk = st.selectbox("Risk Level", risk_filter, key="exp_risk")

            inv_filt = inv_raw.copy()
            risk_col_name = "risk_level" if "risk_level" in inv_filt.columns else "risk"
            if sel_risk != "All":
                inv_filt = inv_filt[inv_filt[risk_col_name] == sel_risk]

            st.markdown(f"**{len(inv_filt):,}** items found")
            st.dataframe(inv_filt.head(500), use_container_width=True, hide_index=True)

            csv_inv = inv_filt.to_csv(index=False)
            st.download_button("📥 Download Inventory Data", csv_inv, "inventory_filtered.csv", "text/csv")

        except requests.RequestException:
            st.warning("Inventory data not available.")

    # ── Tab 5: Weather ──
    with tab5:
        st.subheader("🌦️ Weather Data")

        try:
            wth_raw = load_weather_impact()
            wth_raw["date"] = pd.to_datetime(wth_raw["date"])

            col1, col2 = st.columns(2)
            with col1:
                locs = ["All"] + sorted(wth_raw["location"].unique().tolist())
                sel_loc = st.selectbox("Location", locs, key="exp_loc")
            with col2:
                conds = ["All"] + sorted(wth_raw["weather_condition"].unique().tolist())
                sel_cond = st.selectbox("Condition", conds, key="exp_cond")

            wth_filt = wth_raw.copy()
            if sel_loc != "All":
                wth_filt = wth_filt[wth_filt["location"] == sel_loc]
            if sel_cond != "All":
                wth_filt = wth_filt[wth_filt["weather_condition"] == sel_cond]

            st.markdown(f"**{len(wth_filt):,}** records found")
            st.dataframe(wth_filt.head(500), use_container_width=True, hide_index=True)

            csv_wth = wth_filt.to_csv(index=False)
            st.download_button("📥 Download Weather Data", csv_wth, "weather_filtered.csv", "text/csv")

        except requests.RequestException:
            st.warning("Weather data not available.")

    st.divider()

    # ── Data Quality Summary ──
    st.subheader("📋 Data Quality Summary")

    try:
        sales_q = load_sales_detail()
        sales_q["transaction_date"] = pd.to_datetime(sales_q["transaction_date"])

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Sales Records", fmt_number(len(sales_q)))
        c2.metric("Date Range",
            f"{sales_q['transaction_date'].min().strftime('%Y-%m-%d')} → "
            f"{sales_q['transaction_date'].max().strftime('%Y-%m-%d')}")
        c3.metric("Unique Products", fmt_number(sales_q["product_id"].nunique()))
        c4.metric("Unique Stores", fmt_number(sales_q["store_id"].nunique()))

        insight_card("📋", "Data Completeness",
            f"Dataset mencakup <strong>{len(sales_q):,}</strong> transaksi "
            f"dari <strong>{sales_q['transaction_date'].min().strftime('%d %B %Y')}</strong> "
            f"hingga <strong>{sales_q['transaction_date'].max().strftime('%d %B %Y')}</strong>. "
            f"Melibatkan <strong>{sales_q['product_id'].nunique()}</strong> produk unik "
            f"di <strong>{sales_q['store_id'].nunique()}</strong> toko. "
            f"Data telah di-validasi dan siap untuk analisis."
        )
    except Exception:
        pass


# ╔══════════════════════════════════════════════════════════════╗
# ║  FOOTER                                                      ║
# ╚══════════════════════════════════════════════════════════════╝

st.markdown("---")
st.markdown(
    """<div style="text-align: center; padding: 20px 0; color: #475569; font-size: 0.75rem;">
    <strong style="color: #64748b;">Smart Retail Intelligence</strong> • 
    Powered by PostgreSQL, FastAPI, Random Forest ML, and Streamlit •
    Built with  for Data-Driven Retail
    </div>""",
    unsafe_allow_html=True,
)