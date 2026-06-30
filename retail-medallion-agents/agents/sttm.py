"""STTM Agent — Source-to-Target Mapping for all three Medallion layers."""
from __future__ import annotations

import json
import re
from pathlib import Path

import anthropic

from tools.file_tools import load_json, save_json

SYSTEM_PROMPT = """You are a data architecture expert specializing in Medallion Architecture.
Given a JSON data profile, design a three-layer transformation plan.
For each layer return structured JSON:
- Bronze rules: rename columns to snake_case, cast types, add ingestion_timestamp
- Silver rules: drop exact duplicates, fill or flag nulls based on column importance,
  standardize date formats to ISO 8601, validate numeric ranges
- Gold rules: aggregations to compute — revenue = quantity * price, daily_revenue by date,
  revenue_by_category, revenue_by_region, top_10_products, store_performance

Infer column roles (date, quantity, price, category, region, store, product, id) from column
names and sample values. Return ONLY valid JSON."""

TOOLS = [
    {
        "name": "load_profile",
        "description": "Load a JSON data profile from disk.",
        "input_schema": {
            "type": "object",
            "properties": {"profile_path": {"type": "string"}},
            "required": ["profile_path"],
        },
    },
    {
        "name": "infer_column_roles",
        "description": "Heuristically map columns to semantic roles (date, quantity, price, etc.).",
        "input_schema": {
            "type": "object",
            "properties": {"profile_path": {"type": "string"}},
            "required": ["profile_path"],
        },
    },
]


def _infer_roles_heuristic(profile: dict) -> dict:
    """Simple pattern-based role inference."""
    role_patterns = {
        "date": re.compile(r"date|time|day|month|year|dt|ts|created|updated", re.I),
        "quantity": re.compile(r"qty|quantity|count|units|amount|num", re.I),
        "price": re.compile(r"price|cost|rate|fee|value|amount|revenue|sales", re.I),
        "category": re.compile(r"category|cat|type|segment|class|group|dept", re.I),
        "region": re.compile(r"region|zone|area|territory|geo|location|country|state|city", re.I),
        "store": re.compile(r"store|shop|branch|outlet|location|site", re.I),
        "product": re.compile(r"product|item|sku|goods|article|name|desc", re.I),
        "id": re.compile(r"^id$|_id$|^order|transaction|invoice|receipt|row", re.I),
    }
    columns = list(profile.get("columns", {}).keys()) if isinstance(profile.get("columns"), dict) else []
    if not columns:
        # Try top-level keys that look like column names
        columns = profile.get("column_names", [])

    roles: dict[str, str] = {}
    for col in columns:
        for role, pat in role_patterns.items():
            if pat.search(col):
                roles[col] = role
                break
        else:
            roles[col] = "unknown"
    return roles


def _dispatch_tool(name: str, inputs: dict) -> str:
    if name == "load_profile":
        result = load_json(inputs["profile_path"])
    elif name == "infer_column_roles":
        profile = load_json(inputs["profile_path"])
        result = _infer_roles_heuristic(profile)
    else:
        result = {"error": f"Unknown tool: {name}"}
    return json.dumps(result, default=str)


class STTMAgent:
    def __init__(self, profile_path: str | Path, output_dir: str | Path = "data/bronze"):
        self.profile_path = Path(profile_path)
        self.output_dir = Path(output_dir)
        self.client = anthropic.Anthropic()

    def run(self) -> dict:
        try:
            stem = self.profile_path.stem.replace("_profile", "")
            sttm_path = self.output_dir / f"{stem}_sttm.json"
            sttm_path.parent.mkdir(parents=True, exist_ok=True)

            messages = [
                {
                    "role": "user",
                    "content": (
                        f"Create a full Medallion Architecture STTM plan for the data profile at: "
                        f"{self.profile_path}\n"
                        "Use load_profile to read the profile, then infer_column_roles to understand "
                        "the semantic roles of each column. Then return a complete JSON STTM plan "
                        "covering Bronze, Silver, and Gold layer rules."
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

            sttm_plan = self._parse_json(final_text)
            save_json(sttm_plan, sttm_path)

            return {
                "success": True,
                "sttm_path": str(sttm_path),
                "sttm_plan": sttm_plan,
                "message": "STTM plan generated for Bronze, Silver, and Gold layers.",
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
            return json.loads(text[start:end])
        return json.loads(text)
