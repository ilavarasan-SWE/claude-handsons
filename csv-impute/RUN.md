# Run Instructions

## Option 1: Open Directly
1. Open `index.html` in your browser.
2. Upload CSV, click **Impute Missing Values**, then click **Download Imputed CSV**.

## Option 2: Run Local Static Server (Recommended)
From a terminal:

```powershell
cd c:\Users\ilab\Documents\git-clone\claude-handsons\csv-impute
python -m http.server 8000
```

Then open:
- http://localhost:8000

## How To Use
1. Click **Choose CSV File** and pick your CSV.
2. Click **Impute Missing Values**.
3. Review preview and summary.
4. Click **Download Imputed CSV**.

## Expected Input Format
- First row is treated as column headers.
- Comma-separated CSV.
- Numeric columns can contain missing cells.

## Troubleshooting
- If Python is unavailable, install Python 3 and retry.
- If CSV fails to load, check that it includes a header row and at least one data row.
- If no values were imputed, your numeric columns may not have missing values or may include non-numeric text.
