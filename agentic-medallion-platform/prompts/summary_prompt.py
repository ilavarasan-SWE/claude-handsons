from string import Template

SUMMARY_PROMPT = Template("""
You are an expert Data Architect and Business Data Analyst.

Your task is to generate a concise business summary.

Dataset Name:
$dataset_name

Metadata:
$metadata

Schema:
$schema

Quality:
$quality

Statistics:
$statistics

Generate a summary covering:

1. Dataset purpose
2. Important entities
3. Overall quality
4. Major issues
5. Business observations

Return only the summary text.
""")