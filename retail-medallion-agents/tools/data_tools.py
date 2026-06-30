"""Data analysis utilities used across agents."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pandas as pd


def compute_column_stats(file_path: str | Path, column_name: str) -> dict:
    """Return statistics for a single column in a CSV file."""
    df = pd.read_csv(Path(file_path), usecols=[column_name], low_memory=False)
    series = df[column_name]
    stats: dict[str, Any] = {
        "column": column_name,
        "dtype": str(series.dtype),
        "null_count": int(series.isna().sum()),
        "null_pct": round(series.isna().mean() * 100, 2),
        "unique_count": int(series.nunique()),
        "sample_values": [str(v) for v in series.dropna().head(3).tolist()],
    }
    if pd.api.types.is_numeric_dtype(series):
        stats["min"] = float(series.min()) if not series.isna().all() else None
        stats["max"] = float(series.max()) if not series.isna().all() else None
        stats["mean"] = float(series.mean()) if not series.isna().all() else None
    return stats


def detect_date_columns(file_path: str | Path) -> list[str]:
    """Heuristically detect columns that likely contain dates."""
    df = pd.read_csv(Path(file_path), nrows=200, low_memory=False)
    date_keywords = re.compile(
        r"date|time|day|month|year|dt|created|updated|ts|timestamp",
        re.IGNORECASE,
    )
    candidates = []
    for col in df.columns:
        if date_keywords.search(col):
            candidates.append(col)
            continue
        sample = df[col].dropna().head(20).astype(str)
        parsed = pd.to_datetime(sample, errors="coerce", infer_datetime_format=True)
        if parsed.notna().mean() > 0.7:
            candidates.append(col)
    return list(dict.fromkeys(candidates))


def count_duplicates(file_path: str | Path) -> int:
    """Return the number of fully duplicate rows in a CSV file."""
    df = pd.read_csv(Path(file_path), low_memory=False)
    return int(df.duplicated().sum())


def to_snake_case(name: str) -> str:
    """Convert a column name to snake_case."""
    name = re.sub(r"[\s\-\.]+", "_", name.strip())
    name = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
    name = re.sub(r"([a-z\d])([A-Z])", r"\1_\2", name)
    return name.lower().lstrip("_")


def build_rename_map(columns: list[str]) -> dict[str, str]:
    """Build a {original: snake_case} rename mapping."""
    return {col: to_snake_case(col) for col in columns}


def safe_cast(series: pd.Series, target_type: str) -> pd.Series:
    """Attempt to cast a Series to target_type; return original on failure."""
    try:
        if target_type in ("int", "int64", "integer"):
            return pd.to_numeric(series, errors="coerce").astype("Int64")
        if target_type in ("float", "float64", "numeric"):
            return pd.to_numeric(series, errors="coerce")
        if target_type in ("date", "datetime", "datetime64"):
            return pd.to_datetime(series, errors="coerce", infer_datetime_format=True)
        if target_type in ("str", "string", "object", "categorical"):
            return series.astype(str).replace("nan", pd.NA)
        return series
    except Exception:
        return series


def summarize_dataframe(df: pd.DataFrame, max_rows: int = 50) -> dict:
    """Return a compact JSON-serialisable summary of a DataFrame."""
    return {
        "shape": list(df.shape),
        "columns": list(df.columns),
        "sample": df.head(max_rows).to_dict(orient="records"),
        "dtypes": {col: str(dt) for col, dt in df.dtypes.items()},
        "null_counts": df.isna().sum().to_dict(),
    }
