import pandas as pd

from tools.quality_analyzer import QualityAnalyzer

df = pd.DataFrame({
    "Customer": [1, 2, 2],
    "Amount": [100, None, None]
})

analyzer = QualityAnalyzer()

quality = analyzer.analyze(df)

print(quality)