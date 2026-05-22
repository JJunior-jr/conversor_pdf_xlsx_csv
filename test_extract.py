# pyrefly: ignore [missing-import]
import pdfplumber, re, pandas as pd

def extrair_contas(pdf):
    contas = []
    padrao_conta = re.compile(
        r'^(\d+)\s+(\d)\s+'
        r'(.+?)\s+'
        r'(Contas de (?:ativo|passivo|resultado))\s+'
        r'([SA])\s+'
        r'(\d*)\s*'
        r'(\d{2}/\d{2}/\d{4})$'
    )
    padrao_ref = re.compile(r'^\d+\s+([\d\.]+)')
    padrao_aglut = re.compile(r'^(\d+)$')

    conta_atual = None
    esperando_ref = False
    esperando_aglut = False

    for page in pdf.pages:
        texto = page.extract_text()
        if not texto:
            continue
        for linha in texto.split('\n'):
            linha = linha.strip()
            if not linha or 'PLANO DE CONTAS' in linha or 'Entidade:' in linha:
                continue
            if 'Escritura' in linha or 'digo N' in linha:
                continue
            if 'Este relat' in linha:
                continue

            m = padrao_conta.match(linha)
            if m:
                if conta_atual:
                    contas.append(conta_atual)
                conta_atual = {
                    'Codigo': m.group(1), 'Nivel': int(m.group(2)),
                    'Descricao': m.group(3).strip(), 'Natureza': m.group(4),
                    'Tipo': m.group(5), 'ContaSuperior': m.group(6) or '',
                    'DataAlteracao': m.group(7), 'ContaRef': '', 'CodAglut': '',
                }
                esperando_ref = False
                esperando_aglut = False
                continue

            if 'Plano de contas referencial' in linha:
                esperando_ref = True
                esperando_aglut = False
                continue

            if esperando_ref and conta_atual:
                m_ref = padrao_ref.match(linha)
                if m_ref:
                    conta_atual['ContaRef'] = m_ref.group(1)
                    esperando_ref = False
                continue

            if 'Aglutina' in linha:
                esperando_aglut = True
                esperando_ref = False
                continue

            if esperando_aglut and conta_atual:
                m_aglut = padrao_aglut.match(linha)
                if m_aglut:
                    conta_atual['CodAglut'] = m_aglut.group(1)
                    esperando_aglut = False
                continue

    if conta_atual:
        contas.append(conta_atual)
    return contas

pdf = pdfplumber.open('arquivo modelo.pdf')
contas = extrair_contas(pdf)
pdf.close()
df = pd.DataFrame(contas)
print(f'Total de contas extraidas: {len(df)}')
sint = len(df[df['Tipo'] == 'S'])
anal = len(df[df['Tipo'] == 'A'])
print(f'Sinteticas: {sint}')
print(f'Analiticas: {anal}')
print(f'Niveis: {sorted(df["Nivel"].unique())}')
print(f'Naturezas: {df["Natureza"].unique().tolist()}')
print()
print('Primeiras 10 contas:')
print(df.head(10).to_string(index=False))
print()
print('Ultimas 5 contas:')
print(df.tail(5).to_string(index=False))
