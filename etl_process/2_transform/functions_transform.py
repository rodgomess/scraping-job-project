import pandas as pd
from datetime import timedelta

def ajustar_data_publicacao(row):
    """
    Ajusta a coluna data_publicacao para:
        - Se for 'Publicada há X dias', subtrair da data de execução
        - Se for 'Publicada ontem' ou 'Publicada hoje' troca para a data correspondente
        - Se for 'Publicada em DD/MM/YYYY', remover o texto e converter

    Args:
        row: linha pandas
    
    Returns:
        pd: Row ajustada
    """
    
    col_data_publicacao = row['data_publicacao']
    col_date_execution = row['date_execution']

    if "Publicada há" in col_data_publicacao:
        # Extrai o número de dias
        dias = int(col_data_publicacao.split(' ')[3])
        # Subtrai da execução
        return col_date_execution - timedelta(days=dias)
    
    elif "Publicada ontem" in col_data_publicacao:
        return col_date_execution - timedelta(days=-1)
    
    elif "Publicada hoje" in col_data_publicacao:
        return col_date_execution
    
    else:
        nova_date = col_data_publicacao.replace('Publicada em ', '').strip()
        nova_date = pd.to_datetime(nova_date, dayfirst=True)
        return nova_date