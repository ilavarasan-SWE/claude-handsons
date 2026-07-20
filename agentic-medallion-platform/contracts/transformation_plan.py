from typing import List

from pydantic import BaseModel, Field

from contracts.base_artifact import BaseArtifact


class TransformationStep(BaseModel):
	step_name: str = Field(description="Step name")
	description: str = Field(description="What the step does")
	owner: str = Field(default="STTMAgent")


class TransformationPlan(BaseArtifact):
	artifact_type: str = Field(default="TransformationPlan")
	source_file_path: str = Field(description="Path to the source dataset")
	objective: str = Field(description="What the plan is trying to achieve")
	steps: List[TransformationStep] = Field(default_factory=list)
	expected_outcome: str = Field(default="")
