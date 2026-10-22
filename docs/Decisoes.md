# Decisões e aprendizados

Registro das escolhas técnicas do projeto `combustivel-anp` (NiFi → Impala → Hive → Streamlit), com o motivo de cada uma e o que foi descartado. Cada decisão tem contexto, escolha e consequência, para que o "porquê" não se perca.

## Decisões

### 1. O NiFi só gera CSV; o Parquet é criado no Impala (ELT)
- **Contexto:** a imagem do NiFi 2.x não traz o `ParquetRecordSetWriter`.
- **Decisão:** o NiFi limpa e padroniza o CSV; a conversão para Parquet é feita no Impala com `CREATE TABLE ... AS SELECT`.
- **Consequência:** a transformação de tipos fica em SQL, versionada em `sql/impala/02_silver/`.

### 2. Delimitador `|` no CSV tratado
- **Contexto:** o campo `complemento` continha `;`, o delimitador original, e deslocava as colunas seguintes (erro `String to Decimal parse failed`).
- **Decisão:** o `CSVRecordSetWriter` grava com `|`, e a tabela raw usa `FIELDS TERMINATED BY '|'`.
- **Descartado:** aspas em todos os campos (mais frágil com o parser de texto do Impala).

### 3. Nome de arquivo sem acento, definido no fluxo
- **Contexto:** o Impala ignorava o arquivo `Preços semestrais ...csv` por causa do `ç`.
- **Decisão:** um `UpdateAttribute` define `filename = precos_2026_01.csv` antes do `PutFile`. O PutFile não tem campo de nome; ele usa o atributo `filename`.
- **Regra:** `data/saida/` contém só o arquivo da tabela, porque a pasta inteira é a `LOCATION` da raw. Backups e imagens ficam fora dela.

### 4. Arquitetura Medallion (Bronze, Silver, Gold)
| Camada | Objeto                        | Papel                                                                        |
|--------|-------------------------------|------------------------------------------------------------------------------|
| Bronze | CSV tratado e `anp.preco_raw` | Dado fiel à fonte, tudo texto                                                |
| Silver | `anp.preco_curated`           | Tipos corretos (`TIMESTAMP`, `DECIMAL(10,2)`), textos em maiúsculas, Parquet |
| Gold   | `anp.gold_*`                  | Agregações prontas para consumo                                              |

- **Decisão:** a Gold é materializada em tabelas, e não calculada a cada consulta. O painel lê a Gold e não varre os 422 mil registros da Silver.
- **Consequência:** se a Silver mudar, as tabelas Gold precisam ser recriadas.

### 5. SQL em arquivos, organizado por camada
- **Decisão:** `sql/impala/01_bronze`, `02_silver`, `03_gold` e `consultas`, um arquivo por tabela, com `DROP TABLE IF EXISTS` no topo.
- **Motivo:** ordem de execução clara e scripts que podem ser repetidos sem erro.
- **Separação:** `sql/impala/` para o que roda no Impala; `sql/hive/` para o Hive.

### 6. NiFi e Impala não rodam ao mesmo tempo
- **Contexto:** o PC tem ~7,4 GB de RAM e o WSL usa ~5 GB (`.wslconfig`).
- **Decisão:** ligar o NiFi, gerar o arquivo, desligá-lo e só então usar o Impala. O `mem_limit` do quickstart caiu de 4 GB para 2 GB.

### 7. HiveServer2 em container separado, no mesmo metastore
- **Decisão:** `apache/hive:3.1.3` (compatível com o metastore do quickstart), na mesma rede e com o mesmo volume `impala-quickstart-warehouse`, apontando para `thrift://quickstart-hive-metastore:9083`.
- **Cuidado:** o caminho `../../data/saida` é relativo ao `.yml` (`sql/hive/`), não à raiz do projeto.

### 8. Credenciais em `.env`
- **Decisão:** a senha do NiFi vive no `.env` (fora do Git), com um `.env.example` como modelo. A senha precisa de 12 caracteres ou mais.
- **Atenção:** o `restart` não relê o `.env`; é preciso recriar o container (`--force-recreate`).

### 9. Python modular
- **Gráficos estáticos:** `python/graficos/`, um módulo por gráfico, reexportado no `__init__.py`.
- **Painel:** `python/painel/`, dividido por responsabilidade:
  - `dados.py` só consulta (o único lugar com SQL);
  - `componentes/` só desenha;
  - `paginas/` só monta o layout.
- **Motivo:** um painel novo vira um arquivo em `paginas/` e uma linha em `app_painel.py`.

### 10. Streamlit para o painel
- **Motivo:** mesma linguagem do restante do projeto, dados via `impyla` + pandas, gráficos interativos com Plotly e pouco código de interface.
- **Limitação:** precisa de um servidor Python e do Impala acessível. Não roda em hospedagem estática (Netlify). Para publicar, o caminho é exportar a Gold para arquivos e usar um site estático ou o Streamlit Community Cloud.

### 11. Permissão aberta no warehouse (somente estudo)
- **Contexto:** o volume `impala-quickstart-warehouse` pertence ao root e o `impalad` não conseguia criar pastas (`Mkdirs failed`).
- **Decisão:** montar o volume no `impalad-1` e liberar a permissão com `chmod -R 777` como root.
- **Atenção:** aceitável num ambiente local de estudo. Em produção, o dono do volume deve ser o usuário do serviço.

## Aprendizados

- **Pequenos detalhes quebram o fluxo:** `filname` em vez de `filename` e `.run()` esquecido no Streamlit deram horas de depuração. Ler o erro e o código com calma economiza tempo.
- **Verifique onde o volume está montado** antes de culpar a permissão: o `impalad` nem enxergava o diretório do warehouse.
- **O estado do NiFi importa:** o `ListFile` guarda estado e só reprocessa depois de **Clear state**.
- **Estatísticas diferem entre motores:** o Hive devolvia `COUNT = 0` por usar as estatísticas do `COMPUTE STATS` do Impala (`SET hive.compute.query.using.stats=false;`).
- **Módulo não é função:** `from graficos import grafico_f1` traz o módulo; é o `__init__.py` que reexporta a função.
- **Gráficos precisam de posição contínua:** no F.2, reiniciar o `y` por estado sobrepunha as barras.
- **O que roda no navegador não roda em qualquer hospedagem:** decidir onde publicar antes de escolher a ferramenta do painel.

## Limitações conhecidas

- A `gold_top3_mun_caros` ainda cobre só gasolina; o painel não filtra os municípios por combustível.
- Os dados cobrem só o 1º semestre de 2026 (um arquivo).
- O painel depende do Impala local no ar.

## Próximas decisões

- Recriar a `gold_top3_mun_caros` com a coluna `produto`.
- Definir como publicar o painel (exportar a Gold para arquivos ou Streamlit Community Cloud).
- Automatizar a execução em ordem (bronze → silver → gold) em um script.