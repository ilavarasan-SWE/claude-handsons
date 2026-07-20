from contracts.dataset_profile import (
    ColumnProfile,
    QualityProfile,
    StatisticsProfile,
)
from tools.summary_generator import SummaryGenerator


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
    ),
    ColumnProfile(
        column_name="Sales_Amount",
        data_type="float64",
        nullable=False,
        unique=False,
        null_count=0,
        distinct_count=5,
        sample_values=[
            "100.50",
            "200.00",
            "350.75",
            "150.25",
            "500.00",
        ],
    ),
]

quality = QualityProfile(
    quality_score=98.5,
    duplicate_rows=0,
    duplicate_percentage=0,
    total_null_values=0,
    null_percentage=0,
    issues=[],
)

statistics = StatisticsProfile(
    numeric_statistics={
        "Sales_Amount": {
            "min": 100.5,
            "max": 500.0,
            "mean": 260.3,
            "median": 200.0,
            "std": 145.2,
        }
    },
    categorical_statistics={},
    date_statistics={},
)

generator = SummaryGenerator()

summary = generator.generate(
    dataset_name="Retail Sales",
    columns=columns,
    quality=quality,
    statistics=statistics,
)

print("\n========== AI SUMMARY ==========\n")
print(summary)