"""Cálculo e exibição da matriz de confusão dos modelos."""

from typing import Any

import numpy as np
from sklearn.metrics import classification_report, confusion_matrix


def exibir_matriz_confusao(y_real: Any, y_predito: Any) -> np.ndarray:
    """Exibe a matriz e o relatório de classificação e retorna a matriz."""
    matriz = confusion_matrix(y_real, y_predito)

    print("\n=== MATRIZ DE CONFUSÃO ===")
    print(matriz)

    print("\n=== RELATÓRIO DE CLASSIFICAÇÃO ===")
    print(classification_report(y_real, y_predito, zero_division=0))

    return matriz
