"""Quality report generation — writes JSON artifacts."""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger("enterprise_pipeline")


class QualityReporter:
    """Collects quality check results and writes them as JSON reports."""

    def __init__(self, output_dir: str = "quality_reports") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results: list[dict[str, object]] = []

    def add_result(self, result: dict[str, object]) -> None:
        self.results.append(result)

    def all_passed(self) -> bool:
        return all(r.get("passed", False) for r in self.results)

    def summary(self) -> dict[str, object]:
        total = len(self.results)
        passed = sum(1 for r in self.results if r.get("passed", False))
        failed = total - passed
        return {
            "total_checks": total,
            "passed": passed,
            "failed": failed,
            "all_passed": self.all_passed(),
        }

    def write_report(self, pipeline_name: str = "enterprise-positions") -> Path:
        """Write the full quality report as a JSON file."""
        report = {
            "pipeline": pipeline_name,
            "timestamp": datetime.utcnow().isoformat(),
            "summary": self.summary(),
            "checks": self.results,
        }
        filename = f"quality_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        report_path = self.output_dir / filename
        report_path.write_text(json.dumps(report, indent=2, default=str))
        logger.info("Quality report written to %s: %s", report_path, self.summary())
        return report_path
