# clustering.py
"""
Módulo para determinar o número ideal de clusters, aplicar K-Means
e analisar as características dos clusters formados.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import config # Importa as configurações
import data_loader # Para teste
import analysis_steps # Para teste

def plot_elbow_method(X_pca, k_range, filename):
    """
    Calcula e plota a inércia para diferentes valores de 'k' (Método do Cotovelo).

    Args:
        X_pca (numpy.ndarray): Dados após PCA.
        k_range (range): Intervalo de valores de 'k' a testar.
        filename (str): Nome do arquivo para salvar o gráfico.
    """
    if X_pca is None:
        print("Erro: Dados de entrada para o Método do Cotovelo são None.")
        return

    inertia = []
    print("\n--- Calculando Inércia (Método do Cotovelo) ---")
    for k in k_range:
        try:
            kmeans = KMeans(n_clusters=k, random_state=42, n_init='auto') # n_init='auto' é o padrão moderno
            kmeans.fit(X_pca)
            inertia.append(kmeans.inertia_)
            print(f"  k={k}, Inércia={kmeans.inertia_:.2f}")
        except Exception as e:
            print(f"Erro ao calcular K-Means para k={k}: {e}")
            inertia.append(np.nan) # Adiciona NaN se houver erro

    plt.figure(figsize=(10, 6))
    plt.plot(k_range, inertia, marker='o', linestyle='--')
    plt.xlabel('Número de Clusters (k)')
    plt.ylabel('Inércia (WSS)')
    plt.title('Método do Cotovelo para Determinar k Ótimo')
    plt.xticks(list(k_range))
    plt.grid(True)
    try:
        plt.savefig(filename)
        print(f"Gráfico do Método do Cotovelo salvo como '{filename}'")
    except Exception as e:
        print(f"Erro ao salvar gráfico do Cotovelo: {e}")
    plt.close() # Fecha a figura para liberar memória

def plot_silhouette_scores(X_pca, k_range, filename):
    """
    Calcula e plota a Pontuação de Silhueta para diferentes valores de 'k'.

    Args:
        X_pca (numpy.ndarray): Dados após PCA.
        k_range (range): Intervalo de valores de 'k' a testar.
        filename (str): Nome do arquivo para salvar o gráfico.
    """
    if X_pca is None:
        print("Erro: Dados de entrada para a Pontuação de Silhueta são None.")
        return

    silhouette_scores = []
    print("\n--- Calculando Pontuação de Silhueta ---")
    for k in k_range:
        try:
            # Garante que k seja menor que o número de amostras
            if k >= X_pca.shape[0]:
                print(f"  Aviso: k={k} é maior ou igual ao número de amostras ({X_pca.shape[0]}). Pulando.")
                silhouette_scores.append(np.nan)
                continue

            kmeans = KMeans(n_clusters=k, random_state=42, n_init='auto')
            cluster_labels = kmeans.fit_predict(X_pca)
            # Evita erro se apenas um cluster for formado ou previsto
            if len(np.unique(cluster_labels)) < 2:
                 print(f"  Aviso: Apenas {len(np.unique(cluster_labels))} cluster(s) encontrado(s) para k={k}. Pontuação de Silhueta não aplicável.")
                 silhouette_scores.append(np.nan) # Ou algum valor indicativo como -1
            else:
                silhouette_avg = silhouette_score(X_pca, cluster_labels)
                silhouette_scores.append(silhouette_avg)
                print(f"  k={k}, Pontuação de Silhueta={silhouette_avg:.4f}")
        except Exception as e:
            print(f"Erro ao calcular Silhueta para k={k}: {e}")
            silhouette_scores.append(np.nan)

    plt.figure(figsize=(10, 6))
    plt.plot(k_range, silhouette_scores, marker='o', linestyle='--')
    plt.xlabel('Número de Clusters (k)')
    plt.ylabel('Pontuação Média de Silhueta')
    plt.title('Análise da Pontuação de Silhueta para Determinar k Ótimo')
    plt.xticks(list(k_range))
    plt.grid(True)
    try:
        plt.savefig(filename)
        print(f"Gráfico da Pontuação de Silhueta salvo como '{filename}'")
    except Exception as e:
        print(f"Erro ao salvar gráfico da Silhueta: {e}")
    plt.close()

def apply_kmeans(X_pca, optimal_k):
    """
    Aplica o algoritmo K-Means aos dados com o número ótimo de clusters.

    Args:
        X_pca (numpy.ndarray): Dados após PCA.
        optimal_k (int): Número de clusters a serem formados.

    Returns:
        tuple: Contendo:
            - numpy.ndarray: Array com os rótulos de cluster para cada modelo.
            - sklearn.cluster.KMeans: O objeto KMeans ajustado.
            Ou (None, None) se ocorrer um erro.
    """
    if X_pca is None:
        print("Erro: Dados de entrada para K-Means são None.")
        return None, None
    if optimal_k <= 0 or optimal_k >= X_pca.shape[0]:
         print(f"Erro: optimal_k ({optimal_k}) inválido para o número de amostras ({X_pca.shape[0]}).")
         return None, None

    try:
        kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init='auto')
        cluster_labels = kmeans.fit_predict(X_pca)
        print(f"\nK-Means aplicado com k={optimal_k}.")
        return cluster_labels, kmeans
    except Exception as e:
        print(f"Erro ao aplicar K-Means: {e}")
        return None, None

def analyze_clusters(df_with_clusters, X_scaled_with_clusters, kmeans_model, scaler, pca, parameter_columns):
    """
    Analisa os clusters formados, calculando tamanhos e centróides.

    Args:
        df_with_clusters (pd.DataFrame): DataFrame original com a coluna 'Cluster'.
        X_scaled_with_clusters (pd.DataFrame): DataFrame escalado com a coluna 'Cluster'.
        kmeans_model (KMeans): Modelo KMeans ajustado.
        scaler (StandardScaler): Scaler ajustado.
        pca (PCA): Modelo PCA ajustado.
        parameter_columns (list): Lista dos nomes das colunas de parâmetros.

    Returns:
        pd.DataFrame: DataFrame com os centróides no espaço original dos parâmetros.
                      Ou None se ocorrer erro.
    """
    if df_with_clusters is None or X_scaled_with_clusters is None or kmeans_model is None or scaler is None or pca is None:
        print("Erro: Entrada inválida para analyze_clusters.")
        return None

    try:
        # Contagem de modelos por cluster
        print("\n--- Tamanho de Cada Cluster ---")
        cluster_counts = df_with_clusters['Cluster'].value_counts().sort_index()
        print(cluster_counts)

        # Centróides (revertendo PCA e escalonamento)
        print("\n--- Centróides dos Clusters (Valores Médios dos Parâmetros Originais) ---")
        centroids_pca = kmeans_model.cluster_centers_
        centroids_scaled = pca.inverse_transform(centroids_pca) # Reverte PCA
        centroids_original = scaler.inverse_transform(centroids_scaled) # Reverte escalonamento
        centroid_df = pd.DataFrame(centroids_original, columns=parameter_columns)
        centroid_df.index.name = 'Cluster'
        print(centroid_df)

        return centroid_df

    except Exception as e:
        print(f"Erro ao analisar clusters: {e}")
        return None

def analyze_of_by_cluster(df_with_clusters, of_column):
    """
    Calcula e exibe estatísticas da Função Objetivo ('OF Value') para cada cluster.

    Args:
        df_with_clusters (pd.DataFrame): DataFrame com a coluna 'Cluster'.
        of_column (str): Nome da coluna da Função Objetivo.
    """
    if df_with_clusters is None or df_with_clusters.empty:
         print("Erro: DataFrame de entrada para análise de OF está vazio ou é None.")
         return None
    if of_column not in df_with_clusters.columns:
         print(f"Erro: Coluna OF '{of_column}' não encontrada.")
         return None

    try:
        print(f"\n--- Estatísticas da '{of_column}' por Cluster ---")
        of_stats = df_with_clusters.groupby('Cluster')[of_column].describe()
        print(of_stats)
        return of_stats
    except Exception as e:
        print(f"Erro ao analisar OF por cluster: {e}")
        return None


# --- Bloco de Teste ---
if __name__ == "__main__":
    print("\nExecutando clustering.py como script principal para teste...")

    # 1. Carregar dados
    print("\n--- Teste: Carregando Dados ---")
    df_cleaned = data_loader.load_and_clean_data(config.INPUT_FILE)

    if df_cleaned is not None:
        # 2. Filtrar melhores modelos
        print("\n--- Teste: Filtrando Melhores Modelos ---")
        df_best = analysis_steps.filter_best_models(df_cleaned, 'OF Value', config.BEST_MODEL_PERCENTILE)

        if df_best is not None:
            # 3. Selecionar parâmetros
            print("\n--- Teste: Selecionando Parâmetros ---")
            X_parameters = analysis_steps.select_parameters(df_best)

            if X_parameters is not None:
                # 4. Escalonar dados
                print("\n--- Teste: Escalonando Dados ---")
                X_scaled_data, fitted_scaler = analysis_steps.scale_data(X_parameters)

                if X_scaled_data is not None:
                    # 5. Aplicar PCA
                    print("\n--- Teste: Aplicando PCA ---")
                    X_pca_data, fitted_pca = analysis_steps.apply_pca(X_scaled_data, config.PCA_VARIANCE_THRESHOLD)

                    if X_pca_data is not None:
                        # 6. Plotar Elbow e Silhouette para análise
                        plot_elbow_method(X_pca_data, config.K_RANGE, config.PLOT_ELBOW)
                        plot_silhouette_scores(X_pca_data, config.K_RANGE, config.PLOT_SILHOUETTE)

                        # 7. Aplicar K-Means (usando OPTIMAL_K do config)
                        cluster_labels, kmeans_model = apply_kmeans(X_pca_data, config.OPTIMAL_K)

                        if cluster_labels is not None:
                            # 8. Adicionar rótulos aos DataFrames
                            df_best['Cluster'] = cluster_labels
                            X_scaled_data['Cluster'] = cluster_labels # Adiciona ao escalado também

                            # 9. Analisar Clusters (tamanho e centróides)
                            centroids_df = analyze_clusters(df_best, X_scaled_data, kmeans_model, fitted_scaler, fitted_pca, X_parameters.columns)

                            # 10. Analisar OF por Cluster
                            of_stats_df = analyze_of_by_cluster(df_best, 'OF Value')

                            # 11. Salvar DataFrame com clusters
                            try:
                                df_best_sorted = df_best.sort_values(by=['Cluster', 'OF Value'])
                                df_best_sorted.to_excel(config.OUTPUT_CLUSTER_RESULTS)
                                print(f"\nDataFrame com clusters salvo em '{config.OUTPUT_CLUSTER_RESULTS}'")

                                # 12. Salvar melhores de cada cluster
                                idx_best = df_best.groupby('Cluster')['OF Value'].idxmin()
                                best_per_cluster_df = df_best.loc[idx_best]
                                best_per_cluster_df.to_excel(config.OUTPUT_BEST_PER_CLUSTER)
                                print(f"Melhores modelos por cluster salvos em '{config.OUTPUT_BEST_PER_CLUSTER}'")

                                print("\nTeste do clustering.py concluído com sucesso.")

                            except Exception as e:
                                 print(f"\nErro ao salvar arquivos de saída: {e}")
                                 print("\nTeste do clustering.py concluído com erros no salvamento.")

                        else:
                            print("\nTeste do clustering.py falhou na aplicação do K-Means.")
                    else:
                        print("\nTeste do clustering.py falhou na etapa PCA.")
                else:
                    print("\nTeste do clustering.py falhou na etapa de escalonamento.")
            else:
                print("\nTeste do clustering.py falhou na seleção de parâmetros.")
        else:
            print("\nTeste do clustering.py falhou na filtragem.")
    else:
        print("\nTeste do clustering.py falhou no carregamento de dados.")