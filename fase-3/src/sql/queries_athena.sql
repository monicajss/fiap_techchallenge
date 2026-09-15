-- ==============================================================================
-- 1) Como está estruturado o mercado brasileiro de Dados?
-- ==============================================================================

-- 1.1) Distribuição de Cargo e Senioridade ao longo dos anos
SELECT 
    ano_pesquisa,
    COALESCE(NULLIF(TRIM(cargo), ''), 'N/I') AS cargo,
    COALESCE(NULLIF(TRIM(senioridade), ''), 'N/I') AS senioridade,
    COUNT(*) AS total_profissionais,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(PARTITION BY ano_pesquisa), 2) AS pct_do_ano
FROM db_state_of_data.yearly
GROUP BY 
    ano_pesquisa,
    COALESCE(NULLIF(TRIM(cargo), ''), 'N/I'),
    COALESCE(NULLIF(TRIM(senioridade), ''), 'N/I')
ORDER BY 
    ano_pesquisa, 
    total_profissionais DESC;

-- 1.2) Distribuição de Profissionais por Setor de Atuação da Empresa
SELECT 
    ano_pesquisa,
    COALESCE(NULLIF(TRIM(setor), ''), 'N/I') AS setor,
    COUNT(*) AS total_profissionais,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(PARTITION BY ano_pesquisa), 2) AS pct_do_ano
FROM db_state_of_data.yearly
GROUP BY 
    ano_pesquisa,
    COALESCE(NULLIF(TRIM(setor), ''), 'N/I')
ORDER BY 
    ano_pesquisa, 
    total_profissionais DESC;

-- 1.3) Tamanho do Time de Dados nas Empresas
SELECT 
    ano_pesquisa,
    COALESCE(NULLIF(TRIM(tamanho_time_dados), ''), 'N/I') AS tamanho_time_dados,
    COUNT(*) AS total_empresas_respondentes,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(PARTITION BY ano_pesquisa), 2) AS pct_do_ano
FROM db_state_of_data.yearly
GROUP BY 
    ano_pesquisa,
    COALESCE(NULLIF(TRIM(tamanho_time_dados), ''), 'N/I')
ORDER BY 
    ano_pesquisa, 
    total_empresas_respondentes DESC;

-- ==============================================================================
-- 2) Quais perfis profissionais são mais valorizados pelo mercado?
-- ==============================================================================

WITH base AS (
    SELECT
        ano_pesquisa,
        cargo,
        senioridade,
        faixa_salarial,
        TRY_CAST(
            REPLACE(
                REGEXP_EXTRACT(
                    faixa_salarial,
                    '([0-9][0-9.]*)',
                    1
                ),
                '.',
                ''
            ) AS BIGINT
        ) AS salario_inicial
    FROM db_state_of_data.yearly
    WHERE faixa_salarial IS NOT NULL
      AND LOWER(faixa_salarial) NOT IN ('n/i', 'não informado', 'nao informado')
)
SELECT
    ano_pesquisa,
    cargo,
    senioridade,
    faixa_salarial,
    salario_inicial,
    COUNT(*) AS total_profissionais,
    ROUND(
        100.0 * COUNT(*)
        / SUM(COUNT(*)) OVER (PARTITION BY ano_pesquisa),
        2
    ) AS pct_no_ano
FROM base
WHERE salario_inicial IS NOT NULL
GROUP BY
    ano_pesquisa,
    cargo,
    senioridade,
    faixa_salarial,
    salario_inicial
ORDER BY
    ano_pesquisa,
    salario_inicial DESC,
    total_profissionais DESC;

-- ==============================================================================
-- 3) Qual é o cenário de diversidade de gênero nas carreiras de dados?
-- ==============================================================================

-- 3.1) Proporção Geral de Gênero por Ano
SELECT 
    ano_pesquisa,
    COALESCE(NULLIF(TRIM(genero), ''), 'N/I') AS genero,
    COUNT(*) AS total,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(PARTITION BY ano_pesquisa), 2) AS pct_genero
FROM db_state_of_data.yearly
GROUP BY 
    ano_pesquisa,
    COALESCE(NULLIF(TRIM(genero), ''), 'N/I')
