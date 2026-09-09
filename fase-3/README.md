# Tech Challenge 3 - State of Data Brasil (AWS + Glue + Athena)

Pipeline de dados para analisar os datasets State of Data Brasil (2023, 2024 e 2025) com arquitetura em camadas no S3 e processamento com AWS Glue (PySpark).

## Objetivo

Construir um fluxo ponta a ponta para:
- ingerir dados brutos (CSV),
- padronizar e harmonizar schemas entre anos,
- gerar camadas analiticas prontas para negocio,
- responder perguntas executivas via Athena,
- suportar visualizacoes em Python.

## Arquitetura

```text
[CSV local ./data]
   -> [S3 Raw]
   -> [Glue Job 1: raw_para_cleansed.py]
   -> [S3 Cleansed/yearly]
   -> [Glue Job 2: cleansed_para_transformed.py]
   -> [S3 Transformed/yearly]
   -> [Glue Job 3: transformed_para_curated.py]
   -> [S3 Curated]
   -> [Glue Data Catalog + Athena]
   -> [Analises e Graficos]
```

## Estrutura do projeto

```text
tech-challenge-3/
  data/
    dataset-2023-2024.csv
    dataset-2024-2025.csv
    dataset-2025-2026.csv
  src/
    raw_para_cleansed.py
    cleansed_para_transformed.py
    transformed_para_curated.py
  notebooks/
    notebook.ipynb
  arquitetura-tech-challenge.drawio
```

## Tecnologias

- AWS S3
- AWS Glue (Spark 3 / Python 3)
- AWS Glue Data Catalog
- Amazon Athena
- Python (boto3, pandas, matplotlib, seaborn)

## Camadas de dados

- Raw: copia fiel dos CSVs de origem.
- Cleansed yearly: limpeza tecnica por ano (nomes de colunas, encoding e vazios de string).
- Transformed yearly: harmonizacao canonica entre anos.
- Curated: agregacoes de negocio prontas para consumo.

## Regras importantes de modelagem

- Unificacao semantica acontece no Transformed/Curated.
- Regra binaria fica centralizada no Transformed:
  - `1` -> `Sim`
  - `0` -> `Nao`
  - vazio/nulo/indefinido -> `N/I`
- Isso preserva rastreabilidade da origem no Raw/Cleansed.

## Perguntas que precisam ser respondidas

- Como está estruturado o mercado brasileiro de Dados?
- Quais perfis profissionais são mais valorizados pelo mercado?
- Qual é o cenário de diversidade de gênero nas carreiras de dados?
- Quais tecnologias apresentam maior adoção entre os profissionais?
- Qual é o índice de adoção de Inteligência Artificial e seu impacto?
- Existem diferenças relevantes entre regiões, senioridades ou modelos de trabalho?
- Quais oportunidades e desafios podem ser identificados para empresas que desejam investir em Dados e Inteligência Artificial?

## Passo a Passo - Data Analytics Pipeline

### Pré-requisitos

- Conta no AWS Academy Lab (fornecida pela pós)
- Python 3.9+ instalado localmente
- AWS CLI instalado
- Bibliotecas: `boto3`, `pandas`, `matplotlib`, `seaborn`

### Configuração AWS

```bash
brew install aws

aws configure
```

Os dados pedidos no momento do `aws configure` estão disponíveis no lab:

Cursos -> Módulos -> AWS Details -> AWS CLI -> Show

### Cria o S3 e cria as pastas

```bash
BUCKET="bucket-tech-challenge-g10"

# Criar o bucket
aws s3 mb s3://$BUCKET --region us-east-1

# Criar as "pastas" (prefixos) para cada camada
aws s3api put-object --bucket $BUCKET --key raw/state-of-data/
aws s3api put-object --bucket $BUCKET --key cleansed/state-of-data/
aws s3api put-object --bucket $BUCKET --key transformed/state-of-data/
aws s3api put-object --bucket $BUCKET --key curated/state-of-data/
aws s3api put-object --bucket $BUCKET --key archives/scripts/
```

### Copia os dados brutos locais para nuvem

```bash
# Subir os 3 arquivos brutos para a Raw
aws s3 cp "<caminho-arquivo-local>" "s3://$BUCKET/raw/state-of-data/"
aws s3 cp "<caminho-arquivo-local>" "s3://$BUCKET/raw/state-of-data/"
aws s3 cp "<caminho-arquivo-local>" "s3://$BUCKET/raw/state-of-data/"

# Verificar se subiu corretamente
aws s3 ls s3://$BUCKET/raw/ --recursive
```

### Subir o arquivo de script no Glue

1. Na console, busque por AWS Glue.
2. Vá em ETL Jobs.
3. Escolha a opção "Script editor".
4. Cole o script na aba dedicada a isso.
5. Configure os detalhes no "Job details", como o S3 onde salvar o script.
6. Após configurar e salvar, rode com o comando:

```bash
aws glue start-job-run \
  --job-name <nome-do-job> \
  --arguments '{"--BUCKET":"<nome-do-bucket>"}' \
  --region <regiao>
```

7. Acompanhe o job na console em "Runs".

### Configure e execute o Crawler

Após rodar o job com sucesso, é necessário configurar e executar o Crawler para que o AWS Glue Catalog catalogue a estrutura da tabela. Ela será necessária para futura adoção do Athena.

Para criar o Crawler, vá na console da AWS e pesquise por "AWS Glue":

1. No menu lateral, na seção "Data Catalog" selecione "Crawlers".
2. Selecione "Create Crawler".
3. Informe o nome desejado e clique em "Next".
4. Em "Data source configuration" selecione a opção "Not Yet".
5. Na sequência clique em "Add a data source" e configure com os dados desejados. No exemplo de criação do curated, selecione a opção S3 e em "S3 path" o caminho da onde estarão os dados do curated.
6. Clique em "Add an S3 data source".
7. Next.
8. Já em IAM Role usaremos a mesma criada automaticamente pela AWS Academy Lab, que é a `LabRole`.
9. Next.
10. Já em "Output configuration", se é a primeira vez que criamos, temos que adicionar um novo database clicando em "Add database". Essa fase é simples e só informamos o nome do banco mantendo o type como `Glue Database`.
11. Next.
12. Revisar e criar.
13. Está pronto o Crawler e é só executar!

> 💡 **NOTA:**
> Ele é sob-demanda, então sempre que rodar um ETL job será necessário rodar o Crawler novamente.

### Criando e configurando AWS Athena

1. No Athena, abra Query editor.
2. Selecione o database criado previamente.
3. Vá em Settings (ou Manage settings).
4. Em Query result location, informe: `s3://bucket-tech-challenge-g10/athena-results/`.
5. Salve.
6. Rode as queries SQL.

## Referencias

- Diagrama: `arquitetura-tech-challenge.drawio`
