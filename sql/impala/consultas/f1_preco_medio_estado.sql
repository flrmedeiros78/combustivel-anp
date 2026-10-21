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