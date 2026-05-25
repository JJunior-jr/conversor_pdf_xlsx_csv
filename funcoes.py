"""
Módulo de funções para extração e exportação do Plano de Contas SPED.

Contém as funções de:
- Extração do cabeçalho do PDF
- Extração das contas contábeis
- Geração de arquivo Excel
- Geração de arquivo CSV
"""

import re
import io
import pandas as pd


def extrair_cabecalho(texto_primeira_pagina: str) -> dict:
    """Extrai informações do cabeçalho do PDF (Entidade, Período, CNPJ, Nº Livro)."""
    info = {"entidade": "", "periodo": "", "cnpj": "", "num_livro": ""}
    linhas = texto_primeira_pagina.split("\n")
    for linha in linhas:
        if "Entidade:" in linha:
            info["entidade"] = linha.split("Entidade:")[-1].strip()
        if "CNPJ:" in linha:
            m = re.search(r"Per[ií]odo da Escritura[çc][ãa]o:\s*(.+?)\s*CNPJ:", linha)
            if m:
                info["periodo"] = m.group(1).strip()
            m2 = re.search(r"CNPJ:\s*([\d\.\/\-]+)", linha)
            if m2:
                info["cnpj"] = m2.group(1).strip()
            m3 = re.search(r"N[úu]mero de Ordem do Livro:\s*(\d+)", linha)
            if m3:
                info["num_livro"] = m3.group(1).strip()
    return info


