-- ----------------------------------------------------------------------
--  Gold --> No shell do Impala
-- ----------------------------------------------------------------------
-- A primeira é a F.1 materializada.
-- Para cada consulta, crie uma tabela anp.gold_* a partir da anp.preco_curated, em Parquet. 
-- Antes de cada uma, use DROP TABLE IF EXISTS para poder rodar de novo.

DROP TABLE IF NOT EXISTS anp.gold_preco_medio_estado;

CREATE TABLE anp.gold_preco_medio_estado STORED AS PARQUET AS 
SELECT 
  produto
 ,estado
 ,ROUND(AVG(vlr_venda),2) AS preco_medio
 ,COUNT(*) AS qtd 
FROM anp.preco_curated 
GROUP BY produto, estado;