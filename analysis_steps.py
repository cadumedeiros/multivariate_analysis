# analysis_steps.py
"""
Módulo contendo as funções para as etapas de análise:
filtragem, seleção de parâmetros, escalonamento e PCA.
Utiliza as configurações de config.py e os dados carregados por data_loader.py.
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import config # Importa as configurações
import data_loader # Importa o módulo de carregamento de dados

def filter_best_models(df, of_column, percentile):
    """
    Filtra o DataFrame para manter apenas os modelos com 'OF Value'
    abaixo de um determinado percentil.

    Args:
        df (pandas.DataFrame): DataFrame original com os dados.
        of_column (str): Nome da coluna da função objetivo.
        percentile (float): Percentil (entre 0 e 1) para o corte.

    Returns:
        pandas.DataFrame: DataFrame filtrado contendo os melhores modelos.
    """
    
    # Calcula o valor de corte (threshold)
    of_threshold = df[of_column].quantile(percentile)
    print(f"Calculando o valor de corte da OF ({percentile*100:.0f}º percentil): {of_threshold:.4f}")

    # Filtra o DataFrame
    best_models_df = df[df[of_column] <= of_threshold].copy()
    print(f"Número de modelos selecionados (melhores {percentile*100:.0f}%): {len(best_models_df)}")

    return best_models_df


def select_parameters(df):
    """
    Seleciona apenas as colunas de parâmetros (multiplicadores) do DataFrame.
    Exclui 'OF Value' e 'Simulation'.

    Args:
        df (pandas.DataFrame): DataFrame (geralmente o filtrado).

    Returns:
        pandas.DataFrame: DataFrame contendo apenas as colunas de parâmetros.
    """

    # Colunas a serem excluídas (assumindo que 'Simulation' exista)
    cols_to_exclude = ['OF Value', 'Simulation']
    parameter_cols = [col for col in df.columns if col not in cols_to_exclude]

    print(f"Colunas de parâmetros selecionadas: {parameter_cols}")
    return df[parameter_cols].copy()

def scale_data(X):
    """
    Padroniza (escala) os dados dos parâmetros (média 0, desvio padrão 1).

    Args:
        X (pandas.DataFrame): DataFrame com os parâmetros selecionados.

    Returns:
        tuple: Contendo:
            - pandas.DataFrame: DataFrame com os parâmetros escalados.
            - sklearn.preprocessing.StandardScaler: O objeto scaler ajustado.
    """

    scaler = StandardScaler()
    X_scaled_array = scaler.fit_transform(X)
    X_scaled_df = pd.DataFrame(X_scaled_array, columns=X.columns, index=X.index)
    print(f"Dados padronizados (escalados). Shape: {X_scaled_df.shape}")

    return X_scaled_df, scaler


def apply_pca(X_scaled, variance_threshold):
    """
    Aplica PCA aos dados escalados para reter uma certa porcentagem da variância.

    Args:
        X_scaled (pandas.DataFrame): DataFrame com os parâmetros escalados.
        variance_threshold (float): Percentual da variância a ser mantido (entre 0 e 1).

    Returns:
        tuple: Contendo:
            - numpy.ndarray: Array com os dados transformados pelo PCA.
            - sklearn.decomposition.PCA: O objeto PCA ajustado.
    """

    pca = PCA(n_components=variance_threshold)
    X_pca_array = pca.fit_transform(X_scaled)
    print(f"PCA aplicado. Número de componentes selecionados: {pca.n_components_}")
    print(f"Variância explicada acumulada: {np.sum(pca.explained_variance_ratio_):.2f}")
    
    return X_pca_array, pca
