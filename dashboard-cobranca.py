import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime

# ─────────────────────────────────────────────
# CONFIG & THEME
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Painel Jurídico",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Corporate color palette
COLORS = {
    "primary": "#1B2A4A",       # Dark navy
    "secondary": "#2E4057",     # Steel blue
    "accent": "#3B82F6",        # Bright blue
    "accent_light": "#60A5FA",  # Light blue
    "success": "#10B981",       # Emerald
    "warning": "#F59E0B",       # Amber
    "danger": "#EF4444",        # Red
    "muted": "#94A3B8",         # Slate
    "bg": "#F8FAFC",            # Off-white
    "card": "#FFFFFF",          # White
    "text": "#1E293B",          # Dark text
    "text_light": "#64748B",    # Light text
    "border": "#E2E8F0",        # Border
}

STATUS_COLORS = {
    "ativo": "#3B82F6",
    "baixado": "#94A3B8",
    "encerrado": "#10B981",
    "suspenso": "#F59E0B",
}

# Plotly chart template
CHART_TEMPLATE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, -apple-system, sans-serif", color=COLORS["text"], size=12),
    margin=dict(l=40, r=20, t=50, b=40),
    hoverlabel=dict(
        bgcolor=COLORS["primary"],
        font_size=12,
        font_family="Inter, sans-serif",
        font_color="white",
    ),
)

AXIS_STYLE = dict(
    showgrid=True,
    gridcolor="#F1F5F9",
    gridwidth=1,
    zeroline=False,
    linecolor=COLORS["border"],
    linewidth=1,
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Main background */
    .stApp {
        background-color: #F8FAFC;
    }

    /* Header styling */
    .dashboard-header {
        background: linear-gradient(135deg, #1B2A4A 0%, #2E4057 100%);
        padding: 2rem 2.5rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        position: relative;
        overflow: hidden;
    }
    .dashboard-header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -10%;
        width: 300px;
        height: 300px;
        background: radial-gradient(circle, rgba(59,130,246,0.15) 0%, transparent 70%);
        border-radius: 50%;
    }
    .dashboard-header h1 {
        color: white;
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        font-size: 1.75rem;
        margin: 0;
        letter-spacing: -0.02em;
    }
    .dashboard-header p {
        color: rgba(255,255,255,0.65);
        font-family: 'Inter', sans-serif;
        font-weight: 400;
        font-size: 0.875rem;
        margin: 0.35rem 0 0 0;
    }

    /* KPI Cards */
    .kpi-row {
        display: flex;
        gap: 1rem;
        margin-bottom: 1.5rem;
    }
    .kpi-card {
        background: white;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 1.25rem 1.5rem;
        flex: 1;
        transition: box-shadow 0.2s;
    }
    .kpi-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.06);
    }
    .kpi-label {
        font-family: 'Inter', sans-serif;
        font-size: 0.75rem;
        font-weight: 500;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.35rem;
    }
    .kpi-value {
        font-family: 'Inter', sans-serif;
        font-size: 1.75rem;
        font-weight: 700;
        color: #1E293B;
        line-height: 1;
    }
    .kpi-sub {
        font-family: 'Inter', sans-serif;
        font-size: 0.75rem;
        font-weight: 400;
        color: #94A3B8;
        margin-top: 0.25rem;
    }

    /* Section titles */
    .section-title {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 1.1rem;
        color: #1E293B;
        margin: 2rem 0 0.5rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #E2E8F0;
        letter-spacing: -0.01em;
    }
    .section-subtitle {
        font-family: 'Inter', sans-serif;
        font-weight: 400;
        font-size: 0.8rem;
        color: #94A3B8;
        margin-top: -0.35rem;
        margin-bottom: 1rem;
    }

    /* Chart container */
    .chart-container {
        background: white;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1rem;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E2E8F0;
    }
    section[data-testid="stSidebar"] .stMarkdown h3 {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 0.85rem;
        color: #1B2A4A;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }

    /* Remove default streamlit padding */
    .block-container {
        padding: 1.5rem 2rem 2rem 2rem !important;
        max-width: 100% !important;
    }

    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
    }
    .stTabs [data-baseweb="tab"] {
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        font-size: 0.85rem;
        color: #64748B;
        border-radius: 8px 8px 0 0;
    }

    /* Divider */
    .divider {
        height: 1px;
        background: #E2E8F0;
        margin: 1.5rem 0;
    }

    /* Hide streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Data table */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_excel("dados.xlsx")
    df.columns = [
        "pasta", "data_distribuicao", "num_processo", "cliente",
        "posicao_cliente", "contrario", "vara_turma", "orgao",
        "status", "cidade", "bairro", "rua"
    ]
    df["data_distribuicao"] = pd.to_datetime(df["data_distribuicao"], errors="coerce")
    df["ano"] = df["data_distribuicao"].dt.year.astype("Int64")
    df["mes"] = df["data_distribuicao"].dt.month.astype("Int64")
    df["ano_mes"] = df["data_distribuicao"].dt.to_period("M").astype(str)
    df["cliente"] = df["cliente"].str.strip().str.title()
    df["contrario"] = df["contrario"].str.strip().str.title()
    df["cidade"] = df["cidade"].str.strip().str.title()
    df["status"] = df["status"].str.strip().str.lower()
    df["vara_turma"] = df["vara_turma"].str.strip()
    return df

