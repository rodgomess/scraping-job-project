import pandas as pd
from datetime import datetime
import os
from functions_transform import ajustar_data_publicacao

# Variaveis
current_date = datetime.now().date()
file_path_extract = f"./data_base/datalake/vagasdotcom/extract.csv"

file_path_history = './data_base/consumezone/vagasdotcom'
file_path_save = f"{file_path_history}/history.csv"

# Lendo o arquivo extraido
df_extract = pd.read_csv(file_path_extract)

# Ajustando a coluna para date para conseguir fazer operações com datas
df_extract['date_execution'] = pd.to_datetime(df_extract['date_execution'])
df_extract['date_execution'] = df_extract['date_execution'].dt.date

# Ajustando coluna data_publicacao para deixar somente a data
df_extract['data_publicacao'] = df_extract.apply(ajustar_data_publicacao, axis=1)

# Verificando se o historico já existe
if os.path.exists(file_path_save):

    # Lendo o historico
    df_history = pd.read_csv(file_path_save)

    # Juntando a extração corrente com o historico
    df_final = pd.concat([df_extract, df_history], ignore_index=True)

    # Retirando duplicidades pela chave unica "link"
    df_final = df_final.drop_duplicates(subset='link')

    df_final['data_publicacao'] = pd.to_datetime(df_final['data_publicacao'])

else:
    df_final = df_extract

# Verificando se o diretório existe, se não, criando-o
if not os.path.exists(file_path_history):
    os.makedirs(file_path_history)

# Salvando os dados
df_final.to_csv(file_path_save, index=False)
print(f"Dados salvos com sucesso em: {file_path_save}")