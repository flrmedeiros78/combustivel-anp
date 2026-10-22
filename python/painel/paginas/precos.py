import streamlit as st
from painel import dados
from painel.componentes import filtros, graficos, kpis, estilo

def render() -> None:
    st.title("Preço de combustivel - ANP - 1º SEMESTRE DE 2026")
    st.caption("Camada gold do pipeline NiFi → Impala. Clique em um combustível ou em uma barra.")
       
    #DADOS
    estados = dados.preco_estado()
    municipios = dados.mun_caros()
    mensal = dados.variacao_mensal()
    
    #FILTROS
    produto = filtros.seletor_produto(estados["produto"].unique())
    d_est = estados[estados["produto"] == produto].sort_values("preco_medio", ascending=False)
    d_mes = mensal[mensal["produto"] == produto]
    d_mun = municipios # a gold só tem gasolina
    #d_mun = municipios[municipios["produto"] == produto]
    
    
    kpis.kpis_precos(d_est, d_mes)
    
    # Estado selecionado: guardado entre cliques e zerado ao trocar de combustível
    if st.session_state.get("produto_ant") != produto:
        st.session_state["uf"], st.session_state["produto_ant"] = None, produto
    uf = st.session_state.get("uf")
        
    col1, col2 = st.columns([1.15, 1])
    
    with col1:
        st.subheader("F.1 -  Preço médio por estado")
        st.caption("Clique em uma barra para ver os municípios do estado.")
        evento =  st.plotly_chart(graficos.fig_preco_estado(d_est, produto),
                                on_select="rerun", selection_mode="points", key="f1")
        
        novo = graficos.estado_clicando(evento)
        if novo != uf:
            st.session_state["uf"] = novo
            st.rerun()

    with col2, st.container(border=True):
        st.subheader("F.2 - Municípios mais caros (gasolina)")
        if uf :
            st.caption(f"Top 3 em {uf}. Clique de novo na barra para limpar.")
            d_mun = d_mun[d_mun["estado"] == uf]
        else:
            st.caption("Município mais caro de cada estado (8 maiores).")
            d_mun = d_mun[d_mun["pos"] == 1].nlargest(8, "preco_medio")
        d_mun = d_mun.sort_values("preco_medio", ascending=False)
        if d_mun.empty:
            st.info("Sem municípios para esse estado.")
        else:
            st.markdown(estilo.lista_html(d_mun, estilo.cor("GASOLINA")),
                        unsafe_allow_html=True)

    with st.container(border=True):
        st.subheader("F.3 · Variação mensal do preço médio")
        st.caption("Todos os combustíveis; o selecionado fica em destaque.")
        st.plotly_chart(graficos.fig_variacao(mensal, produto), width="stretch")   
            
    #     st.dataframe(d_mun[["estado", "municipio", "preco_medio", "qtd"]],
    #                  hide_index=True, use_container_width=True)
    # st.subheader("F.3 · Variação mensal do preço médio")
    # st.plotly_chart(graficos.fig_variacao(d_mes), use_container_width=True)
            
            