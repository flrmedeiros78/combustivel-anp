SELECT COUNT(*) FROM anp.preco_raw;

SELECT *
FROM anp.preco_raw
WHERE valor_venda RLIKE '^[0-9]{2}/[0-9]{2}/[0-9]{4}$'
LIMIT 10; 

SELECT * FROM anp.preco_raw LIMIT 10; 

 -----------------------------------------------
 -- Tabela criada e lendo o CSV do NiFi com impala.
 -----------------------------------------------
-- consulta de verificação e as estatísticas:
-- command:
COMPUTE STATS anp.preco_raw;
SELECT produto, COUNT(*) AS qtd FROM anp.preco_raw GROUP BY produto ORDER BY qtd DESC;

-- command: No shell do Impala:
SELECT COUNT(*) FROM anp.preco_raw;
SHOW FILES IN anp.preco_raw;