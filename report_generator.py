# report_generator.py
"""
Módulo para gerar um relatório resumido da análise de calibração
em formato Markdown, incluindo tabelas e links para os gráficos.
"""

import os
import pandas as pd
import numpy as np # Necessário para np.sum no teste
import config # Importa as configurações
import data_loader # Para teste
import analysis_steps # Para teste
import clustering # Para teste
import plotting # Para teste (indiretamente via clustering no teste)
from datetime import datetime # Para adicionar data/hora ao relatório

def generate_markdown_report(report_filename,
                               df_cleaned,
                               df_best,
                               pca_model,
                               kmeans_model, # Passando o modelo kmeans para obter n_clusters
                               centroid_df,
                               of_stats_df,
                               best_per_cluster_df):
    """
    Gera um relatório da análise em formato Markdown.

    Args:
        report_filename (str): Nome do arquivo .md a ser criado.
        df_cleaned (pd.DataFrame): DataFrame com todos os dados limpos.
        df_best (pd.DataFrame): DataFrame com os melhores modelos e coluna 'Cluster'.
        pca_model (PCA): Modelo PCA ajustado.
        kmeans_model (KMeans): Modelo KMeans ajustado.
        centroid_df (pd.DataFrame): DataFrame com os centróides dos clusters (escala original).
        of_stats_df (pd.DataFrame): DataFrame com estatísticas de OF por cluster.
        best_per_cluster_df (pd.DataFrame): DataFrame com a melhor simulação de cada cluster.
    """
    # Verifica se todas as entradas são válidas
    # Verifica explicitamente se alguma das entradas necessárias é None
    required_inputs = {
        'report_filename': report_filename,
        'df_cleaned': df_cleaned,
        'df_best': df_best,
        'pca_model': pca_model,
        'kmeans_model': kmeans_model,
        'centroid_df': centroid_df,
        'of_stats_df': of_stats_df,
        'best_per_cluster_df': best_per_cluster_df
    }
    none_inputs = [name for name, value in required_inputs.items() if value is None]

    if none_inputs:
        print(f"Erro: Uma ou mais entradas para generate_markdown_report são None: {none_inputs}")
        return

    try:
        with open(report_filename, 'w', encoding='utf-8') as f:
            # --- Cabeçalho ---
            f.write(f"# Relatório de Análise de Calibração\n\n")
            f.write(f"Relatório gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"Arquivo de entrada: `{config.INPUT_FILE}`\n\n")

            # --- Resumo das Configurações ---
            f.write("## Resumo das Configurações da Análise\n\n")
            f.write(f"* **Percentil para Melhores Modelos:** {config.BEST_MODEL_PERCENTILE*100:.0f}%\n")
            f.write(f"* **Variância Mantida pelo PCA:** {config.PCA_VARIANCE_THRESHOLD*100:.0f}%\n")
            f.write(f"* **Número de Componentes Principais:** {pca_model.n_components_}\n")
            f.write(f"* **Número de Clusters (k):** {kmeans_model.n_clusters}\n\n") # Usa n_clusters do modelo

            # --- Seleção de Modelos ---
            f.write("## Seleção dos Melhores Modelos\n\n")
            f.write(f"Total de simulações: {len(df_cleaned)}\n")
            f.write(f"Número de modelos selecionados (melhores {config.BEST_MODEL_PERCENTILE*100:.0f}%): {len(df_best)}\n\n")
            f.write(f"![Gráfico de Dispersão OF]({os.path.basename(config.PLOT_OF_SCATTER)})\n")
            f.write("*Gráfico 1: Dispersão dos valores da Função Objetivo (OF). Pontos laranjas indicam os modelos selecionados.*\n\n")

            # --- Determinação do Número de Clusters ---
            f.write("## Determinação do Número de Clusters (k)\n\n")
            f.write(f"Foram analisados valores de k no intervalo: {list(config.K_RANGE)}\n\n")
            f.write(f"![Método do Cotovelo]({os.path.basename(config.PLOT_ELBOW)})\n")
            f.write("*Gráfico 2: Método do Cotovelo (Inércia vs. k). O 'cotovelo' sugere um k ótimo.*\n\n")
            f.write(f"![Pontuação de Silhueta]({os.path.basename(config.PLOT_SILHOUETTE)})\n")
            f.write("*Gráfico 3: Pontuação Média de Silhueta vs. k. Valores mais altos indicam melhor separação dos clusters.*\n\n")
            f.write(f"**Número de clusters escolhido (k): {config.OPTIMAL_K}**\n\n")

            # --- Visualização e Análise dos Clusters ---
            f.write("## Visualização e Análise dos Clusters\n\n")
            # PCA Plot
            variance_explained = pca_model.explained_variance_ratio_
            total_var_2pc = np.sum(variance_explained[:2]) * 100
            f.write(f"![Clusters PCA]({os.path.basename(config.PLOT_PCA_CLUSTERS)})\n")
            f.write(f"*Gráfico 4: Visualização dos {config.OPTIMAL_K} clusters no espaço dos dois primeiros Componentes Principais (Total Var. Explicada: {total_var_2pc:.1f}%).*\n\n")

            # Tamanho dos Clusters
            f.write("### Tamanho dos Clusters\n\n")
            cluster_counts = df_best['Cluster'].value_counts().sort_index().reset_index()
            cluster_counts.columns = ['Cluster', 'Número de Modelos']
            f.write(cluster_counts.to_markdown(index=False))
            f.write("\n\n")

            # Centróides
            f.write("### Centróides dos Clusters (Valores Médios dos Parâmetros Originais)\n\n")
            f.write(centroid_df.to_markdown(floatfmt=".4f")) # Formata floats
            f.write("\n*Tabela 1: Valores médios dos multiplicadores para cada cluster.*\n\n")

            # Estatísticas OF
            f.write(f"### Estatísticas da Função Objetivo ('OF Value') por Cluster\n\n")
            f.write(of_stats_df.to_markdown(floatfmt=".4f"))
            f.write("\n*Tabela 2: Estatísticas descritivas do 'OF Value' para os modelos dentro de cada cluster.*\n\n")

            # Boxplots
            f.write("### Distribuição dos Parâmetros por Cluster\n\n")
            f.write(f"![Boxplots Parâmetros]({os.path.basename(config.PLOT_BOXPLOTS)})\n")
            f.write("*Gráfico 5: Boxplots mostrando a distribuição dos valores de cada parâmetro (multiplicador) dentro de cada cluster.*\n\n")

            # --- Seleção dos Modelos Representativos ---
            f.write("## Seleção dos Modelos Representativos ('Campeões' por Cluster)\n\n")
            f.write("A tabela abaixo mostra a simulação com o menor 'OF Value' dentro de cada um dos clusters identificados.\n\n")
            f.write(best_per_cluster_df.to_markdown(index=True, floatfmt=".4f")) # Inclui o Simulation_ID como índice
            f.write("\n*Tabela 3: Melhores simulações representativas de cada cluster.*\n\n")
            

        print(f"Relatório Markdown gerado com sucesso em '{report_filename}'")

    except Exception as e:
        print(f"Erro ao gerar o relatório Markdown: {e}")
