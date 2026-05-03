# Olist Analise de Receita por UF

Projeto de analise exploratoria de receita a partir da base publica da Olist, com foco em consolidacao de pedidos, clientes e itens do pedido para gerar visualizacoes por UF.

## Objetivo

Este projeto organiza parte da base da Olist para responder perguntas como:

- qual e a receita total por estado;
- quais UFs concentram maior participacao na receita;
- qual e o ticket medio por UF;
- como apresentar esses dados em graficos mais claros para analise e apresentacao.

## Estrutura do projeto

```text
Olist_Analise_Receita/
├── data/
│   ├── external/
│   │   ├── olist_customers_dataset.csv
│   │   ├── olist_order_items_dataset.csv
│   │   └── olist_orders_dataset.csv
│   └── processed/
│       ├── dados.xlsx
│       └── pedidos_clientes.xlsx
├── src/
│   ├── data/
│   │   └── clean_data.py
│   └── visualization/
│       ├── analise.py
│       ├── analise_mapa_top10.py
│       ├── comparativo_estados_2017_2018.py
│       ├── salvar_graficos.py
│       └── images/
│           ├── comparativo_receita_2017_2018.png
│           ├── receita_por_uf.png
│           └── mapa_receita_top10.png
└── README.md
```

## O que cada script faz

### `src/data/clean_data.py`

- lê os arquivos brutos em `data/external/`;
- calcula a receita por pedido com base na coluna `price` dos itens;
- cruza pedidos com clientes;
- gera uma base consolidada por pedido para analise de receita;
- limpa nomes de colunas e remove duplicatas com `pyjanitor`;
- converte colunas de data para formato de data;
- exporta os arquivos processados em `data/processed/`.

Arquivos gerados:

- `data/processed/dados.xlsx`
- `data/processed/pedidos_clientes.xlsx`

### `src/visualization/analise.py`

Cria um grafico de barras de receita por UF com:

- paleta de cores refinada;
- destaque visual para a media da receita;
- valores abreviados em mil e milhao;
- periodo analisado;
- total de receita consolidada.

Ao final da execucao, o grafico tambem e salvo automaticamente em `src/visualization/images/`.

### `src/visualization/analise_mapa_top10.py`

Cria uma visualizacao combinada com:

- mapa coropletico do Brasil por UF;
- siglas das UFs sobre o mapa;
- tabela lateral com top 10 estados por receita;
- ticket medio por UF;
- participacao percentual na receita;
- periodo analisado.

Observacao: esse script busca online um arquivo GeoJSON dos estados do Brasil em tempo de execucao.

Ao final da execucao, o mapa tambem e salvo automaticamente em `src/visualization/images/`.

### `src/visualization/comparativo_estados_2017_2018.py`

Cria uma tabela visual comparando a receita por UF entre 2017 e 2018, com foco em variacao de consumo.

Essa visualizacao mostra:

- top 5 aumentos de receita entre 2017 e 2018;
- top 5 quedas de receita no mesmo periodo;
- receita abreviada por ano;
- variacao percentual com indicador visual de subida ou descida.

Ao final da execucao, a tabela tambem e salva automaticamente em `src/visualization/images/`.

### `src/visualization/salvar_graficos.py`

Arquivo utilitario responsavel por salvar os graficos gerados em alta resolucao dentro da pasta `src/visualization/images/`.

## Requisitos

Recomenda-se Python 3.11 ou superior.

Bibliotecas utilizadas no projeto:

- pandas
- matplotlib
- seaborn
- pyjanitor
- openpyxl

## Instalacao

No terminal, a partir da raiz do projeto:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install pandas matplotlib seaborn pyjanitor openpyxl
```

## Como executar

### 1. Preparar os dados

Entre na pasta do script de tratamento:

```bash
cd src\data
python clean_data.py
```

### 2. Gerar o grafico de barras

```bash
cd ..\visualization
python analise.py
```

Arquivo salvo automaticamente:

- `src/visualization/images/receita_por_uf.png`

### 3. Gerar o mapa com top 10

```bash
cd ..\visualization
python analise_mapa_top10.py
```

Arquivo salvo automaticamente:

- `src/visualization/images/mapa_receita_top10.png`

### 4. Gerar a tabela comparativa entre 2017 e 2018

```bash
cd ..\visualization
python comparativo_estados_2017_2018.py
```

Arquivo salvo automaticamente:

- `src/visualization/images/comparativo_receita_2017_2018.png`

## Base utilizada

O projeto utiliza arquivos da base publica da Olist colocados manualmente em `data/external/`.

Arquivos esperados:

- `olist_customers_dataset.csv`
- `olist_order_items_dataset.csv`
- `olist_orders_dataset.csv`

Observacao: a receita consolidada atual e calculada a partir da soma da coluna `price` dos itens por `order_id`.

## Principais metricas

As visualizacoes usam principalmente estas metricas:

- `receita_uf`: soma de `price` por estado;
- `pedidos`: quantidade de pedidos unicos por UF;
- `ticket_medio`: receita total dividida pela quantidade de pedidos;
- `participacao_receita`: peso percentual da UF sobre a receita total.