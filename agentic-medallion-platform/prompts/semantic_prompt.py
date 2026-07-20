from string import Template

SEMANTIC_PROMPT = Template("""
You are an expert Data Architect.

Your task is to determine the business meaning of a dataset column.

Dataset Name:
$dataset_name

Column Name:
$column_name

Detected Data Type:
$data_type

Sample Values:
$sample_values

Choose ONLY one semantic type from this list:

UNKNOWN
CUSTOMER_ID
PRODUCT_ID
TRANSACTION_ID
DATE
SALES_AMOUNT
QUANTITY
PRICE
STORE
REGION

Return ONLY valid JSON.

Example:

{
    "semantic_type": "CUSTOMER_ID",
    "confidence": 98,
    "reasoning": "Column name and sample values strongly indicate customer identifiers."
}
""")