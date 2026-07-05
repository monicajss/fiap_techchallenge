# Classificação da qualidade de vinhos

Este projeto faz parte do Tech Challenge da fase 2 da Pós Tech em Data Analytics da FIAP.

A ideia é usar dados sobre as características dos vinhos para identificar se eles são de alta qualidade ou de baixa/média qualidade.

Para isso, a coluna `quality` foi transformada em uma nova variável chamada `quality_binary`:

- `1` para vinhos com qualidade maior ou igual a 7;
- `0` para vinhos com qualidade menor que 7.

## Sobre a base

A base tem 1.143 registros de vinhos tintos. Entre as informações disponíveis estão acidez, açúcar residual, cloretos, densidade, pH, sulfatos, teor alcoólico e qualidade.

Fonte: [Wine Quality Dataset, no Kaggle](https://www.kaggle.com/datasets/yasserh/wine-quality-dataset).

## Etapas do Projeto

- **Leitura e conferência** da base de dados;
- **Análise exploratória** dos dados (EDA) e mapeamento de correlações;
- **Engenharia de recursos** para criação da variável alvo binária;
- **Preparação e divisão dos dados** entre treino e teste mantendo a proporção das classes;
- **Treinamento, ajuste e comparação** dos modelos de Machine Learning (Regressão Logística, Árvore de Decisão, Random Forest e SVM).

## Resultados do torneio de modelos

Os modelos foram avaliados no conjunto de testes com os seguintes resultados:

| Modelo de Classificação          | Acurácia Geral | Precisão (Classe 1) | Recall (Classe 1) | F1-Score (Classe 1) | ROC-AUC Estatístico |
| :--------------------------------- | :--------------: | :------------------: | :---------------: | :-----------------: | :------------------: |
| **1. Regressão Logística** |      79,91%      |        37,93%        |      68,75%      |       0,4889       |        0,8504        |
| **2. Árvore de Decisão**   |      80,35%      |        39,68%        | **78,12%** |       0,5263       |        0,8258        |
| **3. Random Forest**         | **86,03%** |   **50,00%**   |      68,75%      |  **0,5789**  |        0,8688        |
| **4. SVM (Kernel RBF)**      |      81,66%      |        41,07%        |      71,88%      |       0,5227       |   **0,8696**   |

### Modelo recomendado para validação: Random Forest

O modelo de **Random Forest (Floresta Aleatória)** é o candidato recomendado para a próxima etapa de validação. No conjunto de teste, ele apresentou a maior Acurácia Geral (86,03%), o maior F1-Score (0,5789) e reduziu os falsos positivos para 22. Esses resultados indicam o melhor equilíbrio prático entre os modelos avaliados, mas ainda devem ser confirmados com novos dados antes de uma aplicação em produção.

## Organização das pastas

- `data/`: base de dados utilizada;
- `notebooks/`: notebook com a análise;
- `results/`: gráficos e tabela de métricas gerados durante a análise;
- `src/`: espaço para scripts auxiliares;
- `requirements.txt`: bibliotecas necessárias para rodar o projeto.

## Como rodar

Na raiz do projeto, instale as bibliotecas:

```bash
pip install -r requirements.txt
```

Depois, abra o notebook:

```bash
jupyter lab notebooks/Notebook_Vinhos.ipynb
```

Com o notebook aberto, basta executar as células na ordem. Os gráficos serão salvos automaticamente na pasta `results/`.
