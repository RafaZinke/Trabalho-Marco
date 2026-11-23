"""Envia a aba escolhida para uma tabela PostgreSQL no Supabase."""
import os
import re
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine
from function import sheets, load_excel

def main():
    load_dotenv()
    url = os.getenv("DATABASE_URL")
    if not url:
        raise SystemExit("Configure DATABASE_URL no .env.")
    table = os.getenv("DB_TABLE", "me07")
    if not re.fullmatch(r"[A-Za-z_][A-Za-z_0-9]*", table):
        raise SystemExit("DB_TABLE inválido.")
    sheet = sys.argv[1] if len(sys.argv) > 1 else sheets()[0]
    data = load_excel(sheet)
    print(f"Aba {sheet}: {len(data)} linhas -> tabela {table}")
    if input("Digite IMPORTAR para substituir essa tabela: ") != "IMPORTAR":
        raise SystemExit("Cancelado.")
    engine = create_engine(url, pool_pre_ping=True)
    data.to_sql(table, engine, if_exists="replace", index=False, chunksize=500, method="multi")
    print("Importação concluída.")

if __name__ == "__main__":
    main()
