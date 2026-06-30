"""Orchestrator — coordinates all agents and streams SSE events."""
from __future__ import annotations

import json
from pathlib import Path
from typing import AsyncGenerator

from agents.data_profiler import DataProfilerAgent
from agents.sttm import STTMAgent
from agents.bronze import BronzeAgent
from agents.silver import SilverAgent
from agents.gold import GoldAgent
from agents.reporter import ReporterAgent


def _event(agent: str, status: str, message: str = "", **extra) -> str:
    payload = {"agent": agent, "status": status, "message": message, **extra}
    return f"data: {json.dumps(payload)}\n\n"


class Orchestrator:
    def __init__(self, file_path: str | Path, base_dir: str | Path = "."):
        self.file_path = Path(file_path)
        self.base_dir = Path(base_dir)

    async def run(self) -> AsyncGenerator[str, None]:
        pipeline_log: dict = {"stages": {}}

        # ── Validate ───────────────────────────────────────────────────────────
        if not self.file_path.exists():
            yield _event("orchestrator", "error", f"File not found: {self.file_path}")
            return
        if self.file_path.suffix.lower() != ".csv":
            yield _event("orchestrator", "error", "Only CSV files are supported")
            return

        # ── Data Profiler ──────────────────────────────────────────────────────
        yield _event("profiler", "running", "Analyzing CSV structure...")
        profiler = DataProfilerAgent(
            self.file_path,
            output_dir=self.base_dir / "data" / "bronze",
        )
        profiler_result = profiler.run()
        if not profiler_result.get("success"):
            yield _event("orchestrator", "error", profiler_result.get("error", ""), agent_failed="profiler")
            return
        pipeline_log["stages"]["profiler"] = profiler_result
        yield _event(
            "profiler", "done",
            profiler_result.get("message", "Profile complete."),
            output=profiler_result.get("profile"),
        )

        # ── STTM ───────────────────────────────────────────────────────────────
        yield _event("sttm", "running", "Designing transformation mappings...")
        sttm_agent = STTMAgent(
            profiler_result["profile_path"],
            output_dir=self.base_dir / "data" / "bronze",
        )
        sttm_result = sttm_agent.run()
        if not sttm_result.get("success"):
            yield _event("orchestrator", "error", sttm_result.get("error", ""), agent_failed="sttm")
            return
        pipeline_log["stages"]["sttm"] = sttm_result
        yield _event("sttm", "done", sttm_result.get("message", "STTM plan ready."), output=sttm_result.get("sttm_plan"))

        # ── Bronze ─────────────────────────────────────────────────────────────
        yield _event("bronze", "running", "Applying Bronze layer transformations...")
        bronze_agent = BronzeAgent(
            self.file_path,
            sttm_result["sttm_path"],
            output_dir=self.base_dir / "data" / "bronze",
        )
        bronze_result = bronze_agent.run()
        if not bronze_result.get("success"):
            yield _event("orchestrator", "error", bronze_result.get("error", ""), agent_failed="bronze")
            return
        pipeline_log["stages"]["bronze"] = bronze_result
        yield _event("bronze", "done", bronze_result.get("message", "Bronze complete."), output=bronze_result.get("log"))

        # ── Silver ─────────────────────────────────────────────────────────────
        yield _event("silver", "running", "Cleansing and standardizing data...")
        silver_agent = SilverAgent(
            bronze_result["bronze_path"],
            sttm_result["sttm_path"],
            output_dir=self.base_dir / "data" / "silver",
        )
        silver_result = silver_agent.run()
        if not silver_result.get("success"):
            yield _event("orchestrator", "error", silver_result.get("error", ""), agent_failed="silver")
            return
        pipeline_log["stages"]["silver"] = silver_result
        yield _event("silver", "done", silver_result.get("message", "Silver complete."), output=silver_result.get("log"))

        # ── Gold ───────────────────────────────────────────────────────────────
        yield _event("gold", "running", "Computing aggregations and KPIs...")
        gold_agent = GoldAgent(
            silver_result["silver_path"],
            sttm_result["sttm_path"],
            output_dir=self.base_dir / "data" / "gold",
        )
        gold_result = gold_agent.run()
        if not gold_result.get("success"):
            yield _event("orchestrator", "error", gold_result.get("error", ""), agent_failed="gold")
            return
        pipeline_log["stages"]["gold"] = gold_result
        yield _event("gold", "done", gold_result.get("message", "Gold complete."), output=gold_result.get("log"))

        # ── Reporter ───────────────────────────────────────────────────────────
        yield _event("reporter", "running", "Generating analytics report...")
        reporter = ReporterAgent(
            gold_result["gold_dir"],
            pipeline_log=pipeline_log,
            output_dir=self.base_dir / "reports",
            report_name=self.file_path.stem,
        )
        reporter_result = reporter.run()
        if not reporter_result.get("success"):
            yield _event("orchestrator", "error", reporter_result.get("error", ""), agent_failed="reporter")
            return
        pipeline_log["stages"]["reporter"] = reporter_result
        yield _event("reporter", "done", reporter_result.get("message", "Report ready."))

        # ── Done ───────────────────────────────────────────────────────────────
        silver_log = silver_result.get("log", {})
        gold_log = gold_result.get("log", {})
        yield _event(
            "orchestrator",
            "complete",
            "Pipeline finished successfully.",
            report_url=reporter_result["report_url"],
            stats={
                "rows_ingested": silver_log.get("input_rows", 0),
                "rows_after_silver": silver_log.get("output_rows", 0),
                "anomalies_flagged": silver_log.get("anomalies_flagged", 0),
                "gold_tables": len(gold_log.get("tables_created", [])),
            },
        )
