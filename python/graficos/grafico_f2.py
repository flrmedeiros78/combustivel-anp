import pandas as pd
import matplotlib.pyplot as plt
# import matplotlib.dates as mdates
from config import OUTPUT_DIR

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