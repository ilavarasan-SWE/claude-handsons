from typing import Any, Dict, TypedDict


class WorkflowState(TypedDict, total=False):
	file_path: str
	dataset_name: str
	bronze: Dict[str, Any]
	silver: Dict[str, Any]
	gold: Dict[str, Any]
	profile: Dict[str, Any]
	plan: Dict[str, Any]
	report: Dict[str, Any]
	status: str
	messages: list[str]
	warnings: list[str]
	error: str
	raw_preview: list[dict[str, Any]]
	cleaned_preview: list[dict[str, Any]]
	final_report: str
