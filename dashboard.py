import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ─── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Sales Dashboard",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Theme / CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.main { background-color: #0f1117; }
.block-container { padding: 1.5rem 2rem 3rem 2rem; max-width: 1400px; }

/* KPI cards */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 14px;
    margin-bottom: 1.5rem;
}
.kpi-card {
    background: linear-gradient(135deg, #1a1d2e 0%, #1e2236 100%);
    border: 1px solid #2a2d4a;
    border-radius: 12px;
    padding: 18px 20px;
    position: relative;
    overflow: hidden;
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #6366f1, #8b5cf6);
    border-radius: 12px 12px 0 0;
}
.kpi-label {
    font-size: 11px;
    font-weight: 500;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 8px;
}
.kpi-value {
    font-size: 28px;
    font-weight: 700;
    color: #f1f5f9;
    line-height: 1;
}
.kpi-sub {
    font-size: 11px;
    color: #4ade80;
    margin-top: 6px;
    font-weight: 500;
}
.kpi-sub.warn { color: #f59e0b; }

/* Insight box */
.insight-box {
    background: linear-gradient(135deg, #1a1d2e, #1a2035);
    border: 1px solid #2a3060;
    border-left: 4px solid #6366f1;
    border-radius: 8px;
    padding: 14px 16px;
    margin-top: 12px;
}
.insight-box p {
    margin: 0;
    font-size: 13px;
    color: #94a3b8;
    line-height: 1.5;
}
.insight-box strong { color: #c7d2fe; }

/* Plotly chart backgrounds */
.js-plotly-plot { border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# ─── Load & prepare data ─────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("Sales Transaction v.4a_clean.csv")
    df["Date"] = pd.to_datetime(df["Date"])
    return df

df = load_data()

# ─── Derived datasets ────────────────────────────────────────────────────────
# Produtos
prod_df = df.groupby("ProductName").agg(
    frequency=("TransactionNo", "count"),
    revenue=("Total_Amount", "sum")
).reset_index()

top_rev  = prod_df.sort_values("revenue",   ascending=False).head(10)
top_freq = prod_df.sort_values("frequency", ascending=False).head(10)

# Tendência mensal — transações únicas por mês (somar z-score não faz sentido)
monthly = df.groupby(df["Date"].dt.to_period("M"))["TransactionNo"].nunique().reset_index()
monthly.columns = ["Date", "transactions"]
monthly["Date"] = monthly["Date"].dt.to_timestamp()

# Tendência diária
daily = df.groupby(df["Date"].dt.date).agg(
    transactions=("TransactionNo", "nunique"),
    revenue=("Total_Amount", "sum"),
).reset_index()
daily.columns = ["date", "transactions", "revenue"]
daily["date"] = pd.to_datetime(daily["date"])

# Países
country_df = df.groupby("Country").agg(
    transactions=("TransactionNo", "count"),
    revenue=("Total_Amount", "sum"),
    customers=("CustomerNo", "nunique")
).reset_index().sort_values("transactions", ascending=False)

intl = country_df[country_df["Country"] != "United Kingdom"].sort_values("revenue", ascending=False).head(8)

# KPI helpers
total_cust = df["CustomerNo"].nunique()
uk_pct = round(
    country_df[country_df["Country"] == "United Kingdom"]["transactions"].values[0] / len(df) * 100, 1
)

# ─── Plotly common theme ─────────────────────────────────────────────────────
LAYOUT = dict(
    paper_bgcolor="#1a1d2e",
    plot_bgcolor="#1a1d2e",
    font=dict(family="Inter", color="#94a3b8"),
    margin=dict(l=0, r=0, t=30, b=0),
    colorway=["#6366f1", "#8b5cf6", "#06b6d4", "#10b981", "#f59e0b"],
)

def apply_theme(fig, title=""):
    fig.update_layout(
        **LAYOUT,
        title=dict(text=title, font=dict(size=14, color="#e2e8f0"), x=0),
        xaxis=dict(gridcolor="#252842", zerolinecolor="#252842"),
        yaxis=dict(gridcolor="#252842", zerolinecolor="#252842"),
    )
    return fig

# ─── Header ──────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom: 24px; padding-bottom: 16px; border-bottom: 1px solid #2a2d4a;">
    <div style="font-size: 11px; color: #6366f1; font-weight: 600; letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 4px;">
        E-Commerce Analytics
    </div>
    <h1 style="font-size: 32px; font-weight: 800; color: #f1f5f9; margin: 0; line-height: 1;">
        Sales Transaction Dashboard
    </h1>
    <p style="margin: 8px 0 0 0; font-size: 13px; color: #6b7280;">
        Período: <strong style="color:#94a3b8;">21 Out — 09 Dez 2019</strong> &nbsp;·&nbsp;
        50 dias · 27 países · Dataset tratado e padronizado
    </p>
</div>
""", unsafe_allow_html=True)

# ─── KPI Cards (4 cartões — o que a análise exploratória sustenta) ────────────

st.markdown(f"""
<div class="kpi-grid">
    <div class="kpi-card">
        <div class="kpi-label">Transações Únicas</div>
        <div class="kpi-value">{df['TransactionNo'].nunique():,}</div>
        <div class="kpi-sub">128.059 registros totais</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">Faturamento Total</div>
        <div class="kpi-value">R$ {df['Total_Amount'].sum():,.3f}</div>
        <div class="kpi-sub">z-score · valor padronizado</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">Produtos Únicos</div>
        <div class="kpi-value">{df['ProductName'].nunique():,}</div>
        <div class="kpi-sub">top 10 = maior fatia da receita</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">Concentração UK</div>
        <div class="kpi-value">{uk_pct}%</div>
        <div class="kpi-sub warn">das transações vêm do Reino Unido</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── Row 1: Tendência de faturamento mensal + diária ─────────────────────────
col1, col2 = st.columns([1, 1], gap="medium")

with col1:
    fig_monthly = go.Figure()
    fig_monthly.add_trace(go.Scatter(
        x=monthly["Date"],
        y=monthly["transactions"],
        mode="lines+markers",
        line=dict(color="#8b5cf6", width=2.5),
        marker=dict(size=7, color="#8b5cf6"),
        fill="tozeroy",
        fillcolor="rgba(139,92,246,0.10)",
        name="Faturamento mensal",
    ))
    apply_theme(fig_monthly, "Transações Mensais (Out–Dez 2019)")
    fig_monthly.update_layout(
        height=300,
        xaxis=dict(tickformat="%b/%Y", tickfont=dict(size=11)),
        yaxis=dict(title="Transações únicas"),
        showlegend=False,
    )
    st.plotly_chart(fig_monthly, use_container_width=True, config={"displayModeBar": False})

with col2:
    fig_daily = go.Figure()
    fig_daily.add_trace(go.Scatter(
        x=daily["date"],
        y=daily["transactions"],
        mode="lines",
        line=dict(color="#6366f1", width=2),
        fill="tozeroy",
        fillcolor="rgba(99,102,241,0.10)",
        name="Transações/dia",
    ))
    apply_theme(fig_daily, "Transações Diárias (Out–Dez 2019)")
    fig_daily.update_layout(
        height=300,
        xaxis=dict(tickformat="%d/%m", tickfont=dict(size=10)),
        yaxis=dict(title="Transações únicas"),
        showlegend=False,
    )
    st.plotly_chart(fig_daily, use_container_width=True, config={"displayModeBar": False})

# ─── Row 2: Top produtos por receita e por frequência ────────────────────────
col3, col4 = st.columns(2, gap="medium")

with col3:
    fig_rev = go.Figure(go.Bar(
        x=top_rev["revenue"],
        y=top_rev["ProductName"],
        orientation="h",
        marker=dict(
            color=top_rev["revenue"],
            colorscale=[[0, "#312e81"], [1, "#818cf8"]],
            showscale=False,
        ),
        text=[f"{v:.1f}" for v in top_rev["revenue"]],
        textposition="outside",
        textfont=dict(size=10, color="#c7d2fe"),
    ))
    apply_theme(fig_rev, "Top 10 Produtos por Faturamento")
    fig_rev.update_layout(
        height=340,
        yaxis=dict(autorange="reversed", tickfont=dict(size=10)),
        xaxis=dict(title="Receita (z-score)"),
    )
    st.plotly_chart(fig_rev, use_container_width=True, config={"displayModeBar": False})

with col4:
    fig_freq = go.Figure(go.Bar(
        x=top_freq["frequency"],
        y=top_freq["ProductName"],
        orientation="h",
        marker=dict(
            color=top_freq["frequency"],
            colorscale=[[0, "#1e3a5f"], [1, "#06b6d4"]],
            showscale=False,
        ),
        text=top_freq["frequency"],
        textposition="outside",
        textfont=dict(size=10, color="#a5f3fc"),
    ))
    apply_theme(fig_freq, "Top 10 Produtos por Frequência de Transações")
    fig_freq.update_layout(
        height=340,
        yaxis=dict(autorange="reversed", tickfont=dict(size=10)),
        xaxis=dict(title="Número de transações"),
    )
    st.plotly_chart(fig_freq, use_container_width=True, config={"displayModeBar": False})

st.markdown("<br>", unsafe_allow_html=True)

# ─── Row 3: Concentração geográfica ──────────────────────────────────────────
col5, col6 = st.columns([1.1, 1], gap="medium")

with col5:
    # Todos os países incluindo UK para mostrar concentração
    top_countries = country_df.head(10)
    colors = ["#6366f1" if c == "United Kingdom" else "#3730a3" for c in top_countries["Country"]]

    fig_geo = go.Figure(go.Bar(
        x=top_countries["transactions"],
        y=top_countries["Country"],
        orientation="h",
        marker_color=colors,
        text=top_countries["transactions"],
        textposition="outside",
        textfont=dict(size=10, color="#e2e8f0"),
    ))
    apply_theme(fig_geo, "Top 10 Países por Volume de Transações")
    fig_geo.update_layout(
        height=340,
        yaxis=dict(autorange="reversed", tickfont=dict(size=10)),
        xaxis=dict(title="Número de registros"),
    )
    st.plotly_chart(fig_geo, use_container_width=True, config={"displayModeBar": False})

with col6:
    fig_intl = go.Figure(go.Bar(
        x=intl["Country"],
        y=intl["revenue"],
        marker=dict(
            color=intl["revenue"],
            colorscale=[[0, "#134e4a"], [1, "#2dd4bf"]],
            showscale=False,
        ),
        text=[f"{v:.1f}" for v in intl["revenue"]],
        textposition="outside",
        textfont=dict(size=11, color="#5eead4"),
    ))
    apply_theme(fig_intl, "Faturamento por País Internacional (excl. UK)")
    fig_intl.update_layout(
        height=340,
        xaxis=dict(title="", tickangle=-30, tickfont=dict(size=10)),
        yaxis=dict(title="Receita (z-score)"),
    )
    st.plotly_chart(fig_intl, use_container_width=True, config={"displayModeBar": False})
# ─── Footer ──────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-top: 2rem; padding-top: 1rem; border-top: 1px solid #2a2d4a;
            text-align: center; font-size: 11px; color: #374151;">
    Sales Transaction v4a · Dataset padronizado (StandardScaler) · 128.059 registros · 4.861 transações únicas
</div>
""", unsafe_allow_html=True)