# plotting.py
"""
Módulo para gerar as visualizações da análise de calibração,
como gráficos de dispersão, PCA e boxplots. Salva os gráficos em arquivos.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np # Importado para o teste
import config # Importa as configurações
import data_loader # Para teste
import analysis_steps # Para teste
import clustering # Para teste

plt.rcParams.update({
    "font.size": 14,
    "axes.titlesize": 20,
    "axes.labelsize": 22,
    "legend.fontsize": 14,
    "xtick.labelsize": 14,
    "ytick.labelsize": 14,
})

# Configurações de estilo para os gráficos (opcional, mas melhora a aparência)
sns.set_theme(style="whitegrid")

def plot_of_scatter(df_all, df_best, x_col, y_col, filename):
    """
    Gera um gráfico de dispersão mostrando todos os OF Values e destacando
    os melhores modelos selecionados.

    Args:
        df_all (pd.DataFrame): DataFrame com todos os dados limpos.
        df_best (pd.DataFrame): DataFrame com os melhores modelos filtrados.
        x_col (str): Nome da coluna para o eixo X (ex: 'Simulation').
        y_col (str): Nome da coluna para o eixo Y (ex: 'OF Value').
        filename (str): Nome do arquivo para salvar o gráfico.
    """

    plt.figure(figsize=(10, 6))
    # Plota todos os pontos
    plt.plot(df_all[x_col], df_all[y_col], marker='o', linestyle='None',
             alpha=0.5, label='Todos os Modelos')
    # Destaca os melhores pontos
    plt.plot(df_best[x_col], df_best[y_col], marker='o', linestyle='None',
             label=f'Melhores {config.BEST_MODEL_PERCENTILE*100:.0f}%')

    plt.xlabel('Simulação', fontsize=18)
    plt.ylabel('Valor da Função Objetivo (OF)', fontsize=18)
    plt.title('Dispersão dos Valores da Função Objetivo', fontsize=18)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    plt.legend()
    plt.grid(True)

    plt.savefig(filename)
    print(f"Gráfico de dispersão OF salvo como '{filename}'")
    plt.close()

def plot_pca_clusters(X_pca, cluster_labels, pca_model, filename):
    """
    Gera um gráfico de dispersão dos dois primeiros componentes principais,
    colorindo os pontos pelos seus clusters.

    Args:
        X_pca (numpy.ndarray): Dados após PCA (pelo menos 2 componentes).
        cluster_labels (numpy.ndarray): Rótulos de cluster para cada ponto.
        pca_model (PCA): Modelo PCA ajustado para obter a variância explicada.
        filename (str): Nome do arquivo para salvar o gráfico.
    """

    plt.figure(figsize=(12, 8))
    unique_clusters = np.unique(cluster_labels)
    colors = plt.cm.viridis(np.linspace(0, 1, len(unique_clusters)))

    for cluster, color in zip(unique_clusters, colors):
        idx = cluster_labels == cluster
        plt.scatter(X_pca[idx, 0], X_pca[idx, 1], color=color,
                    label=f'Cluster {cluster}', s=100, alpha=0.8)

    # Adiciona variância explicada aos rótulos dos eixos
    variance_explained = pca_model.explained_variance_ratio_
    pc1_var = variance_explained[0] * 100
    pc2_var = variance_explained[1] * 100
    total_var = np.sum(variance_explained[:2]) * 100

    plt.title(f'Clusters no Espaço PCA (Total Var. Explicada nos 2 PCs: {total_var:.1f}%)', fontsize=18)
    plt.xlabel(f'Componente Principal 1 ({pc1_var:.1f}%)', fontsize=18)
    plt.ylabel(f'Componente Principal 2 ({pc2_var:.1f}%)', fontsize=18)
    plt.legend(title='Cluster', fontsize=14, title_fontsize=16)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.6)

    plt.savefig(filename)
    print(f"Gráfico de clusters PCA salvo como '{filename}'")
    
    plt.close()

def plot_parameter_boxplots(X_params_with_clusters, filename):
    """
    Gera boxplots para cada parâmetro, agrupados por cluster.

    Args:
        X_params_with_clusters (pd.DataFrame): DataFrame original (não escalado)
                                                dos parâmetros com a coluna 'Cluster'.
        filename (str): Nome do arquivo para salvar o gráfico.
    """
    if X_params_with_clusters is None:
        print("Erro: DataFrame de entrada para plot_parameter_boxplots é None.")
        return

    parameter_cols = [col for col in X_params_with_clusters.columns if col != 'Cluster']
    n_params = len(parameter_cols)
    # Ajusta o layout (ex: 3 colunas de gráficos)
    n_cols = 3
    n_rows = (n_params + n_cols - 1) // n_cols

    plt.figure(figsize=(5 * n_cols, 4 * n_rows)) # Ajusta tamanho da figura
    for i, column in enumerate(parameter_cols):
        plt.subplot(n_rows, n_cols, i + 1)
        sns.boxplot(x='Cluster', y=column, data=X_params_with_clusters)
        plt.title(f'{column}', fontsize=14)
        plt.xlabel('Cluster', fontsize=14) # Opcional, pode remover se ficar muito cheio
        plt.ylabel('Valor do Multiplicador', fontsize=14) # Opcional
        plt.xticks(fontsize=14)
        plt.yticks(fontsize=14)

    plt.suptitle('Distribuição dos Parâmetros por Cluster', fontsize=22, y=1.02) # Título geral
    plt.tight_layout(rect=[0, 0.03, 1, 0.98]) # Ajusta layout para não sobrepor títulos
  
    plt.savefig(filename)
    print(f"Gráfico de boxplots salvo como '{filename}'")
    
    plt.close()
