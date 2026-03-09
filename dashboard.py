"""
Painel de Gestao Juridica — Dal'Col, Laranja & Sa
Streamlit dashboard: modular architecture with KPI engine, dynamic insights.
"""
import streamlit as st
from data_loader import load_data, get_file_mtime, get_file_mtime_display
from filters import apply_filters
from kpi_engine import compute_kpis, compute_insight, compute_posicao_summary
from charts import (
    chart_clients_dual_bar, build_abc_data, chart_abc_curve,
    chart_top_clients_by_year, chart_monthly_trend, chart_client_area,
    chart_city_distribution, chart_abc_by_city,
    chart_top_opposing, chart_aging, chart_resolution_rate,
)
from styles import COLORS, GLOBAL_CSS, render_kpi_card

st.set_page_config(
    page_title="Dal'Col, Laranja & Sa — Painel Juridico",
    page_icon="briefcase",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# ─── Sidebar ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Dal'Col, Laranja & Sa")
    st.markdown("Painel de Gestao Juridica")
    st.markdown("---")

    freshness = get_file_mtime_display()
    st.caption(f"Dados atualizados em: {freshness}")

    df_raw = load_data(get_file_mtime())

    all_status = sorted(df_raw["status"].dropna().unique())
    sel_status = st.multiselect("Status", all_status, default=all_status)

    all_years = sorted(df_raw["ano"].dropna().unique())
    sel_years = st.multiselect("Ano", all_years, default=all_years)

    all_cities = sorted(df_raw["cidade"].dropna().unique())
    sel_cities = st.multiselect("Cidade", all_cities, default=all_cities)

    all_clients = sorted(df_raw["cliente"].dropna().unique())
    sel_clients = st.multiselect("Cliente", all_clients, default=all_clients)

    all_varas = sorted(df_raw["vara_turma"].dropna().unique())
    sel_varas = st.multiselect("Vara/Turma", all_varas, default=all_varas)

    st.markdown("---")

df, df_ativos = apply_filters(
    df_raw, sel_status, sel_years, sel_cities, sel_clients, sel_varas
)

# ─── Header ──────────────────────────────────────────────
st.markdown("""
<div class="dash-header">
    <h1>Painel de Gestao Juridica</h1>
    <p class="subtitle">Diagnostico operacional — concentracao, gargalos e tendencias</p>
    <p class="brand">Dal'Col, Laranja & Sa — Advogados Associados</p>
</div>
""", unsafe_allow_html=True)

# ─── KPIs ────────────────────────────────────────────────
kpis = compute_kpis(df, df_ativos)

cards_html = '<div class="kpi-row">'
cards_html += render_kpi_card("Total Processos", f"{kpis['total']:,}", "na base filtrada")
cards_html += render_kpi_card(
    "Ativos", f"{kpis['ativos']:,}",
    f"{kpis['ativos']*100//max(kpis['total'],1)}% do total"
)
cards_html += render_kpi_card(
    "Taxa de Resolucao", f"{kpis['taxa_res']}%",
    f"{kpis['baixados']+kpis['encerrados']} resolvidos",
    semaphore=kpis["taxa_res_sem"], action_text=kpis["taxa_res_action"]
)
cards_html += render_kpi_card(
    "Idade Media Ativos", f"{kpis['age_months']}m",
    f"{kpis['age_days']} dias",
    semaphore=kpis["age_sem"], action_text=kpis["age_action"]
)
cards_html += render_kpi_card(
    "Concentracao Top 3", f"{kpis['top3_pct']}%",
    f"maior cliente: {kpis['top1_pct']}%",
    semaphore=kpis["top3_sem"], action_text=kpis["top3_action"]
)
cards_html += render_kpi_card(
    "Clientes", str(kpis["n_clientes"]),
    f"{kpis['n_cidades']} cidades"
)
cards_html += '</div>'
st.markdown(cards_html, unsafe_allow_html=True)

# ─── Posicao Cliente (CLI-05) ────────────────────────────
posicao = compute_posicao_summary(df)
posicao_text = posicao["summary"]
if posicao["exceptions"]:
    exc_parts = [f"{k}: {v}" for k, v in posicao["exceptions"].items()]
    posicao_text += f" | Excecoes: {', '.join(exc_parts)}"
st.caption(posicao_text)

# ─── Dynamic Insight Box (KPI-06) ────────────────────────
insight_html = compute_insight(kpis, df_ativos)
st.markdown(f"""
<div class="insight-box">
    <h4>Diagnostico — Primeiro Problema a Atacar</h4>
    {insight_html}
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# TABS
# ═══════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4 = st.tabs([
    "Clientes", "Tendencias", "Geografico", "Operacional",
])

abc = build_abc_data(df_ativos)

# ─── TAB 1: Clientes ─────────────────────────────────────
with tab1:
    st.markdown('<p class="sec-title">Volume por cliente</p>'
                '<p class="sec-headline">Processos por Cliente</p>'
                '<p class="sec-sub">Comparativo total vs ativos — '
                'barras verticais agrupadas</p>', unsafe_allow_html=True)

    st.plotly_chart(chart_clients_dual_bar(df, df_ativos),
                    use_container_width=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    st.markdown('<p class="sec-title">Concentracao</p>'
                '<p class="sec-headline">Curva ABC</p>'
                '<p class="sec-sub">Poucos clientes concentram a maioria '
                'dos processos ativos</p>', unsafe_allow_html=True)

    st.plotly_chart(chart_abc_curve(abc), use_container_width=True)

    if not abc.empty:
        a_c = len(abc[abc["classe"] == "A"])
        b_c = len(abc[abc["classe"] == "B"])
        c_c = len(abc[abc["classe"] == "C"])
        a_p = abc[abc["classe"] == "A"]["pct"].sum()
        b_p = abc[abc["classe"] == "B"]["pct"].sum()
        c_p = abc[abc["classe"] == "C"]["pct"].sum()

        st.markdown(f"""
        <div class="kpi-row">
            <div class="kpi-card" style="border-left:3px solid {COLORS['navy']}">
                <div class="kpi-label">Classe A</div>
                <div class="kpi-value">{a_c}</div>
                <div class="kpi-sub">clientes = {a_p:.0f}% dos processos</div>
            </div>
            <div class="kpi-card" style="border-left:3px solid {COLORS['blue']}">
                <div class="kpi-label">Classe B</div>
                <div class="kpi-value">{b_c}</div>
                <div class="kpi-sub">clientes = {b_p:.0f}% dos processos</div>
            </div>
            <div class="kpi-card" style="border-left:3px solid {COLORS['gray_300']}">
                <div class="kpi-label">Classe C</div>
                <div class="kpi-value">{c_c}</div>
                <div class="kpi-sub">clientes = {c_p:.0f}% dos processos</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    st.markdown('<p class="sec-title">Evolucao</p>'
                '<p class="sec-headline">Top Clientes por Ano</p>'
                '<p class="sec-sub">Somente processos ativos</p>',
                unsafe_allow_html=True)
    top_n = st.slider("Clientes no grafico", 3, 10, 6, key="top_n")
    st.plotly_chart(chart_top_clients_by_year(df_ativos, top_n),
                    use_container_width=True)

# ─── TAB 2: Tendencias ───────────────────────────────────
with tab2:
    st.markdown('<p class="sec-title">Tendencia temporal</p>'
                '<p class="sec-headline">Processos Ajuizados</p>'
                '<p class="sec-sub">Tendencia mensal, comparacao ano a ano</p>',
                unsafe_allow_html=True)
    st.plotly_chart(chart_monthly_trend(df), use_container_width=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    st.markdown('<p class="sec-title">Composicao</p>'
                '<p class="sec-headline">Processos Ativos por Cliente</p>'
                '<p class="sec-sub">Area empilhada — evolucao anual</p>',
                unsafe_allow_html=True)
    top_area = st.slider("Clientes", 3, 6, 6, key="top_area")
    st.plotly_chart(chart_client_area(df_ativos, top_area),
                    use_container_width=True)

# ─── TAB 3: Geografico ───────────────────────────────────
with tab3:
    st.markdown('<p class="sec-title">Distribuicao geografica</p>'
                '<p class="sec-headline">Processos por Cidade</p>'
                '<p class="sec-sub">Onde estao concentrados os processos</p>',
                unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(chart_city_distribution(df), use_container_width=True)
    with c2:
        st.plotly_chart(chart_abc_by_city(df_ativos, abc),
                        use_container_width=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    st.markdown('<p class="sec-title">Partes contrarias</p>'
                '<p class="sec-headline">Reus Mais Frequentes</p>'
                '<p class="sec-sub">Potencial para negociacao em bloco</p>',
                unsafe_allow_html=True)
    st.plotly_chart(chart_top_opposing(df), use_container_width=True)

# ─── TAB 4: Operacional ──────────────────────────────────
with tab4:
    st.markdown('<p class="sec-title">Eficiencia</p>'
                '<p class="sec-headline">Indicadores Operacionais</p>'
                '<p class="sec-sub">Aging dos processos e taxa de resolucao</p>',
                unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(chart_aging(df_ativos), use_container_width=True)
    with c2:
        st.plotly_chart(chart_resolution_rate(df), use_container_width=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    vara_load = df_ativos["vara_turma"].value_counts().reset_index()
    vara_load.columns = ["Vara/Turma", "Processos"]
    orgao_load = df_ativos["orgao"].value_counts().reset_index()
    orgao_load.columns = ["Orgao", "Processos"]
    orgao_load["Orgao"] = orgao_load["Orgao"].str.title()

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<p class="sec-headline">Processos por Vara</p>',
                    unsafe_allow_html=True)
        st.dataframe(vara_load, use_container_width=True, hide_index=True,
                     height=280)
    with c2:
        st.markdown('<p class="sec-headline">Processos por Orgao</p>',
                    unsafe_allow_html=True)
        st.dataframe(orgao_load, use_container_width=True, hide_index=True,
                     height=280)

# ─── Data Table ──────────────────────────────────────────
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown('<p class="sec-headline">Base Completa</p>',
            unsafe_allow_html=True)

table = df[["pasta", "data_distribuicao", "num_processo", "cliente",
            "contrario", "vara_turma", "status", "cidade"]].copy()
table.columns = ["Pasta", "Data", "Processo", "Cliente",
                 "Parte Contraria", "Vara", "Status", "Cidade"]
table["Cliente"] = table["Cliente"].str.title()
table["Parte Contraria"] = table["Parte Contraria"].str.title()
table["Cidade"] = table["Cidade"].str.title()
table = table.sort_values("Data", ascending=False)

st.dataframe(table, use_container_width=True, height=400, hide_index=True,
             column_config={"Data": st.column_config.DateColumn(
                 "Data", format="DD/MM/YYYY")})

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.caption("Dal'Col, Laranja & Sa — Advogados Associados")
