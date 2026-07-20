from contracts.bronze import BronzeArtifact
from contracts.silver import SilverArtifact
from tools.transformation_tool import TransformationTool


class SilverAgent:
	def __init__(self) -> None:
		self.transformation_tool = TransformationTool()

	def execute(self, bronze_artifact: BronzeArtifact) -> SilverArtifact:
		if bronze_artifact.dataframe is None:
			raise ValueError("Bronze artifact does not contain a dataframe.")

		cleaned_dataframe, notes = self.transformation_tool.clean_dataframe(bronze_artifact.dataframe)

		return SilverArtifact(
			created_by="SilverAgent",
			source_file_path=bronze_artifact.source_file_path,
			row_count_before=bronze_artifact.row_count,
			row_count_after=int(len(cleaned_dataframe)),
			column_count=int(len(cleaned_dataframe.columns)),
			columns=[str(column) for column in cleaned_dataframe.columns],
			dataframe_preview=cleaned_dataframe.head(10).fillna("").to_dict(orient="records"),
			transformation_notes=notes,
			dataframe=cleaned_dataframe,
		)
