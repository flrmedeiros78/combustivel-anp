DROP TABLE IF EXISTS anp.gold_variacao_mensal;
CREATE TABLE anp.gold_variacao_mensal STORED AS PARQUET AS
WITH m AS (
  SELECT produto, 
   trunc(data_coleta,'MM') AS mes, 
   AVG(vlr_venda) AS preco_medio
  FROM anp.preco_curated GROUP BY produto, trunc(data_coleta,'MM'))
SELECT produto, mes, ROUND(preco_medio,3) AS preco_medio,
       ROUND((preco_medio / LAG(preco_medio) OVER (PARTITION BY produto ORDER BY mes) - 1) * 100, 2) AS var_pct
FROM m;

-- select cast(mes,"$m") from anp.gold_variacao_mensal;