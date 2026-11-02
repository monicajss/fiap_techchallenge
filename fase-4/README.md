# Tech Challenge — Fase 4 | Amazon Product Performance & Customer Insights

## Contexto e objetivo

Esta etapa explora dados de produtos da Amazon para organizar informações sobre categorias, preços, descontos, engajamento e satisfação dos consumidores. O objetivo é preparar uma base que apoie decisões de negócio e a elaboração posterior do dashboard no Power BI.

## Fonte dos dados

Foi utilizado o dataset [Amazon Sales Dataset, no Kaggle](https://www.kaggle.com/datasets/karkavelrajaj/amazon-sales-dataset), publicado por KARKAVELRAJA J. A página do dataset informa a licença [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)](https://creativecommons.org/licenses/by-nc-sa/4.0/). O uso e a redistribuição dos arquivos devem respeitar essa licença, incluindo atribuição, indicação das alterações e compartilhamento de adaptações sob os mesmos termos.

## Tecnologias utilizadas

- Python e pandas para leitura, exploração, tratamento e validação dos dados.
- Jupyter Notebook para documentar e executar as etapas de análise.
- Power BI como ferramenta prevista para a construção do dashboard na próxima etapa.

## Etapas desenvolvidas

1. Importação da base e exploração inicial.
2. Identificação dos tipos de dados e dos valores ausentes.
3. Tratamento de preços, descontos e avaliações.
4. Separação dos níveis da hierarquia de categorias.
5. Validação de faixas, quantidade de registros e identificador técnico.
6. Exportação da base tratada e do dicionário para uso no Power BI.

## Resultados do tratamento

- 1.465 registros preservados.
- 22 colunas na base tratada.
- 1.351 valores distintos de `product_id`.
- `record_id` único para identificar cada linha da fonte.
- Arquivo CSV tratado exportado em UTF-8 com BOM.
- Base original preservada em `data/raw/amazon.csv`.

## Limitações

- Há `product_id` repetidos. Eles foram preservados porque alguns grupos apresentam diferenças em atributos; os indicadores de produtos devem considerar IDs distintos quando apropriado.
- `rating_count` representa contagens associadas aos registros e não deve ser somado indiscriminadamente, especialmente diante de `product_id` repetidos.
- Títulos e comentários permanecem agrupados por produto. Como a vírgula também aparece dentro dos textos, não é seguro interpretar cada trecho como uma avaliação individual.
- A avaliação inválida foi mantida como nula, assim como as contagens ausentes.

## Estrutura do projeto

```text
fase-4/
├── README.md
├── data/
│   ├── raw/
│   │   └── amazon.csv
│   └── processed/
│       ├── amazon_powerbi.csv
│       └── dicionario_dados_amazon.csv
├── notebooks/
│   └── 01_exploracao_tipos_dados_amazon.ipynb
└── powerbi/
    └── README.md
```

- `data/raw/`: arquivo original recebido do Kaggle, preservado sem alterações.
- `data/processed/`: base tratada e dicionário de dados.
- `notebooks/`: notebook de exploração, preparação e validação.
- `powerbi/`: espaço reservado para o dashboard, ainda em desenvolvimento.

## Como executar

A partir da pasta `fase-4`, instale as dependências mínimas e abra o notebook:

```bash
python -m pip install pandas notebook
jupyter notebook notebooks/01_exploracao_tipos_dados_amazon.ipynb
```

Execute as células em ordem. A pasta `data/processed/` é criada automaticamente, se necessário, e recebe os arquivos tratados ao final da validação.

## Power BI

`data/processed/amazon_powerbi.csv` é a fonte preparada para o dashboard. O arquivo `data/processed/dicionario_dados_amazon.csv` descreve as colunas, seus tipos recomendados e os tratamentos realizados. A construção das visualizações, dos insights e das recomendações de negócio será desenvolvida pelo integrante responsável pelo Power BI.
