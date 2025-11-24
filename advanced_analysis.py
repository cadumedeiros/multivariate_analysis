"""
Módulo de análises estatísticas multivariadas avançadas:
- Hierarchical clustering (Ward)
- Linear Discriminant Analysis (LDA)
- Validação de clusters
- ANOVA/MANOVA (comparação estatística entre clusters)
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.cluster.hierarchy import linkage, dendrogram, fcluster
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score
import statsmodels.api as sm
from statsmodels.formula.api import ols

import config

def hierarchical_clustering(X_pca, method='ward', max_clusters=10, filename=None):
    """
    Realiza clustering hierárquico (Ward) e plota o dendrograma.
    
    Args:
        X_pca (numpy.ndarray): Dados reduzidos pelo PCA.
        method (str): Método de ligação (default: 'ward').
        max_clusters (int): Número máximo de clusters a destacar no dendrograma.
        filename (str): Caminho para salvar o gráfico.
    
    Returns:
        numpy.ndarray: Rótulos de cluster gerados.
    """
    print("\n--- Hierarchical Clustering ---")
    linkage_matrix = linkage(X_pca, method=method)
    
    plt.figure(figsize=(12, 6))
    dendrogram(linkage_matrix, truncate_mode='level', p=5)
    plt.title(f"Dendrograma - Método {method.capitalize()}")
    plt.xlabel("Amostras")
    plt.ylabel("Distância Euclidiana")
    
    if filename:
        plt.savefig(filename)
        print(f"Dendrograma salvo em '{filename}'")
    plt.close()

    # Gera rótulos cortando o dendrograma em 'max_clusters' grupos
    clusters_hier = fcluster(linkage_matrix, t=max_clusters, criterion='maxclust')
    print(f"Clusters hierárquicos formados: {np.unique(clusters_hier)}")
    
    return clusters_hier


def validate_clusters(X_pca, cluster_labels):
    """
    Calcula métricas de validação dos clusters.

    Args:
        X_pca (numpy.ndarray): Dados no espaço PCA.
        cluster_labels (numpy.ndarray): Rótulos dos clusters.

    Returns:
        dict: Dicionário com as métricas calculadas.
    """
    print("\n--- Validação dos Clusters ---")
    results = {}
    results['Silhouette'] = silhouette_score(X_pca, cluster_labels)
    results['Calinski-Harabasz'] = calinski_harabasz_score(X_pca, cluster_labels)
    results['Davies-Bouldin'] = davies_bouldin_score(X_pca, cluster_labels)
    
    print(f"Silhouette Score: {results['Silhouette']:.3f}")
    print(f"Calinski-Harabasz Index: {results['Calinski-Harabasz']:.2f}")
    print(f"Davies-Bouldin Index: {results['Davies-Bouldin']:.2f}")
    
    return results


def lda_analysis(X_scaled, cluster_labels, feature_names=None, filename=None):
    """
    Aplica Análise Discriminante Linear (LDA) para identificar os parâmetros mais discriminantes.

    Args:
        X_scaled (pd.DataFrame): Dados padronizados (sem a coluna 'Cluster').
        cluster_labels (array-like): Rótulos dos clusters.
        feature_names (list | None): Lista de nomes das variáveis. Se None, usa X_scaled.columns.
        filename (str): Caminho para salvar gráfico opcional.

    Returns:
        pd.Series: Coeficientes discriminantes médios, ordenados.
    """
    print("\n--- Análise Discriminante Linear (LDA) ---")
    # garante que os nomes batem com as colunas realmente usadas
    if feature_names is None:
        feature_names = list(X_scaled.columns)
    else:
        # se vieram nomes de fora (ex.: X_parameters.columns), vamos garantir
        # que eles têm o mesmo tamanho das colunas do X_scaled
        # filtrando tudo que não está no X_scaled
        feature_names = [f for f in feature_names if f in X_scaled.columns]

    lda = LinearDiscriminantAnalysis()
    lda.fit(X_scaled, cluster_labels)

    # lda.coef_ tem shape (n_classes - 1, n_features)
    coef_mean = np.mean(lda.coef_, axis=0)

    # agora o tamanho bate porque veio de X_scaled.columns
    coef_series = pd.Series(coef_mean, index=feature_names).sort_values(ascending=False)
    print("Parâmetros mais discriminantes:\n", coef_series)

    if filename:
        plt.figure(figsize=(10, 5))
        coef_series.plot(kind='bar')
        plt.title("Coeficientes Discriminantes (LDA)")
        plt.ylabel("Importância Relativa")
        plt.tight_layout()
        plt.savefig(filename)
        plt.close()
        print(f"Gráfico LDA salvo em '{filename}'")

    return coef_series



def anova_by_cluster(df, dependent_var, cluster_col='Cluster'):
    """
    Executa uma ANOVA para testar diferenças entre clusters.

    Args:
        df (pd.DataFrame): DataFrame com variável dependente e coluna 'Cluster'.
        dependent_var (str): Nome da variável a ser testada.
        cluster_col (str): Nome da coluna de clusters.

    Returns:
        DataFrame: Tabela de ANOVA.
    """
    print(f"\n--- ANOVA para {dependent_var} por {cluster_col} ---")

    formula = f"Q('{dependent_var}') ~ C({cluster_col})"
    model = ols(formula, data=df).fit()
    anova_table = sm.stats.anova_lm(model, typ=2)
    print(anova_table)
    return anova_table
