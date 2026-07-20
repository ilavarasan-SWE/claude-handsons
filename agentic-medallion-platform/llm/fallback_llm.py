from __future__ import annotations

import json
import re

from llm.base_llm import BaseLLM


class FallbackLLM(BaseLLM):
    def invoke(self, prompt: str) -> str:
        prompt_lower = prompt.lower()

        if "semantic type" in prompt_lower or "return only valid json" in prompt_lower:
            return self._infer_semantic(prompt)

        return self._generate_summary(prompt)

    def _infer_semantic(self, prompt: str) -> str:
        column_name = self._extract_section(prompt, "Column Name:")
        sample_values = self._extract_section(prompt, "Sample Values:")
        candidate = f"{column_name} {sample_values}".lower()

        semantic_type = "UNKNOWN"
        confidence = 55
        reasoning = "Heuristic fallback inference."

        if any(token in candidate for token in ["customer", "cust", "client"]):
            semantic_type = "CUSTOMER_ID"
            confidence = 92
            reasoning = "Column name suggests a customer identifier."
        elif any(token in candidate for token in ["product", "item", "sku"]):
            semantic_type = "PRODUCT_ID"
            confidence = 90
            reasoning = "Column name suggests a product identifier."
        elif any(token in candidate for token in ["transaction", "order", "invoice", "receipt"]):
            semantic_type = "TRANSACTION_ID"
            confidence = 90
            reasoning = "Column name suggests a transaction identifier."
        elif any(token in candidate for token in ["date", "time", "timestamp"]):
            semantic_type = "DATE"
            confidence = 94
            reasoning = "Column name and sample values indicate a date field."
        elif any(token in candidate for token in ["amount", "sales", "revenue", "total"]):
            semantic_type = "SALES_AMOUNT"
            confidence = 88
            reasoning = "Column name suggests a sales amount field."
        elif any(token in candidate for token in ["qty", "quantity", "units"]):
            semantic_type = "QUANTITY"
            confidence = 88
            reasoning = "Column name suggests a quantity field."
        elif any(token in candidate for token in ["price", "cost", "rate"]):
            semantic_type = "PRICE"
            confidence = 86
            reasoning = "Column name suggests a price field."
        elif any(token in candidate for token in ["store", "shop"]):
            semantic_type = "STORE"
            confidence = 85
            reasoning = "Column name suggests a store dimension."
        elif any(token in candidate for token in ["region", "state", "area"]):
            semantic_type = "REGION"
            confidence = 85
            reasoning = "Column name suggests a region dimension."

        return json.dumps(
            {
                "semantic_type": semantic_type,
                "confidence": confidence,
                "reasoning": reasoning,
            }
        )

    def _generate_summary(self, prompt: str) -> str:
        dataset_name = self._extract_after(prompt, "Dataset Name:") or "the dataset"
        quality_match = re.search(r'"quality_score"\s*:\s*([0-9.]+)', prompt)
        quality_score = quality_match.group(1) if quality_match else "unknown"

        return (
            f"{dataset_name} is a structured dataset profiled through the medallion pipeline. "
            f"The overall quality score is {quality_score}, and the dataset is ready for downstream review "
            f"after applying the cleaning and summarization steps."
        )

    @staticmethod
    def _extract_section(prompt: str, header: str) -> str:
        pattern = re.escape(header) + r"\s*(.*?)(?:\n\n|$)"
        match = re.search(pattern, prompt, flags=re.S)
        return match.group(1).strip() if match else ""

    @staticmethod
    def _extract_after(prompt: str, header: str) -> str:
        pattern = re.escape(header) + r"\s*(.*)"
        match = re.search(pattern, prompt, flags=re.S)
        return match.group(1).strip().splitlines()[0] if match else ""