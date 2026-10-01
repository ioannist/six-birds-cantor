"""Keep sampled numerical reports separate from mathematical certification."""
from __future__ import annotations

from typing import Any
from datetime import datetime, timezone

REVIEW_PATH = "docs/internal/mathematics_review_2026_10_01.md"


def mark_diagnostic_report(report: dict[str, Any], scope: str) -> None:
    """Preserve provenance while withdrawing unsupported closure decisions."""
    report["historical_workflow_generated_at_utc"] = report.get("generated_at_utc")
    report["generated_at_utc"] = datetime.now(timezone.utc).isoformat()
    report["historical_workflow_decision"] = report.get("decision")
    report["decision"] = "diagnostic_only_not_certified"
    certification = report.setdefault("mathematical_certification", {})
    certification.update({"main_theorem_certified": False, "scope": scope, "review": REVIEW_PATH})
