import pandas as pd
import matplotlib.pyplot as plt
# import matplotlib.dates as mdates
from config import OUTPUT_DIR , CORES

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
        bars = ax.barh(range(len(sub)),                          # posições verticais (0, 1, 2, ...)
                sub["preco_medio"],                             # largura de cada barra
                color=CORES.get(produto.lower(), "#68BCE2"))    # cor do produto
        
        # infoma ao lado da barra o valor em real
        ax.bar_label(bars, fmt="R$ %.2f", padding=3, fontsize=9)
        
        # # informar o valor em percentual
        # max_val = sub["preco_medio"].max()
        # pcts = [f"{(v / max_val * 100):.2f}%" 
                # for v in sub["preco_medio"]]
        # ax.bar_label(bars, labels=pcts, padding=3, fontsize=9)
        
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
