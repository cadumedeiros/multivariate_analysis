# main.py
"""
Importa e executa funções dos módulos:
- config: Carrega configurações.
- data_loader: Carrega e limpa os dados.
- analysis_steps: Filtra, seleciona parâmetros, escala e aplica PCA.
- clustering: Determina k, aplica K-Means, analisa clusters.
- plotting: Gera os gráficos da análise.
- report_generator: Cria o relatório final em Markdown.
"""

import config
import data_loader
import analysis_steps
import clustering
import plotting
import report_generator
import pandas as pd # Necessário para salvar arquivos Excel aqui

def main():
    """Função principal que executa a análise."""

    # 1. Carregar e Limpar Dados
    print("\n--- Etapa 1: Carregando e Limpando Dados ---")
    df_cleaned = data_loader.load_and_clean_data(config.INPUT_FILE)

    # 2. Filtrar Melhores Modelos
    print("\n--- Etapa 2: Filtrando Melhores Modelos ---")
    df_best = analysis_steps.filter_best_models(df_cleaned, 'OF Value', config.BEST_MODEL_PERCENTILE)

    # 3. Selecionar Parâmetros
    print("\n--- Etapa 3: Selecionando Parâmetros ---")
    X_parameters = analysis_steps.select_parameters(df_best)

    # 4. Escalonar Dados
    print("\n--- Etapa 4: Escalonando Dados ---")
    X_scaled_data, fitted_scaler = analysis_steps.scale_data(X_parameters)

    # 5. Aplicar PCA
    print("\n--- Etapa 5: Aplicando PCA ---")
    X_pca_data, fitted_pca = analysis_steps.apply_pca(X_scaled_data, config.PCA_VARIANCE_THRESHOLD)

    # 6. Determinar k Ótimo (Gerar Gráficos de Análise)
    print("\n--- Etapa 6: Gerando Gráficos para Determinar k ---")
    clustering.plot_elbow_method(X_pca_data, config.K_RANGE, config.PLOT_ELBOW)
    clustering.plot_silhouette_scores(X_pca_data, config.K_RANGE, config.PLOT_SILHOUETTE)
    # Nota: A escolha de OPTIMAL_K é feita manualmente no config.py

    # 7. Aplicar K-Means
    print("\n--- Etapa 7: Aplicando K-Means ---")
    cluster_labels, kmeans_model = clustering.apply_kmeans(X_pca_data, config.OPTIMAL_K)

    # Adiciona rótulos aos DataFrames relevantes
    df_best['Cluster'] = cluster_labels
    X_scaled_data['Cluster'] = cluster_labels # Adicionado ao escalado também
    X_parameters['Cluster'] = cluster_labels  # Adicionado ao original (não escalado)

    # 8. Analisar Clusters
    print("\n--- Etapa 8: Analisando Clusters ---")
    parameter_columns = [col for col in X_parameters.columns if col != 'Cluster'] # Nomes originais
    centroids_df = clustering.analyze_clusters(df_best, X_scaled_data, kmeans_model, fitted_scaler, fitted_pca, parameter_columns)
    of_stats_df = clustering.analyze_of_by_cluster(df_best, 'OF Value')

    # 9. Gerar Gráficos de Visualização
    print("\n--- Etapa 9: Gerando Gráficos de Visualização ---")
    plotting.plot_of_scatter(df_cleaned, df_best, 'Simulation', 'OF Value', config.PLOT_OF_SCATTER)
    plotting.plot_pca_clusters(X_pca_data, cluster_labels, fitted_pca, config.PLOT_PCA_CLUSTERS)
    plotting.plot_parameter_boxplots(X_parameters, config.PLOT_BOXPLOTS) # Usa X_parameters original com 'Cluster'

    # 10. Salvar Resultados Intermediários e Finais (Arquivos Excel)
    print("\n--- Etapa 10: Salvando Resultados em Excel ---")
    # Salva todos os melhores modelos com seus clusters
    df_best_sorted = df_best.sort_values(by=['Cluster', 'OF Value'])
    df_best_sorted.to_excel(config.OUTPUT_CLUSTER_RESULTS)
    print(f"  - DataFrame com clusters salvo em '{config.OUTPUT_CLUSTER_RESULTS}'")

    # Encontra e salva os melhores de cada cluster
    idx_best = df_best.groupby('Cluster')['OF Value'].idxmin()
    best_per_cluster_df = df_best.loc[idx_best]
    best_per_cluster_df.to_excel(config.OUTPUT_BEST_PER_CLUSTER)
    print(f"  - Melhores modelos por cluster salvos em '{config.OUTPUT_BEST_PER_CLUSTER}'")

    # 11. Gerar Relatório Final
    print("\n--- Etapa 11: Gerando Relatório Markdown ---")
    report_generator.generate_markdown_report(config.OUTPUT_REPORT,
                                                df_cleaned,
                                                df_best, # Já contém a coluna 'Cluster'
                                                fitted_pca,
                                                kmeans_model, # Passando o modelo kmeans
                                                centroids_df,
                                                of_stats_df,
                                                best_per_cluster_df)

    print("\n--- Pipeline de Análise de Calibração Concluído ---")

# --- Ponto de Entrada do Script ---
# Este código só será executado se você rodar este arquivo diretamente (python main.py)
if __name__ == "__main__":
    main()