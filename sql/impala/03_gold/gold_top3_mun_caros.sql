CREATE TABLE anp.gold_top3_mun_caros STORED AS PARQUET AS 
with ranked as (
SELECT
  estado
 ,municipio
 ,ROUND(AVG(vlr_venda),2) as preco_medio
 ,count(1)                as qtd
 ,RANK() OVER (
    PARTITION BY estado 
    ORDER BY AVG(vlr_venda) DESC
    ) AS pos
FROM anp.preco_curated
WHERE  
    produto = 'GASOLINA'
GROUP BY estado, municipio
HAVING COUNT(1) >= 10
)
select
  estado
 ,municipio
 ,preco_medio
 ,qtd
 ,pos
from ranked
ORDER BY estado, pos LIMIT 15

-- ou dessa forma
/*
CREATE TABLE anp.gold_top3_mun_caros STORED AS PARQUET AS
SELECT estado, municipio, preco_medio, qtd, pos
 FROM(
  SELECT estado, municipio,
    ROUND(AVG(vlr_venda),2)           AS preco_medio,
    COUNT(1)                          AS qtd,          
    RANK() OVER(PARTITION BY estado
        ORDER BY AVG(vlr_venda) DESC) AS pos -- posição 
  FROM anp.preco_curated
  WHERE produto = 'GASOLINA'
  GROUP BY estado, municipio
  HAVING COUNT(1) >= 10
 ) t
 WHERE pos <= 3
 ORDER BY estado, pos;
*/