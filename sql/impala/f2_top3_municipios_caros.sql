-- F.2 Top 3 municípios mais caros por estado (Gasolina, mín. 10 coletas)
SELECT * FROM (
  SELECT estado,
         municipio,
         ROUND(AVG(vlr_venda), 2) AS preco_medio,  -- média p/ 2 casas AVG = soma_de_todos_os_valores / quantidade_de_linhas 
         COUNT(1)                 AS qtd,
         -- Ranqueia municípios do mais caro ao mais barato DENTRO de cada estado.
         -- Empates recebem o mesmo rank (ex.: dois no 3º → ambos aparecem).
         RANK() OVER (PARTITION BY estado ORDER BY AVG(vlr_venda) DESC) AS pos
  FROM anp.preco_curated
  WHERE produto = 'GASOLINA'      
  GROUP BY estado, municipio
  HAVING COUNT(1) >= 10           -- exige mín. 10 coletas
) t
WHERE pos <= 3                    -- pega só os top 3 de cada estado
ORDER BY estado, pos;