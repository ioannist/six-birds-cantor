from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = REPO_ROOT / "results" / "continuous_regime_diagnostics" / "report.json"
ASSUMPTIONS_PATH = REPO_ROOT / "docs" / "internal" / "continuous_lawful_regime_assumptions_v1.json"
NOTE_PATH = REPO_ROOT / "docs" / "internal" / "continuous_lawful_regime_v1.md"

ALLOWED_DECISIONS = {
    "lawful_regime_extracted",
    "continuous_regime_too_brittle",
    "continuous_regime_needs_richer_search",
}


def test_continuous_regime_artifacts_exist() -> None:
    assert REPORT_PATH.exists()
    assert ASSUMPTIONS_PATH.exists()
    assert NOTE_PATH.exists()


def test_continuous_regime_report_structure() -> None:
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    assert report["decision"] in ALLOWED_DECISIONS
    assert report["working_regime_class"]
    assert report["stretch_regime_class"]
    runs = report.get("runs", [])
    assert len(runs) >= 12
    assert all("regime_label" in run and run["regime_label"] for run in runs)
    assert {run["regime_label"] for run in runs}


def test_continuous_regime_assumptions_structure() -> None:
    assumptions = json.loads(ASSUMPTIONS_PATH.read_text(encoding="utf-8"))
    assert assumptions["decision"] in ALLOWED_DECISIONS
    assert assumptions["working_regime_class"]
    assert assumptions["stretch_regime_class"]
    classes = assumptions.get("regime_classes", [])
    assert sum(1 for entry in classes if entry["selection_status"] == "working") == 1
    assert sum(1 for entry in classes if entry["selection_status"] == "stretch") == 1
    assert len(assumptions.get("candidate_assumptions", [])) >= 6
    primitive_necessity = assumptions.get("primitive_necessity", {})
    assert set(primitive_necessity) == {"P1", "P2", "P3", "P4", "P5", "P6"}

