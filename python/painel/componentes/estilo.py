import streamlit as st
from html import escape

# Mesma paleta do HTML. Chave em maiúsculas, como vem da camada silver.
CORES = {"GASOLINA": "#c2410c", "GASOLINA ADITIVADA": "#9a3412", "ETANOL": "#15803d",
         "DIESEL": "#1d4ed8", "DIESEL S10": "#1e3a8a", "GNV": "#7c8f00"}


def cor(produto: str) -> str:
    return CORES.get(produto.upper(), "#475569")


def aplicar_css() -> None:
    st.markdown("""<style>
    .block-container {max-width: 100%; padding: 1.5rem 2.5rem;}
    h1 {font-size: 1.6rem !important; font-weight: 600 !important;}
    h3 {font-size: 1rem !important; font-weight: 600 !important;}
    [data-testid="stMetric"] {border: 1px solid rgba(128,128,128,.28); border-radius: 6px; padding: 12px 14px;}
    [data-testid="stMetricValue"] {font-family: ui-monospace, monospace; font-size: 1.6rem;}
    [data-testid="stVerticalBlockBorderWrapper"] {border-radius: 6px;}
    </style>""", unsafe_allow_html=True)
    
def lista_html(df, cor_barra: str) -> str:
    """Lista com UF, município, barra proporcional e preço (como no HTML)."""
    maximo = df["preco_medio"].max()
    linhas = []
    for _, r in df.iterrows():
        pct = r["preco_medio"] / maximo * 100
        linhas.append(
            f'<div style="display:grid;grid-template-columns:34px 1fr auto;gap:10px;align-items:center;padding:6px 4px">'
            f'<span style="font:500 12px ui-monospace,monospace;opacity:.6">{escape(str(r["estado"]))}</span>'
            f'<div><div>{escape(str(r["municipio"]).title())}</div>'
            f'<div style="height:6px;border-radius:3px;background:rgba(128,128,128,.25);margin-top:4px;overflow:hidden">'
            f'<div style="width:{pct:.1f}%;height:100%;background:{cor_barra}"></div></div></div>'
            f'<span style="font:500 13px ui-monospace,monospace">R$ {r["preco_medio"]:.2f}</span>'
            f'</div>'
        )
    return "".join(linhas)