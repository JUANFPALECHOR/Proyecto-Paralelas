from typing import Dict

import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


def compute_daily_features(news_df: pd.DataFrame) -> pd.DataFrame:
    """Compute per-date features from ingested news.

    Input columns: 'fecha', 'texto', 'longitud'.
    Output columns: 'date', 'article_count', 'avg_length', 'sentiment_mean'.
    """
    if "fecha" not in news_df.columns:
        raise ValueError("Expected 'fecha' column in news_df")

    df = news_df.copy()
    df = df.dropna(subset=["fecha"]).copy()

    # Sentiment per article (compound)
    analyzer = SentimentIntensityAnalyzer()
    sentiments = []
    texts = df["texto"].fillna("").astype(str).tolist()
    for t in texts:
        s = analyzer.polarity_scores(t)["compound"]
        sentiments.append(s)
    df["sentiment"] = sentiments

    # Aggregate per date
    grp = df.groupby("fecha")
    agg = grp.agg(
        article_count=("url", "count"),
        avg_length=("longitud", "mean"),
        sentiment_mean=("sentiment", "mean"),
    ).reset_index()

    agg = agg.rename(columns={"fecha": "date"})
    return agg
