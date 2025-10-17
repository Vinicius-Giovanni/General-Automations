import pandas as pd
from collections import Counter
import numpy as np

def load_data(xlsx_file, txt_file) -> pd.DataFrame:
    """
    Lê e processa os arquivos Excel e TXT, criando colunas calculadas como PEDIDO, nvjer e Ticket.
    Compatível com arquivos locais (Path) ou uploads do Streamlit (UploadedFile).
    """

    # --- Leitura das 3 primeiras linhas do TXT para formar o cabeçalho ---
    if hasattr(txt_file, "read"):  # UploadedFile
        txt_file.seek(0)
        header_lines = [txt_file.readline().decode('latin1').strip() for _ in range(3)]
        txt_file.seek(0)  # Volta para o início do arquivo para o pandas
    else:  # Path ou str
        with open(txt_file, 'r', encoding='latin1') as f:
            header_lines = [f.readline().strip() for _ in range(3)]

    # Cabeçalho duplo
    header1 = header_lines[1].split(';')
    header2 = header_lines[2].split(';')
    max_len = max(len(header1), len(header2))
    header1 += [''] * (max_len - len(header1))
    header2 += [''] * (max_len - len(header2))
    combined_columns = [f"{h1.strip()} {h2.strip()}".strip() for h1, h2 in zip(header1, header2)]

    # Remove duplicatas e nomes vazios
    col_counter = Counter()
    final_columns = []
    for col in combined_columns:
        if not col:
            col = 'unnamed'
        if col in col_counter:
            col_counter[col] += 1
            col = f"{col}_{col_counter[col]}"
        else:
            col_counter[col] = 0
        final_columns.append(col)

    # --- Leitura do TXT em DataFrame ---
    df_txt = pd.read_csv(
        txt_file,
        sep=';',
        header=None,
        names=final_columns,
        skiprows=3,
        encoding='latin1',
        engine='python',
        dtype=str
    )

    # Criação da coluna PEDIDO
    if 'Numero Pedido' not in df_txt.columns or 'Tipo Pedido' not in df_txt.columns:
        raise ValueError('As colunas "Numero Pedido" ou "Tipo Pedido" não foram encontradas no TXT.')
    df_txt['PEDIDO'] = df_txt['Numero Pedido'].fillna('') + df_txt['Tipo Pedido'].fillna('')

    # --- Leitura do Excel ---
    if hasattr(xlsx_file, "read"):  # UploadedFile
        df_excel = pd.read_excel(xlsx_file, parse_dates=['OTS'])
    else:
        df_excel = pd.read_excel(xlsx_file, parse_dates=['OTS'])

    # Cria PEDIDO no Excel se necessário
    if 'PEDIDO' not in df_excel.columns:
        if 'Numero Pedido' in df_excel.columns and 'Tipo Pedido' in df_excel.columns:
            df_excel['PEDIDO'] = df_excel['Numero Pedido'].fillna('') + df_excel['Tipo Pedido'].fillna('')
        else:
            raise ValueError("O Excel precisa ter 'PEDIDO' ou 'Numero Pedido' + 'Tipo Pedido'.")

    # --- Merge ---
    df = pd.merge(df_excel, df_txt, on='PEDIDO', how='left')

    # -- Definindo Tipos ---
    DATA_TYPES ={
        'PEDIDO': 'string',
        'TIPO DO PEDIDO': 'string',
        'LEGENDA TIPO': 'string',
        'CONCESSIONÁRIA': 'string',
        'TRANSPORTADORA': 'string',
        'LINHAS': 'Int64',
        'STATUS': 'Int64',
        'LEGENDA STATUS': 'string',
        'Valor Venda': 'float64',
    }

    REMOVE_COLS = [
        'Filial/Fabrica',
        'Numero Pedido',
        'Tipo Pedido',
        'Ultimo Sts',
        'Proximo Sts',
        'Data Pedido',
        'Lista Data',
        'Data Lote Etiqueta',
        'Dias',
        'Cod Susp',
        'Cod Cliente',
        'Nome do Cliente',
        'Nome da Transportadora',
        'Cr Ativo',
        'Qtde Linhas',
        'Cond Pagto',
        'Valor US$',
        'Etiq Emitida',
        'Pedido Atendente',
        'Lista Atender'
    ]
    df.drop(columns=REMOVE_COLS, errors='ignore', inplace=True)

    df['Valor Venda'].replace(',', '.', regex=True, inplace=True)

    for col, dtype in DATA_TYPES.items():
        if col in df.columns:
            df[col] = df[col].astype(dtype)

    df['> R$ 1.000,00 ?'] = np.where(df['Valor Venda'] < 1000, '< R$ 1.000,00','> R$ 1.000,00')

    df['Ticket'] = df['Valor Venda'] / df['LINHAS'].astype('float64')

    # --- nvjer ---
    df['nvjer'] = df['PEDIDO'].astype(str).str[:8].astype('string')

    print(df.dtypes)

    # Remove duplicatas
    df = df.drop_duplicates(subset=['PEDIDO']).reset_index(drop=True)

    return df
