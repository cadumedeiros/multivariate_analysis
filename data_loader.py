# data_loader.py
"""
Módulo para carregar e limpar os dados de calibração do arquivo Excel.
Utiliza as configurações definidas em config.py.
"""

import pandas as pd
import config # Importa as configurações do arquivo config.py

def load_and_clean_data(file_path):
    """
    Carrega os dados do arquivo Excel, limpa colunas desnecessárias e define o índice.

    Args:
        file_path (str): O caminho para o arquivo Excel de entrada.

    Returns:
        pandas.DataFrame: O DataFrame limpo com os dados de calibração
    """
   
    # Carrega o arquivo Excel
    df = pd.read_excel(file_path)
    print(f"Arquivo '{file_path}' carregado com sucesso.")

    # Limpa colunas desnecessárias (ignora se não existirem)
    df_cleaned = df.drop(['OutputPath', 'Ambiguity'], axis=1, errors='ignore')
    print("Colunas 'OutputPath' e 'Ambiguity' removidas (se existiam).")

    # Renomeia 'Unnamed: 0' para 'Simulation_ID' e define como índice
    if 'Unnamed: 0' in df_cleaned.columns:
        df_cleaned = df_cleaned.rename(columns={'Unnamed: 0': 'Simulation_ID'})
        df_cleaned = df_cleaned.set_index('Simulation_ID')
        print("Coluna 'Unnamed: 0' renomeada para 'Simulation_ID' e definida como índice.")

    # Verifica se as colunas essenciais 'OF Value' e 'Simulation' existem
    essential_cols = ['OF Value', 'Simulation']
    missing_essentials = [col for col in essential_cols if col not in df_cleaned.columns and col != 'Simulation_ID'] # Não verifica Simulation_ID se já for índice
    if missing_essentials:
        print(f"Erro Crítico: Colunas essenciais não encontradas no DataFrame: {missing_essentials}")
        return None

    print("Limpeza inicial dos dados concluída.")
    return df_cleaned
