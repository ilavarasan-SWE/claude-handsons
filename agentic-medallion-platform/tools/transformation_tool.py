from __future__ import annotations

from typing import List, Tuple

import pandas as pd


class TransformationTool:
	def clean_dataframe(self, dataframe: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
		cleaned = dataframe.copy()
		notes: List[str] = []

		cleaned.columns = [self._normalize_column_name(column) for column in cleaned.columns]
		notes.append("Normalized column names to snake_case style.")

		object_columns = cleaned.select_dtypes(include=["object", "string"]).columns
		for column in object_columns:
			cleaned[column] = cleaned[column].astype("string").str.strip()
			cleaned[column] = cleaned[column].replace({"": pd.NA})

		duplicate_rows = int(cleaned.duplicated().sum())
		if duplicate_rows:
			cleaned = cleaned.drop_duplicates().reset_index(drop=True)
			notes.append(f"Removed {duplicate_rows} duplicate rows.")

		null_columns = int(cleaned.isnull().any().sum())
		if null_columns:
			notes.append(f"Preserved missing values in {null_columns} columns for downstream handling.")

		if not notes:
			notes.append("No structural transformations were required.")

		return cleaned, notes

	@staticmethod
	def _normalize_column_name(column_name: str) -> str:
		normalized = "".join(char.lower() if char.isalnum() else "_" for char in column_name)
		while "__" in normalized:
			normalized = normalized.replace("__", "_")
		return normalized.strip("_") or "column"
