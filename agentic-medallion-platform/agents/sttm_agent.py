from contracts.dataset_profile import DatasetProfile
from contracts.transformation_plan import TransformationPlan, TransformationStep


class STTMAgent:
	def execute(self, file_path: str, dataset_name: str, profile: DatasetProfile) -> TransformationPlan:
		steps = [
			TransformationStep(
				step_name="bronze_load",
				description="Load the source CSV into the bronze layer.",
			),
			TransformationStep(
				step_name="silver_clean",
				description="Normalize column names and trim text fields in the silver layer.",
			),
			TransformationStep(
				step_name="gold_summarize",
				description="Summarize curated data and generate business metrics in the gold layer.",
			),
			TransformationStep(
				step_name="report_publish",
				description="Publish a markdown report for business stakeholders.",
			),
		]

		if profile.quality.issues:
			steps.insert(
				2,
				TransformationStep(
					step_name="quality_review",
					description="Review quality issues and decide whether to fix or flag them.",
				),
			)

		return TransformationPlan(
			created_by="STTMAgent",
			source_file_path=file_path,
			objective=f"Create a clean medallion-style flow for {dataset_name}.",
			steps=steps,
			expected_outcome="A usable report-ready dataset with a reproducible transformation trail.",
		)
