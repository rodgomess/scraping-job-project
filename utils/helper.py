from datetime import datetime
import pandas as pd
import os

def save_output(output):
    # Path para salvar
    current_date = datetime.now().date()

    # Definindo o caminho do diretório e do arquivo
    directory_path = f"datalake/vagasdotcom/{current_date}"
    file_path = f"{directory_path}/vagas_extraidas.csv"
    
    # Criando Data Frame
    df = pd.DataFrame(output)

    # Adicionando campos de controle
    df['datetime_execution'] = pd.to_datetime(datetime.now())
    df['date_execution'] = pd.to_datetime(datetime.now().date())

    # Verificando se o diretório existe, se não, criando-o
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
    
    # Salvando os dados
    df.to_csv(file_path, index=False)
    print(f"✅ Dados salvos com sucesso em: {file_path}")