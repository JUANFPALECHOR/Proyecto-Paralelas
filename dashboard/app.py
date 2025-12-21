import os
import streamlit as st
import requests
import pandas as pd


API_URL = os.getenv("ANALYSIS_API_URL", "http://localhost:8000")

st.set_page_config(page_title="Noticias vs COLCAP", layout="wide")
st.title("Dashboard: Correlación Noticias vs COLCAP")
st.caption(f"API: {API_URL}")

st.sidebar.header("Configuración")
backend = st.sidebar.selectbox("Backend", ["pandas", "multiprocessing", "dask", "spark"], index=0)
rolling = st.sidebar.multiselect("Ventanas rolling", [7, 14, 30], default=[7, 14, 30])
mp_procs = st.sidebar.number_input("Procesos (MP)", min_value=1, value=4)
dask_nparts = st.sidebar.number_input("Particiones (Dask)", min_value=1, value=8)
dask_distributed = st.sidebar.checkbox("Dask Distributed", value=False)
dask_scheduler = st.sidebar.text_input("Dask Scheduler", value="")
spark_master = st.sidebar.text_input("Spark Master", value="")

st.subheader("Subir CSVs")
news_file = st.file_uploader("CSV de noticias (output.csv)", type=["csv"])
colcap_file = st.file_uploader("CSV de COLCAP (date,close)", type=["csv"], key="colcap")

run_btn = st.button("Calcular correlación")

if run_btn:
    if not news_file or not colcap_file:
        st.error("Debes subir ambos CSVs.")
    else:
        news_text = news_file.read().decode("utf-8")
        colcap_text = colcap_file.read().decode("utf-8")

        payload = {
            "backend": backend,
            "rolling": rolling,
            "mp_procs": mp_procs,
            "dask_nparts": dask_nparts,
            "dask_distributed": dask_distributed,
            "dask_scheduler": dask_scheduler or None,
            "spark_master": spark_master or None,
            "news_csv_text": news_text,
            "colcap_csv_text": colcap_text,
        }

        try:
            resp = requests.post(f"{API_URL}/correlate-inline", json=payload, timeout=60)
            if resp.status_code != 200:
                st.error(f"Error: {resp.status_code} - {resp.text}")
            else:
                data = resp.json()["results"]
                st.success("Correlación calculada")

                # Show tables
                st.subheader("Pearson")
                st.table(pd.DataFrame([data.get("pearson", {})]))
                st.subheader("Spearman")
                st.table(pd.DataFrame([data.get("spearman", {})]))

                # Rolling as df
                rolling_df = pd.DataFrame(data.get("rolling", {})).T
                st.subheader("Rolling (último valor por ventana)")
                st.dataframe(rolling_df)
        except Exception as e:
            st.error(str(e))
