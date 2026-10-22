import streamlit as st

def seletor_produto(produtos)->str:
    """Radio horinzontal de combustível: 
        devolve o produto selecionado
    """
    opcoes = sorted(produtos)
    escolha = st.pills("Combustível", opcoes, default=opcoes[0], label_visibility="collapsed")
    return escolha or opcoes[0]  # se desmarcar, volta ao primeiro
    #return st.radio("Combustível", sorted(produtos), horizontal=True)