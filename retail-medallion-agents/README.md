# Retail Sales Medallion Pipeline

A full-stack Python application where multiple AI agents collaborate to ingest, cleanse, aggregate, and report on retail sales CSV data using a **Medallion Architecture** (Bronze → Silver → Gold layers).

---

## Architecture Overview

```
Raw CSV Upload
      │
      ▼
┌─────────────────┐
│  Data Profiler  │  → Analyzes structure, types, nulls, duplicates
└────────┬────────┘
         │ profile.json
         ▼
┌─────────────────┐
│  STTM Designer  │  → Designs transformation rules for all 3 layers
└────────┬────────┘
         │ sttm.json
         ▼
┌─────────────────┐
│  Bronze Agent   │  → Rename columns, cast types, add metadata
└────────┬────────┘
         │ bronze.csv
         ▼
┌─────────────────┐
│  Silver Agent   │  → Deduplicate, handle nulls, standardize dates
└────────┬────────┘
         │ silver.csv
         ▼
┌─────────────────┐
│   Gold Agent    │  → Compute revenue, daily/category/region KPIs
└────────┬────────┘
         │ gold/*.csv
         ▼
┌─────────────────┐
│    Reporter     │  → Generate self-contained HTML analytics report
└─────────────────┘
```

---

## Setup

### 1. Prerequisites
- Python 3.11+
- An [Anthropic API key](https://console.anthropic.com/)

### 2. Install dependencies

```bash
cd retail-medallion-agents
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env and set your ANTHROPIC_API_KEY
```

### 4. Generate sample data

```bash
python generate_sample_data.py
```

This creates `data/raw/sample_retail_sales.csv` with 5,150 rows including intentional nulls, duplicates, mixed date formats, and negative quantities for testing.

### 5. Run the server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Open your browser at **http://localhost:8000**

---

## Usage

1. Open the web UI at `http://localhost:8000`
2. Drag and drop (or browse for) a CSV file
3. Click **Run Pipeline**
4. Watch each agent's progress in real time via the SSE stream
5. When complete, click **View Full Report** to open the HTML analytics report

---

## Agent Descriptions

| Agent | File | Role |
|-------|------|------|
| **Data Profiler** | `agents/data_profiler.py` | Analyzes CSV structure, computes per-column stats (nulls, types, unique counts, min/max), detects date columns, counts duplicates. Outputs a JSON profile. |
| **STTM Designer** | `agents/sttm.py` | Source-to-Target Mapping — designs Bronze, Silver, and Gold transformation rules based on the data profile. Infers semantic column roles (date, quantity, price, category, etc.). |
| **Bronze Agent** | `agents/bronze.py` | Applies minimal transformations: renames columns to snake_case, casts types, adds `ingestion_timestamp` and `source_file` metadata columns. Preserves all rows. |
| **Silver Agent** | `agents/silver.py` | Data quality layer: removes duplicates, fills/drops nulls, standardizes dates to ISO 8601, flags negative quantities/prices as `is_anomaly=True`. |
| **Gold Agent** | `agents/gold.py` | Computes aggregations: `revenue = quantity × price`, daily revenue trend, revenue by category/region, store performance, top 10 products. Outputs multiple CSVs. |
| **Reporter** | `agents/reporter.py` | Synthesizes Gold outputs into a self-contained HTML report with KPI tables, trend sections, and data quality summary. |
| **Orchestrator** | `agents/orchestrator.py` | Python controller that runs all agents in sequence, passes outputs between them, and streams SSE events to the frontend. |

---

## Data Flow

```
data/raw/           ← uploaded CSV files
data/bronze/        ← renamed + typed CSV + profile.json + sttm.json
data/silver/        ← cleansed CSV
data/gold/          ← aggregation CSVs (daily_revenue, revenue_by_category, etc.)
reports/            ← HTML report files
```

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Serves the web UI |
| `POST` | `/upload` | Upload a CSV file (max 50 MB) |
| `GET` | `/run/{file_id}` | SSE stream — runs the full pipeline |
| `GET` | `/reports/{filename}` | Serves a generated HTML report |
| `GET` | `/data/...` | Static access to data layer files |

---

## Tech Stack

- **FastAPI** + **uvicorn** — async web server
- **Anthropic SDK** (`claude-sonnet-4-6`) — AI agents with tool use
- **Pandas** — data processing
- **Server-Sent Events (SSE)** — real-time agent status streaming
- **Plain HTML + Vanilla JS** — no frontend framework
