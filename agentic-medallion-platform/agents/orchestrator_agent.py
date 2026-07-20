from agents.bronze_agent import BronzeAgent
from agents.gold_agent import GoldAgent
from agents.profiler_agent import ProfilerAgent
from agents.reporter_agent import ReporterAgent
from agents.silver_agent import SilverAgent
from agents.sttm_agent import STTMAgent
from contracts.workflow_state import WorkflowState
from tools.file_tool import infer_dataset_name, load_csv


class OrchestratorAgent:
	def __init__(self) -> None:
		self.bronze_agent = BronzeAgent()
		self.silver_agent = SilverAgent()
		self.gold_agent = GoldAgent()
		self.reporter_agent = ReporterAgent()
		self.sttm_agent = STTMAgent()
		self.profiler_agent = ProfilerAgent()

	def execute(self, file_path: str, dataset_name: str | None = None) -> WorkflowState:
		resolved_dataset_name = dataset_name or infer_dataset_name(file_path)
		dataframe = load_csv(file_path)

		bronze_artifact = self.bronze_agent.execute(file_path=file_path, dataframe=dataframe)
		profile = self.profiler_agent.execute(
			dataset_name=resolved_dataset_name,
			file_path=file_path,
			dataframe=dataframe,
		)
		plan = self.sttm_agent.execute(file_path=file_path, dataset_name=resolved_dataset_name, profile=profile)
		silver_artifact = self.silver_agent.execute(bronze_artifact)
		gold_artifact = self.gold_agent.execute(bronze_artifact, silver_artifact)

		workflow_notes = [
			f"Bronze stage loaded {bronze_artifact.row_count} rows.",
			f"Silver stage produced {silver_artifact.row_count_after} cleaned rows.",
			f"Gold stage summarized {gold_artifact.row_count} curated rows.",
		]

		report = self.reporter_agent.execute(
			dataset_name=resolved_dataset_name,
			quality_profile=profile.quality,
			gold_artifact=gold_artifact,
			workflow_notes=workflow_notes,
		)

		return {
			"file_path": file_path,
			"dataset_name": resolved_dataset_name,
			"bronze": bronze_artifact.model_dump(),
			"silver": silver_artifact.model_dump(),
			"gold": gold_artifact.model_dump(),
			"profile": profile.model_dump(),
			"plan": plan.model_dump(),
			"report": report.model_dump(),
			"status": "COMPLETED",
			"messages": workflow_notes,
			"warnings": [],
			"raw_preview": bronze_artifact.dataframe_preview,
			"cleaned_preview": silver_artifact.dataframe_preview,
			"final_report": report.markdown_report,
		}
