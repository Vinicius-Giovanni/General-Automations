import streamlit as st
import pandas as pd
from back_end import load_data

st.set_page_config(page_title="Upload de Relatórios", layout="wide")

# --- Estilos Globais ---
st.markdown("""
<style>
/* Estilo geral dos títulos */
h2, h3 {
    font-family: 'Arial', sans-serif;
}

/* Cards métricas */
.metric-card {
    background-color: #E8F5E9;
    border-radius: 12px;
    padding: 15px;
    text-align: center;
    color: #2E7D32;
    font-weight: bold;
    box-shadow: 1px 2px 8px rgba(0,0,0,0.1);
}

/* Box upload moderno */
.upload-box {
    border: 2px dashed #4CAF50;
    border-radius: 15px;
    padding: 40px;
    text-align: center;
    color: #4CAF50;
    font-size: 18px;
    background-color: #F0F8F5;
    transition: background-color 0.3s;
}
.upload-box:hover {
    background-color: #E0F2F1;
}
</style>
""", unsafe_allow_html=True)

# --- Abas ---
TAB_IMPORT, TAB_VIEW, TAB_GRAPH = st.tabs(
    ["📥 Importação de Dados", "📋 Visualização de Dados", "📊 Gráfico & Tabelas"]
)

# --- Aba 1: Importação de Dados ---
with TAB_IMPORT:
    st.markdown("<h2 style='text-align: center; color: #4CAF50;'>📥 Importação de Dados</h2>", unsafe_allow_html=True)

    # Uploaders centralizados
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        excel_file = st.file_uploader("📄 Arquivo de pedidos (XLSX ou XLS)", type=["xlsx","xls"], label_visibility="visible")
        txt_file = st.file_uploader("📄 Arquivo de valores (TXT)", type=["txt"], label_visibility="visible")

    # Feedback visual
    if excel_file and txt_file:
        st.success("✅ Arquivos carregados com sucesso!")

