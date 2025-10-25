# streamlit_app.py
import streamlit as st
from app.data_loader import load_dataset, profile_dataframe
import os

st.set_page_config(page_title="Data-to-Insights Analyst", layout="wide")
st.title("Data-to-Insights Analyst (LangChain + CSV)")

f = st.file_uploader("Upload CSV or Parquet (≤ ~100 MB)", type=["csv","parquet"])
if f:
    os.makedirs(".cache", exist_ok=True)
    tmp_path = f".cache/_tmp_{f.name}"
    with open(tmp_path, "wb") as out:
        out.write(f.getbuffer())

    df = load_dataset(tmp_path)
    prof = profile_dataframe(df)

    st.success(f"Loaded {len(df):,} rows × {len(df.columns)} columns")
    with st.expander("Schema & Profile"):
        st.json(prof)
    st.dataframe(df.head(50))
