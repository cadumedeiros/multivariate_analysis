# som_diagnostics.py

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import config


# Ajuste se, no seu caso, maior OF for melhor.
# Normalmente, em função objetivo de calibração, menor OF é melhor.
LOWER_OF_IS_BETTER = True


PARAM_COLUMNS = [
    "S1Supply0",
    "S2Supply0",
    "Carbo_GrainsProdvsTime",
    "Carbo_MudProdvsTime",
    "Carbo_RudProdvsTime",
    "LutitesProdvsTime",
]


def load_som_combined():
    path = os.path.join(config.RESULTS_DIR, "som_combined_results.xlsx")

    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Arquivo não encontrado: {path}\n"
            "Rode primeiro som_exploration.py para gerar som_combined_results.xlsx."
        )

    df = pd.read_excel(path, index_col=0)

    print("\n--- Arquivo carregado ---")
    print(path)
    print(df.shape)
    print(df.head())
    print("\nColunas:")
    print(list(df.columns))

    required = ["BMU", "Ret_x", "Ret_y", "q-error", "Udist", "Cluster", "OF Value"]

    for col in required:
        if col not in df.columns:
            raise ValueError(f"Coluna obrigatória ausente: {col}")

    return df


def summarize_bmus(df):
    print("\n--- Resumo por BMU ---")

    agg_dict = {
        "BMU": "size",
        "Ret_x": "first",
        "Ret_y": "first",
        "Udist": "mean",
        "q-error": "mean",
        "OF Value": ["mean", "min", "max"],
    }

    bmu_summary = df.groupby("BMU").agg(agg_dict)

    bmu_summary.columns = [
        "hits",
        "Ret_x",
        "Ret_y",
        "Udist_mean",
        "qerror_mean",
        "OF_mean",
        "OF_min",
        "OF_max",
    ]

    bmu_summary = bmu_summary.sort_values("hits", ascending=False)

    out_path = os.path.join(config.RESULTS_DIR, "som_bmu_summary.xlsx")
    bmu_summary.to_excel(out_path)

    print(bmu_summary.head(20))
    print(f"\nResumo por BMU salvo em: {out_path}")

    return bmu_summary


def assign_regions(df):
    """
    Divide o SOM em regiões simples usando Ret_x e Ret_y.

    Você pode ajustar os limites depois olhando a U-matrix.
    """

    xmax = df["Ret_x"].max()
    ymax = df["Ret_y"].max()

    x_low = xmax / 3
    x_high = 2 * xmax / 3

    y_low = ymax / 3
    y_high = 2 * ymax / 3

    def region(row):
        x = row["Ret_x"]
        y = row["Ret_y"]

        if x >= x_high and y >= y_high:
            return "topo_direita"
        elif x >= x_high and y <= y_low:
            return "base_direita"
        elif x <= x_low and y >= y_high:
            return "topo_esquerda"
        elif x <= x_low and y <= y_low:
            return "base_esquerda"
        elif x_low < x < x_high and y_low < y < y_high:
            return "centro"
        elif x >= x_high:
            return "direita"
        elif x <= x_low:
            return "esquerda"
        elif y >= y_high:
            return "topo"
        elif y <= y_low:
            return "base"
        else:
            return "intermediaria"

    df = df.copy()
    df["SOM_Region"] = df.apply(region, axis=1)

    return df


def summarize_regions(df):
    print("\n--- Resumo por região SOM ---")

    available_params = [c for c in PARAM_COLUMNS if c in df.columns]

    summary_mean = df.groupby("SOM_Region")[available_params + ["OF Value", "Udist", "q-error"]].mean()
    summary_median = df.groupby("SOM_Region")[available_params + ["OF Value", "Udist", "q-error"]].median()
    counts = df.groupby("SOM_Region").size().rename("n_modelos")

    cluster_counts = pd.crosstab(df["SOM_Region"], df["Cluster"])

    out_path = os.path.join(config.RESULTS_DIR, "som_region_summary.xlsx")

    with pd.ExcelWriter(out_path) as writer:
        counts.to_excel(writer, sheet_name="counts")
        summary_mean.to_excel(writer, sheet_name="mean")
        summary_median.to_excel(writer, sheet_name="median")
        cluster_counts.to_excel(writer, sheet_name="cluster_counts")

    print("\nModelos por região:")
    print(counts)

    print("\nMédias por região:")
    print(summary_mean)

    print("\nClusters por região:")
    print(cluster_counts)

    print(f"\nResumo por região salvo em: {out_path}")

    return summary_mean, cluster_counts


