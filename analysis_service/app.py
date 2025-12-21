from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import io
import pandas as pd
import os

from analysis.engine.factory import get_engine


class CorrelationRequest(BaseModel):
    backend: str = "pandas"
    news_csv: str = os.path.join(os.path.dirname(__file__), "..", "analysis", "..", "data", "output.csv")
    colcap_csv: str
    rolling: list[int] = [7, 14, 30]
    # Parallelization options
    mp_procs: int | None = None
    dask_nparts: int | None = None
    dask_distributed: bool = False
    dask_scheduler: str | None = None
    spark_master: str | None = None


class CorrelationInlineRequest(BaseModel):
    backend: str = "pandas"
    rolling: list[int] = [7, 14, 30]
    # Parallelization options
    mp_procs: int | None = None
    dask_nparts: int | None = None
    dask_distributed: bool = False
    dask_scheduler: str | None = None
    spark_master: str | None = None
    # CSV contents
    news_csv_text: str
    colcap_csv_text: str


app = FastAPI(title="Análisis Noticias vs COLCAP")


@app.post("/correlate")
def correlate(req: CorrelationRequest):
    try:
        engine = get_engine(
            req.backend,
            nprocs=req.mp_procs,
            npartitions=req.dask_nparts,
            distributed=req.dask_distributed,
            scheduler_address=req.dask_scheduler,
            master=req.spark_master,
        )  # type: ignore
        news_df = engine.load_news(req.news_csv)
        news_feat = engine.compute_news_features(news_df)
        colcap_df = engine.load_colcap(req.colcap_csv)
        joined = engine.align_series(news_feat, colcap_df)
        results = engine.compute_correlations(joined, methods=["pearson", "spearman"], rolling_windows=req.rolling)
        return {"status": "ok", "results": results}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/correlate-inline")
def correlate_inline(req: CorrelationInlineRequest):
    try:
        engine = get_engine(
            req.backend,
            nprocs=req.mp_procs,
            npartitions=req.dask_nparts,
            distributed=req.dask_distributed,
            scheduler_address=req.dask_scheduler,
            master=req.spark_master,
        )  # type: ignore

        # Parse CSV text into DataFrames
        news_df = pd.read_csv(io.StringIO(req.news_csv_text))
        news_df["fecha"] = news_df["fecha"].astype(str)
        news_feat = engine.compute_news_features(news_df)

        colcap_df = pd.read_csv(io.StringIO(req.colcap_csv_text))
        joined = engine.align_series(news_feat, colcap_df)
        results = engine.compute_correlations(joined, methods=["pearson", "spearman"], rolling_windows=req.rolling)
        return {"status": "ok", "results": results}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
