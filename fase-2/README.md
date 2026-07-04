# Classificação da qualidade de vinhos

Projeto de análise de dados e aprendizado de máquina para classificar vinhos tintos a partir de características físico-químicas.

A variável alvo é `quality_binary`:

- `1`: vinho de alta qualidade (`quality >= 7`);
- `0`: vinho de baixa ou média qualidade (`quality < 7`).

## Estrutura do projeto

```text
.
├── data/
│   └── winequality-red.csv
├── notebooks/
│   └── Notebook_Vinhos.ipynb
├── src/
│   └── README.md
├── results/
│   ├── balanceamento_classes.png
│   └── matriz_correlacao.png
├── requirements.txt
└── README.md
```

## Como executar

Requer Python 3.10 ou superior.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
jupyter lab notebooks/Notebook_Vinhos.ipynb
```

No Windows, ative o ambiente com `.venv\\Scripts\\activate`.

Depois de abrir o notebook, selecione **Executar tudo**. O notebook encontra o dataset automaticamente quando iniciado pela raiz do projeto ou pela pasta `notebooks/`. Os gráficos gerados são salvos em `results/`.

## Etapas presentes no notebook

1. compreensão do problema;
2. análise exploratória dos dados;
3. preparação das variáveis para machine learning.

A coluna `quality` não é usada como entrada do modelo, pois ela origina a variável alvo e causaria vazamento de informação.
