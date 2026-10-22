import streamlit as st
from painel.paginas import precos
from painel.componentes.estilo import aplicar_css

st.set_page_config(page_title="Combustivel ANP", layout="wide")
aplicar_css()

# Para um novo painel: crie painel/paginas/xxx.py  e acrescente uma aqui:
paginas = [
    st.Page(precos.render, title="Preços", url_path="precos", default=True),
    
]

st.navigation(paginas).run()