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

    inertia = []
    print("\n--- Calculando Inércia (Método do Cotovelo) ---")
    for k in k_range:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init='auto') # n_init='auto' é o padrão moderno
        kmeans.fit(X_pca)
        inertia.append(kmeans.inertia_)
        print(f"  k={k}, Inércia={kmeans.inertia_:.2f}")

    plt.figure(figsize=(10, 6))
    plt.plot(k_range, inertia, marker='o', linestyle='--')
    plt.xlabel('Número de Clusters (k)')
    plt.ylabel('Inércia (WSS)')
    plt.title('Método do Cotovelo para Determinar k Ótimo')
    plt.xticks(list(k_range))
    plt.grid(True)
 
    plt.savefig(filename)
    print(f"Gráfico do Método do Cotovelo salvo como '{filename}'")
    plt.close()

def plot_silhouette_scores(X_pca, k_range, filename):
    """
    Calcula e plota a Pontuação de Silhueta para diferentes valores de 'k'.

    Args:
        X_pca (numpy.ndarray): Dados após PCA.
        k_range (range): Intervalo de valores de 'k' a testar.
        filename (str): Nome do arquivo para salvar o gráfico.
    """

    silhouette_scores = []
    print("\n--- Calculando Pontuação de Silhueta ---")
    for k in k_range:
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
    """

    kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init='auto')
    cluster_labels = kmeans.fit_predict(X_pca)
    print(f"\nK-Means aplicado com k={optimal_k}.")
    return cluster_labels, kmeans

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
    """


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


def analyze_of_by_cluster(df_with_clusters, of_column):
    """
    Calcula e exibe estatísticas da Função Objetivo ('OF Value') para cada cluster.

    Args:
        df_with_clusters (pd.DataFrame): DataFrame com a coluna 'Cluster'.
        of_column (str): Nome da coluna da Função Objetivo.
    """

    print(f"\n--- Estatísticas da '{of_column}' por Cluster ---")
    of_stats = df_with_clusters.groupby('Cluster')[of_column].describe()
    print(of_stats)
    return of_stats