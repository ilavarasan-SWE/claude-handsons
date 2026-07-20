from typing import List

import pandas as pd

from tools.quality_analyzer import QualityAnalyzer


class QualityTool:
	def __init__(self) -> None:
		self.analyzer = QualityAnalyzer()

	def analyze(self, dataframe: pd.DataFrame):
		return self.analyzer.analyze(dataframe)

	@staticmethod
	def describe(quality_profile) -> List[str]:
		notes = [f"Quality score: {quality_profile.quality_score}/100"]

		if quality_profile.duplicate_rows:
			notes.append(f"Duplicate rows detected: {quality_profile.duplicate_rows}")

		if quality_profile.total_null_values:
			notes.append(f"Missing values detected: {quality_profile.total_null_values}")

		if quality_profile.issues:
			notes.extend(quality_profile.issues)

		return notes
