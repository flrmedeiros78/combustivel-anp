import pandas as pd
from pathlib import Path
from impala.dbapi import connect
from config import IMPALA_HOST, IMPALA_PORT

destino = Path(__file__).parent / "painel" / "dados_gold" # 'sql'/'impala'/'03_gold'
tabelas = ["gold_preco_medio_estado", "gold_top3_mun_caros", "gold_variacao_mensal"]

def main() -> None:
    destino.mkdir(exist_ok=True)
    conn = connect(host=IMPALA_HOST, port=IMPALA_PORT)
    
    for t in tabelas:
        cur = conn.cursor()
        cur. execute(f"SELECT * FROOM anp.{t}")
        df = pd.DataFrame(cur.fetchall(), columns=[c[0] for c in cur.description])
        df.to_csv(destino / f"{t}.csv", index=False)
        print(f"[ok] {t}: {len(df)} Registros")
    conn.close()
    
if __name__ == "__main__":
    main()