"""Cálculo e exibição das métricas dos modelos de classificação."""

from typing import Any

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


def avaliar_modelo(y_real: Any, y_predito: Any, y_probabilidade: Any) -> dict[str, float]:
    """Calcula, exibe e retorna as principais métricas de classificação."""
    metricas = {
        "acuracia": accuracy_score(y_real, y_predito),
        "precisao": precision_score(y_real, y_predito, zero_division=0),
        "recall": recall_score(y_real, y_predito, zero_division=0),
        "f1_score": f1_score(y_real, y_predito, zero_division=0),
        "roc_auc": roc_auc_score(y_real, y_probabilidade),
    }

    print(f"Acurácia: {metricas['acuracia']:.4f}")
    print(f"Precisão: {metricas['precisao']:.4f}")
    print(f"Recall:   {metricas['recall']:.4f}")
    print(f"F1-Score: {metricas['f1_score']:.4f}")
    print(f"ROC-AUC: {metricas['roc_auc']:.4f}")

    print("\nClassification Report:")
    print(
        classification_report(
            y_real,
            y_predito,
            target_names=["Baixa/Média", "Alta"],
            zero_division=0,
        )
    )

    return metricas