df_raw = load_data()

# ─────────────────────────────────────────────
# SIDEBAR FILTERS
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚖️ Painel Jurídico")
    st.markdown('<div style="height:0.5rem"></div>', unsafe_allow_html=True)
    st.markdown("### Filtros")

    # Status filter
    all_status = sorted(df_raw["status"].dropna().unique())
    sel_status = st.multiselect(
        "Status",
        options=all_status,
        default=all_status,
        key="filter_status",
    )

    # Year filter
    all_years = sorted(df_raw["ano"].dropna().unique())
    sel_years = st.multiselect(
        "Ano de Distribuição",
        options=all_years,
        default=all_years,
        key="filter_years",
    )

    # City filter
    all_cities = sorted(df_raw["cidade"].dropna().unique())
    sel_cities = st.multiselect(
        "Cidade",
        options=all_cities,
        default=all_cities,
        key="filter_cities",
    )

    # Client filter
    all_clients = sorted(df_raw["cliente"].dropna().unique())
    sel_clients = st.multiselect(
        "Cliente",
        options=all_clients,
        default=all_clients,
        key="filter_clients",
    )

    # Vara/turma filter
    all_varas = sorted(df_raw["vara_turma"].dropna().unique())
    sel_varas = st.multiselect(
        "Vara/Turma",
        options=all_varas,
        default=all_varas,
        key="filter_varas",
    )

    st.markdown("---")
    st.markdown(
        '<p style="font-size:0.7rem;color:#94A3B8;text-align:center;">Dados atualizados conforme planilha importada</p>',
        unsafe_allow_html=True,
    )

# Apply filters
df = df_raw[
    (df_raw["status"].isin(sel_status))
    & (df_raw["ano"].isin(sel_years))
    & (df_raw["cidade"].isin(sel_cities))
    & (df_raw["cliente"].isin(sel_clients))
    & (df_raw["vara_turma"].isin(sel_varas))
].copy()

df_ativos = df[df["status"] == "ativo"].copy()

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="dashboard-header">
    <h1>⚖️ Painel de Gestão Jurídica</h1>
    <p>Visão consolidada do escritório — processos, clientes e tendências</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# KPI ROW (minimal, contextual)
# ─────────────────────────────────────────────
total = len(df)
ativos = len(df[df["status"] == "ativo"])
baixados = len(df[df["status"] == "baixado"])
encerrados = len(df[df["status"] == "encerrado"])
suspensos = len(df[df["status"] == "suspenso"])
n_clientes = df["cliente"].nunique()