ORDER BY 
    ano_pesquisa, 
    total DESC;

-- 3.2) Cruzamento Gênero x Cargo x Senioridade x Faixa Salarial
SELECT 
    ano_pesquisa,
    COALESCE(NULLIF(TRIM(cargo), ''), 'N/I') AS cargo,
    COALESCE(NULLIF(TRIM(senioridade), ''), 'N/I') AS senioridade,
    COALESCE(NULLIF(TRIM(genero), ''), 'N/I') AS genero,
    COALESCE(NULLIF(TRIM(faixa_salarial), ''), 'N/I') AS faixa_salarial,
    COUNT(*) AS total_respondentes,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(PARTITION BY ano_pesquisa, COALESCE(NULLIF(TRIM(cargo), ''), 'N/I'), COALESCE(NULLIF(TRIM(senioridade), ''), 'N/I')), 2) AS pct_dentro_do_nivel
FROM db_state_of_data.yearly
WHERE COALESCE(NULLIF(TRIM(genero), ''), 'N/I') IN ('Feminino', 'Masculino')
GROUP BY 
    ano_pesquisa,
    COALESCE(NULLIF(TRIM(cargo), ''), 'N/I'),
    COALESCE(NULLIF(TRIM(senioridade), ''), 'N/I'),
    COALESCE(NULLIF(TRIM(genero), ''), 'N/I'),
    COALESCE(NULLIF(TRIM(faixa_salarial), ''), 'N/I')
ORDER BY 
    ano_pesquisa,
    cargo,
    senioridade,
    genero,
    total_respondentes DESC;

-- ==============================================================================
-- 4) Quais tecnologias apresentam maior adoção entre os profissionais?
-- ==============================================================================

