import streamlit as st
from functions_load import extract_parameters, get_default_path, load_data, filter_input

st.set_page_config(layout="wide")
st.title("Dados de Vagas.com")


# Carrega DataFrame
df = load_data(st, str(get_default_path()))

if df.empty:
    st.warning("Nenhum dado carregado. Faça a primeira extração")
else:
    # Botões de filtro da tabela
    filter_input(st, df)

    # Exibe tabela filtrada
    st.dataframe(df, use_container_width=True)

# Botões de parametros e rodar extração manual
extract_parameters(st)