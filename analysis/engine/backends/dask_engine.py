from typing import Any, Dict, List, Optional

import dask.dataframe as dd
import numpy as np
from scipy import stats

from ..base import AnalysisEngine
from ...features.news_features import compute_daily_features
from ...utils.date import to_date


class DaskEngine(AnalysisEngine):
    def __init__(self, npartitions: int | None = None, distributed: bool = False, scheduler_address: str | None = None) -> None:
        self.npartitions = npartitions
        self.distributed = distributed
        self.scheduler_address = scheduler_address

        if self.distributed:
            try:
                from dask.distributed import Client
                self.client = Client(address=self.scheduler_address) if self.scheduler_address else Client()
            except Exception:
                self.client = None

    def load_news(self, csv_path: str) -> dd.DataFrame:
        ddf = dd.read_csv(csv_path, assume_missing=True)
        ddf["fecha"] = ddf["fecha"].map_partitions(lambda s: s.astype(str).apply(to_date), meta=("fecha", "object"))
        ddf = ddf.dropna(subset=["fecha"])  # type: ignore
        return ddf

    def compute_news_features(self, news_df: dd.DataFrame) -> dd.DataFrame:
        # For sentiment, compute in Pandas then convert to Dask (simpler, keeps correctness)
        pdf = news_df.compute()
        pdf_feat = compute_daily_features(pdf)
        nparts = self.npartitions or max(1, len(pdf_feat) // 50)
        return dd.from_pandas(pdf_feat, npartitions=nparts)

    def load_colcap(self, csv_path: str) -> dd.DataFrame:
        ddf = dd.read_csv(csv_path, assume_missing=True)
        ddf["date"] = ddf["date"].map_partitions(lambda s: s.astype(str).apply(to_date), meta=("date", "object"))
        ddf = ddf.dropna(subset=["date", "close"])  # type: ignore
        return ddf

    def align_series(self, news_features_df: dd.DataFrame, colcap_df: dd.DataFrame) -> dd.DataFrame:
        joined = dd.merge(news_features_df, colcap_df, on="date", how="inner")
        return joined

    def compute_correlations(
        self,
        joined_df: dd.DataFrame,
        methods: Optional[List[str]] = None,
        rolling_windows: Optional[List[int]] = None,
    ) -> Dict[str, Any]:
        # Compute to Pandas for stats
        pdf = joined_df.compute()
        from .pandas_engine import PandasEngine

        return PandasEngine().compute_correlations(pdf, methods, rolling_windows)
