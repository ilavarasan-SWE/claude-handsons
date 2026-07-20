"""Gold Agent — aggregations and KPI computation."""
from __future__ import annotations

import json
from pathlib import Path

import anthropic
import pandas as pd

from tools.file_tools import load_dataframe, load_json, save_dataframe, save_json

SYSTEM_PROMPT = """You are a Gold layer analytics engineer. Using Silver data and the STTM plan,
compute all aggregations: revenue = quantity * price, daily_revenue, revenue_by_category,
revenue_by_region, store_performance, top_10_products.
Return ONLY valid JSON specifying column role mappings needed for aggregations."""

TOOLS = [
    {
        "name": "get_gold_rules",
        "description": "Load the STTM plan and extract Gold layer rules and column roles.",
        "input_schema": {
            "type": "object",
            "properties": {"sttm_path": {"type": "string"}},
            "required": ["sttm_path"],
        },
    },
    {
        "name": "get_silver_columns",
        "description": "Return the column names and dtypes of the Silver CSV.",
        "input_schema": {
            "type": "object",
            "properties": {"silver_path": {"type": "string"}},
            "required": ["silver_path"],
        },
    },
]


def _dispatch_tool(name: str, inputs: dict) -> str:
    if name == "get_gold_rules":
        plan = load_json(inputs["sttm_path"])
        gold = plan.get("gold", plan.get("Gold", plan.get("gold_rules", {})))
        roles = plan.get("column_roles", {})
        result = {"gold_rules": gold, "column_roles": roles}
    elif name == "get_silver_columns":
        df = pd.read_csv(inputs["silver_path"], nrows=3, low_memory=False)
        result = {"columns": list(df.columns), "dtypes": {c: str(t) for c, t in df.dtypes.items()}}
    else:
        result = {"error": f"Unknown tool: {name}"}
    return json.dumps(result, default=str)


def _find_col(df: pd.DataFrame, keywords: list[str]) -> str | None:
    """Return first column matching any keyword (case-insensitive)."""
    import re
    pat = re.compile("|".join(keywords), re.I)
    for col in df.columns:
        if pat.search(col):
            return col
    return None


class GoldAgent:
    def __init__(
        self,
        silver_path: str | Path,
        sttm_path: str | Path,
        output_dir: str | Path = "data/gold",
    ):
        self.silver_path = Path(silver_path)
        self.sttm_path = Path(sttm_path)
        self.output_dir = Path(output_dir)
        self.client = anthropic.Anthropic()

    def run(self) -> dict:
        try:
            tables_created: list[str] = []

            df = load_dataframe(self.silver_path)
            actions: list[str] = [f"Loaded {len(df)} rows from Silver layer"]

            # Ask LLM for column role mapping
            messages = [
                {
                    "role": "user",
                    "content": (
                        f"Map columns for Gold aggregations. Silver CSV: {self.silver_path}. "
                        f"STTM: {self.sttm_path}.\n"
                        "Return JSON with keys: quantity_col, price_col, date_col, category_col, "
                        "region_col, store_col, product_col."
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

            roles = self._parse_json(final_text)
            cols = list(df.columns)

            qty_col = roles.get("quantity_col") or _find_col(df, ["qty", "quantity", "units", "count"])
            price_col = roles.get("price_col") or _find_col(df, ["price", "unit_price", "cost", "rate"])
            date_col = roles.get("date_col") or _find_col(df, ["date", "order_date", "sale_date", "ts"])
            cat_col = roles.get("category_col") or _find_col(df, ["category", "cat", "dept", "segment"])
            region_col = roles.get("region_col") or _find_col(df, ["region", "zone", "area", "territory"])
            store_col = roles.get("store_col") or _find_col(df, ["store", "shop", "branch", "outlet"])
            product_col = roles.get("product_col") or _find_col(df, ["product", "item", "sku", "name"])

            # 1. Compute revenue
            if qty_col and price_col and qty_col in cols and price_col in cols:
                df["revenue"] = pd.to_numeric(df[qty_col], errors="coerce") * pd.to_numeric(df[price_col], errors="coerce")
                actions.append(f"Computed revenue = {qty_col} × {price_col}")
            else:
                # Try to infer a revenue column that already exists
                rev_col = _find_col(df, ["revenue", "total", "sales"])
                if rev_col:
                    df["revenue"] = pd.to_numeric(df[rev_col], errors="coerce")
                else:
                    df["revenue"] = 0.0
                actions.append("Revenue column set from existing or defaulted to 0")

            # Save fact table
            fact_path = self.output_dir / "gold_fact_table.csv"
            save_dataframe(df, fact_path)
            tables_created.append("gold_fact_table")

            # 2. daily_revenue
            if date_col and date_col in df.columns:
                daily = df.groupby(date_col)["revenue"].sum().reset_index()
                daily.columns = ["date", "total_revenue"]
                daily = daily.sort_values("date")
                save_dataframe(daily, self.output_dir / "daily_revenue.csv")
                tables_created.append("daily_revenue")
                actions.append(f"Computed daily_revenue ({len(daily)} dates)")

            # 3. revenue_by_category
            if cat_col and cat_col in df.columns:
                cat_rev = df.groupby(cat_col)["revenue"].sum().reset_index().sort_values("revenue", ascending=False)
                save_dataframe(cat_rev, self.output_dir / "revenue_by_category.csv")
                tables_created.append("revenue_by_category")

            # 4. revenue_by_region
            if region_col and region_col in df.columns:
                reg_rev = df.groupby(region_col)["revenue"].sum().reset_index().sort_values("revenue", ascending=False)
                save_dataframe(reg_rev, self.output_dir / "revenue_by_region.csv")
                tables_created.append("revenue_by_region")

            # 5. store_performance
            if store_col and store_col in df.columns:
                store_perf = df.groupby(store_col).agg(
                    total_revenue=("revenue", "sum"),
                    total_orders=("revenue", "count"),
                ).reset_index().sort_values("total_revenue", ascending=False)
                save_dataframe(store_perf, self.output_dir / "store_performance.csv")
                tables_created.append("store_performance")

            # 6. top_10_products
            if product_col and product_col in df.columns:
                top10 = (
                    df.groupby(product_col)["revenue"].sum()
                    .reset_index()
                    .sort_values("revenue", ascending=False)
                    .head(10)
                )
                save_dataframe(top10, self.output_dir / "top_10_products.csv")
                tables_created.append("top_10_products")

            log = {
                "actions": actions,
                "tables_created": tables_created,
                "output_dir": str(self.output_dir),
                "total_revenue": float(df["revenue"].sum()),
                "total_orders": len(df),
            }
            log_path = self.output_dir / "gold_log.json"
            save_json(log, log_path)

            return {
                "success": True,
                "gold_dir": str(self.output_dir),
                "tables_created": tables_created,
                "log_path": str(log_path),
                "log": log,
                "message": f"Gold complete. Created {len(tables_created)} tables.",
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
