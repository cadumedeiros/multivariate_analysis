# report_generator.py
"""
Módulo para gerar um relatório resumido da análise de calibração
em formato Markdown, incluindo tabelas e links para os gráficos.
"""

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
            f.write(f"![Gráfico de Dispersão OF]({config.PLOT_OF_SCATTER})\n")
            f.write("*Gráfico 1: Dispersão dos valores da Função Objetivo (OF). Pontos laranjas indicam os modelos selecionados.*\n\n")

            # --- Determinação do Número de Clusters ---
            f.write("## Determinação do Número de Clusters (k)\n\n")
            f.write(f"Foram analisados valores de k no intervalo: {list(config.K_RANGE)}\n\n")
            f.write(f"![Método do Cotovelo]({config.PLOT_ELBOW})\n")
            f.write("*Gráfico 2: Método do Cotovelo (Inércia vs. k). O 'cotovelo' sugere um k ótimo.*\n\n")
            f.write(f"![Pontuação de Silhueta]({config.PLOT_SILHOUETTE})\n")
            f.write("*Gráfico 3: Pontuação Média de Silhueta vs. k. Valores mais altos indicam melhor separação dos clusters.*\n\n")
            f.write(f"**Número de clusters escolhido (k): {config.OPTIMAL_K}**\n\n")

            # --- Visualização e Análise dos Clusters ---
            f.write("## Visualização e Análise dos Clusters\n\n")
            # PCA Plot
            variance_explained = pca_model.explained_variance_ratio_
            total_var_2pc = np.sum(variance_explained[:2]) * 100
            f.write(f"![Clusters PCA]({config.PLOT_PCA_CLUSTERS})\n")
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
            f.write(f"![Boxplots Parâmetros]({config.PLOT_BOXPLOTS})\n")
            f.write("*Gráfico 5: Boxplots mostrando a distribuição dos valores de cada parâmetro (multiplicador) dentro de cada cluster.*\n\n")

            # --- Seleção dos Modelos Representativos ---
            f.write("## Seleção dos Modelos Representativos ('Campeões' por Cluster)\n\n")
            f.write("A tabela abaixo mostra a simulação com o menor 'OF Value' dentro de cada um dos clusters identificados.\n\n")
            f.write(best_per_cluster_df.to_markdown(index=True, floatfmt=".4f")) # Inclui o Simulation_ID como índice
            f.write("\n*Tabela 3: Melhores simulações representativas de cada cluster.*\n\n")

            # --- Conclusão (Sugestão) ---
            f.write("---\n\n")
            f.write("## Próximos Passos (Sugestão)\n\n")
            f.write("Analisar os parâmetros dos centróides (Tabela 1) e os modelos representativos (Tabela 3) em conjunto com especialistas de domínio (geólogos) para verificar se os diferentes clusters representam cenários geologicamente distintos e plausíveis. Utilizar os modelos representativos para análises de incerteza posteriores.\n")

        print(f"Relatório Markdown gerado com sucesso em '{report_filename}'")

    except Exception as e:
        print(f"Erro ao gerar o relatório Markdown: {e}")

# --- Bloco de Teste ---
if __name__ == "__main__":
    print("\nExecutando report_generator.py como script principal para teste...")

    # Reexecuta todo o pipeline para obter os resultados necessários
    df_cleaned = data_loader.load_and_clean_data(config.INPUT_FILE)
    if df_cleaned is not None:
        df_best = analysis_steps.filter_best_models(df_cleaned, 'OF Value', config.BEST_MODEL_PERCENTILE)
        if df_best is not None:
            X_parameters = analysis_steps.select_parameters(df_best)
            if X_parameters is not None:
                X_scaled_data, fitted_scaler = analysis_steps.scale_data(X_parameters)
                if X_scaled_data is not None:
                    X_pca_data, fitted_pca = analysis_steps.apply_pca(X_scaled_data, config.PCA_VARIANCE_THRESHOLD)
                    if X_pca_data is not None:
                        # Gera gráficos Elbow/Silhouette (necessário para contexto do relatório)
                        clustering.plot_elbow_method(X_pca_data, config.K_RANGE, config.PLOT_ELBOW)
                        clustering.plot_silhouette_scores(X_pca_data, config.K_RANGE, config.PLOT_SILHOUETTE)
                        # Aplica K-Means
                        cluster_labels, kmeans_model = clustering.apply_kmeans(X_pca_data, config.OPTIMAL_K)
                        if cluster_labels is not None:
                            df_best['Cluster'] = cluster_labels
                            X_scaled_data['Cluster'] = cluster_labels # Adiciona ao escalado também
                            X_parameters['Cluster'] = cluster_labels # Adiciona ao original

                            # Gera os outros gráficos
                            plotting.plot_of_scatter(df_cleaned, df_best, 'Simulation', 'OF Value', config.PLOT_OF_SCATTER)
                            plotting.plot_pca_clusters(X_pca_data, cluster_labels, fitted_pca, config.PLOT_PCA_CLUSTERS)
                            plotting.plot_parameter_boxplots(X_parameters, config.PLOT_BOXPLOTS) # Usa X_parameters original com 'Cluster'

                            # Analisa clusters e OF
                            centroids_df = clustering.analyze_clusters(df_best, X_scaled_data, kmeans_model, fitted_scaler, fitted_pca, X_parameters.drop('Cluster', axis=1).columns) # Passa nomes sem 'Cluster'
                            of_stats_df = clustering.analyze_of_by_cluster(df_best, 'OF Value')

                            # Encontra melhores por cluster
                            idx_best = df_best.groupby('Cluster')['OF Value'].idxmin()
                            best_per_cluster_df = df_best.loc[idx_best]

                            # Gera o relatório
                            print("\n--- Teste: Gerando Relatório Markdown ---")
                            generate_markdown_report(config.OUTPUT_REPORT,
                                                     df_cleaned,
                                                     df_best,
                                                     fitted_pca,
                                                     kmeans_model,
                                                     centroids_df,
                                                     of_stats_df,
                                                     best_per_cluster_df)

                            print("\nTeste do report_generator.py concluído.")
                        else: print("Falha no K-Means, pulando geração do relatório.")
                    else: print("Falha no PCA, pulando geração do relatório.")
                else: print("Falha no escalonamento, pulando geração do relatório.")
            else: print("Falha na seleção de parâmetros, pulando geração do relatório.")
        else: print("Falha na filtragem, pulando geração do relatório.")
    else: print("Falha no carregamento, pulando geração do relatório.")