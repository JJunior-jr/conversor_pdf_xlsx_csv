"""
Módulo de frontend (interface visual) do app Streamlit.

Contém:
- Configuração da página
- CSS customizado
- Componentes visuais reutilizáveis (cabeçalho, cards, métricas, estado vazio)
"""

import streamlit as st


def configurar_pagina():
    """Configura as propriedades da página Streamlit."""
    st.set_page_config(
        page_title="Extrator de PDF",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def aplicar_css():
    """Injeta o CSS customizado na página."""
    st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .main-header {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        padding: 2rem 2.5rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        color: white;
        text-align: center;
    }
    .main-header h1 {
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
        background: linear-gradient(90deg, #a78bfa, #60a5fa, #34d399);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .main-header p {
        color: #cbd5e1;
        margin-top: 0.5rem;
        font-size: 0.95rem;
    }

    .info-card {
        background: linear-gradient(135deg, #1e1b4b, #312e81);
        border: 1px solid #4338ca;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 1rem;
        color: #e0e7ff;
    }
    .info-card h4 { color: #a5b4fc; margin: 0 0 0.5rem 0; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px; }
    .info-card p { margin: 0.2rem 0; font-size: 0.9rem; }
    .info-card .value { color: #fff; font-weight: 600; }

    .metric-row {
        display: flex;
        gap: 1rem;
        margin-bottom: 1.5rem;
        flex-wrap: wrap;
    }
    .metric-card {
        flex: 1;
        min-width: 150px;
        background: linear-gradient(135deg, #064e3b, #065f46);
        border: 1px solid #10b981;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        text-align: center;
        color: white;
    }
    .metric-card .number { font-size: 1.8rem; font-weight: 700; color: #34d399; }
    .metric-card .label { font-size: 0.8rem; color: #a7f3d0; text-transform: uppercase; letter-spacing: 1px; }

    .stDataFrame { border-radius: 12px; overflow: hidden; }

    div[data-testid="stFileUploader"] {
        border: 2px dashed #4338ca;
        border-radius: 12px;
        padding: 1rem;
        background: #1e1b4b22;
    }

    .download-section {
        background: linear-gradient(135deg, #1e1b4b, #312e81);
        border: 1px solid #4338ca;
        border-radius: 12px;
        padding: 1.5rem;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)


def renderizar_cabecalho():
    """Renderiza o cabeçalho principal da página."""
    st.markdown("""
<div class="main-header">
    <h1>📊 Extrator de Plano de Contas — SPED</h1>
    <p>Faça upload do PDF do Plano de Contas gerado pelo SPED e exporte para Excel ou CSV</p>
</div>
""", unsafe_allow_html=True)


def renderizar_sidebar():
    """Renderiza a sidebar com uploader e informações. Retorna o arquivo enviado."""
    with st.sidebar:
        st.markdown("### ⚙️ Configurações")
        st.markdown("---")

        uploaded_file = st.file_uploader(
            "📁 Selecione o PDF do Plano de Contas",
            type=["pdf"],
            help="Arquivo PDF gerado pelo visualizador do SPED Contábil",
        )

        st.markdown("---")
        st.markdown("### 📋 Sobre")
        st.markdown(
            "Esta ferramenta extrai automaticamente os dados do PDF e trasnforma em planilhas .xlsx e .csv "
            
        )
        st.markdown(
            "**Dados extraídos:**\n"
            "- Código da conta\n"
            "- Nível hierárquico\n"
            "- Descrição\n"
            "- Natureza (Ativo/Passivo/Resultado)\n"
            "- Tipo (S - Sintética / A - Analítica)\n"
            "- Conta de nível superior\n"
            "- Data de alteração\n"
            "- Conta referencial\n"
            "- Código de aglutinação"
        )

    return uploaded_file


def renderizar_info_entidade(info: dict):
    """Renderiza os cards com informações da entidade e escrituração."""
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(f"""
        <div class="info-card">
            <h4>🏢 Entidade</h4>
            <p class="value">{info['entidade']}</p>
            <p>CNPJ: <span class="value">{info['cnpj']}</span></p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="info-card">
            <h4>📅 Escrituração</h4>
            <p>Período: <span class="value">{info['periodo']}</span></p>
            <p>Livro nº: <span class="value">{info['num_livro']}</span></p>
        </div>
        """, unsafe_allow_html=True)


def renderizar_metricas(total: int, sinteticas: int, analiticas: int, niveis: int):
    """Renderiza os cards de métricas."""
    st.markdown(f"""
    <div class="metric-row">
        <div class="metric-card">
            <div class="number">{total}</div>
            <div class="label">Total de Contas</div>
        </div>
        <div class="metric-card">
            <div class="number">{sinteticas}</div>
            <div class="label">Sintéticas (S)</div>
        </div>
        <div class="metric-card">
            <div class="number">{analiticas}</div>
            <div class="label">Analíticas (A)</div>
        </div>
        <div class="metric-card">
            <div class="number">{niveis}</div>
            <div class="label">Níveis</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def renderizar_estado_vazio():
    """Renderiza a tela quando nenhum arquivo foi carregado."""
    st.markdown("""
    <div style="text-align: center; padding: 4rem 2rem; color: #94a3b8;">
        <div style="font-size: 4rem; margin-bottom: 1rem;">📄</div>
        <h3 style="color: #cbd5e1;">Nenhum arquivo carregado</h3>
        <p>Utilize o menu lateral para fazer upload do PDF do Plano de Contas do SPED.</p>
    </div>
    """, unsafe_allow_html=True)
