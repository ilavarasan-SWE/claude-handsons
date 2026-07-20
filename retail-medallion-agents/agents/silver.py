"""Silver Agent — cleansing, deduplication, standardization."""
from __future__ import annotations

import json
from pathlib import Path

import anthropic
import pandas as pd

from tools.file_tools import load_dataframe, load_json, save_dataframe, save_json

SYSTEM_PROMPT = """You are a Silver layer data quality engineer. Apply Silver rules:
- Drop exact duplicate rows and log the count
- Handle nulls per column: drop row if ID/date column is null, fill with median if numeric,
  fill with 'UNKNOWN' if categorical
- Standardize all date columns to ISO 8601 format (YYYY-MM-DD)
- Validate that quantity and price columns contain only positive values
  (flag negatives/zeros in a new is_anomaly column rather than dropping)
- Ensure no column has >30% nulls after filling (warn if so)
Log every transformation. Return ONLY valid JSON."""

TOOLS = [
    {
        "name": "get_silver_rules",
        "description": "Load the STTM plan and extract Silver layer rules.",
        "input_schema": {
            "type": "object",
            "properties": {"sttm_path": {"type": "string"}},
            "required": ["sttm_path"],
        },
    },
    {
        "name": "get_column_info",
        "description": "Return column names, dtypes, and null counts for a Bronze CSV.",
        "input_schema": {
            "type": "object",
            "properties": {"bronze_path": {"type": "string"}},
            "required": ["bronze_path"],
        },
    },
]


def _dispatch_tool(name: str, inputs: dict) -> str:
    if name == "get_silver_rules":
        plan = load_json(inputs["sttm_path"])
        result = plan.get("silver", plan.get("Silver", plan.get("silver_rules", {})))
    elif name == "get_column_info":
        df = pd.read_csv(inputs["bronze_path"], nrows=5, low_memory=False)
        result = {
            "columns": list(df.columns),
            "dtypes": {c: str(t) for c, t in df.dtypes.items()},
        }
    else:
        result = {"error": f"Unknown tool: {name}"}
    return json.dumps(result, default=str)


def _find_columns_by_role(columns: list[str], keywords: list[str]) -> list[str]:
    import re
    pattern = re.compile("|".join(keywords), re.I)
    return [c for c in columns if pattern.search(c)]


