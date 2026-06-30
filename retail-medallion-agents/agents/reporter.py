"""Reporter Agent — synthesizes Gold outputs into an HTML report."""
from __future__ import annotations

import json
from pathlib import Path

import anthropic
import pandas as pd

from tools.file_tools import save_json

SYSTEM_PROMPT = """You are a retail analytics reporter. You will receive JSON summaries of all Gold
layer aggregations and pipeline logs. Write a professional, self-contained HTML report including:
- Executive summary paragraph (3-5 sentences highlighting top insights)
- KPI summary table (total revenue, total orders, avg order value, top category, top region, top product)
- Daily revenue trend section (HTML table)
- Category breakdown section
- Regional performance section
- Store performance section
- Top 10 products section
- Data quality summary (rows ingested, rows after Silver cleansing, anomalies flagged)

Use clean inline CSS. Dark-friendly color scheme. No external CDN dependencies.
Return complete, self-contained HTML only — no prose before or after."""


class ReporterAgent:
    def __init__(
        self,
        gold_dir: str | Path,
        pipeline_log: dict,
        output_dir: str | Path = "reports",
        report_name: str = "report",
    ):
        self.gold_dir = Path(gold_dir)
        self.pipeline_log = pipeline_log
        self.output_dir = Path(output_dir)
        self.report_name = report_name
        self.client = anthropic.Anthropic()

    def run(self) -> dict:
        try:
            tables = self._load_gold_tables()
            summary = self._summarize_for_llm(tables)
            html = self._generate_report_html(summary)

            self.output_dir.mkdir(parents=True, exist_ok=True)
            report_path = self.output_dir / f"{self.report_name}.html"
            report_path.write_text(html, encoding="utf-8")

            return {
                "success": True,
                "report_path": str(report_path),
                "report_url": f"/reports/{report_path.name}",
                "message": f"HTML report saved to {report_path.name}",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _load_gold_tables(self) -> dict[str, pd.DataFrame]:
        tables: dict[str, pd.DataFrame] = {}
        for csv_file in self.gold_dir.glob("*.csv"):
            try:
                tables[csv_file.stem] = pd.read_csv(csv_file)
            except Exception:
                pass
        return tables

    def _summarize_for_llm(self, tables: dict[str, pd.DataFrame]) -> dict:
        summary: dict = {"tables": {}, "pipeline_log": self.pipeline_log}
        for name, df in tables.items():
            summary["tables"][name] = {
                "shape": list(df.shape),
                "columns": list(df.columns),
                "data": df.head(50).to_dict(orient="records"),
            }
        # Compute top-level KPIs
        if "gold_fact_table" in tables:
            fact = tables["gold_fact_table"]
            summary["kpis"] = {
                "total_revenue": float(fact["revenue"].sum()) if "revenue" in fact.columns else 0,
                "total_orders": len(fact),
                "avg_order_value": float(fact["revenue"].mean()) if "revenue" in fact.columns else 0,
            }
        if "revenue_by_category" in tables:
            df = tables["revenue_by_category"]
            if len(df) > 0:
                top_row = df.iloc[0]
                summary["kpis"]["top_category"] = str(top_row.iloc[0])
        if "revenue_by_region" in tables:
            df = tables["revenue_by_region"]
            if len(df) > 0:
                top_row = df.iloc[0]
                summary["kpis"]["top_region"] = str(top_row.iloc[0])
        if "top_10_products" in tables:
            df = tables["top_10_products"]
            if len(df) > 0:
                top_row = df.iloc[0]
                summary["kpis"]["top_product"] = str(top_row.iloc[0])
        return summary

    def _generate_report_html(self, summary: dict) -> str:
        summary_json = json.dumps(summary, default=str, indent=2)
        # Truncate if very large to stay within token limits
        if len(summary_json) > 60000:
            # Trim data rows in each table
            for tbl in summary.get("tables", {}).values():
                tbl["data"] = tbl["data"][:20]
            summary_json = json.dumps(summary, default=str, indent=2)

        response = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=8192,
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": (
                        "Generate a complete, self-contained HTML report from this retail analytics data:\n\n"
                        f"{summary_json}\n\n"
                        "Return ONLY the HTML — start with <!DOCTYPE html> and end with </html>."
                    ),
                }
            ],
        )

        html = ""
        for block in response.content:
            if hasattr(block, "text"):
                html = block.text
                break

        # Strip any markdown fences
        html = html.strip()
        if html.startswith("```"):
            lines = html.splitlines()
            html = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

        # Ensure it starts with DOCTYPE
        if not html.lstrip().startswith("<!"):
            idx = html.find("<!DOCTYPE")
            if idx == -1:
                idx = html.find("<html")
            if idx != -1:
                html = html[idx:]

        return html
