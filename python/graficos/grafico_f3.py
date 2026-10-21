import pandas as pd
import matplotlib.pyplot as plt
#import matplotlib.dates as mdates
from config import OUTPUT_DIR, CORES

 # F.3 - Variação mensal do preço médio por produto
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