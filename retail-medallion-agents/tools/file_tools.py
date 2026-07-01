"""File I/O utilities used across agents."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


def read_csv_sample(file_path: str | Path, n_rows: int = 1000) -> dict:
    """Return headers and sample rows from a CSV file."""
    file_path = Path(file_path)
    df = pd.read_csv(file_path, nrows=n_rows, low_memory=False)
    return {
        "headers": list(df.columns),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "rows": df.head(5).to_dict(orient="records"),
        "shape": list(df.shape),
    }


def load_json(path: str | Path) -> dict:
    """Load a JSON file and return its contents."""
    path = Path(path)
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data: dict, path: str | Path) -> None:
    """Save a dict to a JSON file, creating parent dirs as needed."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)


def save_dataframe(df: pd.DataFrame, path: str | Path) -> None:
    """Save a DataFrame to CSV, creating parent dirs as needed."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def load_dataframe(path: str | Path) -> pd.DataFrame:
    """Load a CSV file into a DataFrame."""
    return pd.read_csv(Path(path), low_memory=False)


def ensure_dirs(*paths: str | Path) -> None:
    """Create directories if they don't exist."""
    for p in paths:
        Path(p).mkdir(parents=True, exist_ok=True)
