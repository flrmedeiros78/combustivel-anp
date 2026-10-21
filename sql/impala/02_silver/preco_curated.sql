DROP TABLE IF NOT EXISTS anp.preco_curated;

CREATE TABLE anp.preco_curated STORED AS PARQUET AS
SELECT                   
  trim(UPPER(regiao_sigla))                                               as REGIAO
 ,trim(UPPER(estado_sigla))                                               as ESTADO
 ,trim(UPPER(municipio))                                                  as MUNICIPIO
 ,trim(UPPER(revenda))                                                    as REVENDA
 ,trim(cnpj_revenda)                                                      as CNPJ
 ,trim(UPPER(produto))                                                    as PRODUTO
 ,to_timestamp(data_coleta, 'dd/MM/yyyy')                                 as DATA_COLETA
 ,CAST(replace(replace(valor_venda, '.', ''), ',', '.') as DECIMAL(10,2)) as VLR_VENDA
 ,unidade_medida                                                          as UN_MEDIDA
 ,trim(UPPER(bandeira))                                                   as BANDEIRA
FROM anp.preco_raw;