WITH tec_unpivot AS (
    SELECT ano_pesquisa, 'Linguagens' AS categoria, 'Python' AS tecnologia, usa_python AS usa FROM db_state_of_data.yearly UNION ALL
    SELECT ano_pesquisa, 'Linguagens', 'SQL', usa_sql FROM db_state_of_data.yearly UNION ALL
    SELECT ano_pesquisa, 'Linguagens', 'R', usa_r FROM db_state_of_data.yearly UNION ALL
    SELECT ano_pesquisa, 'Linguagens', 'Java', usa_java FROM db_state_of_data.yearly UNION ALL
    SELECT ano_pesquisa, 'Linguagens', 'JavaScript', usa_javascript FROM db_state_of_data.yearly UNION ALL
    SELECT ano_pesquisa, 'Linguagens', 'Scala', usa_scala FROM db_state_of_data.yearly UNION ALL
    SELECT ano_pesquisa, 'Linguagens', 'Julia', usa_julia FROM db_state_of_data.yearly UNION ALL
    SELECT ano_pesquisa, 'Linguagens', 'Rust', usa_rust FROM db_state_of_data.yearly UNION ALL
    SELECT ano_pesquisa, 'Linguagens', 'VBA', usa_vba FROM db_state_of_data.yearly UNION ALL
    SELECT ano_pesquisa, 'Linguagens', 'DAX', usa_dax FROM db_state_of_data.yearly UNION ALL

    SELECT ano_pesquisa, 'Bancos / Warehouses', 'MySQL', usa_mysql FROM db_state_of_data.yearly UNION ALL
    SELECT ano_pesquisa, 'Bancos / Warehouses', 'PostgreSQL', usa_postgresql FROM db_state_of_data.yearly UNION ALL
    SELECT ano_pesquisa, 'Bancos / Warehouses', 'MongoDB', usa_mongodb FROM db_state_of_data.yearly UNION ALL
    SELECT ano_pesquisa, 'Bancos / Warehouses', 'BigQuery', usa_bigquery FROM db_state_of_data.yearly UNION ALL
    SELECT ano_pesquisa, 'Bancos / Warehouses', 'Redshift', usa_redshift FROM db_state_of_data.yearly UNION ALL
    SELECT ano_pesquisa, 'Bancos / Warehouses', 'Athena', usa_athena FROM db_state_of_data.yearly UNION ALL
    SELECT ano_pesquisa, 'Bancos / Warehouses', 'Snowflake', usa_snowflake FROM db_state_of_data.yearly UNION ALL
    SELECT ano_pesquisa, 'Bancos / Warehouses', 'Databricks', usa_databricks FROM db_state_of_data.yearly UNION ALL

    SELECT ano_pesquisa, 'Cloud Providers', 'AWS', usa_aws FROM db_state_of_data.yearly UNION ALL
    SELECT ano_pesquisa, 'Cloud Providers', 'GCP', usa_gcp FROM db_state_of_data.yearly UNION ALL
    SELECT ano_pesquisa, 'Cloud Providers', 'Azure', usa_azure FROM db_state_of_data.yearly UNION ALL

    SELECT ano_pesquisa, 'BI & Visualização', 'PowerBI', usa_powerbi FROM db_state_of_data.yearly UNION ALL
    SELECT ano_pesquisa, 'BI & Visualização', 'Tableau', usa_tableau FROM db_state_of_data.yearly UNION ALL
    SELECT ano_pesquisa, 'BI & Visualização', 'Qlik', usa_qlik FROM db_state_of_data.yearly UNION ALL
    SELECT ano_pesquisa, 'BI & Visualização', 'Looker', usa_looker FROM db_state_of_data.yearly UNION ALL
    SELECT ano_pesquisa, 'BI & Visualização', 'Metabase', usa_metabase FROM db_state_of_data.yearly UNION ALL
    SELECT ano_pesquisa, 'BI & Visualização', 'Grafana', usa_grafana FROM db_state_of_data.yearly UNION ALL

    SELECT ano_pesquisa, 'Engenharia de Dados & ETL', 'Airflow', usa_airflow FROM db_state_of_data.yearly UNION ALL
    SELECT ano_pesquisa, 'Engenharia de Dados & ETL', 'AWS Glue', usa_glue FROM db_state_of_data.yearly UNION ALL
    SELECT ano_pesquisa, 'Engenharia de Dados & ETL', 'Fivetran', usa_fivetran FROM db_state_of_data.yearly UNION ALL
    SELECT ano_pesquisa, 'Engenharia de Dados & ETL', 'Stitch', usa_stitch FROM db_state_of_data.yearly UNION ALL
    SELECT ano_pesquisa, 'Engenharia de Dados & ETL', 'NiFi', usa_nifi FROM db_state_of_data.yearly UNION ALL
    SELECT ano_pesquisa, 'Engenharia de Dados & ETL', 'Talend', usa_talend FROM db_state_of_data.yearly UNION ALL
    SELECT ano_pesquisa, 'Engenharia de Dados & ETL', 'Pentaho', usa_pentaho FROM db_state_of_data.yearly
)
SELECT 
    ano_pesquisa,
    categoria,
    tecnologia,
    COUNT(CASE WHEN LOWER(TRIM(usa)) = 'sim' THEN 1 END) AS total_usuarios,
    COUNT(CASE WHEN LOWER(TRIM(usa)) IN ('sim', 'não', 'nao') THEN 1 END) AS total_respostas_validas,
    ROUND(
        COUNT(CASE WHEN LOWER(TRIM(usa)) = 'sim' THEN 1 END) * 100.0 / 
        NULLIF(COUNT(CASE WHEN LOWER(TRIM(usa)) IN ('sim', 'não', 'nao') THEN 1 END), 0),
        2
    ) AS pct_adocao
FROM tec_unpivot
GROUP BY 
    ano_pesquisa,
    categoria,
    tecnologia
ORDER BY 
    ano_pesquisa,
    categoria,
    pct_adocao DESC;

-- ==============================================================================
-- 5) Qual é o índice de adoção de Inteligência Artificial e seu impacto?
-- ==============================================================================

