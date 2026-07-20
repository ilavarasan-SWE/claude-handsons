from pathlib import Path
from typing import Iterable, Optional

import pandas as pd


def load_csv(file_path: str, encodings: Optional[Iterable[str]] = None) -> pd.DataFrame:
	attempts = list(encodings or ("utf-8-sig", "utf-8", "latin1"))
	last_error: Exception | None = None

	for encoding in attempts:
		try:
			return pd.read_csv(file_path, encoding=encoding)
		except Exception as error:
			last_error = error

	raise last_error or ValueError(f"Unable to read CSV: {file_path}")


def describe_file(file_path: str) -> dict:
	path = Path(file_path)
	return {
		"file_name": path.name,
		"file_size_bytes": path.stat().st_size if path.exists() else 0,
		"source_type": path.suffix.lstrip(".").upper() or "CSV",
	}


def infer_dataset_name(file_path: str) -> str:
	return Path(file_path).stem.replace("_", " ").replace("-", " ").title()
