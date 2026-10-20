-- F.1 Preço médio por produto e estado
-- Agrupa por produto + estado, calcula média e quantidade de coletas.
-- Ordena do estado mais caro para o mais barato dentro de cada produto.
SELECT produto,
       estado,
       ROUND(AVG(vlr_venda), 2) AS preco_medio,   -- média arredondada p/ 2 casas
       COUNT(*)                 AS qtd            -- nº de coletas
FROM anp.preco_curated
GROUP BY produto, estado
ORDER BY produto, preco_medio DESC;


-- F.2 Top 3 municípios mais caros por estado (Gasolina, mín. 10 coletas)
SELECT * FROM (
  SELECT estado,
         municipio,
         ROUND(AVG(vlr_venda), 2) AS preco_medio,  -- média p/ 2 casas AVG = soma_de_todos_os_valores / quantidade_de_linhas 
         COUNT(*)                 AS qtd,
         -- Ranqueia municípios do mais caro ao mais barato DENTRO de cada estado.
         -- Empates recebem o mesmo rank (ex.: dois no 3º → ambos aparecem).
         RANK() OVER (PARTITION BY estado ORDER BY AVG(vlr_venda) DESC) AS pos
  FROM anp.preco_curated
  WHERE produto = 'GASOLINA'      
  GROUP BY estado, municipio
  HAVING COUNT(*) >= 10           -- exige mín. 10 coletas
) t
WHERE pos <= 3                    -- pega só os top 3 de cada estado
ORDER BY estado, pos;


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

