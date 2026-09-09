import sys
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql import functions as F

args = getResolvedOptions(sys.argv, ['JOB_NAME', 'BUCKET'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

BUCKET = args['BUCKET']
transformed_path = f"s3://{BUCKET}/transformed/state-of-data/yearly/"
curated_path = f"s3://{BUCKET}/curated/state-of-data/"

# Ler dados da camada Transformed
df = spark.read.parquet(transformed_path)
print(f"Total de registros Transformed: {df.count()}")
print("Colunas disponíveis:", df.columns[:20])

def com_padrao_nao_informado(df_base, coluna):
    return (
        df_base.withColumn(
            coluna,
            F.when(
                F.col(coluna).isNull() | (F.trim(F.col(coluna)) == ''),
                F.lit('N/I')
            ).otherwise(F.col(coluna))
        )
    )

def agregar_dimensao(df_base, coluna, destino):
    if coluna not in df_base.columns:
        print(f"[AVISO] Coluna '{coluna}' nao encontrada. Pulando {destino}.")
        return

    df_agg = (
        com_padrao_nao_informado(df_base, coluna)
        .groupBy('ano_pesquisa', coluna)
        .count()
        .withColumnRenamed('count', 'total')
        .orderBy('ano_pesquisa', F.desc('total'))
    )
    df_agg.write.mode('overwrite').parquet(f"{curated_path}{destino}/")
    print(f"Curated salvo: {curated_path}{destino}/")

def indicador_sim_nao_ni(coluna):
    valor = F.lower(F.trim(F.col(coluna).cast('string')))
    return (
        F.when(valor == 'sim', F.lit(1))
        .when(valor == 'não', F.lit(0))
        .when(valor == 'nao', F.lit(0))
        .otherwise(F.lit(None).cast('int'))
    )

# ---- AGREGAÇÃO 1: Distribuição por cargo ----
agregar_dimensao(df, 'cargo', 'cargos')

# ---- AGREGAÇÃO 2: Faixa salarial por senioridade ----
if 'senioridade' in df.columns and 'faixa_salarial' in df.columns:
    df_salario = (
        com_padrao_nao_informado(df, 'senioridade')
        .transform(lambda x: com_padrao_nao_informado(x, 'faixa_salarial'))
        .groupBy('ano_pesquisa', 'senioridade', 'faixa_salarial')
        .count()
        .withColumnRenamed('count', 'total')
        .orderBy('ano_pesquisa', F.desc('total'))
    )
    df_salario.write.mode('overwrite').parquet(f"{curated_path}salario_senioridade/")
    print(f"Curated salvo: {curated_path}salario_senioridade/")
else:
    print("[AVISO] Colunas 'senioridade' e/ou 'faixa_salarial' ausentes.")

# ---- AGREGAÇÃO 3: Distribuição por gênero ----
agregar_dimensao(df, 'genero', 'genero')

# ---- AGREGAÇÃO 4: Tecnologias mais usadas (Sim/Não/N/I) ----
colunas_tecnologia = [
    'usa_python', 'usa_sql', 'usa_tableau', 'usa_r', 'usa_java', 'usa_javascript',
    'usa_scala', 'usa_julia', 'usa_rust', 'usa_vba', 'usa_dax', 'usa_mysql',
    'usa_postgresql', 'usa_mongodb', 'usa_bigquery', 'usa_redshift', 'usa_athena',
    'usa_snowflake', 'usa_databricks', 'usa_aws', 'usa_gcp', 'usa_azure',
    'usa_powerbi', 'usa_qlik', 'usa_looker', 'usa_metabase', 'usa_grafana',
    'usa_airflow', 'usa_glue', 'usa_fivetran', 'usa_stitch', 'usa_nifi',
    'usa_talend', 'usa_pentaho'
]

existentes_tecnologia = [c for c in colunas_tecnologia if c in df.columns]
if existentes_tecnologia:
    exprs = []
    for c in existentes_tecnologia:
        exprs.append(f"'{c}'")
        exprs.append(f"{c}")

    stack_expr = f"stack({len(existentes_tecnologia)}, {', '.join(exprs)}) as (tecnologia, resposta)"

    df_tec = (
        df.select('ano_pesquisa', F.expr(stack_expr))
        .withColumn(
            'resposta',
            F.when(F.col('resposta').isNull() | (F.trim(F.col('resposta')) == ''), F.lit('N/I'))
            .otherwise(F.col('resposta'))
        )
        .groupBy('ano_pesquisa', 'tecnologia', 'resposta')
        .count()
        .withColumnRenamed('count', 'total')
        .orderBy('ano_pesquisa', 'tecnologia', F.desc('total'))
    )
    df_tec.write.mode('overwrite').parquet(f"{curated_path}tecnologias/")
    print(f"Curated salvo: {curated_path}tecnologias/")
else:
    print('[AVISO] Nenhuma coluna de tecnologia encontrada.')

# ---- AGREGAÇÃO 5: Modelo de trabalho ----
agregar_dimensao(df, 'modelo_trabalho', 'modelo_trabalho')

# ---- AGREGAÇÃO 6: Distribuição por região/UF ----
if 'regiao' in df.columns:
    agregar_dimensao(df, 'regiao', 'regiao')
elif 'uf' in df.columns:
    agregar_dimensao(df, 'uf', 'regiao')
else:
    print("[AVISO] Colunas 'regiao' e 'uf' ausentes.")

# ---- AGREGAÇÃO 7: Adoção de IA (taxa de Sim) ----
colunas_ia = [
    'ia_prioridade_negocio',
    'ia_nao_prioridade',
    'ia_desafio_roi',
    'ia_desafio_dado_pronto'
]

existentes_ia = [c for c in colunas_ia if c in df.columns]
if existentes_ia:
    df_ia_base = df.select('ano_pesquisa', *existentes_ia)

    exprs_ia = []
    for c in existentes_ia:
        exprs_ia.append(f"'{c}'")
        exprs_ia.append(f"{c}")

    stack_ia = f"stack({len(existentes_ia)}, {', '.join(exprs_ia)}) as (indicador_ia, resposta)"

    df_ia = (
        df_ia_base
        .select('ano_pesquisa', F.expr(stack_ia))
        .withColumn('valor_binario', indicador_sim_nao_ni('resposta'))
        .groupBy('ano_pesquisa', 'indicador_ia')
        .agg(
            F.count('valor_binario').alias('total_respostas_validas'),
            F.sum('valor_binario').alias('total_sim')
        )
        .withColumn(
            'pct_sim',
            F.when(
                F.col('total_respostas_validas') > 0,
                F.round((F.col('total_sim') * 100.0) / F.col('total_respostas_validas'), 2)
            ).otherwise(F.lit(None).cast('double'))
        )
        .orderBy('ano_pesquisa', 'indicador_ia')
    )
    df_ia.write.mode('overwrite').parquet(f"{curated_path}adocao_ia/")
    print(f"Curated salvo: {curated_path}adocao_ia/")
else:
    print('[AVISO] Nenhuma coluna de IA encontrada.')

job.commit()
print("Curated layer concluída com sucesso!")