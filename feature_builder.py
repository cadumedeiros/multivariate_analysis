# feature_builder.py
"""
Modos principais:
1. multiplicadores puros: já feito pelo pipeline original;
2. curvas reais multiplicadas: multiplicador x curva base;
3. normalização por bloco de parâmetro.
"""

import numpy as np
import pandas as pd


def load_base_curves(curves_file, time_column="Time"):
    """
    Carrega as curvas base dos parâmetros.

    Args:
        curves_file (str): caminho do arquivo Excel com as curvas.
        time_column (str): nome da coluna de tempo.

    Returns:
        pd.DataFrame: DataFrame com as curvas, ordenado pelo tempo.
    """
    curves_df = pd.read_excel(curves_file)

    curves_df = curves_df.sort_values(by=time_column).reset_index(drop=True)

    return curves_df


def build_curve_feature_matrix(
    multipliers_df,
    curves_file,
    parameter_curve_map,
    time_column="Time",
):
    """
    Constrói a matriz de entrada usando:
    
        curva_modelo(t) = multiplicador_modelo * curva_base(t)

    Cada ponto temporal vira uma coluna.

    Args:
        multipliers_df (pd.DataFrame): DataFrame com multiplicadores dos modelos.
        curves_file (str): arquivo Excel com curvas base.
        parameter_curve_map (dict): mapeia coluna de multiplicador -> coluna da curva.
        time_column (str): coluna de tempo.

    Returns:
        tuple:
            - X_curves (pd.DataFrame): matriz modelo x variáveis temporais.
            - curve_blocks (dict): dicionário com colunas pertencentes a cada parâmetro.
    """
    curves_df = load_base_curves(curves_file, time_column=time_column)

    features = {}
    curve_blocks = {}

    for multiplier_col, curve_col in parameter_curve_map.items():

        base_curve = curves_df[curve_col].to_numpy(dtype=float)
        times = curves_df[time_column].to_numpy()

        block_cols = []

        for idx, time_value in enumerate(times):
            col_name = f"{multiplier_col}__t_{time_value}"

            features[col_name] = multipliers_df[multiplier_col].to_numpy(dtype=float) * base_curve[idx]
            block_cols.append(col_name)

        curve_blocks[multiplier_col] = block_cols

    X_curves = pd.DataFrame(features, index=multipliers_df.index)

    return X_curves, curve_blocks


def block_scale_curve_matrix(X_curves, curve_blocks, eps=1e-12):
    """
    Normaliza a matriz por bloco de parâmetro.

    A ideia é:
    - centralizar as colunas de cada bloco;
    - dividir o bloco por uma escala global;
    - evitar que parâmetros com magnitude maior ou mais pontos temporais dominem o PCA.

    Args:
        X_curves (pd.DataFrame): matriz modelo x curvas discretizadas.
        curve_blocks (dict): colunas pertencentes a cada parâmetro.
        eps (float): valor pequeno para evitar divisão por zero.

    Returns:
        tuple:
            - X_scaled_df (pd.DataFrame): matriz escalada por bloco.
            - block_scaler (dict): informações para rastrear a escala usada.
    """
    X_scaled = pd.DataFrame(index=X_curves.index)
    block_scaler = {}

    for block_name, cols in curve_blocks.items():
        block = X_curves[cols].copy()

        # Centraliza cada coluna temporal
        block_mean = block.mean(axis=0)
        block_centered = block - block_mean

        # Escala global do bloco
        # Soma das variâncias das colunas do bloco
        block_scale = np.sqrt(block_centered.var(axis=0, ddof=1).sum())

        if block_scale < eps:
            print(f"[AVISO] Bloco '{block_name}' tem variância quase zero. Usando escala 1.")
            block_scale = 1.0

        block_scaled = block_centered / block_scale

        X_scaled[cols] = block_scaled

        block_scaler[block_name] = {
            "columns": cols,
            "mean": block_mean,
            "scale": block_scale,
        }

    print(f"Matriz escalada por bloco. Shape: {X_scaled.shape}")

    return X_scaled, block_scaler


def summarize_curves_by_cluster(X_curves, cluster_labels, curve_blocks):
    """
    Calcula curvas médias por cluster para cada parâmetro.

    Isso ajuda a interpretar os grupos depois do k-means.

    Args:
        X_curves (pd.DataFrame): matriz original de curvas multiplicadas.
        cluster_labels (array-like): rótulos dos clusters.
        curve_blocks (dict): colunas de cada parâmetro.

    Returns:
        dict: médias por cluster e por parâmetro.
    """
    df = X_curves.copy()
    df["Cluster"] = cluster_labels

    summaries = {}

    for block_name, cols in curve_blocks.items():
        summaries[block_name] = df.groupby("Cluster")[cols].mean()

    return summaries