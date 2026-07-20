from contracts.gold import GoldArtifact
from contracts.report import BusinessReport
from tools.quality_tool import QualityTool
from tools.reporting_tool import ReportingTool


class ReporterAgent:
	def __init__(self) -> None:
		self.reporting_tool = ReportingTool()

	def execute(self, dataset_name: str, quality_profile, gold_artifact: GoldArtifact, workflow_notes: list[str]) -> BusinessReport:
		quality_notes = QualityTool.describe(quality_profile)
		key_findings = list(gold_artifact.insights)
		key_findings.append(f"Quality score: {quality_profile.quality_score}/100")

		recommendations = []
		if quality_profile.duplicate_rows:
			recommendations.append("Review duplicate source rows before publishing downstream extracts.")
		if quality_profile.total_null_values:
			recommendations.append("Address missing values in critical business columns.")
		if not recommendations:
			recommendations.append("Dataset is ready for downstream consumption.")

		executive_summary = (
			f"{dataset_name} is a structured dataset with {gold_artifact.row_count} curated rows and "
			f"{gold_artifact.column_count} columns."
		)

		markdown_report = self.reporting_tool.generate_markdown(
			dataset_name=dataset_name,
			executive_summary=executive_summary,
			key_findings=key_findings,
			recommendations=recommendations,
			quality_notes=quality_notes,
			workflow_notes=workflow_notes,
		)

		return BusinessReport(
			created_by="ReporterAgent",
			source_file_path=gold_artifact.source_file_path,
			executive_summary=executive_summary,
			key_findings=key_findings,
			recommendations=recommendations,
			quality_notes=quality_notes,
			workflow_notes=workflow_notes,
			metrics=gold_artifact.key_metrics,
			markdown_report=markdown_report,
		)
