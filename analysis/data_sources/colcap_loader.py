import pandas as pd
from typing import Optional

from ..utils.date import to_date


def load_colcap_csv(csv_path: str) -> pd.DataFrame:
    """Load COLCAP series from CSV.

    Expected columns: 'date' (YYYY-MM-DD or variants), 'close' (float).
    """
    df = pd.read_csv(csv_path)
    if "date" not in df.columns or "close" not in df.columns:
        raise ValueError("COLCAP CSV must have 'date' and 'close' columns")
    df["date"] = df["date"].apply(to_date)
    df = df.dropna(subset=["date", "close"]).copy()
    df = df.sort_values("date")
    return df
