from typing import List

import pandas as pd

from contracts.dataset_profile import QualityProfile


class QualityAnalyzer:
    """
    Analyzes the overall quality of a dataset.
    """

    def analyze(self, dataframe: pd.DataFrame) -> QualityProfile:
        """
        Analyze dataset quality.

        Args:
            dataframe: Input pandas DataFrame

        Returns:
            QualityProfile
        """

        total_rows = len(dataframe)

        total_cells = dataframe.shape[0] * dataframe.shape[1]

        duplicate_rows = int(dataframe.duplicated().sum())

        duplicate_percentage = (
            (duplicate_rows / total_rows) * 100
            if total_rows > 0
            else 0
        )

        total_null_values = int(dataframe.isnull().sum().sum())

        null_percentage = (
            (total_null_values / total_cells) * 100
            if total_cells > 0
            else 0
        )

        issues: List[str] = []

        if duplicate_rows > 0:
            issues.append(
                f"Dataset contains {duplicate_rows} duplicate rows."
            )

        if total_null_values > 0:
            issues.append(
                f"Dataset contains {total_null_values} missing values."
            )

        quality_score = max(
            0,
            100 - duplicate_percentage - null_percentage
        )

        return QualityProfile(
            quality_score=round(quality_score, 2),
            duplicate_rows=duplicate_rows,
            duplicate_percentage=round(duplicate_percentage, 2),
            total_null_values=total_null_values,
            null_percentage=round(null_percentage, 2),
            issues=issues,
        )