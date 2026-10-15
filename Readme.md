# Projeto combustivel-anp: NiFi → Impala

Pipeline de estudo com dados abertos da ANP (preços de combustíveis, 1º semestre de 2026, ~422 mil linhas).

```
CSV da ANP (data/)  →  NiFi (limpa e padroniza)  →  data/saida/*.csv  →  Impala (consulta SQL)
```

## O que cada ferramenta faz

| Ferramenta | Papel | Onde roda |
|---|---|---|
| **Docker** | Executa NiFi e Impala em "caixas" (containers) isoladas | Dentro do WSL (Ubuntu) |
| **NiFi** | Lê o CSV original, aplica schema com nomes limpos e grava o CSV tratado em `data/saida` | Container `nifi` (porta 8443) |
| **Impala** | Lê o CSV tratado e permite consultas SQL rápidas | Containers `impala-*` e `quickstart-hive-metastore` |
| **Hive Metastore** | "Catálogo" que guarda nome e estrutura das tabelas | Container `quickstart-hive-metastore` |

## Estrutura de pastas

```
combustivel-anp/
├── docker-compose.yml     # sobe o NiFi
├── impala/quickstart.yml  # sobe o Impala (copiado do repositório oficial e ajustado)
├── data/                  # CSV original da ANP (fora do Git)
│   └── saida/             # CSV tratado pelo NiFi (fora do Git)
├── impala-src/            # download do repositório oficial (fora do Git, pode apagar)
├── sql/  python/  docs/
```

Ajustes feitos no `impala/quickstart.yml`: `mem_limit` de 4 GB para 2 GB (o WSL tem ~5 GB) e 
a pasta `../data/saida` montada em `/data/saida` nos serviços `hms`, `catalogd` e `impalad-1`.

---

## A. Iniciar tudo depois de ligar o PC

Rode no **Ubuntu (WSL)**. O Docker não inicia sozinho no WSL.

**1. Iniciar o Docker**

```bash
sudo service docker start
```

**2. Ir para o projeto**

```bash
cd ~/Projetos/combustivel-anp
```

**3. Subir o Impala**

```bash
export QUICKSTART_LISTEN_ADDR=127.0.0.1
export IMPALA_QUICKSTART_IMAGE_PREFIX="apache/impala:81d5377c2-"
docker compose -f impala/quickstart.yml up -d
```

As variáveis valem só para o terminal atual: repita os `export` em cada terminal novo.
Se der erro de rede inexistente: `docker network create -d bridge quickstart-network`.
Confira com `docker ps` (4 containers `Up`).

**4. Abrir o shell do Impala** (aguarde ~1 min)

```bash
docker run -it --rm --network=quickstart-network ${IMPALA_QUICKSTART_IMAGE_PREFIX}impala_quickstart_client impala-shell -i impala-impalad-1-1:21050
```

As tabelas continuam lá: ficam no volume Docker `impala-quickstart-warehouse`.
Dicas: `Ctrl+L` limpa a tela (`clear` não existe); cole comandos longos em **uma linha só**.

**5. Subir o NiFi (só quando precisar ingerir dados)**

```bash
docker compose up -d nifi
```

Aguarde ~2 min e abra `https://localhost:8443/nifi` (aceite o aviso do certificado).
Usuário `admin`, senha `senhaNifi12345`. O fluxo salvo continua lá (volume `nifi_conf`).

**Por quê não deixar os dois ligados:** o computador tem ~7,4 GB de RAM. NiFi e Impala juntos apertam a memória, então ligue o NiFi, gere o arquivo, desligue-o e use o Impala.

---

## B. Rodar o fluxo do NiFi (gerar o CSV tratado)

Fluxo: `ListFile → FetchFile → ConvertRecord → PutFile` (grupo `ingestao_combustiveis`).

| Processador | O que faz |
|---|---|
| **ListFile** | Lista os CSVs em `/data` (guarda estado para não repetir arquivos) |
| **FetchFile** | Lê o conteúdo do arquivo listado |
| **ConvertRecord** | Usa o **CSVReader** (schema com nomes limpos, separador `;`) e o **CSVRecordSetWriter** (sem cabeçalho) |
| **PutFile** | Grava o resultado em `/data/saida` |

