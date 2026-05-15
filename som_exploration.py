# som_exploration.py

import os
import pandas as pd

import config
from intrasom import SOMFactory
from intrasom.visualization import PlotFactory
from intrasom.clustering import ClusterFactory
import matplotlib.pyplot as plt



def main():
    # ============================================================
    # 1. Carregar matriz já escalada pelo pipeline principal
    # ============================================================

    input_path = os.path.join(config.RESULTS_DIR, "som_input_matrix.csv")

    X = pd.read_csv(input_path, index_col=0)

    component_names = list(X.columns)
    sample_names = list(X.index.astype(str))

    # ============================================================
    # 2. Criar SOM
    # ============================================================

    som = SOMFactory.build(
        data=X.values,
        mapsize=[12, 12],
        mapshape="toroid",
        lattice="hexa",
        normalization=None,
        initialization="random",
        component_names=component_names,
        sample_names=sample_names,
        name="SOM_calibration_inputs",
    )

    # ============================================================
    # 3. Treinar SOM
    # ============================================================

    som.train(
        train_rough_len=50,
        train_finetune_len=200,
        save=True,
        summary=True,
    )


    # ============================================================
    # 4. Salvar tabelas nativas do SOM
    # ============================================================

    results_df = som.results_dataframe
    results_path = os.path.join(config.RESULTS_DIR, "som_results.csv")
    results_df.to_csv(results_path, index=True)

    
    neurons_df = som.neurons_dataframe
    neurons_path = os.path.join(config.RESULTS_DIR, "som_neurons.csv")
    neurons_df.to_csv(neurons_path, index=True)


    # ============================================================
    # 5. Testes com U-matrix nativa
    # ============================================================
    
    # U-matrix nativa sem hits
    som.plot_umatrix(
        figsize=(14, 8),
        hits=False,
        save=True,
        file_name="som_umatrix_native_no_hits",
        file_path=config.RESULTS_DIR,
    )

    # U-matrix nativa com hits usando coluna BMU
    bmu_values = som.results_dataframe["BMU"].values.astype(int)
    som.plot_umatrix(
        figsize=(14, 8),
        hits=True,
        save=True,
        file_name="som_umatrix_native_hits_bmu",
        file_path=config.RESULTS_DIR,
        bmu=(bmu_values,),
    )

    # clusterer = ClusterFactory(som)

    # # Agrupa os neurônios do SOM
    # som_clusters = clusterer.kmeans(
    #     k=5,
    #     init="random",
    #     n_init=50,
    #     max_iter=300,
    # )

    # # Plota o cluster map
    # clusterer.plot_kmeans(
    #     clusters=som_clusters,
    #     figsize=(16, 14),
    #     save=True,
    #     file_name="som_cluster_map_k5",
    #     file_path=config.RESULTS_DIR,
    #     umatrix=True,
    #     hits=True,
    #     cluster_outline=True,
    #     watermark_neurons=False,
    #     colormap="gist_rainbow",
    # )

    # ============================================================
    # 7. Cluster Map nativo do IntraSOM
    # ============================================================

    clusterer = ClusterFactory(som)

    # ------------------------------------------------------------
    # 7.1 Davies-Bouldin para sugerir número de clusters
    # ------------------------------------------------------------

    # clusterer.Davies_Bouldin_analysis(
    #     max_clust=15,
    #     n_iter=100,
    #     min_type="ensamble",
    #     plot=True,
    #     save=True,
    #     verbose=True,
    # )

    # ------------------------------------------------------------
    # 7.2 Cluster maps para diferentes k
    # ------------------------------------------------------------

    for k in [3, 4, 5, 6, 8, 10]:
        som_clusters = clusterer.kmeans(
            k=k,
            init="random",
            n_init=50,
            max_iter=300,
        )

        clusterer.plot_kmeans(
            clusters=som_clusters,
            figsize=(16, 14),
            save=True,
            file_name=f"som_cluster_map_k{k}",
            file_path=config.RESULTS_DIR,
            umatrix=True,
            hits=True,
            cluster_outline=True,
            watermark_neurons=False,
            colormap="gist_rainbow",
        )

        # Tenta salvar/gerar tabela nativa
        cluster_results = clusterer.results_cluster(
            clusters=som_clusters,
            save=True,
            savetype="parquet",
        )

        print(f"\nCluster map SOM gerado para k={k}")
        print(f"Tipo de cluster_results: {type(cluster_results)}")

    # ============================================================
    # Projeções toroidais nativas do IntraSOM
    # ============================================================

    plotter = PlotFactory(som)

    torus_configs = [
        (0.3, 2, False),
        (0.4, 4, False),
        (0.5, 6, False),
        (0.4, 4, True),
    ]

    for inner_out_prop, red_factor, hits in torus_configs:
        print(
            f"\nGerando torus: inner_out_prop={inner_out_prop}, "
            f"red_factor={red_factor}, hits={hits}"
        )

        plotter.plot_torus(
            inner_out_prop=inner_out_prop,
            red_factor=red_factor,
            hits=hits,
        )

        suffix = f"inner{inner_out_prop}_red{red_factor}_hits{hits}"

        out_path = os.path.join(
            config.RESULTS_DIR,
            f"som_toroidal_projection_{suffix}.png"
        )

        plt.savefig(
            out_path,
            dpi=300,
            bbox_inches="tight"
        )

        plt.close()

        print(f"Salvo em: {out_path}")

    # ============================================================
    # 6. Component plots nativos
    # ============================================================

    plotter = PlotFactory(som)

    # Pasta para salvar os component plots
    component_dir = os.path.join(config.RESULTS_DIR, "som_component_plots")
    os.makedirs(component_dir, exist_ok=True)

    # ------------------------------------------------------------
    # 6.1 Teste simples: primeiro componente
    # ------------------------------------------------------------

    plotter.component_plot(
        component_name=0,
        figsize=(10, 10),
        full_title=True,
        save=True,
        file_name="component_000",
        file_path=component_dir,
    )

    # ------------------------------------------------------------
    # 6.2 Gerar component plots para todos os componentes
    # ------------------------------------------------------------

    for i, comp_name in enumerate(component_names):
        safe_name = (
            str(comp_name)
            .replace("/", "_")
            .replace("\\", "_")
            .replace(":", "_")
            .replace("*", "_")
            .replace("?", "_")
            .replace('"', "_")
            .replace("<", "_")
            .replace(">", "_")
            .replace("|", "_")
        )

        plotter.component_plot(
            component_name=i,
            figsize=(10, 10),
            title=comp_name,
            full_title=True,
            save=True,
            file_name=f"component_{i:03d}_{safe_name}",
            file_path=component_dir,
        )

        print(f"  OK: {i} - {comp_name}")


    # ------------------------------------------------------------
    # 6.3 Collage com todos os componentes
    # ------------------------------------------------------------
    plotter.component_plot_collage(
        grid=(4, 4),
        wich="all",
        full_title=True,
        file_path=component_dir,
    )

    # ============================================================
    # 7. Tabela combinada com clusters do pipeline principal
    # ============================================================
    clustered_path = config.OUTPUT_CLUSTER_RESULTS

    if os.path.exists(clustered_path):
        df_clusters = pd.read_excel(clustered_path, index_col=0)
        results_df = som.results_dataframe.copy()

        df_clusters.index = df_clusters.index.astype(str)
        results_df.index = results_df.index.astype(str)

        combined_df = df_clusters.join(
            results_df,
            how="left",
            rsuffix="_SOM",
        )

        combined_path = os.path.join(config.RESULTS_DIR, "som_combined_results.xlsx")
        combined_df.to_excel(combined_path)



if __name__ == "__main__":
    main()