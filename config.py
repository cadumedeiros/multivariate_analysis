# config.py
"""
Arquivo de configuração para a análise de calibração.
Armazena constantes como nomes de arquivos, parâmetros de análise e nomes de gráficos.
"""

# --- Arquivos de Entrada/Saída ---
INPUT_FILE = '5Pocos_SemEustasia.xlsx'
OUTPUT_CLUSTER_RESULTS = 'simulacoes_por_cluster.xlsx'
OUTPUT_BEST_PER_CLUSTER = 'melhores_simulacoes_por_grupo.xlsx'
OUTPUT_REPORT = 'relatorio_analise_calibracao.md'

# --- Parâmetros da Análise ---
BEST_MODEL_PERCENTILE = 0.30  # Percentil para selecionar os melhores modelos (30%)
PCA_VARIANCE_THRESHOLD = 0.95 # Variância a ser mantida pelo PCA (95%)
K_RANGE = range(2, 11)        # Intervalo de 'k' para testar no Elbow/Silhouette
OPTIMAL_K = 10                 # Número de clusters escolhido (baseado na sua análise)

# --- Nomes dos Arquivos de Gráfico ---
PLOT_OF_SCATTER = 'grafico_dispersao_OF.png'
PLOT_ELBOW = 'grafico_metodo_cotovelo.png'
PLOT_SILHOUETTE = 'grafico_pontuacao_silhueta.png'
PLOT_PCA_CLUSTERS = 'grafico_clusters_pca.png'
PLOT_BOXPLOTS = 'grafico_boxplots_parametros.png'

print("Configurações carregadas.")