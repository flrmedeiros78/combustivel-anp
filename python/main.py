from pathlib import Path
from db import executar_query
from graficos import grafico_f1, grafico_f2, grafico_f3

SQL_DIR = Path(__file__).parent.parent / "sql" / "impala"

def ler_sql(nome:str)-> str:
    return (SQL_DIR / nome).read_text(encoding="utf-8")

def main():
# F.1
    df1 =  executar_query("f1_preco_medio_estado")
    grafico_f1(df1)

    # F.2
    df2 = executar_query("f2_top3_municipios_caros")
    grafico_f2(df2)

    # F.3
    df3 = executar_query("f3_variacao_mensal_preco")
    grafico_f3(df3)
    
    
if __name__ == "__main__":
    main()

     
     
     

 

