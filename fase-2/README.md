# Classificação da qualidade de vinhos

Este projeto faz parte do Tech Challenge da fase 2 da Pós Tech em Data Analytics da FIAP.

A ideia é usar dados sobre as características dos vinhos para identificar se eles são de alta qualidade ou de baixa/média qualidade.

Para isso, a coluna `quality` foi transformada em uma nova variável chamada `quality_binary`:

- `1` para vinhos com qualidade maior ou igual a 7;
- `0` para vinhos com qualidade menor que 7.

## Tecnologias utilizadas

Para o desenvolvimento deste projeto, foram utilizadas as seguintes ferramentas e bibliotecas listadas no `requirements.txt`:

- **Análise e Manipulação de Dados:** Pandas (v3.0.3) e NumPy (v2.4.4)
- **Visualização de Dados:** Matplotlib (v3.10.9) e Seaborn (v0.13.2)
- **Machine Learning e Métricas:** Scikit-Learn (v1.8.0)
- **Ambiente de Execução Interativa:** JupyterLab (v4.6.1)

## Sobre a base

A base tem 1.143 registros de vinhos tintos. Entre as informações disponíveis estão acidez, açúcar residual, cloretos, densidade, pH, sulfatos, teor alcoólico e qualidade.

Fonte: [Wine Quality Dataset, no Kaggle](https://www.kaggle.com/datasets/yasserh/wine-quality-dataset).

## Etapas do projeto

- **Leitura e conferência** da base de dados;
- **Análise exploratória** dos dados (EDA) e mapeamento de correlações;
- **Engenharia de recursos** para criação da variável alvo binária;
- **Preparação e divisão dos dados** entre treino e teste mantendo a proporção das classes;
- **Treinamento, ajuste e comparação** dos modelos de Machine Learning (Regressão Logística, Árvore de Decisão, Random Forest e SVM).

## Resultados dos modelos

Os modelos foram avaliados no conjunto de teste com os seguintes resultados:

| Modelo de Classificação       | Acurácia Geral | Precision Classe Alta | Recall Classe Alta | F1-Score Classe Alta |     ROC-AUC     |
| :------------------------------ | :--------------: | :-------------------: | :----------------: | :------------------: | :--------------: |
| **Regressão Logística** |      78,60%      |        35,59%        |       65,62%       |        46,15%        |      87,01%      |
| **Árvore de Decisão**   |      79,91%      |        39,39%        |  **81,25%**  |        53,06%        |      82,35%      |
| **Random Forest**         | **91,70%** |   **76,00%**   |       59,38%       |   **66,67%**   | **90,43%** |
| **SVM com RBF**           |      81,66%      |        40,74%        |       68,75%       |        51,16%        |      86,62%      |

## Modelo recomendado: Random Forest

O modelo recomendado é o **Random Forest**, pois apresentou o melhor desempenho geral entre os modelos avaliados.

Ele obteve:

- **Acurácia geral:** 91,70%;
- **Precision da classe Alta:** 76,00%;
- **Recall da classe Alta:** 59,38%;
- **F1-score da classe Alta:** 66,67%;
- **ROC-AUC:** 90,43%.

Apesar de a Árvore de Decisão ter apresentado o maior recall para a classe Alta, o Random Forest teve melhor equilíbrio geral, com maior acurácia, maior precision, maior F1-score e maior ROC-AUC.

Isso indica que o modelo foi mais seletivo: ele deixou de identificar parte dos vinhos realmente classificados como alta qualidade, mas quando classificou um vinho como Alta, teve uma taxa de acerto superior aos demais modelos.

## Organização do projeto

A estrutura do projeto foi organizada da seguinte forma:

- `data/`: base de dados utilizada no projeto;
- `notebooks/`: notebook principal com análise e modelagem;
  - `Notebook_Vinhos.ipynb`;
- `results/`: resultados gerados durante a análise;
  - `metricas_modelos.csv`: tabela final com as métricas dos modelos;
  - `distribuicao_histogramas.png`: gráficos de distribuição das variáveis;
  - `matriz_correlacao.png`: heatmap da matriz de correlação;
  - `balanceamento_classes.png`: gráfico de balanceamento da variável alvo;
  - `analise_outliers_boxplots.png`: boxplots para análise de outliers;
  - `regressao_logistica_outputs.png` plot do modelo de regresão logistica;
  - `arvore_decisao_outputs.png`plot do modelo da árvore de decisão ;
  - `floresta_aleatoria_outputs.png`plot do modelo da floresta aleatória;
  - `svm_rbf_outputs.png`plot do modelo de RVM;
- `src/`: scripts auxiliares utilizados no notebook;
  - `__init__.py`;
  - `avaliacao_metricas.py`: funções auxiliares para avaliação e exportação de métricas;
  - `feature_engineering.py`: funções para criação de novas variáveis;
  - `README.md`;
- `.gitignore`: arquivos e pastas ignorados pelo Git;
- `README.md`: documentação principal do projeto;
- `requirements.txt`: bibliotecas necessárias para execução.

## Organização das pastas

- `data/`: base de dados utilizada;
- `notebooks/`: notebook com a análise;
- `results/`: gráficos e tabela de métricas gerados durante a análise;
- `src/`: espaço para scripts auxiliares;
- `requirements.txt`: bibliotecas necessárias para rodar o projeto.

## Como executar

Na raiz do projeto, instale as bibliotecas:

```bash
pip install -r requirements.txt
```
