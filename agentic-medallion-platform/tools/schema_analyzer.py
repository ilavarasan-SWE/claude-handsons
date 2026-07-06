from typing import List

import pandas as pd

from contracts.dataset_profile import ColumnProfile


class SchemaAnalyzer:
    """
    Analyzes the schema of a Pandas DataFrame and returns
    a list of ColumnProfile objects.
    """

    def analyze(self, dataframe: pd.DataFrame) -> List[ColumnProfile]:
        """
        Analyze the DataFrame schema.

        Args:
            dataframe: Input pandas DataFrame

        Returns:
            List of ColumnProfile objects
        """

        column_profiles = []

        for column in dataframe.columns:

            series = dataframe[column]

            profile = ColumnProfile(

                column_name=column,

                data_type=str(series.dtype),

                nullable=series.isnull().any(),

                unique=series.is_unique,

                null_count=int(series.isnull().sum()),

                distinct_count=int(series.nunique()),

                sample_values=[
                    str(value)
                    for value in series.dropna().head(5).tolist()
                ]
            )

            column_profiles.append(profile)

        return column_profiles