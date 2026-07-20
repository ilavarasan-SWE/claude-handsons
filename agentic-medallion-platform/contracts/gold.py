from typing import Any, Dict, List, Optional

from pandas import DataFrame
from pydantic import ConfigDict, Field

from contracts.base_artifact import BaseArtifact


class GoldArtifact(BaseArtifact):
	model_config = ConfigDict(arbitrary_types_allowed=True)

	artifact_type: str = Field(default="GoldArtifact")
	source_file_path: str = Field(description="Path to the source dataset")
	row_count: int = Field(description="Row count in the curated dataset")
	column_count: int = Field(description="Column count in the curated dataset")
	key_metrics: Dict[str, Any] = Field(default_factory=dict)
	summary_tables: Dict[str, Any] = Field(default_factory=dict)
	insights: List[str] = Field(default_factory=list)
	dataframe_preview: List[Dict[str, Any]] = Field(default_factory=list)
	dataframe: Optional[DataFrame] = Field(default=None, exclude=True)
