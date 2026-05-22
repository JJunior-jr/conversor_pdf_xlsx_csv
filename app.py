"""
App principal - Extrator de Plano de Contas SPED.

Ponto de entrada do Streamlit.
Execução: streamlit run app.py
"""

import streamlit as st
import pdfplumber
import pandas as pd
from pathlib import Path
from datetime import datetime

from funcoes import extrair_cabecalho, extrair_contas, gerar_excel, gerar_csv
from frontend import (
    configurar_pagina,
    aplicar_css,
    renderizar_cabecalho,
    renderizar_sidebar,
    renderizar_info_entidade,
    renderizar_metricas,
    renderizar_estado_vazio,
)

# ─── Inicialização ───
configurar_pagina()
aplicar_css()
renderizar_cabecalho()

# ─── Sidebar (upload do arquivo) ───
uploaded_file = renderizar_sidebar()

# ─── Processamento ───
if uploaded_file is not None:
    with st.spinner("🔄 Processando PDF... Aguarde."):
        pdf = pdfplumber.open(uploaded_file)

        # Cabeçalho
        texto_p1 = pdf.pages[0].extract_text() or ""
        info = extrair_cabecalho(texto_p1)

        # Contas
        contas = extrair_contas(pdf)
        pdf.close()

        df = pd.DataFrame(contas)

    # ─── Informações da Entidade ───
    renderizar_info_entidade(info)

    # ─── Métricas ───
    total = len(df)
    sinteticas = len(df[df["Tipo"] == "S"]) if not df.empty else 0
    analiticas = len(df[df["Tipo"] == "A"]) if not df.empty else 0
    niveis = df["Nível"].nunique() if not df.empty else 0
    renderizar_metricas(total, sinteticas, analiticas, niveis)

    # ─── Filtros ───
    st.markdown("### 🔍 Filtros")
    fc1, fc2, fc3, fc4 = st.columns(4)
    with fc1:
        filtro_codigo = st.text_input("🔢 Buscar por código", "")
    with fc2:
        filtro_tipo = st.multiselect("Tipo", options=["S", "A"], default=["S", "A"])
    with fc3:
        naturezas = df["Natureza"].unique().tolist() if not df.empty else []
        filtro_nat = st.multiselect("Natureza", options=naturezas, default=naturezas)
    with fc4:
        filtro_texto = st.text_input("🔎 Buscar na descrição", "")

    # Aplicar filtros
    df_filtrado = df.copy()
    if filtro_codigo:
        df_filtrado = df_filtrado[
            df_filtrado["Código"].str.contains(filtro_codigo, case=False, na=False)
        ]
    if filtro_tipo:
        df_filtrado = df_filtrado[df_filtrado["Tipo"].isin(filtro_tipo)]
    if filtro_nat:
        df_filtrado = df_filtrado[df_filtrado["Natureza"].isin(filtro_nat)]
    if filtro_texto:
        df_filtrado = df_filtrado[
            df_filtrado["Descrição"].str.contains(filtro_texto, case=False, na=False)
        ]

    # ─── Tabela ───
    st.markdown(f"### 📋 Plano de Contas ({len(df_filtrado)} registros)")
    st.dataframe(
        df_filtrado,
        use_container_width=True,
        height=500,
        column_config={
            "Código": st.column_config.TextColumn("Código", width="small"),
            "Nível": st.column_config.NumberColumn("Nível", width="small"),
            "Descrição": st.column_config.TextColumn("Descrição", width="large"),
            "Tipo": st.column_config.TextColumn("Tipo", width="small"),
        },
    )

    # ─── Downloads ───
    st.markdown("### 📥 Exportar Dados")

    nome_base = f"plano_contas_{info['cnpj'].replace('/', '_').replace('.', '').replace('-', '')}_{datetime.now().strftime('%Y%m%d')}"

    dl1, dl2, _ = st.columns([1, 1, 2])

    with dl1:
        excel_data = gerar_excel(df_filtrado)
        st.download_button(
            label="⬇️ Baixar Excel (.xlsx)",
            data=excel_data,
            file_name=f"{nome_base}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            type="primary"
        )

    with dl2:
        csv_data = gerar_csv(df_filtrado)
        st.download_button(
            label="⬇️ Baixar CSV (.csv)",
            data=csv_data,
            file_name=f"{nome_base}.csv",
            mime="text/csv",
            use_container_width=True,
            type="primary"
        )

else:
    renderizar_estado_vazio()
