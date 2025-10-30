# config.py
"""
Arquivo de configuração para a análise de calibração.
Armazena constantes como nomes de arquivos, parâmetros de análise e nomes de gráficos.
"""

import os

# --- Arquivos de Entrada/Saída ---
INPUT_FILE = '5_well_7param_RangeMaior_35x40.xlsx'

# Diretório de resultados baseado no nome do arquivo de entrada
_input_stem = os.path.splitext(os.path.basename(INPUT_FILE))[0]
RESULTS_DIR = f"results_{_input_stem}"
os.makedirs(RESULTS_DIR, exist_ok=True)

# Arquivos de saída (Excel e relatório) dentro do diretório de resultados
OUTPUT_CLUSTER_RESULTS = os.path.join(RESULTS_DIR, 'simulacoes_por_cluster.xlsx')
OUTPUT_BEST_PER_CLUSTER = os.path.join(RESULTS_DIR, 'melhores_simulacoes_por_grupo.xlsx')
OUTPUT_REPORT = os.path.join(RESULTS_DIR, 'relatorio_analise_calibracao.md')

# --- Parâmetros da Análise ---
BEST_MODEL_PERCENTILE = 0.30  # Percentil para selecionar os melhores modelos (30%)
PCA_VARIANCE_THRESHOLD = 0.95 # Variância a ser mantida pelo PCA (95%)
K_RANGE = range(2, 11)        # Intervalo de 'k' para testar no Elbow/Silhouette
OPTIMAL_K = 10                 # Número de clusters escolhido (baseado na sua análise)

# --- Nomes dos Arquivos de Gráfico ---
# Salvamos as imagens dentro do diretório de resultados
PLOT_OF_SCATTER = os.path.join(RESULTS_DIR, 'grafico_dispersao_OF.png')
PLOT_ELBOW = os.path.join(RESULTS_DIR, 'grafico_metodo_cotovelo.png')
PLOT_SILHOUETTE = os.path.join(RESULTS_DIR, 'grafico_pontuacao_silhueta.png')
PLOT_PCA_CLUSTERS = os.path.join(RESULTS_DIR, 'grafico_clusters_pca.png')
PLOT_BOXPLOTS = os.path.join(RESULTS_DIR, 'grafico_boxplots_parametros.png')

print("Configurações carregadas.")
