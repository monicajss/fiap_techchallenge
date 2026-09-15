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
entrada_yearly = f"s3://{BUCKET}/cleansed/state-of-data/yearly/"
saida = f"s3://{BUCKET}/transformed/state-of-data/yearly/"

# Evita erro de merge de schema lendo ano a ano e unindo com unionByName.
# Alguns campos mudam de tipo entre anos (ex.: int em um ano e string em outro).
anos = [2023, 2024, 2025]
dfs = []

for ano in anos:
    caminho_ano = f"{entrada_yearly}ano_pesquisa={ano}/"
    df_ano = spark.read.parquet(caminho_ano)

    # Padroniza todas as colunas (exceto particao) como string para harmonizar tipos.
    for c in df_ano.columns:
        if c != 'ano_pesquisa':
            df_ano = df_ano.withColumn(c, F.col(c).cast('string'))

    df_ano = df_ano.withColumn('ano_pesquisa', F.lit(int(ano)))
    dfs.append(df_ano)

df = dfs[0]
for df_ano in dfs[1:]:
    df = df.unionByName(df_ano, allowMissingColumns=True)

print(f"Lendo entrada yearly por particao: {entrada_yearly}")

# Mapeamento robusto com base nas colunas reais do catálogo (2023, 2024 e 2025).
# A ideia é mapear nomes explícitos e também usar fallback por padrões,
# pois o crawler pode gerar variações entre anos.
def selecionar_candidatas(candidatas_explicitas, termos=None):
    existentes = [c for c in candidatas_explicitas if c in df.columns]

    if termos:
        for c in df.columns:
            c_lower = c.lower()
            if all(t in c_lower for t in termos):
                existentes.append(c)

    # Remove duplicadas preservando ordem.
    existentes_unicas = []
    for c in existentes:
        if c not in existentes_unicas:
            existentes_unicas.append(c)
    return existentes_unicas

def coalesce_cols(candidatas, tipo='string', termos=None):
    nomes = selecionar_candidatas(candidatas, termos=termos)
    existentes = [F.col(c) for c in nomes]
    if not existentes:
        return F.lit(None).cast(tipo)
    return F.coalesce(*existentes).cast(tipo)

# Padroniza colunas binarias (0/1) para Sim/Nao/N/I e normaliza valores nulos.
def indicador_binario(candidatas, termos=None):
    existentes = selecionar_candidatas(candidatas, termos=termos)
    if not existentes:
        return F.lit('N/I')

    valores = []
    for c in existentes:
        valor = F.lower(F.trim(F.col(c).cast('string')))
        valores.append(
            F.when(
                valor.isin('1', 'true', 'sim', 'yes'),
                F.lit(1)
            )
            .when(
                valor.isin('0', 'false', 'nao', 'não', 'no'),
                F.lit(0)
            )
            .otherwise(F.lit(None).cast('int'))
        )

    combinado = valores[0] if len(valores) == 1 else F.greatest(*valores)

    return (
        F.when(combinado == 1, F.lit('Sim'))
        .when(combinado == 0, F.lit('Não'))
        .otherwise(F.lit('N/I'))
    )

