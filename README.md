# Pipeline ANP: NiFi → Impala → Hive

Pipeline de estudo com dados abertos da ANP (preços de combustíveis, 1º semestre de 2026, ~422 mil linhas).

O NiFi limpa e padroniza o CSV, o Impala consulta em SQL (camadas Bronze, Silver e Gold), 
o Hive lê o mesmo metastore, o Python gera gráficos e um painel interativo em Streamlit consome a camada Gold.
Tudo roda em containers Docker no WSL.

![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)
![NiFi](https://img.shields.io/badge/Apache%20NiFi-2.x-728E9B)
![Impala](https://img.shields.io/badge/Apache%20Impala-SQL-F8A100)
![Hive](https://img.shields.io/badge/Apache%20Hive-3.1.3-FDEE21?logoColor=black)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-painel-FF4B4B?logo=streamlit&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-gr%C3%A1ficos-3F4F75?logo=plotly&logoColor=white)
![Poetry](https://img.shields.io/badge/Poetry-gerenciador-60A5FA?logo=poetry&logoColor=white)

## O que o projeto faz

- Lê o CSV original da ANP (`data/entrada/`) e aplica um schema com nomes de colunas limpos (NiFi).
- Grava o CSV tratado em `data/saida/precos_2026_01.csv`, com delimitador `|`.
- Expõe o arquivo como tabela externa `anp.preco_raw` (Bronze, tudo texto) no Impala.
- Cria a camada Silver `anp.preco_curated` em **Parquet**, com tipos corretos (data, `DECIMAL`) e textos padronizados.
- Cria a camada Gold (`anp.gold_*`) com agregações e rankings, usando window functions.
- Disponibiliza o HiveServer2 no mesmo Hive Metastore.
- Gera gráficos estáticos em Python (matplotlib), salvos em `docs/graficos/`.
- Oferece um **painel interativo em Streamlit** (filtro por combustível e clique no estado) lendo a camada Gold.

## Stack

| Camada             | Tecnologia                                         |
|--------------------|----------------------------------------------------|
| Containers         | Docker e Docker Compose (WSL/Ubuntu)               |
| Ingestão e limpeza | Apache NiFi 2.x                                    |
| Consulta SQL       | Apache Impala (quickstart oficial, ajustado)       |
| Catálogo           | Hive Metastore                                     |
| SQL via Hive       | HiveServer2 (`apache/hive:3.1.3`)                  |
| Formato analítico  | Parquet                                            |
| Análise e gráficos | Python 3.12, `impyla`, pandas, matplotlib          |
| Painel             | Streamlit e Plotly                                 |
| Dependências       | Poetry (`pyproject.toml`, `poetry.lock`)           |
| Versionamento      | Git e GitHub                                       |

## Arquitetura

O projeto segue a **Arquitetura Medallion** (Bronze → Silver → Gold), com ingestão no NiFi e processamento ELT no Impala:

```mermaid
flowchart TD
    SOURCE[("CSV da ANP<br/>data/entrada")]
    NIFI[/"Apache NiFi<br/>limpa e padroniza"/]

    BRONZE["Bronze<br/>CSV tratado + anp.preco_raw<br/>(texto)"]
    SILVER["Silver<br/>anp.preco_curated<br/>(Parquet, tipos corretos)"]
    GOLD["Gold<br/>anp.gold_*<br/>(agregações e rankings)"]

    ANALYTICS["Consumo<br/>Impala SQL, Hive e gráficos PNG"]
    PAINEL["Painel Streamlit<br/>filtros e gráficos interativos"]

    HMS[/"Hive Metastore<br/>catálogo de tabelas"/]
    VOL[/"Volume Docker<br/>impala-quickstart-warehouse"/]

    SOURCE -->|"ListFile, FetchFile"| NIFI
    NIFI -->|"ConvertRecord, PutFile"| BRONZE
    BRONZE -->|"CREATE TABLE AS SELECT"| SILVER
    SILVER -->|"agregação"| GOLD
    GOLD --> ANALYTICS
    GOLD -->|"impyla + pandas"| PAINEL
    SILVER --> ANALYTICS

    BRONZE -.-> HMS
    SILVER -.-> HMS
    SILVER -.-> VOL

    classDef fonte fill:#bde0fe,stroke:#1d4e89,color:#000
    classDef ingestao fill:#e0a8e8,stroke:#7b2d8b,color:#000
    classDef bronze fill:#8d6e63,stroke:#4e342e,color:#fff
    classDef silver fill:#cfcfcf,stroke:#757575,color:#000
    classDef gold fill:#ffd54f,stroke:#f9a825,color:#000
    classDef consumo fill:#81c784,stroke:#2e7d32,color:#000
    classDef painel fill:#ffab91,stroke:#d84315,color:#000
    classDef infra fill:#d0e6ff,stroke:#1565c0,color:#000

    class SOURCE fonte
    class NIFI ingestao
    class BRONZE bronze
    class SILVER silver
    class GOLD gold
    class ANALYTICS consumo
    class PAINEL painel
    class HMS,VOL infra
```

| Camada     | Onde                            | Conteúdo                                                                   | Formato                       |
|------------|---------------------------------|----------------------------------------------------------------------------|-------------------------------|
| **Bronze** | `data/saida/` e `anp.preco_raw` | Dados da ANP sem transformar de tipo (tudo texto), nomes de colunas limpos | CSV com `\|` / tabela externa |
| **Silver** | `anp.preco_curated`             | Data como `TIMESTAMP`, preço como `DECIMAL(10,2)`, textos padronizados     | Parquet                       |
| **Gold**   | `anp.gold_*`                    | Preço médio por produto/estado, top municípios mais caros, variação mensal | Parquet (tabelas)             |

### Serviços

| Serviço               | Container                                    | Porta(s)                  |
|-----------------------|----------------------------------------------|---------------------------|
| NiFi                  | `nifi`                                       | `8443`                    |
| Impala (coord + exec) | `impala-impalad-1-1`                         | `21000`, `21050`, `25000` |
| Catalog / Statestore  | `impala-catalogd-1` / `impala-statestored-1` | `25020` / `25010`         |
| Hive Metastore        | `quickstart-hive-metastore`                  | interna                   |
| HiveServer2           | `quickstart-hiveserver2`                     | `10000`, `10002`          |
| Painel Streamlit      | processo local (`poetry run streamlit`)      | `8501`                    |

O NiFi e o Impala não devem rodar juntos: no meu caso o PC tem ~7,4 GB de RAM (WSL com ~5 GB).
Se o seu caso for o mesmo, ligue o NiFi, gere o arquivo, desligue-o e use o Impala.

### Fluxo do NiFi (grupo `ingestao_combustiveis`)

| Processador         | O que faz                                                                                                 |
|---------------------|-----------------------------------------------------------------------------------------------------------|
| **ListFile**        | Lista os CSVs em `/data/entrada` (guarda estado para não repetir arquivos)                                |
| **FetchFile**       | Lê o conteúdo do arquivo listado                                                                          |
| **ConvertRecord**   | CSVReader (schema com nomes limpos, separador `;`) e CSVRecordSetWriter (sem cabeçalho, delimitador `\|`) |
| **UpdateAttribute** | Define `filename = precos_2026_01.csv` (nome sem acento)                                                  |
| **PutFile**         | Grava em `/data/saida`                                                                                    |

## Estrutura de diretórios

```
combustivel-anp/
├── docker-compose.yml          # sobe o NiFi
├── impala/
│   ├── quickstart.yml          # Impala (repositório oficial, ajustado)
│   └── quickstart_conf/
├── sql/
│   ├── hive/                   # HiveServer2 (hs2.yml)
│   └── impala/
│       ├── 01_bronze/          # DDL da anp.preco_raw
│       ├── 02_silver/          # CTAS da anp.preco_curated
│       ├── 03_gold/            # CTAS das anp.gold_*
│       └── consultas/          # consultas F.1, F.2 e F.3 (leitura)
├── python/
│   ├── main.py                 # gera os gráficos PNG
│   ├── db.py                   # conexão com o Impala e leitura dos .sql
│   ├── config.py               # constantes (host, porta, pastas)
│   ├── graficos/               # um módulo por gráfico (matplotlib)
│   ├── app_painel.py           # entrada do painel Streamlit
│   └── painel/
│       ├── dados.py            # acesso à camada Gold (único lugar com SQL)
│       ├── componentes/        # filtros, kpis, graficos (Plotly) e estilo
│       └── paginas/            # uma página por painel (precos.py)
├── docs/
│   └── graficos/               # PNGs gerados pelo Python
├── pyproject.toml / poetry.lock
├── .env                        # credenciais (fora do Git)
├── .env.example                # modelo das credenciais
└── data/                       # fora do Git
    ├── entrada/                # CSV original da ANP
    ├── saida/                  # CSV tratado pelo NiFi (só ele; é a LOCATION da tabela)
    └── backup/
```

Ajustes no `impala/quickstart.yml`: `mem_limit` de 4 GB para 2 GB;
`../data/saida` montada em `/data/saida` no `hms`, `catalogd` e `impalad-1`;
volume `impala-quickstart-warehouse` também montado no `impalad-1`.

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
Confira com `wc -l data/saida/precos_2026_01.csv` (qtd registros: 422418). 
Pare o fluxo e o NiFi: `docker compose stop nifi`.

**Gerar as camadas Silver e Gold** (no impala-shell, nesta ordem): 
execute os arquivos de `sql/impala/01_bronze`, `02_silver` e `03_gold`.

**Gerar os gráficos PNG** (com o Impala no ar):

```bash
poetry run python python/main.py
```

Os PNGs são salvos em `docs/graficos/`.

**Abrir o painel interativo** (com o Impala no ar e a Gold criada):

```bash
poetry run streamlit run python/app_painel.py
```

Abra `http://localhost:8501`.

**Desligar:**
`docker compose stop nifi`,
`docker compose -f sql/hive/hs2.yml stop`,
`docker compose -f impala/quickstart.yml stop`.
obs - Evite `docker compose down -v`: ele apaga as tabelas do Impala e o fluxo do NiFi.

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

As tabelas Gold (`gold_preco_medio_estado`, `gold_top3_mun_caros` e `gold_variacao_mensal`) 
agregam a Silver e alimentam os gráficos e o painel.

A `anp.preco_curated` (Parquet) converte `data_coleta` para `TIMESTAMP`,
`valor_venda` para `DECIMAL(10,2)` (`vlr_venda`) e padroniza os textos com `trim(UPPER(...))`.

## Consultas analíticas

As tabelas Gold são criadas em [`sql/impala/03_gold/`](sql/impala/03_gold/). 
As consultas de leitura ficam em [`sql/impala/consultas/`](sql/impala/consultas/): 
    preço médio por produto e estado (`f1_preco_medio_estado.sql`), 
    top 3 municípios mais caros por estado com `RANK` (`f2_top3_municipios_caros.sql`) e 
    variação mensal do preço médio com `LAG` (`f3_variacao_mensal_preco.sql`).

Resultados em destaque: o diesel subiu cerca de 15% em março de 2026 e depois recuou; o etanol caiu em maio e junho.

## Gráficos e painel

Gráficos estáticos, gerados por `python/main.py`:

![Preço médio por estado](docs/graficos/f1_preco_medio_estado.png)
![Top 3 municípios mais caros](docs/graficos/f2_top3_municipios_caros.png)
![Variação mensal do preço](docs/graficos/f3_variacao_mensal.png)

### Painel interativo (Streamlit)

- Filtro por combustível: os indicadores (preço médio nacional, estado mais caro e mais barato, variação no semestre) e os gráficos reagem à escolha.
- Clique em uma barra do F.1 para ver os municípios mais caros do estado (F.2).
- O F.3 mostra todos os combustíveis, com o selecionado em destaque.

O código é dividido por responsabilidade: 
`dados.py` só consulta, 
`componentes/` só desenha e 
`paginas/` monta o layout.

Para um novo painel: 
    crie a tabela Gold, 
    uma função em `dados.py`, 
    uma página em `paginas/` e 
    uma linha em `app_painel.py`.

## Habilidades praticadas

- Containers com Docker Compose, redes e volumes compartilhados entre serviços
- Ingestão e limpeza de dados com NiFi (Record processors, estado, atributos)
- Arquitetura Medallion (Bronze, Silver e Gold) com Parquet no Impala
- SQL analítico: window functions (`RANK`, `LAG`), CTEs e agregações
- Hive Metastore compartilhado entre Impala e Hive
- Python com Poetry, `impyla`, pandas e matplotlib
- Painéis interativos com Streamlit e Plotly, em estrutura modular
- Git e GitHub

## Desafios resolvidos durante o desenvolvimento

| Problema                                             | Causa                                                  | Solução                                                              |
|------------------------------------------------------|--------------------------------------------------------|----------------------------------------------------------------------|
| `Cannot connect to the Docker daemon`                | WSL sem systemd                                        | `sudo service docker start`                                          |
| Containers morriam/travavam                          | WSL limitado a ~3,6 GB                                 | `.wslconfig` com `memory=5GB` e `swap=4GB`, depois `wsl --shutdown`  |
| Colunas vazias no CSV de saída                       | Cabeçalho do CSV diferente do schema                   | Schema Text + `Ignore CSV Header Column Names = true`                |
| GetFile relia o arquivo em loop                      | Sem estado com `Keep Source File = true`               | ListFile + FetchFile                                                 |
| `ParquetRecordSetWriter` ausente                     | Módulo Parquet não vem na imagem 2.x                   | NiFi gera CSV; Parquet é criado no Impala (ELT)                      |
| Impala retornava 0 linhas                            | `ç` no nome do arquivo                                 | `UpdateAttribute` com `filename` sem acento                          |
| Colunas deslocadas, `String to Decimal parse failed` | `;` dentro de `complemento`                            | Delimitador `\|` no NiFi e na raw                                    |
| `Mkdirs failed to create .../preco_curated`          | `impalad-1` sem o volume do warehouse                  | Montar o volume no `impalad-1` e liberar permissão                   |
| `Invalid parquet fallback schema resolution`         | Variável de sessão inválida                            | `SET PARQUET_FALLBACK_SCHEMA_RESOLUTION=POSITION;`                   |
| Login do NiFi recusado após trocar a senha           | Container não recriado                                 | `docker compose up -d --force-recreate nifi`                         |
| Hive retornava `COUNT = 0`                           | Usava estatísticas do `COMPUTE STATS` do Impala        | `SET hive.compute.query.using.stats=false;`                          |
| Hive via `/data/saida` vazia                         | Volume relativo é contado a partir do yml (`sql/hive`) | Usar `../../data/saida` e recriar com `--force-recreate`             |
| `Connection refused` no Beeline logo após subir      | O HiveServer2 leva 1 a 2 min para abrir a porta        | Aguardar e conferir `docker logs quickstart-hiveserver2`             |
| Painel em branco no Streamlit                        | Faltava `.run()` em `st.navigation(paginas)`           | `st.navigation(paginas).run()`                                       |
| `'module' object is not callable` nos gráficos       | `from graficos import grafico_f1` trazia o módulo      | Reexportar as funções no `graficos/__init__.py`                      |
| Barras do F.2 sobrepostas                            | Posição `y` reiniciava a cada estado                   | Posição contínua, com rótulo `UF - Município`                        |
| Gráficos dentro de `data/saida`                      | A folder é a `LOCATION` da tabela raw                  | Salvar os PNGs em `docs/graficos/`                                   |

## Próximos passos

- [x] NiFi com `UpdateAttribute` (nome do arquivo sem acento)
- [x] Camada Silver em Parquet
- [x] Consultas analíticas com window functions
- [x] HiveServer2 no mesmo metastore
- [x] Ambiente Python com Poetry e `impyla`
- [x] Testar a leitura da `anp.preco_curated` (Parquet) pelo Hive
- [x] Gráficos em Python (`main.py`)
- [x] Criar `.env.example`
- [x] Materializar a camada Gold em tabelas `anp.gold_*`
- [x] Painel interativo em Streamlit
- [ ] Recriar a `gold_top3_mun_caros` com a coluna `produto` (hoje só gasolina)
- [x] Publicar o painel (exportar a Gold para arquivos e usar site estático ou Streamlit Community Cloud)
- [x] Documentar decisões e aprendizados em `docs/`

## Créditos

Projeto de estudo com dados abertos da ANP.
Desenvolvido como parte do aprendizado contínuo e práticas modernas de Engenharia de Dados/Análise de dados.

# Contato

- Fabio Medeiros
- Engenharia de Dados/Análise de dados
- Email: fabiolrm78@gmail.com
- Telefone: (21) 99663-7177