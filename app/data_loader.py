# app/data_loader.py
from __future__ import annotations
import hashlib, os, duckdb, pandas as pd

CACHE_DIR = ".cache"

def _file_fingerprint(path: str, head_bytes: int = 2_000_000) -> str:
    h = hashlib.md5()
    size = os.path.getsize(path)
    with open(path, "rb") as f:
        h.update(f.read(head_bytes))
    h.update(str(size).encode())
    return h.hexdigest()

#CSV --> Parquet 
def csv_to_parquet_cache(csv_path: str) -> str:
    os.makedirs(CACHE_DIR, exist_ok=True)
    fp = _file_fingerprint(csv_path)
    pq_path = os.path.join(CACHE_DIR, f"{fp}.parquet")
    if not os.path.exists(pq_path):
        con = duckdb.connect()
        con.execute(
            f"COPY (SELECT * FROM read_csv_auto('{csv_path}', SAMPLE_SIZE=200000)) "
            f"TO '{pq_path}' (FORMAT 'parquet');"
        )
        con.close()
    return pq_path

#Dataframe conversion to parquet 
def load_dataset(path: str) -> pd.DataFrame:
    if path.lower().endswith(".csv"):
        path = csv_to_parquet_cache(path)
    return pd.read_parquet(path)

#Defining dataset dtype , column, unqiue & null value for further processing
def profile_dataframe(df: pd.DataFrame) -> dict:
    cols = []
    for c in df.columns:
        s = df[c]
        cols.append({
            "column": c,
            "dtype": str(s.dtype),
            "null_pct": float(s.isna().mean() * 100),
            "unique": int(s.nunique()) if s.nunique() < 1_000_000 else 1_000_000
        })
    return {"n_rows": int(len(df)), "n_cols": len(df.columns), "columns": cols}