class SilverAgent:
    def __init__(
        self,
        bronze_path: str | Path,
        sttm_path: str | Path,
        output_dir: str | Path = "data/silver",
    ):
        self.bronze_path = Path(bronze_path)
        self.sttm_path = Path(sttm_path)
        self.output_dir = Path(output_dir)
        self.client = anthropic.Anthropic()

    def run(self) -> dict:
        try:
            actions: list[str] = []
            warnings: list[str] = []

            df = load_dataframe(self.bronze_path)
            original_rows = len(df)
            actions.append(f"Loaded {original_rows} rows from Bronze layer")

            # Ask LLM for column role mapping
            messages = [
                {
                    "role": "user",
                    "content": (
                        f"Analyze the Bronze CSV at {self.bronze_path} and the STTM plan at {self.sttm_path}. "
                        "Return a JSON with keys: "
                        "id_columns (list), date_columns (list), numeric_columns (list), "
                        "categorical_columns (list), quantity_columns (list), price_columns (list), "
                        "null_rules (dict of col→'drop'|'median'|'unknown'|'mean')."
                    ),
                }
            ]

            final_text = ""
            while True:
                response = self.client.messages.create(
                    model="claude-sonnet-4-6",
                    max_tokens=4096,
                    system=SYSTEM_PROMPT,
                    tools=TOOLS,
                    messages=messages,
                )
                tool_calls_made = False
                for block in response.content:
                    if block.type == "tool_use":
                        tool_calls_made = True
                        result = _dispatch_tool(block.name, block.input)
                        messages.append({"role": "assistant", "content": response.content})
                        messages.append({
                            "role": "user",
                            "content": [{"type": "tool_result", "tool_use_id": block.id, "content": result}],
                        })
                        break
                    elif block.type == "text":
                        final_text = block.text
                if not tool_calls_made:
                    break

            plan = self._parse_json(final_text)
            cols = list(df.columns)

            id_cols = plan.get("id_columns", _find_columns_by_role(cols, ["id", "order", "transaction"]))
            date_cols = plan.get("date_columns", _find_columns_by_role(cols, ["date", "time", "ts"]))
            numeric_cols = plan.get("numeric_columns", [])
            cat_cols = plan.get("categorical_columns", [])
            qty_cols = plan.get("quantity_columns", _find_columns_by_role(cols, ["qty", "quantity", "units"]))
            price_cols = plan.get("price_columns", _find_columns_by_role(cols, ["price", "cost", "rate"]))
            null_rules: dict = plan.get("null_rules", {})

            # 1. Remove duplicates
            before = len(df)
            df = df.drop_duplicates()
            removed = before - len(df)
            actions.append(f"Removed {removed} duplicate rows")

            # 2. Handle nulls
            for col in cols:
                if col not in df.columns:
                    continue
                null_pct = df[col].isna().mean()
                if null_pct > 0.30:
                    warnings.append(f"Column '{col}' has {null_pct:.1%} nulls after Bronze")

                rule = null_rules.get(col)
                if not rule:
                    if col in id_cols or col in date_cols:
                        rule = "drop"
                    elif pd.api.types.is_numeric_dtype(df[col]):
                        rule = "median"
                    else:
                        rule = "unknown"

                if rule == "drop":
                    before_drop = len(df)
                    df = df.dropna(subset=[col])
                    dropped = before_drop - len(df)
                    if dropped:
                        actions.append(f"Dropped {dropped} rows with null '{col}'")
                elif rule in ("median", "mean"):
                    if pd.api.types.is_numeric_dtype(df[col]):
                        fill_val = df[col].median() if rule == "median" else df[col].mean()
                        df[col] = df[col].fillna(fill_val)
                        actions.append(f"Filled nulls in '{col}' with {rule} ({fill_val:.4g})")
                elif rule == "unknown":
                    df[col] = df[col].fillna("UNKNOWN")
                    actions.append(f"Filled nulls in '{col}' with 'UNKNOWN'")

            # 3. Standardize dates
            for col in date_cols:
                if col in df.columns:
                    try:
                        df[col] = pd.to_datetime(df[col], errors="coerce", infer_datetime_format=True)
                        df[col] = df[col].dt.strftime("%Y-%m-%d")
                        actions.append(f"Standardized '{col}' to ISO 8601")
                    except Exception:
                        pass

            # 4. Validate numerics (flag anomalies)
            anomaly_mask = pd.Series([False] * len(df), index=df.index)
            for col in qty_cols + price_cols:
                if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
                    neg_mask = df[col] <= 0
                    anomaly_mask = anomaly_mask | neg_mask
                    flagged = int(neg_mask.sum())
                    if flagged:
                        actions.append(f"Flagged {flagged} anomalous rows where '{col}' ≤ 0")

            df["is_anomaly"] = anomaly_mask
            anomaly_count = int(anomaly_mask.sum())

            # Save
            output_path = self.output_dir / f"{self.bronze_path.stem.replace('_bronze', '')}_silver.csv"
            save_dataframe(df, output_path)
            actions.append(f"Saved Silver CSV with {len(df)} rows × {len(df.columns)} columns")

            log = {
                "actions": actions,
                "warnings": warnings,
                "input_rows": original_rows,
                "output_rows": len(df),
                "duplicates_removed": removed,
                "anomalies_flagged": anomaly_count,
                "output_path": str(output_path),
            }
            log_path = self.output_dir / f"{self.bronze_path.stem.replace('_bronze', '')}_silver_log.json"
            save_json(log, log_path)

            return {
                "success": True,
                "silver_path": str(output_path),
                "log_path": str(log_path),
                "log": log,
                "message": (
                    f"Silver complete. {len(df)} rows retained, "
                    f"{removed} duplicates removed, {anomaly_count} anomalies flagged."
                ),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _parse_json(self, text: str) -> dict:
        text = text.strip()
        if text.startswith("```"):
            lines = text.splitlines()
            text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end > start:
            try:
                return json.loads(text[start:end])
            except Exception:
                pass
        return {}
