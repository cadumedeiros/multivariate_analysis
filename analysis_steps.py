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
    if df is None or df.empty:
        print("Erro: DataFrame de entrada está vazio ou é None.")
        return None

    if of_column not in df.columns:
        print(f"Erro: Coluna da função objetivo '{of_column}' não encontrada.")
        return None

    try:
        # Calcula o valor de corte (threshold)
        of_threshold = df[of_column].quantile(percentile)
        print(f"Calculando o valor de corte da OF ({percentile*100:.0f}º percentil): {of_threshold:.4f}")

        # Filtra o DataFrame
        best_models_df = df[df[of_column] <= of_threshold].copy()
        print(f"Número de modelos selecionados (melhores {percentile*100:.0f}%): {len(best_models_df)}")

        if best_models_df.empty:
            print("Aviso: Nenhum modelo passou no filtro. Verifique o percentil ou os dados.")

        return best_models_df

    except Exception as e:
        print(f"Erro ao filtrar os melhores modelos: {e}")
        return None

def select_parameters(df):
    """
    Seleciona apenas as colunas de parâmetros (multiplicadores) do DataFrame.
    Exclui 'OF Value' e 'Simulation'.

    Args:
        df (pandas.DataFrame): DataFrame (geralmente o filtrado).

    Returns:
        pandas.DataFrame: DataFrame contendo apenas as colunas de parâmetros.
    """
    if df is None or df.empty:
        print("Erro: DataFrame de entrada para seleção de parâmetros está vazio ou é None.")
        return None

    # Colunas a serem excluídas (assumindo que 'Simulation' exista)
    cols_to_exclude = ['OF Value', 'Simulation']
    parameter_cols = [col for col in df.columns if col not in cols_to_exclude]

    # Verifica se sobraram colunas de parâmetros
    if not parameter_cols:
         print("Erro: Nenhuma coluna de parâmetro encontrada após excluir 'OF Value' e 'Simulation'.")
         return None

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
            Ou (None, None) se ocorrer um erro.
    """
    if X is None or X.empty:
        print("Erro: DataFrame de entrada para escalonamento está vazio ou é None.")
        return None, None

    try:
        scaler = StandardScaler()
        X_scaled_array = scaler.fit_transform(X)
        X_scaled_df = pd.DataFrame(X_scaled_array, columns=X.columns, index=X.index)
        print(f"Dados padronizados (escalados). Shape: {X_scaled_df.shape}")
        return X_scaled_df, scaler
    except Exception as e:
        print(f"Erro ao escalonar os dados: {e}")
        return None, None

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
            Ou (None, None) se ocorrer um erro.
    """
    if X_scaled is None or X_scaled.empty:
        print("Erro: DataFrame de entrada para PCA está vazio ou é None.")
        return None, None

    try:
        pca = PCA(n_components=variance_threshold)
        X_pca_array = pca.fit_transform(X_scaled)
        print(f"PCA aplicado. Número de componentes selecionados: {pca.n_components_}")
        print(f"Variância explicada acumulada: {np.sum(pca.explained_variance_ratio_):.2f}")
        return X_pca_array, pca
    except Exception as e:
        print(f"Erro ao aplicar PCA: {e}")
        return None, None

# --- Bloco de Teste ---
if __name__ == "__main__":
    print("\nExecutando analysis_steps.py como script principal para teste...")

    # 1. Carregar dados
    print("\n--- Teste: Carregando Dados ---")
    df_cleaned = data_loader.load_and_clean_data(config.INPUT_FILE)

    if df_cleaned is not None:
        # 2. Filtrar melhores modelos
        print("\n--- Teste: Filtrando Melhores Modelos ---")
        df_best = filter_best_models(df_cleaned, 'OF Value', config.BEST_MODEL_PERCENTILE)

        if df_best is not None:
            # 3. Selecionar parâmetros
            print("\n--- Teste: Selecionando Parâmetros ---")
            X_parameters = select_parameters(df_best)

            if X_parameters is not None:
                # 4. Escalonar dados
                print("\n--- Teste: Escalonando Dados ---")
                X_scaled_data, fitted_scaler = scale_data(X_parameters)

                if X_scaled_data is not None:
                    # 5. Aplicar PCA
                    print("\n--- Teste: Aplicando PCA ---")
                    X_pca_data, fitted_pca = apply_pca(X_scaled_data, config.PCA_VARIANCE_THRESHOLD)

                    if X_pca_data is not None:
                        print(f"\nShape dos dados após PCA: {X_pca_data.shape}")
                        print("\nTeste do analysis_steps.py concluído com sucesso.")
                    else:
                        print("\nTeste do analysis_steps.py falhou na etapa PCA.")
                else:
                    print("\nTeste do analysis_steps.py falhou na etapa de escalonamento.")
            else:
                print("\nTeste do analysis_steps.py falhou na seleção de parâmetros.")
        else:
            print("\nTeste do analysis_steps.py falhou na filtragem.")
    else:
        print("\nTeste do analysis_steps.py falhou no carregamento de dados.")