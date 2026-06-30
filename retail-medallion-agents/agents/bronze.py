"""Bronze Agent — minimal transformation, preserves raw fidelity."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import anthropic
import pandas as pd

from tools.data_tools import build_rename_map, safe_cast
from tools.file_tools import load_json, save_dataframe, save_json

SYSTEM_PROMPT = """You are a Bronze layer data engineer. Apply only Bronze rules from the STTM plan:
rename columns to snake_case, cast columns to their target data types, add an ingestion_timestamp column
with the current UTC datetime, add a source_file column with the original filename.
Do not remove any rows. Log every action taken. Return ONLY valid JSON."""

TOOLS = [
    {
        "name": "load_raw_csv",
        "description": "Load a raw CSV file and return its shape and column info.",
        "input_schema": {
            "type": "object",
            "properties": {"file_path": {"type": "string"}},
            "required": ["file_path"],
        },
    },
    {
        "name": "get_bronze_rules",
        "description": "Load the STTM plan and extract Bronze layer rules.",
        "input_schema": {
            "type": "object",
            "properties": {"sttm_path": {"type": "string"}},
            "required": ["sttm_path"],
        },
    },
]


def _dispatch_tool(name: str, inputs: dict) -> str:
    if name == "load_raw_csv":
        df = pd.read_csv(inputs["file_path"], nrows=5, low_memory=False)
        result = {
            "columns": list(df.columns),
            "dtypes": {c: str(t) for c, t in df.dtypes.items()},
            "sample": df.head(3).to_dict(orient="records"),
        }
    elif name == "get_bronze_rules":
        plan = load_json(inputs["sttm_path"])
        result = plan.get("bronze", plan.get("Bronze", plan.get("bronze_rules", {})))
    else:
        result = {"error": f"Unknown tool: {name}"}
    return json.dumps(result, default=str)


class BronzeAgent:
    def __init__(
        self,
        file_path: str | Path,
        sttm_path: str | Path,
        output_dir: str | Path = "data/bronze",
    ):
        self.file_path = Path(file_path)
        self.sttm_path = Path(sttm_path)
        self.output_dir = Path(output_dir)
        self.client = anthropic.Anthropic()

    def run(self) -> dict:
        try:
            actions: list[str] = []

            # Load raw data
            df = pd.read_csv(self.file_path, low_memory=False)
            original_shape = df.shape
            actions.append(f"Loaded {original_shape[0]} rows × {original_shape[1]} columns from {self.file_path.name}")

            # Load STTM plan
            sttm_plan = load_json(self.sttm_path)
            bronze_rules = sttm_plan.get("bronze", sttm_plan.get("Bronze", sttm_plan.get("bronze_rules", {})))

            # Ask LLM for a structured action plan
            messages = [
                {
                    "role": "user",
                    "content": (
                        f"Apply Bronze layer rules to the CSV at {self.file_path}.\n"
                        f"STTM plan location: {self.sttm_path}\n"
                        "Use the tools to inspect the data and rules, then return a JSON action plan "
                        "with keys: rename_map (dict), type_map (dict of col→type), notes (list of strings)."
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

            action_plan = self._parse_json(final_text)

            # Apply rename
            rename_map = action_plan.get("rename_map", {})
            if not rename_map:
                rename_map = build_rename_map(list(df.columns))
            # Only rename columns that actually exist
            rename_map = {k: v for k, v in rename_map.items() if k in df.columns}
            df = df.rename(columns=rename_map)
            actions.append(f"Renamed {len(rename_map)} columns to snake_case")

            # Apply type casting
            type_map = action_plan.get("type_map", {})
            cast_count = 0
            for col, target_type in type_map.items():
                # Column may have been renamed
                snake_col = rename_map.get(col, col)
                if snake_col in df.columns:
                    df[snake_col] = safe_cast(df[snake_col], target_type)
                    cast_count += 1
            if cast_count:
                actions.append(f"Cast {cast_count} columns to target types")

            # Add metadata columns
            df["ingestion_timestamp"] = datetime.now(timezone.utc).isoformat()
            df["source_file"] = self.file_path.name
            actions.append("Added ingestion_timestamp and source_file metadata columns")

            # Save
            output_path = self.output_dir / f"{self.file_path.stem}_bronze.csv"
            save_dataframe(df, output_path)
            actions.append(f"Saved Bronze CSV with {df.shape[0]} rows × {df.shape[1]} columns")

            log = {
                "actions": actions,
                "input_shape": list(original_shape),
                "output_shape": list(df.shape),
                "rename_map": rename_map,
                "output_path": str(output_path),
            }
            log_path = self.output_dir / f"{self.file_path.stem}_bronze_log.json"
            save_json(log, log_path)

            return {
                "success": True,
                "bronze_path": str(output_path),
                "log_path": str(log_path),
                "log": log,
                "message": f"Bronze complete. {df.shape[0]} rows, {df.shape[1]} columns.",
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
        return {"rename_map": {}, "type_map": {}, "notes": []}
