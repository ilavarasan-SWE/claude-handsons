from agents.reporter_agent import ReporterAgent


class ReportingService:
	def __init__(self) -> None:
		self.reporter = ReporterAgent()

	def build_report(self, dataset_name: str, quality_profile, gold_artifact, workflow_notes: list[str]):
		return self.reporter.execute(dataset_name, quality_profile, gold_artifact, workflow_notes)
