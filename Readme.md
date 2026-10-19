# Pipeline ANP: NiFi → Impala → Hive

Pipeline de estudo com dados abertos da ANP (preços de combustíveis, 1º semestre de 2026, ~422 mil linhas). 

O NiFi limpa e padroniza o CSV, o Impala consulta em SQL (camadas raw e curated em Parquet) e o Hive lê o mesmo metastore. 
Tudo roda em containers Docker no WSL.

![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)
![NiFi](https://img.shields.io/badge/Apache%20NiFi-2.x-728E9B)
![Impala](https://img.shields.io/badge/Apache%20Impala-SQL-F8A100)
![Hive](https://img.shields.io/badge/Apache%20Hive-3.1.3-FDEE21?logoColor=black)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![Poetry](https://img.shields.io/badge/Poetry-gerenciador-60A5FA?logo=poetry&logoColor=white)

## O que o projeto faz

- Lê o CSV original da ANP (`data/entrada/`) e aplica um schema com nomes de colunas limpos (NiFi).
- Grava o CSV tratado em `data/saida/precos_2026_01.csv`, com delimitador `|`.
- Expõe o arquivo como tabela externa `anp.preco_raw` (tudo texto) no Impala.
- Cria a camada `anp.preco_curated` em **Parquet**, com tipos corretos (data, `DECIMAL`) e textos padronizados.
- Roda consultas analíticas com window functions (`sql/analises.sql`).
- Disponibiliza o HiveServer2 no mesmo Hive Metastore e uma análise em Python (`impyla` + pandas).

## Stack

| Camada            | Tecnologia                                                  |
|-------------------|-------------------------------------------------------------|
| Containers        | Docker e Docker Compose (WSL/Ubuntu)                        |
| Ingestão e limpeza| Apache NiFi 2.x                                             |
| Consulta SQL      | Apache Impala (quickstart oficial, ajustado)                |
| Catálogo          | Hive Metastore                                              |
| SQL via Hive      | HiveServer2 (`apache/hive:3.1.3`)                           |
| Formato analítico | Parquet                                                     |
| Análise           | Python 3.12, `impyla`, pandas                               |
| Dependências      | Poetry (`pyproject.toml`, `poetry.lock`)                    |
| Versionamento     | Git e GitHub                                                |

## Arquitetura

O projeto segue a **Arquitetura Medallion** (Bronze → Silver → Gold), com ingestão no NiFi e processamento ELT no Impala:

```mermaid
flowchart TD
    SOURCE[("CSV da ANP<br/>data/entrada")]
    NIFI["Apache NiFi<br/>limpa e padroniza"]

    BRONZE["Bronze<br/>CSV tratado + anp.preco_raw<br/>(texto)"]
    SILVER["Silver<br/>anp.preco_curated<br/>(Parquet, tipos corretos)"]
    GOLD["Gold<br/>agregações e rankings<br/>(sql/analises.sql)"]

    ANALYTICS["Consumo<br/>Impala SQL, Hive e Python"]

    HMS[/"Hive Metastore<br/>catálogo de tabelas"/]
    VOL[/"Volume Docker<br/>impala-quickstart-warehouse"/]

    SOURCE -->|"ListFile, FetchFile"| NIFI
    NIFI -->|"ConvertRecord, PutFile"| BRONZE
    BRONZE -->|"CREATE TABLE AS SELECT"| SILVER
    SILVER -->|"agregação"| GOLD
    GOLD --> ANALYTICS
    SILVER --> ANALYTICS

    BRONZE -.-> HMS
    SILVER -.-> HMS
    SILVER -.-> VOL
```

| Camada     | Onde                            | Conteúdo                                                                   | Formato                            |
|------------|---------------------------------|----------------------------------------------------------------------------|------------------------------------|
| **Bronze** | `data/saida/` e `anp.preco_raw` | Dados da ANP sem transformar de tipo (tudo texto), nomes de colunas limpos | CSV com `\|` / tabela externa      |
| **Silver** | `anp.preco_curated`             | Data como `TIMESTAMP`, preço como `DECIMAL(10,2)`, textos padronizados     | Parquet                            |
| **Gold**   | `sql/analises.sql`              | Preço médio por produto/estado, ranking de municípios, variação mensal     | Consultas (ou tabelas `anp.gold_*`)|


| Serviço                       | Container                                  | Porta(s)                    |
|-------------------------------|--------------------------------------------|-----------------------------|
| NiFi                          | `nifi`                                     | `8443`                      |
| Impala (coord + exec)         | `impala-impalad-1-1`                       | `21000`, `21050`, `25000`   |
| Catalog / Statestore          | `impala-catalogd-1`/`impala-statestored-1` | `25020` / `25010`           |
| Hive Metastore                | `quickstart-hive-metastore`                | interna                     |
| HiveServer2                   | `quickstart-hiveserver2`                   | `10000`, `10002`            |


O NiFi e o Impala não devem rodar juntos: no meu caso o pc tem ~7,4 GB de RAM (WSL com ~5 GB). 
se o seu caso for o mesmo: Ligue o NiFi, gere o arquivo, desligue-o e use o Impala.

### Fluxo do NiFi (grupo `ingestao_combustiveis`)
   
| Processador         | O que faz                                                                                                 |
|---------------------|-----------------------------------------------------------------------------------------------------------|
| **ListFile**        | Lista os CSVs em `/data/entrada` (guarda estado para não repetir arquivos)                                |
| **FetchFile**       | Lê o conteúdo do arquivo listado                                                                          |
| **ConvertRecord**   | CSVReader (schema com nomes limpos, separador `;`) e CSVRecordSetWriter (sem cabeçalho, delimitador `\|`) |
| **UpdateAttribute** | Define `filename = precos_2026_01.csv` (nome sem acento)                                                  |
| **PutFile**         | Grava em `/data/saida`                                                                                    |

## Estrutura de pastas

```
combustivel-anp/
├── docker-compose.yml       # sobe o NiFi
├── impala/
│   ├── quickstart.yml       # Impala (repositório oficial, ajustado)
│   └── quickstart_conf/
├── sql/
│   ├── analises.sql         # consultas analíticas
│   └── hive/hs2.yml         # HiveServer2
├── python/analise_precos.py # análise com impyla
├── docs/                    # decisões e aprendizados
├── pyproject.toml / poetry.lock
├── .env                     # credenciais (fora do Git)
├── .env.example             # credenciais (dentro do Git)
└── data/                    # fora do Git
    ├── entrada/             # CSV original da ANP
    ├── saida/               # CSV tratado pelo NiFi
    └── backup/
```

Ajustes no `impala/quickstart.yml`: `mem_limit` de 4 GB para 2 GB; 
`../data/saida` montada em `/data/saida` no `hms`, `catalogd` e 
`impalad-1`; volume `impala-quickstart-warehouse` também montado no `impalad-1`.

## Como executar

Pré-requisitos: Docker e Docker Compose no WSL (Ubuntu), Poetry e Python 3.12.

```bash
git clone https://github.com/flrmedeiros78/combustivel-anp.git
cd combustivel-anp
cp .env.example .env     # defina NIFI_PASSWORD (12+ caracteres)
poetry install
sudo service docker start
```

**Subir o Impala**

```bash
export QUICKSTART_LISTEN_ADDR=127.0.0.1
export IMPALA_QUICKSTART_IMAGE_PREFIX="apache/impala:81d5377c2-"
docker compose -f impala/quickstart.yml up -d
docker run -it --rm --network=quickstart-network ${IMPALA_QUICKSTART_IMAGE_PREFIX}impala_quickstart_client impala-shell -i impala-impalad-1-1:21050
```

Se der erro de rede: `docker network create -d bridge quickstart-network`.

**Subir o Hive e o NiFi (só quando precisar)**

```bash
docker compose -f sql/hive/hs2.yml up -d     # depois do Impala
docker compose up -d nifi                    # https://localhost:8443/nifi
```

**Gerar o CSV tratado:** 
no grupo `ingestao_combustiveis`, ListFile → View state → Clear state, depois Play. 
Confira com `wc -l data/saida/precos_2026_01.csv` (esperado: 422418). Pare o fluxo e o NiFi: `docker compose stop nifi`.

**Desligar:** 
`docker compose stop nifi`, 
`docker compose -f sql/hive/hs2.yml stop`, 
`docker compose -f impala/quickstart.yml stop`. 
Evite `docker compose down -v`: pois ele apaga as tabelas do Impala e o fluxo do NiFi.

## Modelo de dados

```sql
CREATE EXTERNAL TABLE anp.preco_raw (
   regiao_sigla STRING 
  ,estado_sigla STRING 
  ,municipio STRING 
  ,revenda STRING
  ,cnpj_revenda STRING
  ,nome_rua STRING
  ,numero_rua STRING
  ,complemento STRING
  ,bairro STRING
  ,cep STRING
  ,produto STRING
  ,data_coleta STRING
  ,valor_venda STRING
  ,valor_compra STRING 
  ,unidade_medida STRING 
  ,bandeira STRING
  )
ROW FORMAT DELIMITED FIELDS TERMINATED BY '|'
STORED AS TEXTFILE LOCATION '/data/saida';
```

A `anp.preco_curated` (Parquet) converte `data_coleta` para `TIMESTAMP`, 
`valor_venda` para `DECIMAL(10,2)` (`vlr_venda`) e padroniza os textos com `trim(UPPER(...))`. 
O SQL completo está na seção "Camada curated" do guia em `docs/`.

## Consultas analíticas

Em [`sql/analises.sql`](sql/analises.sql): preço médio por produto e estado, top 3 municípios mais caros por estado (`RANK`) e variação mensal do preço médio (`LAG`).

## Habilidades praticadas

- Containers com Docker Compose, redes e volumes compartilhados entre serviços
- Ingestão e limpeza de dados com NiFi (Record processors, estado, atributos)
- Modelagem raw → curated (ELT) com Parquet no Impala
- SQL analítico: window functions (`RANK`, `LAG`), CTEs e agregações
- Hive Metastore compartilhado entre Impala e Hive
- Python com Poetry, `impyla` e pandas
- Git e GitHub

## Desafios resolvidos durante o desenvolvimento

| Problema                                            | Causa                                   | Solução                                                            |
|-----------------------------------------------------|-----------------------------------------|--------------------------------------------------------------------|
| `Cannot connect to the Docker daemon`               | WSL sem systemd                         | `sudo service docker start`                                        |
| Containers morriam/travavam                         | WSL limitado a ~3,6 GB                  | `.wslconfig` com `memory=5GB` e `swap=4GB`, depois `wsl --shutdown`|
| Colunas vazias no CSV de saída                      | Cabeçalho do CSV diferente do schema    | Schema Text + `Ignore CSV Header Column Names = true`              |
| GetFile relia o arquivo em loop                     | Sem estado com `Keep Source File = true`| ListFile + FetchFile                                               |
| `ParquetRecordSetWriter` ausente                    | Módulo Parquet não vem na imagem 2.x    | NiFi gera CSV; Parquet é criado no Impala (ELT)                    |
| Impala retornava 0 linhas                           | `ç` no nome do arquivo                  | `UpdateAttribute` com `filename` sem acento                        |
| Colunas deslocadas, `String to Decimal parse failed`| `;` dentro de `complemento`             | Delimitador `\|` no NiFi e na raw                                  |
| `Mkdirs failed to create .../preco_curated`         | `impalad-1` sem o volume do warehouse   | Montar o volume no `impalad-1` e liberar permissão                 |
| `Invalid parquet fallback schema resolution`        | Variável de sessão inválida             | `SET PARQUET_FALLBACK_SCHEMA_RESOLUTION=POSITION;`                 |
| Login do NiFi recusado após trocar a senha          | Container não recriado                  | `docker compose up -d --force-recreate nifi`                       |
|-----------------------------------------------------|-----------------------------------------|--------------------------------------------------------------------|

## Próximos passos

- [x] NiFi com `UpdateAttribute` (nome do arquivo sem acento)
- [x] Camada curated em Parquet
- [x] Consultas analíticas com window functions
- [x] HiveServer2 no mesmo metastore
- [x] Ambiente Python com Poetry e `impyla`
- [x] Testar a leitura da `anp.preco_curated` (Parquet) pelo Hive
- [ ] Documentar decisões e aprendizados em `docs/`
- [ ] Criar `.env.example`
- [ ] Materializar a camada Gold em tabelas `anp.gold_*` (CTAS a partir de `sql/analises.sql`)

## Créditos 

Projeto de estudo com dados abertos da ANP.
Desenvolvido como parte do aprendizado contínuo e práticas modernas de Engenharia de Dados/Analise de dados.

# Contato:
Fabio Medeiros
Engenharia de Dados/Analise de dados
Email: fabiolrm78@gmail.com
Telefone: (21) 99663-7177


