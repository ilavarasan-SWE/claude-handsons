from typing import Any, Dict, List, Optional

from pydantic import Field

from contracts.base_artifact import BaseArtifact
from contracts.enums import WorkflowStatus


class ExecutionResult(BaseArtifact):
	artifact_type: str = Field(default="ExecutionResult")
	stage_name: str = Field(description="Workflow stage name")
	status: WorkflowStatus = Field(default=WorkflowStatus.PENDING)
	message: str = Field(default="")
	payload: Dict[str, Any] = Field(default_factory=dict)
	warnings: List[str] = Field(default_factory=list)
	errors: List[str] = Field(default_factory=list)
	next_stage: Optional[str] = Field(default=None)
