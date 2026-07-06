import json
from typing import List

from contracts.dataset_profile import (
    ColumnProfile,
    SemanticHint,
)
from contracts.enums import ColumnSemanticType
from llm.llm_factory import LLMFactory
from llm.prompt_manager import PromptManager


class SemanticAnalyzer:
    """
    Uses an LLM to infer the business meaning of dataset columns.
    """

    def __init__(self):
        self.llm = LLMFactory.create()

    def analyze(
        self,
        dataset_name: str,
        columns: List[ColumnProfile],
    ) -> List[SemanticHint]:

        semantic_hints = []

        for column in columns:

            prompt = PromptManager.semantic_prompt(
                dataset_name=dataset_name,
                column_name=column.column_name,
                data_type=column.data_type,
                sample_values=", ".join(column.sample_values),
            )

            response = self.llm.invoke(prompt)

            hint = self._parse_response(
                column.column_name,
                response,
            )

            semantic_hints.append(hint)

        return semantic_hints

    def _parse_response(
        self,
        column_name: str,
        response: str,
    ) -> SemanticHint:

        response = response.replace("```json", "")
        response = response.replace("```", "")
        response = response.strip()

        try:

            data = json.loads(response)

            return SemanticHint(
                column_name=column_name,
                semantic_type=ColumnSemanticType(
                    data["semantic_type"]
                ),
                confidence=float(data["confidence"]),
                reasoning=data["reasoning"],
            )

        except Exception:

            return SemanticHint(
                column_name=column_name,
                semantic_type=ColumnSemanticType.UNKNOWN,
                confidence=0,
                reasoning="Unable to parse LLM response."
            )