def summarize_hot_cold_udist(df):
    """
    Compara modelos em regiões de alta Udist e baixa Udist.
    Alta Udist = regiões de maior contraste local.
    Baixa Udist = regiões mais homogêneas.
    """

    print("\n--- Comparação entre alta e baixa Udist ---")

    available_params = [c for c in PARAM_COLUMNS if c in df.columns]

    q80 = df["Udist"].quantile(0.80)
    q20 = df["Udist"].quantile(0.20)

    df = df.copy()

    df["Udist_Class"] = "intermediaria"
    df.loc[df["Udist"] >= q80, "Udist_Class"] = "alta_Udist"
    df.loc[df["Udist"] <= q20, "Udist_Class"] = "baixa_Udist"

    comparison = df.groupby("Udist_Class")[available_params + ["OF Value", "q-error"]].mean()
    counts = df.groupby("Udist_Class").size().rename("n_modelos")

    out_path = os.path.join(config.RESULTS_DIR, "som_udist_hot_cold_summary.xlsx")

    with pd.ExcelWriter(out_path) as writer:
        counts.to_excel(writer, sheet_name="counts")
        comparison.to_excel(writer, sheet_name="mean")

    print("\nModelos por classe Udist:")
    print(counts)

    print("\nMédias por classe Udist:")
    print(comparison)

    print(f"\nResumo alta/baixa Udist salvo em: {out_path}")

    return df


def save_best_models_by_region(df):
    print("\n--- Melhores modelos por região SOM ---")

    if LOWER_OF_IS_BETTER:
        best = df.sort_values("OF Value", ascending=True).groupby("SOM_Region").head(5)
    else:
        best = df.sort_values("OF Value", ascending=False).groupby("SOM_Region").head(5)

    cols = [
        "SOM_Region",
        "Cluster",
        "BMU",
        "Ret_x",
        "Ret_y",
        "OF Value",
        "q-error",
        "Udist",
    ]

    cols += [c for c in PARAM_COLUMNS if c in df.columns]

    out_path = os.path.join(config.RESULTS_DIR, "som_best_models_by_region.xlsx")
    best[cols].to_excel(out_path)

    print(best[cols].head(30))
    print(f"\nMelhores modelos por região salvos em: {out_path}")


def test_native_umatrix_labels(som, df, n_labels=10):
    """
    Testa U-matrix nativa com labels de alguns modelos.
    Seleciona os melhores modelos por OF Value.
    """

    print("\n--- Testando U-matrix nativa com labels ---")

    if "OF Value" not in df.columns:
        print("Coluna 'OF Value' não encontrada. Pulando labels.")
        return

    # menor OF = melhor, ajuste se seu caso for o contrário
    selected_names = (
        df.sort_values("OF Value", ascending=True)
        .head(n_labels)
        .index.astype(str)
        .tolist()
    )

    print("Modelos selecionados para label:")
    print(selected_names)

    sample_names = list(som.results_dataframe.index.astype(str))

    selected_indices = [
        sample_names.index(name)
        for name in selected_names
        if name in sample_names
    ]

    print("Índices encontrados:")
    print(selected_indices)

    if not selected_indices:
        print("Nenhum índice encontrado para labels. Verifique nomes das simulações.")
        return

    som.plot_umatrix(
        figsize=(16, 9),
        hits=True,
        save=True,
        file_name="diag_umatrix_07_labeled_best_OF",
        file_path=config.RESULTS_DIR,
        bmu=som.results_dataframe["BMU"].values,
        label_plot=True,
        samples_label=True,
        samples_label_index=selected_indices,
        samples_label_fontsize=8,
    )



def main():
    df = load_som_combined()

    summarize_bmus(df)

    df = assign_regions(df)

    # salva dataframe com regiões
    region_labeled_path = os.path.join(config.RESULTS_DIR, "som_combined_results_with_regions.xlsx")
    df.to_excel(region_labeled_path)
    print(f"\nTabela com regiões salva em: {region_labeled_path}")

    summarize_regions(df)
    df = summarize_hot_cold_udist(df)


    save_best_models_by_region(df)



if __name__ == "__main__":
    main()