WITH ia_prioridade_unpivot AS (
    SELECT ano_pesquisa, 'IA é prioridade como principal frente' AS indicador, ia_prioridade_negocio AS resposta FROM db_state_of_data.yearly UNION ALL
    SELECT ano_pesquisa, 'IA não é prioridade na empresa', ia_nao_prioridade FROM db_state_of_data.yearly
)
SELECT 
    ano_pesquisa,
    indicador,
    COUNT(CASE WHEN LOWER(TRIM(resposta)) = 'sim' THEN 1 END) AS total_sim,
    COUNT(CASE WHEN LOWER(TRIM(resposta)) IN ('sim', 'não', 'nao') THEN 1 END) AS total_respostas_validas,
    ROUND(
        COUNT(CASE WHEN LOWER(TRIM(resposta)) = 'sim' THEN 1 END) * 100.0 / 
        NULLIF(COUNT(CASE WHEN LOWER(TRIM(resposta)) IN ('sim', 'não', 'nao') THEN 1 END), 0),
        2
    ) AS pct_sim
FROM ia_prioridade_unpivot
GROUP BY 
    ano_pesquisa,
    indicador
ORDER BY 
    ano_pesquisa,
    indicador;

-- ==============================================================================
-- 6) Existem diferenças relevantes entre regiões, senioridades ou modelos de trabalho?
-- ==============================================================================

-- 6.1) Faixa Salarial por Região
SELECT 
    ano_pesquisa,
    COALESCE(NULLIF(TRIM(regiao), ''), 'N/I') AS regiao,
    COALESCE(NULLIF(TRIM(faixa_salarial), ''), 'N/I') AS faixa_salarial,
    COUNT(*) AS total_profissionais,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(PARTITION BY ano_pesquisa, COALESCE(NULLIF(TRIM(regiao), ''), 'N/I')), 2) AS pct_na_regiao
FROM db_state_of_data.yearly
WHERE COALESCE(NULLIF(TRIM(regiao), ''), 'N/I') != 'N/I'
  AND COALESCE(NULLIF(TRIM(faixa_salarial), ''), 'N/I') != 'N/I'
GROUP BY 
    ano_pesquisa,
    COALESCE(NULLIF(TRIM(regiao), ''), 'N/I'),
    COALESCE(NULLIF(TRIM(faixa_salarial), ''), 'N/I')
ORDER BY 
    ano_pesquisa,
    regiao,
    total_profissionais DESC;

-- 6.2) Distribuição dos Modelos de Trabalho ao Longo dos Anos
SELECT 
    ano_pesquisa,
    COALESCE(NULLIF(TRIM(modelo_trabalho), ''), 'N/I') AS modelo_trabalho,
    COUNT(*) AS total_profissionais,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(PARTITION BY ano_pesquisa), 2) AS pct_modelo
FROM db_state_of_data.yearly
GROUP BY 
    ano_pesquisa,
    COALESCE(NULLIF(TRIM(modelo_trabalho), ''), 'N/I')
ORDER BY 
    ano_pesquisa,
    total_profissionais DESC;

-- 6.3) Adoção de Tecnologias Avançadas (Databricks, Snowflake, Cloud, Airflow) por Senioridade
SELECT 
    ano_pesquisa,
    COALESCE(NULLIF(TRIM(senioridade), ''), 'N/I') AS senioridade,
    COUNT(*) AS total_respondentes,
    ROUND(COUNT(CASE WHEN LOWER(TRIM(usa_databricks)) = 'sim' THEN 1 END) * 100.0 / COUNT(*), 2) AS pct_databricks,
    ROUND(COUNT(CASE WHEN LOWER(TRIM(usa_snowflake)) = 'sim' THEN 1 END) * 100.0 / COUNT(*), 2) AS pct_snowflake,
    ROUND(COUNT(CASE WHEN LOWER(TRIM(usa_aws)) = 'sim' OR LOWER(TRIM(usa_gcp)) = 'sim' OR LOWER(TRIM(usa_azure)) = 'sim' THEN 1 END) * 100.0 / COUNT(*), 2) AS pct_cloud,
    ROUND(COUNT(CASE WHEN LOWER(TRIM(usa_airflow)) = 'sim' THEN 1 END) * 100.0 / COUNT(*), 2) AS pct_airflow
FROM db_state_of_data.yearly
WHERE COALESCE(NULLIF(TRIM(senioridade), ''), 'N/I') != 'N/I'
GROUP BY 
    ano_pesquisa,
    COALESCE(NULLIF(TRIM(senioridade), ''), 'N/I')
ORDER BY 
    ano_pesquisa,
    senioridade;

