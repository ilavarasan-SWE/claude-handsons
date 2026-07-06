from typing import Any

import pandas as pd

from contracts.dataset_profile import StatisticsProfile


class StatisticsAnalyzer:
    """
    Generates statistical summaries for a dataset.
    """

    def analyze(self, dataframe: pd.DataFrame) -> StatisticsProfile:

        numeric_statistics = {}
        categorical_statistics = {}
        date_statistics = {}

        # ---------- Numeric Columns ----------
        numeric_columns = dataframe.select_dtypes(include=["number"]).columns

        for column in numeric_columns:

            series = dataframe[column]

            numeric_statistics[column] = {
                "min": float(series.min()),
                "max": float(series.max()),
                "mean": float(series.mean()),
                "median": float(series.median()),
                "std": float(series.std()) if len(series) > 1 else 0.0
            }

        # ---------- Categorical Columns ----------
        categorical_columns = dataframe.select_dtypes(
            include=["object", "category"]
        ).columns

        for column in categorical_columns:

            series = dataframe[column]

            mode = series.mode()

            categorical_statistics[column] = {
                "distinct_values": int(series.nunique()),
                "most_frequent": (
                    str(mode.iloc[0])
                    if not mode.empty
                    else None
                )
            }

        # ---------- Date Columns ----------
        for column in dataframe.columns:

            try:

                parsed = pd.to_datetime(
                    dataframe[column],
                    errors="raise"
                )

                date_statistics[column] = {
                    "min_date": str(parsed.min()),
                    "max_date": str(parsed.max())
                }

            except Exception:
                pass

        return StatisticsProfile(
            numeric_statistics=numeric_statistics,
            categorical_statistics=categorical_statistics,
            date_statistics=date_statistics
        )