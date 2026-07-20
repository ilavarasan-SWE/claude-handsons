from typing import Any, Dict, List, Optional

from pandas import DataFrame
from pydantic import ConfigDict, Field

from contracts.base_artifact import BaseArtifact


class SilverArtifact(BaseArtifact):
	model_config = ConfigDict(arbitrary_types_allowed=True)

	artifact_type: str = Field(default="SilverArtifact")
	source_file_path: str = Field(description="Path to the source dataset")
	row_count_before: int = Field(description="Row count before cleaning")
	row_count_after: int = Field(description="Row count after cleaning")
	column_count: int = Field(description="Number of columns")
	columns: List[str] = Field(default_factory=list)
	dataframe_preview: List[Dict[str, Any]] = Field(default_factory=list)
	transformation_notes: List[str] = Field(default_factory=list)
	dataframe: Optional[DataFrame] = Field(default=None, exclude=True)
