import pandas as pd

from contracts.dataset_profile import (
    DatasetMetadata,
    DatasetProfile,
)
from tools.quality_analyzer import QualityAnalyzer
from tools.schema_analyzer import SchemaAnalyzer
from tools.semantic_analyzer import SemanticAnalyzer
from tools.statistics_analyzer import StatisticsAnalyzer
from tools.summary_generator import SummaryGenerator


class ProfilerAgent:

    def __init__(self):

        self.schema = SchemaAnalyzer()
        self.quality = QualityAnalyzer()
        self.statistics = StatisticsAnalyzer()
        self.semantic = SemanticAnalyzer()
        self.summary = SummaryGenerator()

    def execute(
        self,
        dataset_name: str,
        dataframe: pd.DataFrame,
    ) -> DatasetProfile:

        metadata = DatasetMetadata(
            dataset_name=dataset_name,
            total_rows=len(dataframe),
            total_columns=len(dataframe.columns),
        )

        columns = self.schema.analyze(dataframe)

        quality = self.quality.analyze(dataframe)

        statistics = self.statistics.analyze(dataframe)

        semantic_hints = self.semantic.analyze(
            dataset_name,
            columns,
        )

        ai_summary = self.summary.generate(
            dataset_name,
            columns,
            quality,
            statistics,
        )

        return DatasetProfile(
            metadata=metadata,
            columns=columns,
            quality=quality,
            statistics=statistics,
            semantic_hints=semantic_hints,
            ai_summary=ai_summary,
        )