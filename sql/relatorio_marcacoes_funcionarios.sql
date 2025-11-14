WITH base AS (
  SELECT
    f.codigo_funcionario,
    f.nome,
    f.cpf,
    f.cargo,
    p.hora_entrada,
    p.hora_saida
  FROM LABDATABASE.FUNCIONARIOS f
  LEFT JOIN LABDATABASE.MARCACOES p
    ON p.codigo_funcionario = f.codigo_funcionario
)
SELECT
  codigo_funcionario,
  nome,
  cpf,
  cargo,
  SUM(
    CASE
      WHEN hora_entrada IS NOT NULL
       AND TO_CHAR(hora_entrada, 'HH24:MI') > '08:00'
      THEN 1 ELSE 0
    END
  ) AS dias_atraso,
  ROUND(
      NVL(SUM(
        CASE
          WHEN hora_entrada IS NOT NULL AND hora_saida IS NOT NULL THEN
            (CAST(hora_saida   AS DATE) - CAST(hora_entrada AS DATE)) * 24
          ELSE 0
        END
      ), 0)
      -
      NVL(SUM(
        CASE
          WHEN hora_entrada IS NOT NULL AND hora_saida IS NOT NULL THEN 8
          ELSE 0
        END
      ), 0)
  , 2) AS banco_de_horas
FROM base
GROUP BY
  codigo_funcionario, nome, cpf, cargo
ORDER BY
  nome