# Campos canônicos para responder as perguntas do desafio.
df_harmonized = (
    df
    .withColumn('genero', coalesce_cols([
        'p1_b_genero',
        '1_b_genero'
    ], termos=['genero']))
    .withColumn('cargo', coalesce_cols([
        'p2_f_cargo_atual',
        '2_f_cargo_atual'
    ], termos=['cargo', 'atual']))
    .withColumn('senioridade', coalesce_cols([
        'p2_g_nivel',
        '2_g_nivel',
    ], termos=['senioridade']))
    .withColumn('faixa_salarial', coalesce_cols([
        'p2_h_faixa_salarial',
        '2_h_faixa_salarial'
    ], termos=['faixa', 'salarial']))
    .withColumn('setor', coalesce_cols([
        'p2_b_setor',
        '2_b_setor'
    ], termos=['setor']))
    .withColumn('mudar_emprego_6m', coalesce_cols([
        'p2_n_voce_pretende_mudar_de_emprego_nos_proximos_6_meses',
        '2_n_planos_de_mudar_de_emprego_6m'
    ], termos=['mudar', 'emprego']))
    .withColumn('criterios_escolha_emprego', coalesce_cols([
        'p2_o_quais_os_principais_criterios_que_voce_leva_em_consideracao_no_momento_de_decidir_onde_trabalhar',
        '2_o_criterios_para_escolha_de_emprego'
    ], termos=['criterios', 'escolha', 'emprego']))
    .withColumn('motivo_escolha_salario', indicador_binario([
        'p2_o_1_remuneracao_salario',
        '2_o_1_remuneracao_salario'
    ], termos=['remuneracao', 'salario']))
    .withColumn('motivo_escolha_beneficios', indicador_binario([
        'p2_o_2_beneficios',
        '2_o_2_beneficios'
    ], termos=['beneficios']))
    .withColumn('motivo_escolha_flex_remoto', indicador_binario([
        'p2_o_4_flexibilidade_de_trabalho_remoto',
        '2_o_4_flexibilidade_de_trabalho_remoto'
    ], termos=['flexibilidade', 'remoto']))
    .withColumn('motivo_escolha_crescimento', indicador_binario([
        'p2_o_7_plano_de_carreira_e_oportunidades_de_crescimento_profissional',
        '2_o_7_plano_de_carreira_e_oportunidades_de_crescimento'
    ], termos=['plano_de_carreira', 'crescimento']))
    .withColumn('uf', coalesce_cols([
        'p1_i_1_uf_onde_mora',
        '1_i_1_uf_onde_mora'
    ], termos=['uf', 'mora']))
    .withColumn('regiao', coalesce_cols([
        'p1_i_2_regiao_onde_mora',
        '1_i_2_regiao_onde_mora'
    ], termos=['regiao', 'mora']))
    .withColumn('modelo_trabalho', coalesce_cols([
        'p2_r_atualmente_qual_a_sua_forma_de_trabalho',
        'p1_r_modelo_de_trabalho_atual',
        '2_r_modelo_de_trabalho_atual',
        '2_q_modelo_de_trabalho_atual',
    ], termos=['modelo', 'trabalho', 'atual']))
    .withColumn('tamanho_time_dados', coalesce_cols([
        'p3_a_qual_o_numero_aproximado_de_pessoas_que_atuam_com_dados_na_sua_empresa_hoje',
        '3_a_numero_aproximado_de_pessoas_no_time_de_dados',
        '3_a_numero_de_pessoas_em_dados'
    ], termos=['numero', 'pessoas', 'dados']))
    .withColumn('usa_python', indicador_binario([
        'p4_d_3_python',
        '4_d_3_python',
        '4_c_3_python',
    ], termos=['python']))
    .withColumn('usa_sql', indicador_binario([
        'p4_d_1_sql',
        '4_d_1_sql',
        '4_c_1_sql',
    ], termos=['sql']))
    .withColumn('usa_tableau', indicador_binario([
        'p4_j_3_tableau',
        '4_j_3_tableau',
        '4_g_3_tableau',
    ], termos=['tableau']))
    # Tecnologias binarias (0/1): padronizacao entre 2023, 2024 e 2025.
    .withColumn('usa_r', indicador_binario([
        'p4_d_2_r',
        '4_d_2_r',
        '4_c_2_r'
    ]))
    .withColumn('usa_java', indicador_binario([
        'p4_d_6_java',
        '4_d_6_java'
    ], termos=['java']))
    .withColumn('usa_javascript', indicador_binario([
        'p4_d_14_javascript',
        '4_d_14_javascript'
    ], termos=['javascript']))
    .withColumn('usa_scala', indicador_binario([
        'p4_d_10_scala',
        '4_d_10_scala',
        '4_c_7_scala'
    ], termos=['scala']))
    .withColumn('usa_julia', indicador_binario([
        'p4_d_7_julia',
        '4_d_7_julia',
        '4_c_5_julia'
    ], termos=['julia']))
    .withColumn('usa_rust', indicador_binario([
        'p4_d_12_rust',
        '4_d_12_rust',
        '4_c_9_rust'
    ], termos=['rust']))
    .withColumn('usa_vba', indicador_binario([
        'p4_d_9_visual_basic_vba',
        '4_d_9_visual_basic_vba',
        '4_c_6_visual_basic_vba'
    ], termos=['visual_basic_vba']))
    .withColumn('usa_dax', indicador_binario([
        '4_c_8_dax'
    ], termos=['dax']))
    .withColumn('usa_mysql', indicador_binario([
        'p4_g_1_mysql',
        '4_g_1_mysql',
        '4_d_1_mysql'
    ], termos=['mysql']))
    .withColumn('usa_postgresql', indicador_binario([
        'p4_g_12_postgresql',
        '4_g_12_postgresql',
        '4_d_12_postgresql'
    ], termos=['postgresql']))
    .withColumn('usa_mongodb', indicador_binario([
        'p4_g_8_mongodb',
        '4_g_8_mongodb',
        '4_d_8_mongodb'
    ], termos=['mongodb']))
    .withColumn('usa_bigquery', indicador_binario([
        'p4_g_22_google_bigquery',
        '4_g_22_google_bigquery',
        '4_d_22_google_bigquery'
    ], termos=['bigquery']))
    .withColumn('usa_redshift', indicador_binario([
        'p4_g_24_amazon_redshift',
        '4_g_24_amazon_redshift',
        '4_d_24_amazon_redshift'
    ], termos=['redshift']))
    .withColumn('usa_athena', indicador_binario([
        'p4_g_25_amazon_athena',
        '4_g_25_amazon_athena',
        '4_d_25_amazon_athena'
    ], termos=['athena']))
    .withColumn('usa_snowflake', indicador_binario([
        'p4_g_26_snowflake',
        '4_g_26_snowflake',
        '4_d_26_snowflake'
    ], termos=['snowflake']))
    .withColumn('usa_databricks', indicador_binario([
        'p4_g_27_databricks',
        '4_g_27_databricks',
        '4_d_27_databricks',
        'p6_b_20_databricks',
        '6_b_20_databricks',
        'p7_b_20_databricks',
        '7_b_20_databricks'
    ], termos=['databricks']))
    .withColumn('usa_aws', indicador_binario([
        'p4_h_2_amazon_web_services_aws',
        '4_h_1_amazon_web_services_aws',
        '4_e_1_amazon_web_services_aws'
    ], termos=['amazon_web_services_aws']))
    .withColumn('usa_gcp', indicador_binario([
        'p4_h_3_google_cloud_gcp',
        '4_h_2_google_cloud_gcp',
        '4_e_2_google_cloud_gcp'
    ], termos=['google_cloud_gcp']))
    .withColumn('usa_azure', indicador_binario([
        'p4_h_1_azure_microsoft',
        '4_h_3_azure_microsoft',
        '4_e_3_azure_microsoft'
    ], termos=['azure_microsoft']))
    .withColumn('usa_powerbi', indicador_binario([
        'p4_j_1_microsoft_powerbi',
        '4_j_1_microsoft_powerbi',
        '4_g_1_microsoft_powerbi'
    ], termos=['powerbi']))
    .withColumn('usa_qlik', indicador_binario([
        'p4_j_2_qlik_view_qlik_sense',
        '4_j_2_qlik_view_qlik_sense',
        '4_g_2_qlik_view_qlik_sense'
    ], termos=['qlik']))
    .withColumn('usa_looker', indicador_binario([
        'p4_j_7_looker',
        '4_j_7_looker',
        '4_g_7_looker'
    ], termos=['looker']))
    .withColumn('usa_metabase', indicador_binario([
        'p4_j_4_metabase',
        '4_j_4_metabase',
        '4_g_4_metabase'
    ], termos=['metabase']))
    .withColumn('usa_grafana', indicador_binario([
        'p4_j_19_grafana',
        '4_j_15_grafana',
        '4_g_15_grafana'
    ], termos=['grafana']))
    .withColumn('usa_airflow', indicador_binario([
        'p6_b_3_apache_airflow',
        '6_b_3_apache_airflow',
        'p7_b_3_apache_airflow',
        '7_b_3_apache_airflow'
    ], termos=['airflow']))
    .withColumn('usa_glue', indicador_binario([
        'p6_b_6_aws_glue',
        '6_b_6_aws_glue',
        'p7_b_6_aws_glue',
        '7_b_6_aws_glue'
    ], termos=['aws_glue']))
    .withColumn('usa_fivetran', indicador_binario([
        'p6_b_11_fivetran',
        '6_b_11_fivetran',
        'p7_b_11_fivetran',
        '7_b_11_fivetran'
    ], termos=['fivetran']))
    .withColumn('usa_stitch', indicador_binario([
        'p6_b_10_stitch',
        '6_b_10_stitch',
        'p7_b_10_stitch',
        '7_b_10_stitch'
    ], termos=['stitch']))
    .withColumn('usa_nifi', indicador_binario([
        'p6_b_4_apache_nifi',
        '6_b_4_apache_nifi',
        'p7_b_4_apache_nifi',
        '7_b_4_apache_nifi'
    ], termos=['nifi']))
    .withColumn('usa_talend', indicador_binario([
        'p6_b_7_talend',
        '6_b_7_talend',
        'p7_b_7_talend',
        '7_b_7_talend'
    ], termos=['talend']))
    .withColumn('usa_pentaho', indicador_binario([
        'p6_b_8_pentaho',
        '6_b_8_pentaho',
        'p7_b_8_pentaho',
        '7_b_8_pentaho'
    ], termos=['pentaho']))
    .withColumn('ia_prioridade_negocio', indicador_binario([
        '3_e_ai_generativa_e_llm_e_uma_prioridade',
        'p3_f_6_ia_generativa_e_llms_como_principal_frente_do_negocio',
        '3_f_6_ia_generativa_e_llms_como_principal_frente_do_negocio',
        '4_i_6_ia_generativa_e_llms_como_principal_frente_do_negocio',
        'p4_l_6_ia_generativa_e_llms_como_principal_frente_do_negocio',
        '4_l_6_ia_generativa_e_llms_como_principal_frente_do_negocio'
    ], termos=['ia', 'prioridade']))
    .withColumn('ia_nao_prioridade', indicador_binario([
        'p3_f_7_ia_generativa_e_llms_nao_e_prioridade',
        '3_f_7_ia_generativa_e_llms_nao_e_prioridade',
        '4_i_7_ia_generativa_e_llms_nao_e_prioridade',
        'p4_l_7_ia_generativa_e_llms_nao_e_prioridade',
        '4_l_7_ia_generativa_e_llms_nao_e_prioridade'
    ], termos=['ia', 'nao_e_prioridade']))
    .withColumn('ia_desafio_roi', indicador_binario([
        'p3_g_5_retorno_sobre_investimento_roi_nao_comprovado_de_ia_generativa',
        '3_g_5_retorno_sobre_investimento_roi_nao_comprovado_de_ia_generativa',
        '3_h_5_retorno_sobre_investimento_roi_nao_comprovado_de_ia_generativa'
    ], termos=['roi']))
    .withColumn('ia_desafio_time_dados_pronto_para_ia', indicador_binario([
        'p3_g_6_dados_da_empresa_nao_estao_prontos_para_uso_de_ia_generativa',
        '3_g_6_dados_da_empresa_nao_estao_prontos_para_uso_de_ia_generativa',
        '3_h_6_dados_da_empresa_nao_estao_prontos_para_uso_de_ia_generativa'
    ], termos=['dados_da_empresa', 'nao_estao_prontos']))
    .withColumn('ia_motivo_falta_compreensao', indicador_binario([
        'p3_g_1_falta_de_compreensao_dos_casos_de_uso',
        '3_g_1_falta_de_compreensao_dos_casos_de_uso',
        '3_h_1_falta_de_compreensao_dos_casos_de_uso'
    ], termos=['compreensao', 'casos_de_uso']))
    .withColumn('ia_motivo_falta_confiabilidade', indicador_binario([
        'p3_g_2_falta_de_confiabilidade_das_saidas_alucinacao_dos_modelos',
        '3_g_2_falta_de_confiabilidade_das_saidas_alucinacao_dos_modelos',
        '3_h_2_falta_de_confiabilidade_das_saidas_alucinacao_dos_modelos'
    ], termos=['confiabilidade', 'alucinacao']))
    .withColumn('ia_motivo_incerteza_regulacao', indicador_binario([
        'p3_g_3_incerteza_em_relacao_a_regulamentacao',
        '3_g_3_incerteza_em_relacao_a_regulamentacao',
        '3_h_3_incerteza_em_relacao_a_regulamentacao'
    ], termos=['incerteza', 'regulamentacao']))
    .withColumn('ia_motivo_seguranca_privacidade', indicador_binario([
        'p3_g_4_preocupacoes_com_seguranca_e_privacidade_de_dados',
        '3_g_4_preocupacoes_com_seguranca_e_privacidade_de_dados',
        '3_h_4_preocupacoes_com_seguranca_e_privacidade_de_dados'
    ], termos=['seguranca', 'privacidade']))
    .withColumn('ia_motivo_falta_expertise', indicador_binario([
        'p3_g_7_falta_de_expertise_ou_falta_de_recursos',
        '3_g_7_falta_de_expertise_ou_falta_de_recursos',
        '3_h_7_falta_de_expertise_ou_falta_de_recursos'
    ], termos=['expertise', 'recursos']))
    .withColumn('ia_motivo_alta_direcao_nao_ve_valor', indicador_binario([
        'p3_g_8_alta_direcao_da_empresa_nao_ve_valor_ou_nao_ve_como_prioridade',
        '3_g_8_alta_direcao_da_empresa_nao_ve_valor_ou_nao_ve_como_prioridade',
        '3_h_8_alta_direcao_da_empresa_nao_ve_valor_ou_nao_ve_como_prioridade'
    ], termos=['alta_direcao', 'valor']))
    .withColumn('ia_motivo_propriedade_intelectual', indicador_binario([
        'p3_g_9_preocupacoes_com_propriedade_intelectual',
        '3_g_9_preocupacoes_com_propriedade_intelectual',
        '3_h_9_preocupacoes_com_propriedade_intelectual'
    ], termos=['propriedade_intelectual']))
)

