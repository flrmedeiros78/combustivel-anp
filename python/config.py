from pathlib import Path

# config de diretorios
BASE_DIR = Path(__file__).resolve().parent.parent
SQL_DIR = BASE_DIR / "sql" / "impala"
OUTPUT_DIR = BASE_DIR /"docs"/"graficos"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Conexão com o Impala
IMPALA_HOST = "localhost"
IMPALA_PORT = 21050
IMPALA_DB = "anp"

CORES ={
    "gasolina": "#580b03",
    "etanol": "#27ae60",
    "diesel": "#2980b9",
    "GNV": "#b7f312",
}