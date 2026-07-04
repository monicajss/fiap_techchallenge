# Classificação da qualidade de vinhos

Este projeto faz parte do Tech Challenge da fase 2 da Pós Tech em Data Analytics da FIAP.

A ideia é usar dados sobre as características dos vinhos para identificar se eles são de alta qualidade ou de baixa/média qualidade.

Para isso, a coluna `quality` foi transformada em uma nova variável chamada `quality_binary`:

- `1` para vinhos com qualidade maior ou igual a 7;
- `0` para vinhos com qualidade menor que 7.

## Sobre a base

A base tem 1.143 registros de vinhos tintos. Entre as informações disponíveis estão acidez, açúcar residual, cloretos, densidade, pH, sulfatos, teor alcoólico e qualidade.

## O que foi feito até agora

- leitura e conferência da base;
- análise exploratória dos dados;
- criação da variável alvo;
- separação das variáveis preditoras em `X` e da variável alvo em `Y`;
- divisão dos dados entre treino e teste, mantendo a proporção das classes.

A próxima etapa é treinar e comparar os modelos de Regressão Logística, Árvore de Decisão, Random Forest e SVM.

## Organização das pastas

- `data/`: base de dados utilizada;
- `notebooks/`: notebook com a análise;
- `results/`: gráficos gerados durante a análise;
- `src/`: espaço para scripts auxiliares;
- `requirements.txt`: bibliotecas necessárias para rodar o projeto.

## Como rodar

Na pasta `fase-2`, instale as bibliotecas:

```bash
pip install -r requirements.txt
```

Depois, abra o notebook:

```bash
jupyter lab notebooks/Notebook_Vinhos.ipynb
```

Com o notebook aberto, basta executar as células na ordem. Os gráficos serão salvos automaticamente na pasta `results/`.
