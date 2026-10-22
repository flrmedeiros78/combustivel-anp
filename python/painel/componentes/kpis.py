import pandas as pd
import streamlit as st

def kpis_precos(estados: pd.DataFrame, mensal: pd.DataFrame) -> None:
    """
    Quatro indicadores:
        'estado' ordenado do mais caro ao mais barato.   
    """
    caro, barato = estados.iloc[0],estados.iloc[1]
    var = (mensal["preco_medio"].iloc[-1] / mensal["preco_medio"].iloc[0] - 1) * 100
   
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Preço médio nacional", f"{estados["preco_medio"].mean():.2f}")
    c2.metric("Estado mais caro", caro["estado"], f"R$ {caro["preco_medio"]:.2f}", delta_color="off")
    c3.metric("Estado mais barato", barato["estado"], f"R$ {barato["preco_medio"]:.2f}", delta_color="off")
    c4.metric("Variação no semestre", f"{var:+.2f}%")
    