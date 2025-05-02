import subprocess, sys
import pandas as pd
from pathlib import Path

# Função para definir o caminho padrão do CSV
def get_default_path():
    # Sobe um nível para encontrar a pasta data_base na raiz do projeto
    base_dir = Path(__file__).resolve().parent.parent.parent
    return base_dir / "data_base" / "consumezone" / "vagasdotcom" / "history.csv"

# Função de carregamento com cache e tratamento de erros
def load_data(st, path):
    p = Path(path)
    if not p.exists():
        st.error(f"Arquivo não encontrado em: {path}")
        return pd.DataFrame()
    try:
        df = pd.read_csv(p)
        return df
    except Exception as e:
        st.error(f"Falha ao ler o arquivo: {e}")
        return pd.DataFrame()

def filter_input(st, df):
    st.sidebar.subheader("Filtros")
    # Seletor de coluna para filtro
    coluna_filtro = st.sidebar.selectbox(
        "Selecionar coluna para filtro", df.columns.tolist())
    # Caixa de texto para valor de filtro
    valor = st.sidebar.text_input(
        f"Filtrar '{coluna_filtro}' (contém):"
    )

    # Aplica filtro caso valor seja informado
    if valor:
        df = df[df[coluna_filtro].astype(str).str.contains(valor, case=False, na=False)]

def run_extract(st, search_word, order_by, times_click_see_more, filter_list):
    cmd = [
        sys.executable,
        "./etl_process/1_extract/extract__vagasdotcom.py",
        "--search_word",          search_word,
        "--order_by",             order_by,
        "--times_click_see_more", str(times_click_see_more)
    ]

    # para cada filtro adiciona um par --filter_list <valor>
    cmd += [arg for f in filter_list for arg in ("--filter_list", f)]
    
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)

    # Exibe saída padrão (stdout)
    st.subheader("Saída do script")
    st.code(result.stdout, language="bash")

    # Se houver erros (stderr), exibe também
    if result.stderr:
        st.subheader("Erros do script (stderr)")
        st.code(result.stderr, language="bash")
    if result.returncode == 0:
        st.success("Extraido com sucesso!")
    else:
        st.error(f"arquivo.py retornou código de erro {result.returncode}")

    # Consolidação com a base final
    subprocess.run([sys.executable, "./etl_process/2_transform/transform_vagasdotcom.py"])

def extract_parameters(st):
    st.sidebar.markdown("---")
    st.sidebar.subheader("Parâmetros de Extração")
    search_word = st.sidebar.text_input("Palavra de Busca", "")
    order_by = st.sidebar.selectbox(
        "Order By", ["mais_recentes", "mais_relevante"], index=0
    )
    filter_input = st.sidebar.text_input(
        "Filtros (separados por vírgula)", ""
    )
    filter_list = [f.strip() for f in filter_input.split(',') if f.strip()]
    times_click_see_more = st.sidebar.number_input(
        "Cliques em 'ver mais'", min_value=0, value=0, step=1
    )

    # Botão rodar extração
    if st.sidebar.button('Rodar extração'):
        with st.spinner("Executando arquivo.py..."):
            try:
                
                run_extract(st, search_word, order_by, times_click_see_more, filter_list)

            except subprocess.CalledProcessError as e:
                st.error(f"Erro ao executar arquivo: {e}")