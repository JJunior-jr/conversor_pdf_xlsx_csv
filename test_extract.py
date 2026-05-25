# pyrefly: ignore [missing-import]
import pdfplumber, re, pandas as pd
from funcoes import extrair_contas

pdf = pdfplumber.open('arquivo modelo.pdf')
contas = extrair_contas(pdf)
pdf.close()
df = pd.DataFrame(contas)
print(f'Total de contas extraidas: {len(df)}')
sint = len(df[df['Tipo'] == 'S']) if not df.empty else 0
anal = len(df[df['Tipo'] == 'A']) if not df.empty else 0
print(f'Sinteticas: {sint}')
print(f'Analiticas: {anal}')
print(f'Niveis: {sorted(df["Nível"].unique()) if not df.empty else []}')
print(f'Naturezas: {df["Natureza"].unique().tolist() if not df.empty else []}')
print()
print('Primeiras 10 contas:')
print(df.head(10).to_string(index=False))
print()
print('Ultimas 5 contas:')
print(df.tail(5).to_string(index=False))
