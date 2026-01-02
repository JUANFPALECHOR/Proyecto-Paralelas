from typing import Any, Dict, List, Optional

try:
    from pyspark.sql import SparkSession, functions as F
except Exception as e:
    raise e

from ..base import AnalysisEngine
from ...utils.date import to_date


class SparkEngine(AnalysisEngine):
    def __init__(self, master: str | None = None, configs: dict | None = None) -> None:
        builder = SparkSession.builder.appName("AnalysisEngine")
        builder = builder.config("spark.sql.execution.arrow.pyspark.enabled", "true")
        if master:
            builder = builder.master(master)
        if configs:
            for k, v in configs.items():
                builder = builder.config(k, v)
        self.spark = builder.getOrCreate()

    def load_news(self, csv_path: str):
        df = self.spark.read.csv(csv_path, header=True, inferSchema=True)
        to_date_udf = F.udf(lambda s: to_date(s), "string")
        df = df.withColumn("fecha", to_date_udf(F.col("fecha"))).dropna(subset=["fecha"])
        return df

    def compute_news_features(self, news_df):
        # Sentiment: offload to Pandas for now due to complexity
        pdf = news_df.toPandas()
        from ...features.news_features import compute_daily_features
        feat = compute_daily_features(pdf)
        return self.spark.createDataFrame(feat)

    def load_colcap(self, csv_path: str):
        df = self.spark.read.csv(csv_path, header=True, inferSchema=True)
        to_date_udf = F.udf(lambda s: to_date(s), "string")
        df = df.withColumn("date", to_date_udf(F.col("date"))).dropna(subset=["date", "close"]).orderBy("date")
        return df

    def align_series(self, news_features_df, colcap_df):
        joined = news_features_df.join(colcap_df, on="date", how="inner")
        return joined

    def compute_correlations(
        self,
        joined_df,
        methods: Optional[List[str]] = None,
        rolling_windows: Optional[List[int]] = None,
    ) -> Dict[str, Any]:
        # Convert to Pandas for stats
        pdf = joined_df.toPandas()
        from .pandas_engine import PandasEngine
        return PandasEngine().compute_correlations(pdf, methods, rolling_windows)
