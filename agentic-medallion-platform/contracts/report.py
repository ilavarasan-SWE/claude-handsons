from typing import Any, Dict, List

from pydantic import Field

from contracts.base_artifact import BaseArtifact


class BusinessReport(BaseArtifact):
	artifact_type: str = Field(default="BusinessReport")
	source_file_path: str = Field(description="Path to the source dataset")
	executive_summary: str = Field(description="Short business summary")
	key_findings: List[str] = Field(default_factory=list)
	recommendations: List[str] = Field(default_factory=list)
	quality_notes: List[str] = Field(default_factory=list)
	workflow_notes: List[str] = Field(default_factory=list)
	metrics: Dict[str, Any] = Field(default_factory=dict)
	markdown_report: str = Field(default="")
