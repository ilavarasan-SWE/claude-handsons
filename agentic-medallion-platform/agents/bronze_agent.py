from pathlib import Path

import pandas as pd

from contracts.bronze import BronzeArtifact
from tools.file_tool import describe_file, load_csv


class BronzeAgent:
	def execute(self, file_path: str, dataframe: pd.DataFrame | None = None) -> BronzeArtifact:
		dataframe = dataframe if dataframe is not None else load_csv(file_path)
		file_info = describe_file(file_path)
		preview = dataframe.head(10).fillna("").to_dict(orient="records")

		return BronzeArtifact(
			created_by="BronzeAgent",
			source_file_path=file_path,
			source_file_name=file_info["file_name"],
			row_count=int(len(dataframe)),
			column_count=int(len(dataframe.columns)),
			columns=[str(column) for column in dataframe.columns],
			dataframe_preview=preview,
			notes=[
				f"Loaded {len(dataframe)} rows and {len(dataframe.columns)} columns.",
				f"Source file: {Path(file_path).name}",
			],
			dataframe=dataframe,
		)
