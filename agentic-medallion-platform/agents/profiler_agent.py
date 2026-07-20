from pathlib import Path

import pandas as pd

from contracts.dataset_profile import DatasetMetadata, DatasetProfile
from tools.file_tool import describe_file, infer_dataset_name, load_csv
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
        file_path: str,
        dataframe: pd.DataFrame | None = None,
    ) -> DatasetProfile:

        dataframe = dataframe if dataframe is not None else load_csv(file_path)
        file_info = describe_file(file_path)
        dataset_name = dataset_name or infer_dataset_name(file_path)

        metadata = DatasetMetadata(
            dataset_name=dataset_name,
            source_type=file_info["source_type"],
            file_name=file_info["file_name"],
            file_size_bytes=file_info["file_size_bytes"],
            row_count=len(dataframe),
            column_count=len(dataframe.columns),
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


class MedallionWorkflowGraph:
    def __init__(self) -> None:
        from agents.orchestrator_agent import OrchestratorAgent

        self.orchestrator = OrchestratorAgent()

    def invoke(self, state: dict) -> dict:
        file_path = state.get("file_path")
        dataset_name = state.get("dataset_name")

        if not file_path:
            raise ValueError("file_path is required to run the workflow.")

        workflow_state = self.orchestrator.execute(file_path=file_path, dataset_name=dataset_name)

        merged_state = dict(state)
        merged_state.update(workflow_state)
        return merged_state


def create_graph() -> MedallionWorkflowGraph:
    return MedallionWorkflowGraph()