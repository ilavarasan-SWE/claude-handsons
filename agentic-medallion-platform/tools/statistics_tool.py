import pandas as pd

from tools.statistics_analyzer import StatisticsAnalyzer


class StatisticsTool:
	def __init__(self) -> None:
		self.analyzer = StatisticsAnalyzer()

	def analyze(self, dataframe: pd.DataFrame):
		return self.analyzer.analyze(dataframe)