def extrair_contas(pdf) -> list[dict]:
    """Extrai todas as contas do plano de contas do PDF do SPED.

    Trata 3 cenários de layout do PDF:
    1. Descrição na mesma linha do código (caso normal)
    2. Descrição na linha anterior (quando a descrição é longa e quebra)
    3. Continuação da descrição na linha seguinte ao código
    """
    contas = []

    # Padrão completo: Código Nível Descrição Natureza Tipo Superior Data
    padrao_conta = re.compile(
        r"^(\d+)\s+(\d)\s+"                           # Código + Nível
        r"(.+?)\s+"                                     # Descrição
        r"(Contas de (?:ativo|passivo|resultado))\s+"   # Natureza
        r"([SA])\s+"                                    # Tipo
        r"(\d*)\s*"                                     # Conta Nível Superior (pode estar vazia)
        r"(\d{2}/\d{2}/\d{4})$"                         # Data Alteração
    )

    # Padrão SEM descrição: Código Nível Natureza Tipo Superior Data
    # (a descrição está na linha anterior e/ou posterior)
    padrao_sem_desc = re.compile(
        r"^(\d+)\s+(\d)\s+"                            # Código + Nível
        r"(Contas de (?:ativo|passivo|resultado))\s+"   # Natureza (direto, sem desc)
        r"([SA])\s+"                                    # Tipo
        r"(\d*)\s*"                                     # Conta Nível Superior
        r"(\d{2}/\d{2}/\d{4})$"                         # Data Alteração
    )

    # Padrão para linha de conta referencial
    padrao_ref = re.compile(r"^\d+\s+([\d\.]+)")

    # Padrão para código de aglutinação (linha com apenas número)
    padrao_aglut = re.compile(r"^(\d+)$")

    # Padrões de linhas a ignorar (cabeçalhos/rodapés)
    def eh_linha_ignorada(linha: str) -> bool:
        if not linha:
            return True
        if linha.startswith("PLANO DE CONTAS") or "Entidade:" in linha:
            return True
        if "Escritura" in linha or "Código Nível" in linha or "Código N" in linha:
            return True
        if "Este relat" in linha:
            return True
        return False

    def eh_linha_estrutural(linha: str) -> bool:
        """Verifica se a linha é estrutural (referencial, aglutinação, etc)."""
        if not linha:
            return True
        if "Plano de contas referencial" in linha:
            return True
        if "Aglutina" in linha:
            return True
        if padrao_ref.match(linha):
            return True
        if padrao_aglut.match(linha):
            return True
        if padrao_conta.match(linha):
            return True
        if padrao_sem_desc.match(linha):
            return True
        if eh_linha_ignorada(linha):
            return True
        return False

    conta_atual = None
    esperando_ref = False
    esperando_aglut = False
    esperando_continuacao = False  # flag para desc. que continua após a linha do código
    linha_anterior = ""  # Armazena a última linha válida não estrutural (para o caso 2)

    # Processamento página por página para evitar manter todas as linhas em memória
    for page in pdf.pages:
        texto = page.extract_text()
        if not texto:
            page.flush_cache()
            continue

        linhas = [l.strip() for l in texto.split("\n") if l.strip()]
        
        i = 0
        while i < len(linhas):
            linha = linhas[i]

            # Pular cabeçalhos e rodapés
            if eh_linha_ignorada(linha):
                i += 1
                continue

            # ─── Caso 1: Linha completa com descrição ───
            m = padrao_conta.match(linha)
            if m:
                if conta_atual:
                    contas.append(conta_atual)

                conta_atual = {
                    "Código": m.group(1),
                    "Nível": int(m.group(2)),
                    "Descrição": m.group(3).strip(),
                    "Natureza": m.group(4),
                    "Tipo": m.group(5),
                    "Conta Nível Superior": m.group(6) if m.group(6) else "",
                    "Data Alteração": m.group(7),
                    "Conta Referencial": "",
                    "Cód. Aglutinação": "",
                }
                esperando_ref = False
                esperando_aglut = False
                esperando_continuacao = False
                linha_anterior = linha
                i += 1
                continue

            # ─── Caso 2: Linha SEM descrição (desc na linha anterior/posterior) ───
            m_sd = padrao_sem_desc.match(linha)
            if m_sd:
                if conta_atual:
                    contas.append(conta_atual)

                # Buscar descrição na linha anterior (pode estar na variável 'linha_anterior')
                desc_anterior = ""
                if linha_anterior and not eh_linha_estrutural(linha_anterior):
                    desc_anterior = linha_anterior

                conta_atual = {
                    "Código": m_sd.group(1),
                    "Nível": int(m_sd.group(2)),
                    "Descrição": desc_anterior,
                    "Natureza": m_sd.group(3),
                    "Tipo": m_sd.group(4),
                    "Conta Nível Superior": m_sd.group(5) if m_sd.group(5) else "",
                    "Data Alteração": m_sd.group(6),
                    "Conta Referencial": "",
                    "Cód. Aglutinação": "",
                }
                esperando_ref = False
                esperando_aglut = False
                esperando_continuacao = True  # pode ter continuação na próxima linha
                linha_anterior = linha
                i += 1
                continue

            # ─── Continuação da descrição (linha após código sem desc) ───
            if esperando_continuacao and conta_atual:
                if not eh_linha_estrutural(linha):
                    if conta_atual["Descrição"]:
                        conta_atual["Descrição"] += " " + linha
                    else:
                        conta_atual["Descrição"] = linha
                    esperando_continuacao = False
                    linha_anterior = linha
                    i += 1
                    continue
                else:
                    esperando_continuacao = False

            # Linha "Plano de contas referencial"
            if "Plano de contas referencial" in linha:
                esperando_ref = True
                esperando_aglut = False
                i += 1
                continue

            # Linha com conta referencial (ex: "1 1.01.01.01.01")
            if esperando_ref and conta_atual:
                m_ref = padrao_ref.match(linha)
                if m_ref:
                    conta_atual["Conta Referencial"] = m_ref.group(1)
                    esperando_ref = False
                i += 1
                continue

            # Linha "Código de Aglutinação"
            if "Aglutina" in linha:
                esperando_aglut = True
                esperando_ref = False
                i += 1
                continue

            # Linha com código de aglutinação
            if esperando_aglut and conta_atual:
                m_aglut = padrao_aglut.match(linha)
                if m_aglut:
                    conta_atual["Cód. Aglutinação"] = m_aglut.group(1)
                    esperando_aglut = False
                i += 1
                continue

            if not eh_linha_estrutural(linha):
                linha_anterior = linha
            i += 1

        # Libera o cache de renderização de objetos desta página no pdfplumber para economizar memória
        page.flush_cache()

    # Salvar última conta
    if conta_atual:
        contas.append(conta_atual)

    return contas


def gerar_excel(df: pd.DataFrame) -> bytes:
    """Gera arquivo Excel (.xlsx) em memória a partir de um DataFrame."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Plano de Contas")
        # Ajustar largura das colunas
        ws = writer.sheets["Plano de Contas"]
        for col_idx, col_name in enumerate(df.columns, 1):
            max_len = max(df[col_name].astype(str).str.len().max(), len(col_name)) + 2
            max_len = min(max_len, 60)
            ws.column_dimensions[chr(64 + col_idx) if col_idx <= 26 else "A"].width = max_len
    return output.getvalue()


def gerar_csv(df: pd.DataFrame) -> bytes:
    """Gera arquivo CSV em memória a partir de um DataFrame."""
    return df.to_csv(index=False, encoding="utf-8-sig", sep=";").encode("utf-8-sig")
