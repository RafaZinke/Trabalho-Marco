"""Fontes de dados da ME07."""
import os
import re
import unicodedata
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent

def normalize(df):
    df = df.dropna(how="all").dropna(axis=1, how="all").copy()
    used = set()
    names = []
    for i, col in enumerate(df.columns, 1):
        base = unicodedata.normalize("NFKD", str(col)).encode("ascii", "ignore").decode()
        base = re.sub(r"[^a-zA-Z0-9]+", "_", base).strip("_").lower() or f"coluna_{i}"
        name, n = base, 2
        while name in used:
            name, n = f"{base}_{n}", n + 1
        used.add(name)
        names.append(name)
    df.columns = names
    return df

def excel_path():
    file = Path(os.getenv("BASE_XLSX", ROOT / "ME07(2).xlsx"))
    if not file.is_file():
        raise FileNotFoundError(f"Coloque ME07(2).xlsx na pasta do projeto: {file}")
    return file

def sheets():
    return pd.ExcelFile(excel_path()).sheet_names

def load_excel(sheet):
    df = normalize(pd.read_excel(excel_path(), sheet_name=sheet))
    if df.empty:
        raise ValueError("A aba selecionada não contém registros.")
    return df

def load_supabase():
    from sqlalchemy import create_engine, text
    url = os.getenv("DATABASE_URL")
    table = os.getenv("DB_TABLE", "me07")
    if not url:
        raise ValueError("Configure DATABASE_URL no .env.")
    if not re.fullmatch(r"[A-Za-z_][A-Za-z_0-9]*", table):
        raise ValueError("Nome de tabela inválido.")
    with create_engine(url, pool_pre_ping=True).connect() as conn:
        df = pd.read_sql_query(text(f'SELECT * FROM "{table}"'), conn)
    if df.empty:
        raise ValueError("A tabela do Supabase está vazia.")
    return normalize(df)
