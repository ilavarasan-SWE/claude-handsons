# CSV Mean Imputer - Code Explanation

## Overview
This web app loads a CSV file in the browser, detects numeric columns, computes each column mean from existing values, fills missing entries in those numeric columns, and lets the user download the imputed CSV.

## Files
- `index.html`: Main UI structure (file upload, action buttons, status, preview).
- `styles.css`: Responsive styling, layout, and visual design.
- `app.js`: Core application logic (parse, impute, preview, download).

## Logic Flow
1. User selects a CSV file.
2. App reads text using `FileReader`.
3. `parseCsv()` converts CSV text into a 2D array.
4. On impute action:
   - Header is preserved.
   - Numeric columns are detected.
   - Mean is computed per numeric column using available non-missing values.
   - Missing values in numeric columns are replaced with the mean.
5. `toCsv()` converts the updated 2D array back to CSV text.
6. Browser downloads a new file named `<original>_imputed.csv`.

## Missing Value Rules
Values are treated as missing if they are:
- Empty (`""`)
- `NA`
- `N/A`
- `null`
- `NaN`

Comparison is case-insensitive and trims surrounding whitespace.

## Numeric Column Rules
A column is considered numeric only if all non-missing cells can be parsed as numbers.
- If a column contains text values, the column is skipped.
- Means are computed only from non-missing numeric values.

## CSV Support Notes
The parser supports:
- Comma-separated fields
- Quoted fields
- Escaped quotes (`""`) inside quoted fields
- Newlines in standard CSV line endings

## Why Browser-Only
Everything runs client-side, so:
- No backend is required
- Data stays local in the user browser
- Setup is minimal