# --- Processamento ---
if excel_file and txt_file:
    try:
        df = load_data(xlsx_file=excel_file, txt_file=txt_file)
        
        # --- Aba 2: Visualização de Dados ---
        with TAB_VIEW:
            st.markdown("<h2 style='text-align: center; color: #4CAF50;'>📋 Base de Dados</h2>", unsafe_allow_html=True)
            
            df_display = df.copy()
            if 'OTS' in df_display.columns:
                df_display['OTS'] = df_display['OTS'].dt.strftime('%d/%m/%Y')

            for col in ['Valor Venda','Ticket']:
                if col in df_display.columns:
                    df_display[col] = df_display[col].apply(
                        lambda x: f'{x:,.2f}'.replace(',', 'v').replace('.', ',').replace('v', '.')
                        if pd.notnull(x) else ''
                    )

            st.markdown("---")
            st.dataframe(df_display, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("---")

        # --- Aba 3: Gráfico & Tabelas ---
        with TAB_GRAPH:
            st.markdown("<h2 style='text-align: center; color: #4CAF50;'>📊 Gráfico & Tabelas</h2>", unsafe_allow_html=True)

            if 'df' in locals():
                if 'OTS' in df.columns:
                    df['OTS_date'] = pd.to_datetime(df['OTS'], dayfirst=True, errors='coerce')

                    # Slider de datas
                    min_date = df['OTS_date'].min().date()
                    max_date = df['OTS_date'].max().date()
                    start_date, end_date = st.slider(
                        "Filtrar por OTS",
                        min_value=min_date,
                        max_value=max_date,
                        value=(min_date, max_date)
                    )
                    start_dt = pd.to_datetime(start_date)
                    end_dt = pd.to_datetime(end_date)

                    df_filtered = df.loc[
                        df['OTS_date'].notna() & 
                        (df['OTS_date'] >= start_dt) & 
                        (df['OTS_date'] <= end_dt)
                    ]
                else:
                    df_filtered = df.copy()

                # --- Filtros adicionais tipo Excel ---
                if 'LEGENDA TIPO' in df_filtered.columns:
                    tipos = df_filtered['LEGENDA TIPO'].unique().tolist()
                    selected_tipos = st.multiselect("Filtrar por LEGENDA TIPO", options=tipos, default=tipos)
                    df_filtered = df_filtered[df_filtered['LEGENDA TIPO'].isin(selected_tipos)]

                if 'LEGENDA STATUS' in df_filtered.columns:
                    status = df_filtered['LEGENDA STATUS'].unique().tolist()
                    selected_status = st.multiselect("Filtrar por LEGENDA STATUS", options=status, default=status)
                    df_filtered = df_filtered[df_filtered['LEGENDA STATUS'].isin(selected_status)]

                # Mostra resumo do filtro
                st.markdown(f"**Pedidos filtrados:** {len(df_filtered)}")

                st.markdown("---")

                # --- Estatísticas básicas ---
                ticket_medio = df_filtered['Ticket'].mean() if 'Ticket' in df_filtered.columns else 0
                valor_total = df_filtered['Valor Venda'].sum() if 'Valor Venda' in df_filtered.columns else 0
                qt_pedido = len(df_filtered)

                ticket_medio_fmt = f'{ticket_medio:,.2f}'.replace(',', 'v').replace('.', ',').replace('v', '.')
                valor_total_fmt = f'{valor_total:,.2f}'.replace(',', 'v').replace('.', ',').replace('v', '.')
                qt_pedido_fmt = f'{qt_pedido:,}'.replace(',', '.')

                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.markdown(f"<div class='metric-card'>Total de Pedidos<br><span style='font-size:24px'>{qt_pedido_fmt}</span></div>", unsafe_allow_html=True)
                with col_b:
                    st.markdown(f"<div class='metric-card'>Ticket Médio<br><span style='font-size:24px'>R$ {ticket_medio_fmt}</span></div>", unsafe_allow_html=True)
                with col_c:
                    st.markdown(f"<div class='metric-card'>Valor Total<br><span style='font-size:24px'>R$ {valor_total_fmt}</span></div>", unsafe_allow_html=True)

                st.markdown("---")

                # --- Tabela Dinâmica ---
                if 'LEGENDA TIPO' in df_filtered.columns and 'LEGENDA STATUS' in df_filtered.columns and 'LINHAS' in df_filtered.columns:
                    pivot = pd.pivot_table(
                        data=df_filtered,
                        index=['LEGENDA TIPO','LEGENDA STATUS'],
                        columns='OTS_date',
                        values='LINHAS',
                        aggfunc='sum',
                        fill_value=0
                    )

                    # Formata colunas datetime
                    pivot.columns = [col.strftime('%d/%m/%Y') for col in pivot.columns]

                    # Adiciona coluna de totais por linha
                    pivot['Total'] = pivot.sum(axis=1)

                    # Calcula total por coluna
                    total_col = pivot.sum(axis=0)
                    total_col.name = ('Total Geral', '')  # nome da linha de total
                    pivot = pd.concat([pivot, pd.DataFrame([total_col])])

                    # Formata valores da tabela
                    pivot_formatted = pivot.applymap(lambda x: f'{x:,.0f}'.replace(',', 'v').replace('.', ',').replace('v', '.'))

                    # Tamanho dinãmico
                    row_height = 500
                    min_height = 500
                    max_height = 1000
                    table_height = min(max(len(pivot_formatted) *  row_height, min_height), max_height)

                    st.subheader("📊 Tabela Dinâmica de Linhas por Legenda Tipo e Legenda Status x Datas (com totais)")
                    st.dataframe(pivot_formatted, use_container_width=True, height=table_height)


                st.markdown("---")

            else:
                st.info("📌 Faça upload dos arquivos na aba 'Importação de Dados' para visualizar os gráficos.")



    except Exception as e:
        st.error(f'Erro ao processar os arquivos: {e}')
else:
    st.info('Arraste os dois arquivos acima ou clique para selecionar.')
