DROP TABLE IF NOT EXISTS anp.preco_raw;
CREATE EXTERNAL TABLE anp.preco_raw (
  regiao_sigla STRING, 
  estado_sigla STRING, 
  municipio STRING, 
  revenda STRING,
  cnpj_revenda STRING, 
  nome_rua STRING, 
  numero_rua STRING, 
  complemento STRING,
  bairro STRING, 
  cep STRING, 
  produto STRING, 
  data_coleta STRING,
  valor_venda STRING, 
  valor_compra STRING, 
  unidade_medida STRING, 
  bandeira STRING
)
ROW FORMAT DELIMITED FIELDS TERMINATED BY '|'
STORED AS TEXTFILE
LOCATION '/data/saida';