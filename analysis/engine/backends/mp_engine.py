from typing import Any, Dict, List, Optional

import pandas as pd
import numpy as np
from multiprocessing import Pool, cpu_count
from scipy import stats

from ..base import AnalysisEngine
from ...features.news_features import compute_daily_features
from ...utils.date import to_date


def _parse_date(text: str) -> Optional[str]:
    return to_date(text)


class MultiprocessingEngine(AnalysisEngine):
    def __init__(self, nprocs: int | None = None) -> None:
        self.nprocs = nprocs or cpu_count()

    def load_news(self, csv_path: str) -> pd.DataFrame:
        df = pd.read_csv(csv_path)
        with Pool(self.nprocs) as pool:
            parsed = pool.map(_parse_date, df["fecha"].astype(str).tolist())
        df["fecha"] = parsed
        df = df.dropna(subset=["fecha"]).copy()
        return df

    def compute_news_features(self, news_df: pd.DataFrame) -> pd.DataFrame:
        # Sentiment computation is inside compute_daily_features
        return compute_daily_features(news_df)

    def load_colcap(self, csv_path: str) -> pd.DataFrame:
        col = pd.read_csv(csv_path)
        col["date"] = col["date"].apply(to_date)
        col = col.dropna(subset=["date", "close"]).copy()
        col = col.sort_values("date")
        return col

    def align_series(self, news_features_df: pd.DataFrame, colcap_df: pd.DataFrame) -> pd.DataFrame:
        joined = pd.merge(news_features_df, colcap_df, on="date", how="inner")
        return joined

    def compute_correlations(
        self,
        joined_df: pd.DataFrame,
        methods: Optional[List[str]] = None,
        rolling_windows: Optional[List[int]] = None,
    ) -> Dict[str, Any]:
        methods = methods or ["pearson", "spearman"]
        rolling_windows = rolling_windows or [7, 14, 30]

        results: Dict[str, Any] = {}

        feature_cols = [c for c in joined_df.columns if c in {"article_count", "avg_length", "sentiment_mean"}]
        close = joined_df["close"].astype(float)

        for m in methods:
            m_res: Dict[str, float] = {}
            for f in feature_cols:
                series = joined_df[f].astype(float)
                if m == "pearson":
                    coef = np.corrcoef(series, close)[0, 1]
                elif m == "spearman":
                    coef, _ = stats.spearmanr(series, close, nan_policy="omit")
                else:
                    continue
                m_res[f] = float(coef) if pd.notnull(coef) else np.nan
            results[m] = m_res

        rolling: Dict[str, Dict[int, Dict[str, float]]] = {}
        df_roll = joined_df.copy()
        for win in rolling_windows:
            roll_res: Dict[str, float] = {}
            for f in feature_cols:
                corr_series = df_roll[f].rolling(win).corr(df_roll["close"])  # type: ignore
                roll_res[f] = float(corr_series.iloc[-1]) if len(corr_series) else np.nan
            rolling[str(win)] = roll_res
        results["rolling"] = rolling

        return results
