from contracts.dataset_profile import (
    ColumnProfile,
    QualityProfile,
    StatisticsProfile,
)
from llm.llm_factory import LLMFactory
from llm.prompt_manager import PromptManager


class SummaryGenerator:
    """
    Uses the LLM to generate a business-friendly dataset summary.
    """

    def __init__(self):
        self.llm = LLMFactory.create()

    def generate(
        self,
        dataset_name: str,
        columns: list[ColumnProfile],
        quality: QualityProfile,
        statistics: StatisticsProfile,
    ) -> str:

        schema = []

        for column in columns:
            schema.append(
                f"{column.column_name} ({column.data_type})"
            )

        prompt = PromptManager.summary_prompt(
            dataset_name=dataset_name,
            metadata=f"Columns={len(columns)}",
            schema="\n".join(schema),
            quality=quality.model_dump_json(indent=2),
            statistics=statistics.model_dump_json(indent=2),
        )

        return self.llm.invoke(prompt)