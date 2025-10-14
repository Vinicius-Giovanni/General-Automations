import pandas as pd

def load_data(csv_file, txt_file) -> pd.DataFrame:
    # Faz a leitura dos aruqivos CSV e TXT
    # Realiza limpeza
    # Mescla e cria novas colunas

    csv_cols = [
        "PEDIDOS","TIPO DO PEDIDO","LEGENDA TIPO",
        "CONCESSIONÁRIA","TRANSPORTADORA","LINHAS",
        "OTS","STATUS","LEGENDA STATUS"
    ]
    
    if csv_file.name.endswith('.csv'):
        df_csv = pd.read_csv(csv_file, sep='\t', encoding='utf-16')
    elif csv_file.name.endswith(('.xlsx', '.xls')):
        df_csv = pd.read_excel(csv_file)
    else:
        raise ValueError("Formato de arquivo CSV inválido.")

    df_txt = pd.read_csv(txt_file, sep=';', dtype=str)

    # Verificação de colunas 'Pedido' existem
    pedidos_cols = [col for col in df_txt.columns if 'Pedido' in col]
    if len(pedidos_cols) <3:
        raise ValueError(f'O arquivo TXT precisa conter pelo menos 3 colunas com "Pedido" no nome, mas encontrei: {pedidos_cols}')
    
    # Coluna Chave
    df_txt['PEDIDOS'] = df_txt[pedidos_cols[0]].fillna('') + df_txt[pedidos_cols[1]].fillna('')

    # Verificação de coluna 'Valor'
    if 'Valor' not in df_txt.columns:
        raise ValueError('A coluna "valor" não foi encontrada no arquivo TXT.')
    
    df_txt = df_txt[["PEDIDOS","Valor"]].copy()

    df_txt["Valor"] = (
        df_txt["Valor"]
        .replace({r'[^\d,.-]': ''}, regex=True)
        .str.replace(',', '.', regex=False)
        .astype(float)
    )

    # Mescla os DataFrames
    df =pd.merge(df_csv, df_txt, on="PEDIDOS", how="left")

    # Criar coluna nvjer
    df['nvjer'] = df['PEDIDOS'].astype(str).str[:0]

    df['LINHAS'] = pd.to_numeric(df['LINHAS'], errors='coerce')
    df['Ticket'] = df['Valor']/df['LINHAS']

    df = df.drop_duplicates(subset=['PEDIDOS']).reset_index(drop=True)

    return df
    