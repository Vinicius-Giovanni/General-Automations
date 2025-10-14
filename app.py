import streamlit as st
import pandas as pd
from back_end import load_data

st.set_page_config(page_title="Upload de Relatórios", layout="wide")

st.markdown("""
            <style>
                .upload-box {
                    border: 2px dashed #4CAF50;
                    padding: 40px;
                    border-radius: 15px;
                    text-align: center;
                    color: #4CAF50;
                    font-size: 18px;
                    background-color: #F9F9F9;
                }
                .upload-box:hover {
                    background-color: #F1F1F1;
                }
            </style>
            """, unsafe_allow_html=True)

st.title("Upload de Relatórios")

st.markdown('<div class="upload-box">Arraste e solve seus arquivos CSV e TXT aqui</div>',unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    csv_file = st.file_uploader("Arquivo CSV", type=["csv", "xlsx", "xls"], label_visibility="collapsed")
with col2:
    txt_file = st.file_uploader("Arquivo TXT", type=["txt"], label_visibility="collapsed")

if csv_file and txt_file:
    try:
        df = load_data(csv_file, txt_file)
        st.success("Arquivos carregados e processados com sucesso!")

        st.subheader(" Prévia dos Dados")
        st.dataframe(df.head(), use_container_width=True)

        # Estatísticas básicas
        st.subheader("Estatísticas Básicas")
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric('Totla de Pedidos', len(df))
        with col_b:
            st.metric('Ticket Médio', f"{df['Ticket'].mean():.2f}")
        with col_c:
            st.metric('Valor Total', f"{df['Valor'].sum():,.2f}")

    except Exception as e:
        st.error(f'Erro ao processar os arquivos: {e}')
else:
    st.info('Arraste os ois arquivos acima ou clique para selecionar.')