st.markdown(f"""
<div class="kpi-row">
    <div class="kpi-card">
        <div class="kpi-label">Total de Processos</div>
        <div class="kpi-value">{total:,}</div>
        <div class="kpi-sub">filtro aplicado</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">Ativos</div>
        <div class="kpi-value" style="color:#3B82F6">{ativos:,}</div>
        <div class="kpi-sub">{ativos/total*100:.1f}% do total</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">Baixados</div>
        <div class="kpi-value" style="color:#94A3B8">{baixados:,}</div>
        <div class="kpi-sub">{baixados/total*100:.1f}% do total</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">Encerrados</div>
        <div class="kpi-value" style="color:#10B981">{encerrados:,}</div>
        <div class="kpi-sub">{encerrados/total*100:.1f}% do total</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">Suspensos</div>
        <div class="kpi-value" style="color:#F59E0B">{suspensos:,}</div>
        <div class="kpi-sub">{suspensos/total*100:.1f}% do total</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">Clientes</div>
        <div class="kpi-value">{n_clientes}</div>
        <div class="kpi-sub">clientes únicos</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# HELPER: Truncate long names
# ─────────────────────────────────────────────
def truncate(text, max_len=30):
    if pd.isna(text):
        return ""
    text = str(text)
    return text[:max_len] + "…" if len(text) > max_len else text


def apply_chart_layout(fig, height=420):
    fig.update_layout(
        **CHART_TEMPLATE,
        height=height,
        xaxis=AXIS_STYLE,
        yaxis=AXIS_STYLE,
        legend=dict(
            font=dict(size=11),
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor=COLORS["border"],
            borderwidth=1,
        ),
    )
    return fig


# ═══════════════════════════════════════════════
# SECTION 1: PROCESSOS POR CLIENTE
# ═══════════════════════════════════════════════
st.markdown('<div class="section-title">Processos por Cliente</div>', unsafe_allow_html=True)
st.markdown('<div class="section-subtitle">Comparativo entre todos os processos e apenas os ativos</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

# --- Chart 1a: ALL processes by client ---
with col1:
    client_all = (
        df.groupby(["cliente", "status"]).size().reset_index(name="qtd")
    )
    client_order = df["cliente"].value_counts().index.tolist()
    client_all["cliente_short"] = client_all["cliente"].apply(lambda x: truncate(x, 25))
    order_short = [truncate(c, 25) for c in client_order]

    fig1a = px.bar(
        client_all,
        x="cliente_short",
        y="qtd",
        color="status",
        color_discrete_map=STATUS_COLORS,
        category_orders={"cliente_short": order_short},
        title="Todos os Processos por Cliente",
        labels={"qtd": "Quantidade", "cliente_short": ""},
    )
    fig1a.update_layout(
        **CHART_TEMPLATE,
        height=480,
        xaxis={**AXIS_STYLE, "tickangle": -45, "tickfont": dict(size=9)},
        yaxis=AXIS_STYLE,
        barmode="stack",
        legend=dict(
            title="",
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=11),
        ),
    )
    st.plotly_chart(fig1a, use_container_width=True)

# --- Chart 1b: ONLY ativos by client ---
with col2:
    client_ativos = (
        df_ativos["cliente"].value_counts().reset_index()
    )
    client_ativos.columns = ["cliente", "qtd"]
    client_ativos["cliente_short"] = client_ativos["cliente"].apply(lambda x: truncate(x, 25))

    fig1b = px.bar(
        client_ativos,
        x="cliente_short",
        y="qtd",
        title="Processos Ativos por Cliente",
        labels={"qtd": "Quantidade", "cliente_short": ""},
        color_discrete_sequence=[COLORS["accent"]],
    )
    fig1b.update_layout(
        **CHART_TEMPLATE,
        height=480,
        xaxis={**AXIS_STYLE, "tickangle": -45, "tickfont": dict(size=9)},
        yaxis=AXIS_STYLE,
    )
    fig1b.update_traces(
        marker=dict(
            color=COLORS["accent"],
            line=dict(width=0),
            cornerradius=3,
        ),
        hovertemplate="<b>%{x}</b><br>Processos: %{y}<extra></extra>",
    )
    st.plotly_chart(fig1b, use_container_width=True)


# ═══════════════════════════════════════════════
# SECTION 2: CURVA ABC — CONCENTRAÇÃO DE CLIENTES
# ═══════════════════════════════════════════════
st.markdown('<div class="section-title">Curva ABC — Concentração de Processos Ativos</div>', unsafe_allow_html=True)
st.markdown('<div class="section-subtitle">Identifique quais clientes concentram o maior volume de processos ativos do escritório</div>', unsafe_allow_html=True)

abc = df_ativos["cliente"].value_counts().reset_index()
abc.columns = ["cliente", "qtd"]
abc = abc.sort_values("qtd", ascending=False).reset_index(drop=True)
abc["pct"] = abc["qtd"] / abc["qtd"].sum() * 100
abc["pct_acum"] = abc["pct"].cumsum()
abc["cliente_short"] = abc["cliente"].apply(lambda x: truncate(x, 28))

# Classify ABC
def classify_abc(pct_acum):
    if pct_acum <= 80:
        return "A"
    elif pct_acum <= 95:
        return "B"
    return "C"

abc["classe"] = abc["pct_acum"].apply(classify_abc)

abc_colors = {"A": "#3B82F6", "B": "#60A5FA", "C": "#CBD5E1"}

fig_abc = make_subplots(specs=[[{"secondary_y": True}]])

# Bars
for classe in ["A", "B", "C"]:
    subset = abc[abc["classe"] == classe]
    fig_abc.add_trace(
        go.Bar(
            x=subset["cliente_short"],
            y=subset["qtd"],
            name=f"Classe {classe}",
            marker_color=abc_colors[classe],
            marker_cornerradius=3,
            hovertemplate="<b>%{x}</b><br>Processos: %{y}<br>Classe: " + classe + "<extra></extra>",
        ),
        secondary_y=False,
    )

# Cumulative line
fig_abc.add_trace(
    go.Scatter(
        x=abc["cliente_short"],
        y=abc["pct_acum"],
        name="% Acumulado",
        mode="lines+markers",
        line=dict(color=COLORS["primary"], width=2.5),
        marker=dict(size=5, color=COLORS["primary"]),
        hovertemplate="<b>%{x}</b><br>Acumulado: %{y:.1f}%<extra></extra>",
    ),
    secondary_y=True,
)

# Reference lines at 80% and 95%
for pct, label in [(80, "80%"), (95, "95%")]:
    fig_abc.add_hline(
        y=pct,
        line_dash="dot",
        line_color="#94A3B8",
        line_width=1,
        annotation_text=label,
        annotation_position="top left",
        annotation_font=dict(size=10, color="#94A3B8"),
        secondary_y=True,
    )

fig_abc.update_layout(
    **CHART_TEMPLATE,
    height=480,
    title="Curva ABC — Pareto de Processos Ativos por Cliente",
    barmode="stack",
    xaxis={**AXIS_STYLE, "tickangle": -45, "tickfont": dict(size=9)},
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.04,
        xanchor="center",
        x=0.5,
        font=dict(size=11),
    ),
)
fig_abc.update_yaxes(title_text="Qtd Processos", secondary_y=False, **AXIS_STYLE)
fig_abc.update_yaxes(title_text="% Acumulado", secondary_y=True, range=[0, 105], **AXIS_STYLE)

st.plotly_chart(fig_abc, use_container_width=True)

# ABC Summary cards
a_count = len(abc[abc["classe"] == "A"])
b_count = len(abc[abc["classe"] == "B"])
c_count = len(abc[abc["classe"] == "C"])
a_procs = abc[abc["classe"] == "A"]["qtd"].sum()

st.markdown(f"""
<div class="kpi-row">
    <div class="kpi-card" style="border-left: 4px solid #3B82F6;">
        <div class="kpi-label">Classe A</div>
        <div class="kpi-value">{a_count} clientes</div>
        <div class="kpi-sub">concentram {a_procs:,} processos ({abc[abc['classe']=='A']['pct'].sum():.1f}%)</div>
    </div>
    <div class="kpi-card" style="border-left: 4px solid #60A5FA;">
        <div class="kpi-label">Classe B</div>
        <div class="kpi-value">{b_count} clientes</div>
        <div class="kpi-sub">{abc[abc['classe']=='B']['pct'].sum():.1f}% dos processos</div>
    </div>
    <div class="kpi-card" style="border-left: 4px solid #CBD5E1;">
        <div class="kpi-label">Classe C</div>
        <div class="kpi-value">{c_count} clientes</div>
        <div class="kpi-sub">{abc[abc['classe']=='C']['pct'].sum():.1f}% dos processos</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════
# SECTION 3: TOP CLIENTES POR ANO (ATIVOS)
# ═══════════════════════════════════════════════
st.markdown('<div class="section-title">Processos Ativos por Cliente e Ano de Distribuição</div>', unsafe_allow_html=True)
st.markdown('<div class="section-subtitle">Evolução temporal dos maiores clientes — somente processos ativos</div>', unsafe_allow_html=True)

top_n = st.slider("Quantidade de clientes no gráfico", min_value=3, max_value=15, value=8, key="top_n_slider")

top_clients = df_ativos["cliente"].value_counts().head(top_n).index.tolist()
df_top = df_ativos[df_ativos["cliente"].isin(top_clients)].copy()
pivot = df_top.groupby(["ano", "cliente"]).size().reset_index(name="qtd")
pivot["cliente_short"] = pivot["cliente"].apply(lambda x: truncate(x, 25))

# Distinct palette for up to 15 clients
palette = [
    "#3B82F6", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6",
    "#EC4899", "#14B8A6", "#F97316", "#6366F1", "#84CC16",
    "#06B6D4", "#D946EF", "#0EA5E9", "#A3E635", "#FB923C",
]

fig3 = px.bar(
    pivot,
    x="ano",
    y="qtd",
    color="cliente_short",
    barmode="group",
    title=f"Top {top_n} Clientes — Processos Ativos por Ano",
    labels={"qtd": "Quantidade", "ano": "Ano", "cliente_short": "Cliente"},
    color_discrete_sequence=palette[:top_n],
)
fig3.update_layout(
    **CHART_TEMPLATE,
    height=500,
    xaxis={**AXIS_STYLE, "dtick": 1, "tickformat": "d"},
    yaxis=AXIS_STYLE,
    legend=dict(
        title="",
        font=dict(size=10),
        bgcolor="rgba(255,255,255,0.9)",
    ),
)
fig3.update_traces(marker_cornerradius=3)
st.plotly_chart(fig3, use_container_width=True)


# ═══════════════════════════════════════════════
# SECTION 4: PROCESSOS AJUIZADOS — TENDÊNCIA TEMPORAL
# ═══════════════════════════════════════════════
st.markdown('<div class="section-title">Processos Ajuizados</div>', unsafe_allow_html=True)
st.markdown('<div class="section-subtitle">Tendência mensal de novos processos distribuídos, comparação ano a ano</div>', unsafe_allow_html=True)

df_tempo = df.dropna(subset=["data_distribuicao"]).copy()
df_tempo["ano"] = df_tempo["data_distribuicao"].dt.year
df_tempo["mes"] = df_tempo["data_distribuicao"].dt.month

monthly = df_tempo.groupby(["ano", "mes"]).size().reset_index(name="qtd")

meses_nome = {
    1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr", 5: "Mai", 6: "Jun",
    7: "Jul", 8: "Ago", 9: "Set", 10: "Out", 11: "Nov", 12: "Dez",
}
monthly["mes_nome"] = monthly["mes"].map(meses_nome)

year_palette = {
    2016: "#CBD5E1", 2019: "#94A3B8", 2021: "#64748B", 2022: "#475569",
    2023: "#60A5FA", 2024: "#3B82F6", 2025: "#1D4ED8", 2026: "#1E3A5F",
}

fig4 = go.Figure()

for ano in sorted(monthly["ano"].unique()):
    subset = monthly[monthly["ano"] == ano].sort_values("mes")
    color = year_palette.get(ano, COLORS["muted"])
    is_main = ano >= 2023
    fig4.add_trace(
        go.Scatter(
            x=subset["mes_nome"],
            y=subset["qtd"],
            name=str(ano),
            mode="lines+markers",
            line=dict(
                color=color,
                width=3 if is_main else 1.5,
                dash="solid" if is_main else "dot",
            ),
            marker=dict(size=7 if is_main else 4, color=color),
            opacity=1 if is_main else 0.6,
            hovertemplate=f"<b>{ano}</b>" + " — %{x}<br>Processos: %{y}<extra></extra>",
        )
    )

fig4.update_layout(
    **CHART_TEMPLATE,
    height=450,
    title="Processos Ajuizados — Tendência Mensal por Ano",
    xaxis={
        **AXIS_STYLE,
        "categoryorder": "array",
        "categoryarray": list(meses_nome.values()),
        "title": "",
    },
    yaxis={**AXIS_STYLE, "title": "Processos Distribuídos"},
    legend=dict(
        title="Ano",
        orientation="h",
        yanchor="bottom",
        y=1.04,
        xanchor="center",
        x=0.5,
        font=dict(size=11),
    ),
)
st.plotly_chart(fig4, use_container_width=True)


# ═══════════════════════════════════════════════
# SECTION 5: DISTRIBUIÇÃO POR CIDADE
# ═══════════════════════════════════════════════
st.markdown('<div class="section-title">Distribuição por Cidade</div>', unsafe_allow_html=True)
st.markdown('<div class="section-subtitle">Concentração geográfica dos processos</div>', unsafe_allow_html=True)

city_data = df["cidade"].value_counts().reset_index()
city_data.columns = ["cidade", "qtd"]
city_data["pct"] = (city_data["qtd"] / city_data["qtd"].sum() * 100).round(1)

fig5 = px.bar(
    city_data,
    y="cidade",
    x="qtd",
    orientation="h",
    title="Processos por Cidade",
    labels={"qtd": "Quantidade", "cidade": ""},
    text=city_data.apply(lambda r: f"{r['qtd']:,}  ({r['pct']}%)", axis=1),
    color_discrete_sequence=[COLORS["accent"]],
)
fig5.update_layout(
    **CHART_TEMPLATE,
    height=max(300, len(city_data) * 50 + 80),
    yaxis={**AXIS_STYLE, "categoryorder": "total ascending"},
    xaxis=AXIS_STYLE,
)
fig5.update_traces(
    textposition="outside",
    textfont=dict(size=11, color=COLORS["text"]),
    marker=dict(cornerradius=3, line=dict(width=0)),
    hovertemplate="<b>%{y}</b><br>Processos: %{x:,}<extra></extra>",
)
st.plotly_chart(fig5, use_container_width=True)


# ═══════════════════════════════════════════════
# SECTION 6: TOP RÉUS RECORRENTES
# ═══════════════════════════════════════════════
st.markdown('<div class="section-title">Partes Contrárias Mais Frequentes</div>', unsafe_allow_html=True)
st.markdown('<div class="section-subtitle">Réus que aparecem com maior recorrência nos processos</div>', unsafe_allow_html=True)

top_reus = df["contrario"].value_counts().head(15).reset_index()
top_reus.columns = ["contrario", "qtd"]
top_reus["contrario_short"] = top_reus["contrario"].apply(lambda x: truncate(x, 40))

fig6 = px.bar(
    top_reus,
    y="contrario_short",
    x="qtd",
    orientation="h",
    title="Top 15 — Partes Contrárias Recorrentes",
    labels={"qtd": "Processos", "contrario_short": ""},
    text="qtd",
    color_discrete_sequence=["#2E4057"],
)
fig6.update_layout(
    **CHART_TEMPLATE,
    height=520,
    yaxis={**AXIS_STYLE, "categoryorder": "total ascending", "tickfont": dict(size=10)},
    xaxis=AXIS_STYLE,
)
fig6.update_traces(
    textposition="outside",
    textfont=dict(size=11, color=COLORS["text"]),
    marker=dict(cornerradius=3),
    hovertemplate="<b>%{y}</b><br>Processos: %{x}<extra></extra>",
)
st.plotly_chart(fig6, use_container_width=True)


# ═══════════════════════════════════════════════
# SECTION 7: TABELA DE DADOS
# ═══════════════════════════════════════════════
st.markdown('<div class="section-title">Base de Dados Detalhada</div>', unsafe_allow_html=True)
st.markdown('<div class="section-subtitle">Tabela completa com filtros aplicados — clique nas colunas para ordenar</div>', unsafe_allow_html=True)

table_df = df[[
    "pasta", "data_distribuicao", "num_processo", "cliente",
    "contrario", "vara_turma", "status", "cidade"
]].copy()
table_df.columns = [
    "Pasta", "Data Distribuição", "Nº Processo", "Cliente",
    "Parte Contrária", "Vara/Turma", "Status", "Cidade"
]
table_df = table_df.sort_values("Data Distribuição", ascending=False)

st.dataframe(
    table_df,
    use_container_width=True,
    height=450,
    hide_index=True,
    column_config={
        "Data Distribuição": st.column_config.DateColumn("Data Distribuição", format="DD/MM/YYYY"),
        "Status": st.column_config.TextColumn("Status"),
    },
)

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown(
    '<p style="text-align:center;font-size:0.75rem;color:#94A3B8;">Painel de Gestão Jurídica — Dados extraídos da planilha importada</p>',
    unsafe_allow_html=True,
)
