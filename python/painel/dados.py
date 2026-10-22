import pandas as pd
import streamlit as st

from impala.dbapi import connect
from config import IMPALA_HOST, IMPALA_PORT
from decimal import Decimal
from pathlib import Path

folder = Path(__file__).parent / "dados_gold"

#@st.cache_data(ttl=600)
#def _consultar(sql: str) -> pd.DataFrame:
#    conn = connect(host=IMPALA_HOST, port=IMPALA_PORT)
#    try:
#        cur = conn.cursor()
#        cur.execute(sql)
#        df = pd.DataFrame(cur.fetchall(), columns=[c[0] for c in cur.description])
#    finally:
#        conn.close()
#    for c in df.columns:
#        if df[c].map(lambda v: isinstance(v, Decimal)).any():
#            df[c] = df[c].astype(float)
#    return df

@st.cache_data(ttl=600)
def _ler (tabela: str) -> pd.DataFrame:
    try:
       conn = connect(host=IMPALA_HOST, port=IMPALA_PORT)
       try:
           cur = conn.cursor() 
           cur.execute(f"select * from anp. {tabela}")
           return pd.DataFrame(cur.fatchall(), columns=[c[0] for c in cur.description])
       finally:
           conn.close()
    except Exception:
        return pd.read_csv(folder / f"{tabela}.csv")

# consultar
#def preco_estado() -> pd.DataFrame:
#    return _consultar("select * from anp.gold_preco_medio_estado")
#
#def mun_caros() -> pd.DataFrame:
#    return _consultar("select * from anp.gold_top3_mun_caros")
#
#def variacao_mensal()-> pd.DataFrame:
#    return _consultar("select * from anp.gold_variacao_mensal order by produto, mes")
#
    
# ler
def preco_estado() -> pd.DataFrame:
    return _ler("anp.gold_preco_medio_estado")

def mun_caros() -> pd.DataFrame:
    return _ler("anp.gold_top3_mun_caros")

def variacao_mensal()-> pd.DataFrame:
     return _ler("gold_variacao_mensal").sort_values(["produto", "mes"])




           