colunas_finais = [
    'ano_pesquisa',
    'genero',
    'cargo',
    'senioridade',
    'faixa_salarial',
    'setor',
    'mudar_emprego_6m',
    'criterios_escolha_emprego',
    'motivo_escolha_salario',
    'motivo_escolha_beneficios',
    'motivo_escolha_flex_remoto',
    'motivo_escolha_crescimento',
    'uf',
    'regiao',
    'modelo_trabalho',
    'tamanho_time_dados',
    'usa_python',
    'usa_sql',
    'usa_tableau',
    'usa_r',
    'usa_java',
    'usa_javascript',
    'usa_scala',
    'usa_julia',
    'usa_rust',
    'usa_vba',
    'usa_dax',
    'usa_mysql',
    'usa_postgresql',
    'usa_mongodb',
    'usa_bigquery',
    'usa_redshift',
    'usa_athena',
    'usa_snowflake',
    'usa_databricks',
    'usa_aws',
    'usa_gcp',
    'usa_azure',
    'usa_powerbi',
    'usa_qlik',
    'usa_looker',
    'usa_metabase',
    'usa_grafana',
    'usa_airflow',
    'usa_glue',
    'usa_fivetran',
    'usa_stitch',
    'usa_nifi',
    'usa_talend',
    'usa_pentaho',
    'ia_prioridade_negocio',
    'ia_nao_prioridade',
    'ia_desafio_roi',
    'ia_desafio_time_dados_pronto_para_ia',
    'ia_motivo_falta_compreensao',
    'ia_motivo_falta_confiabilidade',
    'ia_motivo_incerteza_regulacao',
    'ia_motivo_seguranca_privacidade',
    'ia_motivo_falta_expertise',
    'ia_motivo_alta_direcao_nao_ve_valor',
    'ia_motivo_propriedade_intelectual'
]

df_harmonized = df_harmonized.select(*colunas_finais)
df_harmonized.write.mode('overwrite').partitionBy('ano_pesquisa').parquet(saida)

job.commit()