"""Data Profiler Agent — analyzes a raw CSV and produces a JSON profile."""
from __future__ import annotations

import json
from pathlib import Path

import anthropic

from tools.data_tools import compute_column_stats, detect_date_columns, count_duplicates
from tools.file_tools import read_csv_sample, save_json

SYSTEM_PROMPT = """You are a data profiling expert. Analyze CSV data and return a structured JSON profile covering:
column names, inferred data types, null counts, null percentages, unique value counts, sample values (first 3),
min/max for numerics, date range for date columns, and a data quality score (0–100) for each column.
Also flag potential issues: duplicates, mixed types, suspicious nulls.
Return ONLY valid JSON, no prose."""

TOOLS = [
    {
        "name": "read_csv_sample",
        "description": "Read headers and sample rows from a CSV file.",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string"},
                "n_rows": {"type": "integer", "default": 1000},
            },
            "required": ["file_path"],
        },
    },
    {
        "name": "compute_column_stats",
        "description": "Compute statistics for a single CSV column.",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string"},
                "column_name": {"type": "string"},
            },
            "required": ["file_path", "column_name"],
        },
    },
    {
        "name": "detect_date_columns",
        "description": "Return a list of column names that likely contain dates.",
        "input_schema": {
            "type": "object",
            "properties": {"file_path": {"type": "string"}},
            "required": ["file_path"],
        },
    },
    {
        "name": "count_duplicates",
        "description": "Return the count of fully duplicate rows in a CSV file.",
        "input_schema": {
            "type": "object",
            "properties": {"file_path": {"type": "string"}},
            "required": ["file_path"],
        },
    },
]


def _dispatch_tool(name: str, inputs: dict) -> str:
    if name == "read_csv_sample":
        result = read_csv_sample(**inputs)
    elif name == "compute_column_stats":
        result = compute_column_stats(**inputs)
    elif name == "detect_date_columns":
        result = detect_date_columns(**inputs)
    elif name == "count_duplicates":
        result = count_duplicates(**inputs)
    else:
        result = {"error": f"Unknown tool: {name}"}
    return json.dumps(result, default=str)


class DataProfilerAgent:
    def __init__(self, file_path: str | Path, output_dir: str | Path = "data/bronze"):
        self.file_path = Path(file_path)
        self.output_dir = Path(output_dir)
        self.client = anthropic.Anthropic()

    def run(self) -> dict:
        try:
            profile_path = self.output_dir / f"{self.file_path.stem}_profile.json"
            profile_path.parent.mkdir(parents=True, exist_ok=True)

            messages = [
                {
                    "role": "user",
                    "content": (
                        f"Profile this CSV file: {self.file_path}\n"
                        "Use the available tools to gather statistics for every column, "
                        "detect date columns, and count duplicates. "
                        "Then return a complete JSON profile object."
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
                        tool_result = _dispatch_tool(block.name, block.input)
                        messages.append({"role": "assistant", "content": response.content})
                        messages.append({
                            "role": "user",
                            "content": [
                                {
                                    "type": "tool_result",
                                    "tool_use_id": block.id,
                                    "content": tool_result,
                                }
                            ],
                        })
                        break
                    elif block.type == "text":
                        final_text = block.text

                if not tool_calls_made:
                    break

            # Extract JSON from final_text
            profile = self._parse_json(final_text)
            save_json(profile, profile_path)

            row_count = profile.get("total_rows", "unknown")
            col_count = len(profile.get("columns", {}))
            return {
                "success": True,
                "profile_path": str(profile_path),
                "profile": profile,
                "message": f"Profile complete. Found {col_count} columns, {row_count} rows.",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _parse_json(self, text: str) -> dict:
        text = text.strip()
        # Strip markdown code fences if present
        if text.startswith("```"):
            lines = text.splitlines()
            text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end > start:
            return json.loads(text[start:end])
        return json.loads(text)
