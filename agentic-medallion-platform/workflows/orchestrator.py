from agents.orchestrator_agent import OrchestratorAgent


def run_workflow(file_path: str, dataset_name: str | None = None) -> dict:
	orchestrator = OrchestratorAgent()
	return orchestrator.execute(file_path=file_path, dataset_name=dataset_name)


class OrchestratorWorkflow:
	def __init__(self) -> None:
		self.orchestrator = OrchestratorAgent()

	def invoke(self, state: dict) -> dict:
		file_path = state.get("file_path")
		dataset_name = state.get("dataset_name")

		if not file_path:
			raise ValueError("file_path is required to execute the workflow.")

		merged = dict(state)
		merged.update(self.orchestrator.execute(file_path=file_path, dataset_name=dataset_name))
		return merged
