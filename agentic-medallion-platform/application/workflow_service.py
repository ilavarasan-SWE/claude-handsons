from workflows.orchestrator import run_workflow


class WorkflowService:
	def run(self, file_path: str, dataset_name: str | None = None) -> dict:
		return run_workflow(file_path=file_path, dataset_name=dataset_name)
