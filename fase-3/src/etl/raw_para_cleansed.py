import ast
import re
import sys
import unicodedata

from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from pyspark.sql import functions as F
from pyspark.sql.functions import udf
from pyspark.sql.types import StringType

args = getResolvedOptions(sys.argv, ["JOB_NAME", "BUCKET"])
sc = SparkContext()
glue_context = GlueContext(sc)
spark = glue_context.spark_session
job = Job(glue_context)
job.init(args["JOB_NAME"], args)

bucket = args["BUCKET"]
arquivos = [
    ("dataset-2023-2024.csv", 2023),
    ("dataset-2024-2025.csv", 2024),
    ("dataset-2025-2026.csv", 2025),
]

def normalizar_coluna(nome: str) -> str:
    nome_original = str(nome)

    # Muitos CSVs desta pesquisa chegam com cabeçalhos no formato:
    # "('P3_a ', 'Qual o número ...')". Mantemos o codigo + descricao
    # para nao perder contexto da pergunta original.
    try:
        tupla = ast.literal_eval(nome_original)
        if isinstance(tupla, tuple) and len(tupla) >= 2:
            codigo = str(tupla[0]).strip()
            descricao = str(tupla[1]).strip()
            nome_original = f"{codigo}_{descricao}" if codigo else descricao
    except Exception:
        pass

    nome_limpo = corrigir_mojibake(nome_original)
    nome_limpo = nome_limpo.lower().strip()
    nome_limpo = nome_limpo.replace(" ", "_").replace("/", "_").replace("-", "_").replace(".", "_")
    nome_limpo = (
        unicodedata.normalize("NFKD", nome_limpo)
        .encode("ascii", "ignore")
        .decode("ascii")
    )
    nome_limpo = re.sub(r"[^a-z0-9_]", "", nome_limpo)
    nome_limpo = re.sub(r"_+", "_", nome_limpo).strip("_")
    return nome_limpo or "coluna_sem_nome"


def normalizar_colunas_unicas(colunas: list[str]) -> list[str]:
    resultado = []
    contagem = {}
    for c in colunas:
        base = normalizar_coluna(c)
        i = contagem.get(base, 0)
        nome_final = base if i == 0 else f"{base}_{i}"
        contagem[base] = i + 1
        resultado.append(nome_final)
    return resultado


def corrigir_mojibake(valor):
    # Corrige textos com encoding quebrado (ex.: 'voc√™' -> 'você').
    # Tenta recodificação em encodings comuns e escolhe a melhor versão.

    if valor is None:
        return None
    if not isinstance(valor, str):
        return valor

    candidatos = [valor]
    for origem in ("latin-1", "cp1252", "mac_roman"):
        try:
            # Conversao estrita evita "comer" caracteres quando a decodificacao falha.
            recodificado = valor.encode(origem).decode("utf-8")
            if recodificado:
                candidatos.append(recodificado)
        except Exception:
            pass

    def score(texto):
        # Penaliza sinais tipicos de mojibake e perda de conteudo.
        ruins = ("√", "Ã", "�", "Â", "¢", "™", "Ð", "�")
        penalidade_ruim = sum(texto.count(ch) for ch in ruins)
        penalidade_tamanho = max(0, len(valor) - len(texto))
        bonus_acentos = sum(texto.count(ch) for ch in "áàâãéêíóôõúçÁÀÂÃÉÊÍÓÔÕÚÇ")
        return (penalidade_ruim + penalidade_tamanho, -bonus_acentos)

    melhor = min(candidatos, key=score)
    return melhor


def normalizar_vazios_string(df):
    # Strings vazias/nulas viram "Não informado".
    colunas_string = [c for c, t in df.dtypes if t == "string"]
    for c in colunas_string:
        df = df.withColumn(
            c,
            F.when(
                F.col(c).isNull() | (F.trim(F.col(c)) == ""),
                F.lit("Não informado"),
            ).otherwise(F.col(c)),
        )
    return df


corrigir_mojibake_udf = udf(corrigir_mojibake, StringType())

dfs_yearly = []

for arquivo, ano_fixo in arquivos:
    caminho = f"s3://{bucket}/raw/state-of-data/{arquivo}"
    print(f"Lendo arquivo: {caminho}")

    df = (
        spark.read.option("header", "true")
        .option("inferSchema", "true")
        .option("sep", ",")
        .option("encoding", "UTF-8")
        .option("quote", '"')
        .option("escape", '"')
        .option("multiLine", "true")
        .csv(caminho)
    )

    df = df.withColumn("ano_pesquisa", F.lit(int(ano_fixo)))

    # Normaliza nomes antes de qualquer operacao para evitar erros com colunas especiais.
    total_colunas_raw = len(df.columns)
    df = df.toDF(*normalizar_colunas_unicas(df.columns))
    print(f"Total de colunas RAW ({ano_fixo}): {total_colunas_raw} | Cleansed: {len(df.columns)}")
    print(f"Primeiras 15 colunas limpas ({ano_fixo}): {df.columns[:15]}")

    # Corrige encoding quebrado para todas as colunas string.
    colunas_string = [c for c, t in df.dtypes if t == "string"]
    for c in colunas_string:
        df = df.withColumn(c, corrigir_mojibake_udf(F.col(c)))

    # Padroniza apenas vazios de colunas string.
    # Regra binaria fica centralizada no passo transformed para evitar duplicidade.
    df = normalizar_vazios_string(df)

    # Limpeza no schema ja padronizado.
    df = df.dropna(how="all").dropDuplicates()

    caminho_yearly = f"s3://{bucket}/cleansed/state-of-data/yearly/ano_pesquisa={ano_fixo}/"
    df.write.mode("overwrite").parquet(caminho_yearly)
    print(f"Cleansed yearly salvo: {caminho_yearly} | registros: {df.count()}")

    dfs_yearly.append(df)

if not dfs_yearly:
    raise RuntimeError("Nenhum dataset foi carregado da camada Raw.")

job.commit()
