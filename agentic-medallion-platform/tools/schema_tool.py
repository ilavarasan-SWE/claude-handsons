import pandas as pd

def analyze_schema(file_path:str) -> dict:
    """
    Analyze the dataset structure
    """

    df = pd.read_csv(file_path)

    schema = []

    for column in df.columns:

        schema.append(
            {
                "column_name": column,
                "data_type": str(df[column].dtype)
            }
        )

    return {
        "row_count": len(df),
        "column_count": len(df.columns),
        "columns": schema
    }