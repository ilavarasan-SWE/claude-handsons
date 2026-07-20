from typing import Any, Dict, List, Optional

from pandas import DataFrame
from pydantic import ConfigDict, Field

from contracts.base_artifact import BaseArtifact


class BronzeArtifact(BaseArtifact):
	model_config = ConfigDict(arbitrary_types_allowed=True)

	artifact_type: str = Field(default="BronzeArtifact")
	source_file_path: str = Field(description="Path to the source dataset")
	source_file_name: str = Field(description="Source file name")
	row_count: int = Field(description="Number of rows in the source file")
	column_count: int = Field(description="Number of columns in the source file")
	columns: List[str] = Field(default_factory=list)
	dataframe_preview: List[Dict[str, Any]] = Field(default_factory=list)
	notes: List[str] = Field(default_factory=list)
	dataframe: Optional[DataFrame] = Field(default=None, exclude=True)
