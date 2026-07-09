"""Criação das variáveis derivadas usadas pelos modelos."""

import pandas as pd


def adicionar_features(df: pd.DataFrame) -> pd.DataFrame:
    """Retorna uma cópia do DataFrame com as variáveis derivadas do vinho."""
    df_com_features = df.copy()

    df_com_features["alcohol_density_ratio"] = (
        df_com_features["alcohol"] / df_com_features["density"]
    )
    df_com_features["total_acidity"] = (
        df_com_features["fixed acidity"]
        + df_com_features["volatile acidity"]
        + df_com_features["citric acid"]
    )
    df_com_features["volatile_fixed_ratio"] = (
        df_com_features["volatile acidity"] / df_com_features["fixed acidity"]
    )
    df_com_features["free_total_sulfur_ratio"] = (
        df_com_features["free sulfur dioxide"]
        / df_com_features["total sulfur dioxide"]
    )
    df_com_features["sulphates_chlorides_ratio"] = (
        df_com_features["sulphates"] / df_com_features["chlorides"]
    )
    df_com_features["alcohol_sulphates"] = (
        df_com_features["alcohol"] * df_com_features["sulphates"]
    )
    df_com_features["alcohol_volatile_acidity"] = (
        df_com_features["alcohol"] * df_com_features["volatile acidity"]
    )

    return df_com_features
