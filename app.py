# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import altair as alt

# ================================================
# CONFIGURAÇÃO BÁSICA
# ================================================
st.set_page_config(
    page_title="Análise de Criatividade",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🎨 Dashboard de Análise de Criatividade")
st.markdown("Faça upload de um arquivo CSV com os dados para gerar as visualizações interativas.")

# ================================================
# UPLOAD DO ARQUIVO
# ================================================
uploaded_file = st.file_uploader("Selecione o arquivo CSV", type=["csv"])

if uploaded_file is not None:
    # Leitura dos dados
    try:
        df = pd.read_csv(uploaded_file, sep=";")
    except UnicodeDecodeError:
        df = pd.read_csv(uploaded_file, sep=";", encoding="latin-1")

    st.subheader("📋 Prévia dos Dados")
    st.dataframe(df.head())

    # ================================================
    # TRATAMENTO DE DADOS
    # ================================================
    df['repetition_rate'] = (
        df['repetition_rate']
        .astype(str)
        .str.replace('%', '', regex=False)
        .str.replace(',', '.', regex=False)
        .astype(float)
    )

    # ================================================
    # PALETA DE CORES
    # ================================================
    color_palette = ["#d80073", "#f7cce3", "#4f3f91", "#ececec", "#e3e3e3", "#262626"]
    color_scale = alt.Scale(range=color_palette)

    # ================================================
    # DISTRIBUIÇÃO GERAL DE CRIATIVIDADE
    # ================================================
    criatividade_counts = df['criatividade'].value_counts().reset_index()
    criatividade_counts.columns = ['criatividade', 'count']

    chart_criatividade = alt.Chart(criatividade_counts).mark_bar().encode(
        y=alt.Y('criatividade', title='Criatividade', sort='x'),
        x=alt.X('count', title='Contagem'),
        color=alt.value(color_palette[0]),
        tooltip=['criatividade', 'count']
    ).properties(title='Distribuição Geral de Criatividade').interactive()

    # ================================================
    # TAXA MÉDIA DE REPETIÇÃO POR LÍDER
    # ================================================
    avg_repetition_rate_per_lider = df.groupby('lider')['repetition_rate'].mean().reset_index()

    chart_avg_repetition_lider = alt.Chart(avg_repetition_rate_per_lider).mark_bar().encode(
        y=alt.Y('lider', title='Líder', sort='x'),
        x=alt.X('repetition_rate', title='Taxa Média de Repetição'),
        color=alt.value(color_palette[0]),
        tooltip=['lider', 'repetition_rate']
    ).properties(title='Taxa Média de Repetição por Equipe (Líder)').interactive()

    # ================================================
    # MATRIZ DE CRIATIVIDADE
    # ================================================
    creativity_by_lider = df.groupby(['lider', 'criatividade']).size().reset_index(name='count')
    creativity_by_lider['percentage'] = creativity_by_lider.groupby('lider')['count'].transform(lambda x: (x / x.sum()) * 100)

    chart_creativity_matrix = alt.Chart(creativity_by_lider).mark_bar().encode(
        y=alt.Y('lider', title='Líder'),
        x=alt.X('percentage', title='% de Criatividade'),
        color=alt.Color('criatividade', scale=color_scale, title='Nível de Criatividade'),
        tooltip=['lider', 'criatividade', alt.Tooltip('percentage', format='.1f')]
    ).properties(title='Composição das Equipes por Nível de Criatividade').interactive()

    # ================================================
    # TOP 10 AUTORES - MENOR TAXA DE REPETIÇÃO
    # ================================================
    top_10_lowest_repetition = df.sort_values(by='repetition_rate', ascending=True).head(10)

    chart_lowest_repetition = alt.Chart(top_10_lowest_repetition).mark_bar().encode(
        y=alt.Y('author', title='Autor', sort='x'),
        x=alt.X('repetition_rate', title='Taxa de Repetição'),
        color=alt.value(color_palette[0]),
        tooltip=['author', 'repetition_rate']
    ).properties(title='Top 10 Autores com Menor Taxa de Repetição').interactive()

    # ================================================
    # TOP 10 AUTORES - MAIOR TAXA DE REPETIÇÃO
    # ================================================
    top_10_highest_repetition = df.sort_values(by='repetition_rate', ascending=False).head(10)

    chart_highest_repetition = alt.Chart(top_10_highest_repetition).mark_bar().encode(
        y=alt.Y('author', title='Autor', sort='x'),
        x=alt.X('repetition_rate', title='Taxa de Repetição'),
        color=alt.value(color_palette[0]),
        tooltip=['author', 'repetition_rate']
    ).properties(title='Top 10 Autores com Maior Taxa de Repetição').interactive()

    # ================================================
    # MATRIZ DE AUTORES - VOLUME VS TAXA DE REPETIÇÃO
    # ================================================
    author_metrics = df.groupby('author').agg(
        total_msgs=('total_msgs', 'sum'),
        repetition_rate=('repetition_rate', 'mean')
    ).reset_index()

    median_total_msgs = author_metrics['total_msgs'].median()
    median_repetition_rate = author_metrics['repetition_rate'].median()

    chart_author_matrix = alt.Chart(author_metrics).mark_circle(size=80).encode(
        x=alt.X('total_msgs', title='Volume de Mensagens'),
        y=alt.Y('repetition_rate', title='Taxa de Repetição'),
        color=alt.Color('repetition_rate', scale=alt.Scale(range=["#4f3f91", "#d80073"]), title='Taxa de Repetição'),
        tooltip=['author', 'total_msgs', 'repetition_rate']
    ).properties(title='Volume de Mensagens vs Taxa de Repetição por Autor').interactive()

    vertical_line = alt.Chart(pd.DataFrame({'median_msgs': [median_total_msgs]})).mark_rule(
        color='gray', strokeDash=[5, 5]).encode(x='median_msgs')

    horizontal_line = alt.Chart(pd.DataFrame({'median_repetition': [median_repetition_rate]})).mark_rule(
        color='gray', strokeDash=[5, 5]).encode(y='median_repetition')

    chart_author_matrix_combined = chart_author_matrix + vertical_line + horizontal_line

    # ================================================
    # DASHBOARD FINAL
    # ================================================
    st.markdown("---")
    st.subheader("📊 Visualizações Interativas")

    st.altair_chart(chart_criatividade, use_container_width=True)
    st.altair_chart(chart_avg_repetition_lider, use_container_width=True)
    st.altair_chart(chart_creativity_matrix, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.altair_chart(chart_lowest_repetition, use_container_width=True)
    with col2:
        st.altair_chart(chart_highest_repetition, use_container_width=True)

    st.altair_chart(chart_author_matrix_combined, use_container_width=True)

else:
    st.info("👆 Faça upload de um arquivo CSV para iniciar a análise.")
