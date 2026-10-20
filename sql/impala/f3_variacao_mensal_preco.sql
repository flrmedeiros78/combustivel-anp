-- F.3 Variação mensal do preço médio por produto (LAG)
-- CTE: calcula o preço médio por produto por mês.
WITH mensal AS (
  SELECT produto,
         trunc(data_coleta, 'MM') AS mes,          -- trunca p/ 1º dia do mês
         AVG(vlr_venda)           AS preco_medio   -- média daquele mês
  FROM anp.preco_curated
  GROUP BY produto, trunc(data_coleta, 'MM')
)
SELECT produto,
       mes,
       ROUND(preco_medio, 3) AS preco_medio,       -- média com 3 casas
       -- LAG pega o preço do mês ANTERIOR (mesmo produto).
       -- (atual / anterior - 1) * 100 = variação percentual.
       -- NULL no 1º mês (não há mês anterior para comparar).
       ROUND((preco_medio / LAG(preco_medio) OVER (PARTITION BY produto ORDER BY mes) - 1) * 100, 2) AS var_pct
FROM mensal
ORDER BY produto, mes;