-- ==============================================================================
-- 7) Quais oportunidades e desafios podem ser identificados para empresas que desejam investir em Dados e IA?
-- ==============================================================================

-- 7.1) Principais Fatores de Decisão/Retenção dos Profissionais (Oportunidades para Empresas)
WITH motivos_decisao AS (
    SELECT ano_pesquisa, 'Salário / Remuneração' AS fator, motivo_escolha_salario AS resposta FROM db_state_of_data.yearly UNION ALL
    SELECT ano_pesquisa, 'Benefícios', motivo_escolha_beneficios FROM db_state_of_data.yearly UNION ALL
    SELECT ano_pesquisa, 'Flexibilidade / Trabalho Remoto', motivo_escolha_flex_remoto FROM db_state_of_data.yearly UNION ALL
    SELECT ano_pesquisa, 'Plano de Carreira / Crescimento', motivo_escolha_crescimento FROM db_state_of_data.yearly
)
SELECT 
    ano_pesquisa,
    fator,
    COUNT(CASE WHEN LOWER(TRIM(resposta)) = 'sim' THEN 1 END) AS total_sim,
    ROUND(
        COUNT(CASE WHEN LOWER(TRIM(resposta)) = 'sim' THEN 1 END) * 100.0 / 
        NULLIF(COUNT(CASE WHEN LOWER(TRIM(resposta)) IN ('sim', 'não', 'nao') THEN 1 END), 0),
        2
    ) AS pct_fator_relevante
FROM motivos_decisao
GROUP BY 
    ano_pesquisa,
    fator
ORDER BY 
    ano_pesquisa,
    pct_fator_relevante DESC;

-- 7.2) Desafios e Barreiras para Adoção de IA nas Empresas
WITH desafios_ia AS (
    SELECT ano_pesquisa, 'ROI não comprovado' AS desafio, ia_desafio_roi AS resposta FROM db_state_of_data.yearly UNION ALL
    SELECT ano_pesquisa, 'Dados da empresa não estão prontos', ia_desafio_time_dados_pronto_para_ia FROM db_state_of_data.yearly UNION ALL
    SELECT ano_pesquisa, 'Falta de compreensão dos casos de uso', ia_motivo_falta_compreensao FROM db_state_of_data.yearly UNION ALL
    SELECT ano_pesquisa, 'Falta de confiabilidade / Alucinação', ia_motivo_falta_confiabilidade FROM db_state_of_data.yearly UNION ALL
    SELECT ano_pesquisa, 'Incerteza na regulamentação', ia_motivo_incerteza_regulacao FROM db_state_of_data.yearly UNION ALL
    SELECT ano_pesquisa, 'Segurança e privacidade de dados', ia_motivo_seguranca_privacidade FROM db_state_of_data.yearly UNION ALL
    SELECT ano_pesquisa, 'Falta de expertise / Recursos', ia_motivo_falta_expertise FROM db_state_of_data.yearly UNION ALL
    SELECT ano_pesquisa, 'Alta direção não vê valor / prioridade', ia_motivo_alta_direcao_nao_ve_valor FROM db_state_of_data.yearly UNION ALL
    SELECT ano_pesquisa, 'Preocupações com propriedade intelectual', ia_motivo_propriedade_intelectual FROM db_state_of_data.yearly
)
SELECT 
    ano_pesquisa,
    desafio,
    COUNT(CASE WHEN LOWER(TRIM(resposta)) = 'sim' THEN 1 END) AS total_sim,
    COUNT(CASE WHEN LOWER(TRIM(resposta)) IN ('sim', 'não', 'nao') THEN 1 END) AS total_respostas_validas,
    ROUND(
        COUNT(CASE WHEN LOWER(TRIM(resposta)) = 'sim' THEN 1 END) * 100.0 / 
        NULLIF(COUNT(CASE WHEN LOWER(TRIM(resposta)) IN ('sim', 'não', 'nao') THEN 1 END), 0),
        2
    ) AS pct_empresas_afetadas
FROM desafios_ia
GROUP BY 
    ano_pesquisa,
    desafio
ORDER BY 
    ano_pesquisa,
    pct_empresas_afetadas DESC;
