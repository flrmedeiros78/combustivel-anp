import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from config import OUTPUT_DIR, CORES



# Graficos de preços por estado
def grafico_f1(df: pd.DataFrame):
    # Abre uma figura de 16×6 polegadas com 2 subplots (1 linha, 2 colunas), Cada um para um produto.
    fig, axes = plt.subplots(1, 2, figsize=(16, 6)) # Cria o "canvas" com 2 painéis lado a lado
    produtos = df["produto"].unique() # Lista os produtos distintos na coluna produto
    
    # Percorre os 2 primeiros produtos e associa cada um a um dos 2 painéis (ax).
    for ax, produto in zip(axes, produtos[:2]):
        # Filtra as linhas daquele produto e ordena do mais caro pro mais barato.
        sub = df[df["produto"] == produto].sort_values("preco_medio", ascending=False)
        
        #Desenha barras horizontais:
        ax.barh(range(len(sub)),                          # posições verticais (0, 1, 2, ...)
                sub["preco_medio"],                       # largura de cada barra
                color=CORES.get(produto, "#2486e0"))    # cor específica do produto (com fallback cinza)
        ax.set_yticks(range(len(sub)))
        ax.set_yticklabels(sub["estado"])
        
        # Rótulos no eixo Y = nome do estado (em vez de 0, 1, 2...).
        ax.set_title(produto)
        ax.set_xlabel("Preço Médio (R$)")
        ax.invert_yaxis()  # Inverte a ordem dos estados para melhor visualização
    
    # Título geral, layout, salvar
    plt.suptitle("F.1 - Preço médio por estado e produto", fontsize=12, fontweight="bold")
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "f1_preco_medio_estado.png", bbox_inches="tight")
    plt.close(fig)
    print(f"[ok] f1_preco_medio_estado.png")

    # F.1 - Preço médio por estado e produto

#   Gasolina                    Etanol
#   ┌──────────────────┐       ┌──────────────────┐
#   │ SP  ████████████ │       │ SP  ████████████ │
#   │ RJ  █████████    │       │ RJ  █████████    │
#   │ MG  ████████     │       │ MG  ████████     │
#   │ BA  ███████      │       │ BA  ███████      │
#   │ PR  ██████       │       │ PR  ██████       │
#   │ ...              │       │ ...              │
#   └──────────────────┘       └──────────────────┘
#     Preço Médio (R$)           Preço Médio (R$)   

# F.2 - Top 3 Municípios Mais Caros por Estado (Gasolina)
def grafico_f2(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(12, 6))
    
    for estado in df["estado"].unique():
        sub =  df[df["estado"] == estado].sort_values("pos")
        y = range(len(sub))
        ax.barh(y, 
                sub["preco_medio"],
                label=estado,
                height=0.8)
        for i, (_, row) in enumerate(sub.iterrows()):
            ax.text(row["preco_medio"] + 0.01,
                    i,
                    row["municipio"],
                    va="center",
                    fontsize=8)
    ax.set_xlabel("Preço Médio (R$)")
    
    # Título geral, layout, salvar
    ax.set_title("F.2 - Top 3 Municípios Mais Caros por Estado (Gasolina)")
    ax.legend(loc="lower right", fontsize=8)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "f2_top3_municipios_caros.png", bbox_inches="tight")
    plt.close(fig)
    print("[ok] f2_top3_municipios_caros.png")
    
# Preço Médio (R$/L)
# 1.50 ┤
    #  │
# 1.45 ┤  ██████████████████████  São Paulo
    #  │  ████████████████████  Campinas
    #  │  ██████████████████    Guarulhos
    #  │
# 1.40 ┤  █████████████████████  Rio de Janeiro
    #  │  ███████████████████   Niterói
    #  │  ██████████████████    Duque de Caxias
    #  │
# 1.35 ┤  █████████████████     Belo Horizonte
    #  │  ████████████████      Contagem
    #  │  ███████████████       Betim
    #  │
    #  └──────────────────────────────────────
    #   (barras horizontais por estado)
    
    
def grafico_f3(df: pd.DataFrame):
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    produtos = df["produto"].unique()
    
    for ax, produto in zip(axes, produtos[:2]):
        sub = df[df["produto"] == produto].sort_values("mes")
        ax.plot(sub["mes"],
                sub["preco_medio"],
                marker="o",
                color=CORES.get(produto, "#7f8c8d"),
                label=produto)
        
        ax.set_title(f"{produto} -  Preço Médio Mensal")
        ax.set_xlabel("Mês")
        ax.set_ylabel("Preço Médio (R$)")
        ax.tick_params(axis="x", rotation=45)
        ax.grid(True, alpha=0.3)
        
    plt.suptitle("F.3 - Variação mensal do preço médio por produto",
                 fontsize=12,
                 fontweight="bold")
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "f3_variacao_mensal.png", bbox_inches="tight")
    plt.close(fig)
    print("[ok] f3_variacao_mensal.png")
    
    
    # F.3 - Variação mensal do preço médio por produto

#   Gasolina                     Etanol
#   ┌──────────────────┐        ┌──────────────────┐
#   │  ●───●───●───●   │        │  ●───●───●───●   │
#   │        ●───●     │        │       ●───●      │
#   │   ●───●          │        │   ●───●          │
#   └──────────────────┘        └──────────────────┘
#    Jan  Feb Mar Apr           Jan  Feb Mar Apr   


 