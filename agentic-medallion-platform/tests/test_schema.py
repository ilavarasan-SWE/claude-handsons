import pandas as pd
from tools.schema_analyzer import SchemaAnalyzer

df = pd.DataFrame({
 "Customer_ID": [101, 102, 103],
 "Amount": [250.5, 300.0, 150.75],
 "City": ["Chennai", "Bangalore", "Hyderabad"]
})

analyzer = SchemaAnalyzer()

profiles = analyzer.analyze(df)

for profile in profiles:
    print(profile)
 