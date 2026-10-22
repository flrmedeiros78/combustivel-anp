import pandas as pd
import plotly.express as px
from plotly.graph_objects import Figure as fg
import plotly.graph_objects as go
from painel.componentes.estilo import cor

# def fig_preco_estado(df: pd.DataFrame) -> fg:
    # fig = px.bar(df, x="preco_medio", y="estado", orientation="h",
                # labels={"preco_medio": "Preço médio R$", "estado":""})
    # fig.update_yaxes(autorange="reversed") # mais caros no topo 
    # fig.update_xaxes(range=[df["preco_medio"].min() - 0.3, df["preco_medio"].max() + 0.1])
    # return fig

# def fig_variacao(df: pd.DataFrame) -> fg:
    # return px.line(df, x="mes", y="preco_medio", markers=True, hover_data=["var_pct"],
                    # labels={"preco_medio": "Preçp médio R$", "mes":"", "var_pct": "var. % no mês"})

def estado_clicando(evento) -> str | None:
    """
    Extrai o estado da seleção doo gráfico e barras ou não.
    """
    pontos = evento.selection.points if evento and evento.selection else []
    return pontos[0]["y"] if pontos else None


import plotly.graph_objects as go
from painel.componentes.estilo import cor

# def fig_preco_estado(df, produto):
#     fig = go.Figure(go.Bar(x=df["preco_medio"], y=df["estado"], orientation="h",
#                            marker_color=cor(produto), hovertemplate="%{y}: R$ %{x:.2f}<extra></extra>"))
#     fig.update_xaxes(range=[float(df["preco_medio"].min()) - 0.3, float(df["preco_medio"].max()) + 0.1],
#                      tickprefix="R$ ", gridcolor="#e6ebef")
#     fig.update_yaxes(autorange="reversed")
#     fig.update_layout(height=360, margin=dict(l=0, r=0, t=0, b=0), plot_bgcolor="#fff",
#                       paper_bgcolor="#fff", showlegend=False)
#     return fig

def fig_preco_estado(df: pd.DataFrame, produto: str, uf: str | None = None) -> fg:
    fig = px.bar(df, x="preco_medio", y="estado", orientation="h", color_discrete_sequence=[cor(produto)])
    fig.update_traces(texttemplate="R$ %{x:.2f}", textposition="outside",
                      marker_opacity=[1 if not uf or e == uf else .3 for e in df["estado"]])  # destaca o estado clicado
    fig.update_yaxes(autorange="reversed", title=None)
    fig.update_xaxes(range=[df["preco_medio"].min() - 0.3, df["preco_medio"].max() + 0.25], title=None)
    fig.update_layout(height=520, margin=dict(l=0, r=10, t=10, b=0), showlegend=False)
    return fig


def fig_variacao(df: pd.DataFrame, produto: str) -> fg:
    """df com TODOS os produtos; o selecionado fica em destaque."""
    fig = px.line(df, x="mes", y="preco_medio", color="produto", markers=True,
                  color_discrete_map={p: cor(p) for p in df["produto"].unique()},
                  hover_data=["var_pct"], labels={"preco_medio": "Preço médio (R$)", "mes": "", "var_pct": "Var. % no mês"})
    for t in fig.data:
        sel = t.name == produto
        t.update(line_width=3.5 if sel else 1.5, opacity=1 if sel else .35)
    fig.update_layout(height=360, margin=dict(l=0, r=25, t=45, b=0), legend_title_text="",
                      legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="left", x=0))
    return fig

# def fig_variacao(mensal, produto):
#     fig = go.Figure()
#     for p, g in mensal.groupby("produto"):
#         on = p == produto
#         fig.add_trace(go.Scatter(
#             x=g["mes"], y=g["preco_medio"], name=p.title(), mode="lines+markers",
#             line=dict(color=cor(p) if on else cor(p) + "66", width=3 if on else 1.5),
#             marker=dict(size=7 if on else 4), customdata=g["var_pct"].fillna(0),
#             hovertemplate="R$ %{y:.2f} (%{customdata:.1f}% vs mês anterior)<extra>" + p.title() + "</extra>"))
#     fig.update_yaxes(tickprefix="R$ ", gridcolor="#e6ebef")
#     fig.update_layout(height=300, margin=dict(l=0, r=0, t=0, b=0), plot_bgcolor="#fff",
#                       paper_bgcolor="#fff", legend=dict(orientation="h"))
#     return fig

