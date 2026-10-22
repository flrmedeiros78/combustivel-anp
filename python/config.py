from pathlib import Path

# config de diretorios
BASE_DIR = Path(__file__).resolve().parent.parent
SQL_DIR = BASE_DIR / "sql" / "impala" / "consultas"
OUTPUT_DIR = BASE_DIR /"docs"/"graficos" 
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Conexão com o Impala
IMPALA_HOST = "localhost"
IMPALA_PORT = 21050
IMPALA_DB = "anp"

CORES ={
    "gasolina": "#8540A5",
    "etanol": "#7088a3",
    "diesel": "#63853cf6",
    "gnv": "#f3a412",
}