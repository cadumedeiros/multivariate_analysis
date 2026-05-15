# main.py

import pandas as pd
import os

import config
import data_loader
import analysis_steps
import clustering
import plotting
import report_generator
import advanced_analysis
import feature_builder



def main():
    """Função principal que executa a análise."""

    # 1. Carregar e Limpar Dados
    df_cleaned = data_loader.load_and_clean_data(config.INPUT_FILE)

    # 2. Filtrar Melhores Modelos
    df_best = analysis_steps.filter_best_models(df_cleaned, 'OF Value', config.BEST_MODEL_PERCENTILE)

    # 3. Selecionar Parâmetros
    X_parameters = analysis_steps.select_parameters(df_best)

    # 4. Construir e Escalonar Dados
    if config.FEATURE_MODE == "multipliers":
        X_input_data = X_parameters.copy()
        X_scaled_data, fitted_scaler = analysis_steps.scale_data(X_input_data)

    elif config.FEATURE_MODE == "curves":
        X_input_data, curve_blocks = feature_builder.build_curve_feature_matrix(
            X_parameters,
            config.PARAM_CURVES_FILE,
            config.PARAMETER_CURVE_MAP,
            time_column=config.CURVE_TIME_COLUMN,
        )

        X_scaled_data, fitted_scaler = feature_builder.block_scale_curve_matrix(
            X_input_data,
            curve_blocks
        )
    
    som_input_path = os.path.join(config.RESULTS_DIR, "som_input_matrix.csv")
    X_scaled_data.to_csv(som_input_path)

    # 5. Aplicar PCA
    X_pca_data, fitted_pca = analysis_steps.apply_pca(X_scaled_data, config.PCA_VARIANCE_THRESHOLD)

    # 6. Determinar k Ótimo (Gerar Gráficos de Análise)
    clustering.plot_elbow_method(X_pca_data, config.K_RANGE, config.PLOT_ELBOW)
    clustering.plot_silhouette_scores(X_pca_data, config.K_RANGE, config.PLOT_SILHOUETTE)

    # 7. Aplicar K-Means
    cluster_labels, kmeans_model = clustering.apply_kmeans(X_pca_data, config.OPTIMAL_K)

    # Adiciona rótulos aos DataFrames relevantes
    df_best['Cluster'] = cluster_labels
    X_scaled_data['Cluster'] = cluster_labels
    X_input_data['Cluster'] = cluster_labels

    # 8. Analisar Clusters
    of_stats_df = clustering.analyze_of_by_cluster(df_best, 'OF Value')

    if config.FEATURE_MODE == "multipliers":
        parameter_columns = [col for col in X_parameters.columns if col != 'Cluster']

        centroids_df = clustering.analyze_clusters(
            df_best,
            X_scaled_data,
            kmeans_model,
            fitted_scaler,
            fitted_pca,
            parameter_columns
        )

    elif config.FEATURE_MODE == "curves":
        X_parameters_for_summary = X_parameters.copy()
        X_parameters_for_summary["Cluster"] = cluster_labels

        centroids_df = X_parameters_for_summary.groupby("Cluster").mean()

    # --- Etapa 9: Análises Avançadas ---
    # 1. Hierarchical Clustering
    hier_clusters = advanced_analysis.hierarchical_clustering(
        X_pca_data,
        max_clusters=config.OPTIMAL_K,
        filename=config.PLOT_DENDROGRAM
    )

    # guarda no df dos melhores
    df_best['Cluster_H'] = hier_clusters

    # 2. Validação
    validation_kmeans = advanced_analysis.validate_clusters(X_pca_data, cluster_labels)
    validation_hier   = advanced_analysis.validate_clusters(X_pca_data, hier_clusters)

    # 3. LDA
    lda_results = advanced_analysis.lda_analysis(
    X_scaled_data.drop(columns=['Cluster']),
    cluster_labels,
    filename=os.path.join(config.RESULTS_DIR, "grafico_coeficientes_LDA.png")
    )

    # 4. ANOVA (OF Value)
    anova_table = advanced_analysis.anova_by_cluster(df_best, 'OF Value')

    # 9. Gerar Gráficos de Visualização
    plotting.plot_of_scatter(df_cleaned, df_best, 'Simulation', 'OF Value', config.PLOT_OF_SCATTER)
    plotting.plot_pca_clusters(X_pca_data, cluster_labels, fitted_pca, config.PLOT_PCA_CLUSTERS)

    X_parameters_plot = X_parameters.copy()
    X_parameters_plot["Cluster"] = cluster_labels

    plotting.plot_parameter_boxplots(
        X_parameters_plot,
        config.PLOT_BOXPLOTS
    )

    # 10. Salvar Resultados Intermediários e Finais (Arquivos Excel)

    # Salva todos os melhores modelos com seus clusters
    df_best_sorted = df_best.sort_values(by=['Cluster', 'OF Value'])
    df_best_sorted.to_excel(config.OUTPUT_CLUSTER_RESULTS)

    # Encontra e salva os melhores de cada cluster
    idx_best = df_best.groupby('Cluster')['OF Value'].idxmin()
    best_per_cluster_df = df_best.loc[idx_best]
    best_per_cluster_df.to_excel(config.OUTPUT_BEST_PER_CLUSTER)

    # 11. Gerar Relatório Final
    report_generator.generate_markdown_report(config.OUTPUT_REPORT,
                                                df_cleaned,
                                                df_best, # Já contém a coluna 'Cluster'
                                                fitted_pca,
                                                kmeans_model, # Passando o modelo kmeans
                                                centroids_df,
                                                of_stats_df,
                                                best_per_cluster_df,
                                                validation_metrics={
                                                "kmeans": validation_kmeans,
                                                "hierarchical": validation_hier
                                            },
                                                lda_results=lda_results,
                                                anova_table=anova_table)


if __name__ == "__main__":
    main()