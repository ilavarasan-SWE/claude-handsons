from typing import Any, Dict, List

from contracts.bronze import BronzeArtifact
from contracts.gold import GoldArtifact
from contracts.silver import SilverArtifact
from tools.statistics_analyzer import StatisticsAnalyzer


class GoldAgent:
	def __init__(self) -> None:
		self.statistics_analyzer = StatisticsAnalyzer()

	def execute(self, bronze_artifact: BronzeArtifact, silver_artifact: SilverArtifact) -> GoldArtifact:
		if silver_artifact.dataframe is None:
			raise ValueError("Silver artifact does not contain a dataframe.")

		dataframe = silver_artifact.dataframe
		statistics_profile = self.statistics_analyzer.analyze(dataframe)

		key_metrics: Dict[str, Any] = {
			"row_count": int(len(dataframe)),
			"column_count": int(len(dataframe.columns)),
			"duplicate_rows_removed": int(bronze_artifact.row_count - silver_artifact.row_count_after),
			"numeric_columns": list(statistics_profile.numeric_statistics.keys()),
			"categorical_columns": list(statistics_profile.categorical_statistics.keys()),
		}

		insights: List[str] = [
			f"The curated dataset now has {len(dataframe)} rows and {len(dataframe.columns)} columns.",
			f"{len(statistics_profile.numeric_statistics)} numeric columns were summarized.",
			f"{len(statistics_profile.categorical_statistics)} categorical columns were summarized.",
		]

		summary_tables = {
			"numeric_statistics": statistics_profile.numeric_statistics,
			"categorical_statistics": statistics_profile.categorical_statistics,
			"date_statistics": statistics_profile.date_statistics,
		}

		return GoldArtifact(
			created_by="GoldAgent",
			source_file_path=bronze_artifact.source_file_path,
			row_count=int(len(dataframe)),
			column_count=int(len(dataframe.columns)),
			key_metrics=key_metrics,
			summary_tables=summary_tables,
			insights=insights,
			dataframe_preview=dataframe.head(10).fillna("").to_dict(orient="records"),
			dataframe=dataframe,
		)
