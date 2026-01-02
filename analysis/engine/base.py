from typing import Any, Dict, List, Optional


class AnalysisEngine:
    """Backend-agnostic analysis engine interface.

    Concrete implementations should provide DataFrame-like operations using
    their respective backends (Pandas, Dask, Spark, Multiprocessing).
    """

    def load_news(self, csv_path: str) -> Any:
        """Load ingested news CSV.

        Expected columns: ['url','dominio','titulo','fecha','texto','longitud'].
        Returns a backend-specific DataFrame.
        """
        raise NotImplementedError

    def compute_news_features(self, news_df: Any) -> Any:
        """Aggregate per-date features like article_count, avg_length, sentiment_mean.

        Returns a backend-specific DataFrame indexed or keyed by date (YYYY-MM-DD).
        """
        raise NotImplementedError

    def load_colcap(self, csv_path: str) -> Any:
        """Load COLCAP time series from CSV with columns ['date','close']."""
        raise NotImplementedError

    def align_series(self, news_features_df: Any, colcap_df: Any) -> Any:
        """Align daily features with COLCAP closes by date, returning joined DataFrame."""
        raise NotImplementedError

    def compute_correlations(
        self,
        joined_df: Any,
        methods: Optional[List[str]] = None,
        rolling_windows: Optional[List[int]] = None,
    ) -> Dict[str, Any]:
        """Compute correlations and rolling correlations.

        Returns a dictionary with keys like 'pearson', 'spearman', 'rolling'.
        """
        raise NotImplementedError