Passos:
1. Entre no grupo `ingestao_combustiveis`.
2. Botão direito no **ListFile** → **View state** → **Clear state** (senão ele acha que já processou).
3. Clique no canvas vazio → **Play** (▶).
4. Confira: `ls -lh data/saida` e `wc -l data/saida/*` (esperado: 422418 linhas).
5. Clique no canvas vazio → **Stop**.
6. Pare o NiFi: `docker compose stop nifi`.

---

## C. Ajustes pendentes e como finalizar

**1. NiFi: gravar o arquivo com nome sem acento** (o Impala ignorou o arquivo `Preços...csv`)
- Adicione um **UpdateAttribute** entre o ConvertRecord e o PutFile.
- Clique no **+**, crie a propriedade `filename` com valor `precos_2026_01.csv`.
- Reconecte: ConvertRecord → UpdateAttribute → PutFile (relação `success`).
- Enquanto não fizer isso, renomeie manualmente: `mv data/saida/Pre*.csv data/saida/precos_2026_01.csv`.

**2. Impala: conferir a tabela raw**
# ##################################################################-- O QUE ESTÁ FALTANDO FAZER --##################################################################
```sql
REFRESH anp.preco_raw;
SELECT COUNT(*) FROM anp.preco_raw;   -- esperado: 422418
```

**3. Camada curated em Parquet (não testado ainda)**
Tudo está como texto na raw. Na curated convertemos os tipos (data e preço) e gravamos em Parquet.

```sql
CREATE TABLE anp.preco_curated STORED AS PARQUET AS
SELECT regiao_sigla, estado_sigla, municipio, revenda, trim(cnpj_revenda) AS cnpj_revenda,
       produto, to_timestamp(data_coleta, 'dd/MM/yyyy') AS data_coleta,
       CAST(regexp_replace(valor_venda, ',', '.') AS DECIMAL(10,2)) AS valor_venda,
       unidade_medida, bandeira
FROM anp.preco_raw;
COMPUTE STATS anp.preco_curated;
```

**4. Próximas etapas do projeto**
- Consultas analíticas (média por produto/estado, ranking de municípios, variação com window functions).
- HiveServer2 apontando para o mesmo metastore.
- Análise em Python (Poetry + `impyla`).
- Documentar decisões e aprendizados em `docs/`.

---

## D. Desligar com segurança

```bash
docker compose stop nifi
docker compose -f impala/quickstart.yml stop
```

**Cuidado:** `docker compose down -v` apaga os volumes (tabelas do Impala e fluxo do NiFi). Use apenas `stop` no dia a dia.

---

## E. Problemas encontrados e por quê

| Problema | Causa | Solução |
|---|---|---|
| `Cannot connect to the Docker daemon` | WSL sem systemd: o Docker não inicia sozinho | `sudo service docker start` |
| Containers morriam/travavam | WSL limitado a ~3,6 GB | `.wslconfig` com `memory=5GB` e `swap=4GB`, depois `wsl --shutdown` |
| Colunas vazias no CSV de saída | CSVReader com nomes de cabeçalho diferentes do schema | Schema Text + `Ignore CSV Header Column Names = true` |
| GetFile relia o arquivo em loop e enchia o disco | Com `Keep Source File = true` ele não guarda estado | Trocar por ListFile + FetchFile |
| `ParquetRecordSetWriter` ausente no NiFi | Módulo Parquet não vem na imagem 2.x | NiFi gera CSV; o Parquet é criado no Impala/Hive (ELT) |
| Impala retornava 0 linhas | O `ç` no nome do arquivo (`Preços`) era ignorado | Renomear para `precos_2026_01.csv` |
| Shell do Impala não conectava | Nome padrão do README (`docker_impalad-1_1`) difere do nosso | `impala-shell -i impala-impalad-1-1:21050` |