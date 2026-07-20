from __future__ import annotations

from typing import Iterable


class ReportingTool:
	def generate_markdown(
		self,
		dataset_name: str,
		executive_summary: str,
		key_findings: Iterable[str],
		recommendations: Iterable[str],
		quality_notes: Iterable[str],
		workflow_notes: Iterable[str],
	) -> str:
		lines = [f"# {dataset_name}", "", "## Executive Summary", executive_summary, ""]
		lines.extend(["## Key Findings"] + [f"- {item}" for item in key_findings] + [""])
		lines.extend(["## Recommendations"] + [f"- {item}" for item in recommendations] + [""])
		lines.extend(["## Quality Notes"] + [f"- {item}" for item in quality_notes] + [""])
		lines.extend(["## Workflow Notes"] + [f"- {item}" for item in workflow_notes] + [""])
		return "\n".join(lines).strip()
