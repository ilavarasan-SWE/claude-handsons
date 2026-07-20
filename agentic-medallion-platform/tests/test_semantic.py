from contracts.dataset_profile import ColumnProfile
from tools.semantic_analyzer import SemanticAnalyzer

columns = [
    ColumnProfile(
        column_name="Customer_ID",
        data_type="int64",
        nullable=False,
        unique=True,
        null_count=0,
        distinct_count=5,
        sample_values=[
            "1001",
            "1002",
            "1003",
            "1004",
            "1005",
        ],
    )
]

analyzer = SemanticAnalyzer()

result = analyzer.analyze(
    dataset_name="Retail Sales",
    columns=columns,
)

print(result)