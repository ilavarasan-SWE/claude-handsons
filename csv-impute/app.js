const fileInput = document.getElementById("csvFile");
const imputeBtn = document.getElementById("imputeBtn");
const downloadBtn = document.getElementById("downloadBtn");
const statusEl = document.getElementById("status");
const summaryEl = document.getElementById("summary");
const previewEl = document.getElementById("preview");

let originalFileName = "imputed.csv";
let parsedRows = [];
let imputedRows = [];

fileInput.addEventListener("change", handleFileSelection);
imputeBtn.addEventListener("click", imputeMissingValues);
downloadBtn.addEventListener("click", downloadImputedCsv);

function handleFileSelection() {
  const file = fileInput.files[0];
  resetState();

  if (!file) {
    setStatus("No file selected.");
    return;
  }

  if (!file.name.toLowerCase().endsWith(".csv")) {
    setStatus("Please select a .csv file.", true);
    return;
  }

  originalFileName = file.name;
  const reader = new FileReader();
  reader.onload = () => {
    try {
      const text = String(reader.result || "");
      parsedRows = parseCsv(text);

      if (parsedRows.length < 2) {
        throw new Error("CSV must include a header and at least one data row.");
      }

      setStatus("CSV loaded. Click 'Impute Missing Values' to continue.");
      imputeBtn.disabled = false;
      renderPreview(parsedRows);
    } catch (error) {
      setStatus(error.message, true);
    }
  };

  reader.onerror = () => setStatus("Failed to read file.", true);
  reader.readAsText(file);
}

function imputeMissingValues() {
  if (parsedRows.length < 2) {
    setStatus("Load a valid CSV first.", true);
    return;
  }

  const header = parsedRows[0];
  const dataRows = parsedRows.slice(1).map((row) => padRow(row, header.length));

  const means = [];
  let imputedCellCount = 0;
  let numericColumns = 0;

  for (let col = 0; col < header.length; col += 1) {
    const nonMissingValues = [];
    let hasNonNumeric = false;

    for (const row of dataRows) {
      const value = row[col];
      if (isMissingValue(value)) {
        continue;
      }

      const num = Number(value);
      if (Number.isNaN(num)) {
        hasNonNumeric = true;
        break;
      }
      nonMissingValues.push(num);
    }

    if (!hasNonNumeric && nonMissingValues.length > 0) {
      const mean = nonMissingValues.reduce((sum, v) => sum + v, 0) / nonMissingValues.length;
      means[col] = mean;
      numericColumns += 1;
    } else {
      means[col] = null;
    }
  }

  for (const row of dataRows) {
    for (let col = 0; col < header.length; col += 1) {
      if (means[col] !== null && isMissingValue(row[col])) {
        row[col] = formatNumber(means[col]);
        imputedCellCount += 1;
      }
    }
  }

  imputedRows = [header, ...dataRows];
  downloadBtn.disabled = false;

  setStatus("Imputation complete.");
  summaryEl.textContent = `Numeric columns: ${numericColumns}. Filled cells: ${imputedCellCount}.`;
  renderPreview(imputedRows);
}

function downloadImputedCsv() {
  if (imputedRows.length === 0) {
    setStatus("No imputed data available.", true);
    return;
  }

  const csvString = toCsv(imputedRows);
  const blob = new Blob([csvString], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);

  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = buildOutputFileName(originalFileName);
  document.body.appendChild(anchor);
  anchor.click();
  document.body.removeChild(anchor);

  URL.revokeObjectURL(url);
}

function resetState() {
  parsedRows = [];
  imputedRows = [];
  imputeBtn.disabled = true;
  downloadBtn.disabled = true;
  summaryEl.textContent = "";
}

function setStatus(message, isError = false) {
  statusEl.textContent = message;
  statusEl.style.color = isError ? "var(--warn)" : "var(--muted)";
}

function parseCsv(input) {
  const rows = [];
  let current = "";
  let row = [];
  let inQuotes = false;

  for (let i = 0; i < input.length; i += 1) {
    const char = input[i];
    const next = input[i + 1];

    if (char === '"') {
      if (inQuotes && next === '"') {
        current += '"';
        i += 1;
      } else {
        inQuotes = !inQuotes;
      }
    } else if (char === "," && !inQuotes) {
      row.push(current);
      current = "";
    } else if ((char === "\n" || char === "\r") && !inQuotes) {
      if (char === "\r" && next === "\n") {
        i += 1;
      }
      row.push(current);
      if (!(row.length === 1 && row[0] === "")) {
        rows.push(row);
      }
      row = [];
      current = "";
    } else {
      current += char;
    }
  }

  if (current.length > 0 || row.length > 0) {
    row.push(current);
    if (!(row.length === 1 && row[0] === "")) {
      rows.push(row);
    }
  }

  if (inQuotes) {
    throw new Error("Malformed CSV: unmatched quote.");
  }

  return rows;
}

function toCsv(rows) {
  return rows
    .map((row) => row.map(escapeCsvCell).join(","))
    .join("\r\n");
}

function escapeCsvCell(cell) {
  const value = String(cell ?? "");
  if (value.includes('"') || value.includes(",") || value.includes("\n") || value.includes("\r")) {
    return `"${value.replace(/"/g, '""')}"`;
  }
  return value;
}

function buildOutputFileName(fileName) {
  const dotIndex = fileName.lastIndexOf(".");
  if (dotIndex <= 0) {
    return `${fileName}_imputed.csv`;
  }
  return `${fileName.slice(0, dotIndex)}_imputed.csv`;
}

function isMissingValue(value) {
  const normalized = String(value ?? "").trim().toLowerCase();
  return normalized === "" || normalized === "na" || normalized === "n/a" || normalized === "null" || normalized === "nan";
}

function padRow(row, targetLength) {
  const result = [...row];
  while (result.length < targetLength) {
    result.push("");
  }
  return result.slice(0, targetLength);
}

function formatNumber(value) {
  return Number(value.toFixed(6)).toString();
}

function renderPreview(rows) {
  const previewRows = rows.slice(0, 9);
  if (previewRows.length === 0) {
    previewEl.textContent = "No data available.";
    return;
  }

  const table = document.createElement("table");
  const [header, ...bodyRows] = previewRows;

  const thead = document.createElement("thead");
  const trHead = document.createElement("tr");
  header.forEach((colName) => {
    const th = document.createElement("th");
    th.textContent = colName;
    trHead.appendChild(th);
  });
  thead.appendChild(trHead);

  const tbody = document.createElement("tbody");
  bodyRows.forEach((row) => {
    const tr = document.createElement("tr");
    row.forEach((cell) => {
      const td = document.createElement("td");
      td.textContent = cell;
      tr.appendChild(td);
    });
    tbody.appendChild(tr);
  });

  table.appendChild(thead);
  table.appendChild(tbody);

  previewEl.innerHTML = "";
  previewEl.appendChild(table);
}
