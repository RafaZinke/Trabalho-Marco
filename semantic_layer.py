"""Camada semântica nativa do PandasAI 3."""
import json
import hashlib
import re
from pathlib import Path
import pandas as pd
import pandasai as pai
from pandas.api.types import is_bool_dtype, is_datetime64_any_dtype, is_integer_dtype, is_numeric_dtype

CONFIG = Path(__file__).with_name("semantic_config.json")

def infer_type(series):
    if is_bool_dtype(series): return "boolean"
    if is_datetime64_any_dtype(series): return "datetime"
    if is_integer_dtype(series): return "integer"
    if is_numeric_dtype(series): return "float"
    return "string"

def create_dataset(df: pd.DataFrame, sheet: str):
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    rules = config.get("columns", {})
    columns = [
        {
            "name": name,
            "type": rules.get(name, {}).get("type") or infer_type(df[name]),
            "description": rules.get(name, {}).get("description")
                or f"Campo {name.replace('_', ' ')} da base ME07; significado pendente de confirmação.",
        }
        for name in df.columns
    ]
    label = (re.sub(r"[^a-z0-9]+", "-", sheet.lower()).strip("-") or "base")[:20]
    fingerprint = hashlib.sha256(
        (pd.util.hash_pandas_object(df, index=True).values.tobytes()
         + json.dumps(config, sort_keys=True).encode("utf-8"))
    ).hexdigest()[:12]
    path = f"unidavi/me07-{label}-{fingerprint}"
    try:
        return pai.load(path), columns
    except Exception as exc:
        # Only a missing dataset permits creation; other loading errors must surface.
        if exc.__class__.__name__ != "DatasetNotFound":
            raise
    # Mantenha o CSV durante a sessão: a camada semântica pode lê-lo após create.
    cache = Path(__file__).resolve().parent / ".cache"
    cache.mkdir(exist_ok=True)
    file = cache / (path.split("/")[-1] + ".csv")
    df.to_csv(file, index=False)
    source = pai.read_csv(str(file))
    dataset = pai.create(
        path=path, df=source,
        description=config.get("description", "Base ME07"),
        columns=columns,
    )
    return dataset, columns
