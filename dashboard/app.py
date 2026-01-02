import os
import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go


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
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Pearson")
                    pearson_data = data.get("pearson", {})
                    pearson_df = pd.DataFrame([pearson_data])
                    st.table(pearson_df)
                    
                    # Gráfica de barras para Pearson
                    if pearson_data:
                        fig_pearson = go.Figure(data=[
                            go.Bar(x=list(pearson_data.keys()), y=list(pearson_data.values()))
                        ])
                        fig_pearson.update_layout(
                            title="Correlación de Pearson",
                            xaxis_title="Feature",
                            yaxis_title="Correlación",
                            height=400,
                            yaxis=dict(range=[-1, 1])
                        )
                        st.plotly_chart(fig_pearson, use_container_width=True)
                
                with col2:
                    st.subheader("Spearman")
                    spearman_data = data.get("spearman", {})
                    spearman_df = pd.DataFrame([spearman_data])
                    st.table(spearman_df)
                    
                    # Gráfica de barras para Spearman
                    if spearman_data:
                        fig_spearman = go.Figure(data=[
                            go.Bar(x=list(spearman_data.keys()), y=list(spearman_data.values()))
                        ])
                        fig_spearman.update_layout(
                            title="Correlación de Spearman",
                            xaxis_title="Feature",
                            yaxis_title="Correlación",
                            height=400,
                            yaxis=dict(range=[-1, 1])
                        )
                        st.plotly_chart(fig_spearman, use_container_width=True)

                # Rolling correlations
                rolling_df = pd.DataFrame(data.get("rolling", {})).T
                st.subheader("Rolling (último valor por ventana)")
                st.dataframe(rolling_df)
                
                # Gráfica de líneas para Rolling
                if not rolling_df.empty:
                    fig_rolling = go.Figure()
                    for col in rolling_df.columns:
                        fig_rolling.add_trace(go.Scatter(
                            x=rolling_df.index.astype(str),
                            y=rolling_df[col],
                            mode='lines+markers',
                            name=col
                        ))
                    fig_rolling.update_layout(
                        title="Correlaciones Rolling",
                        xaxis_title="Ventana (días)",
                        yaxis_title="Correlación",
                        height=400
                    )
                    st.plotly_chart(fig_rolling, use_container_width=True)
        except Exception as e:
            st.error(str(e))
