import pandas as pd
from pathlib import Path
from impala.dbapi import connect
from config import IMPALA_HOST, IMPALA_PORT, IMPALA_DB, SQL_DIR
import warnings

# Ignora a mensagem indicando usar o SQLAlchemy
warnings.filterwarnings("ignore", message="pandas only supports SQLAlchemy")   

def conectar():
    return connect(
        host=IMPALA_HOST,
        port=IMPALA_PORT,
        database=IMPALA_DB
        ) # noqa: S113
def carregar_query(nome:str):
    return (SQL_DIR / f"{nome}.sql").read_text(encoding="utf-8").strip()

def executar_query(nome: str) -> pd.DataFrame:
    conn = conectar()
    sql = carregar_query(nome)
    return pd.read_sql(sql, conn)