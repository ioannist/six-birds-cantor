from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = REPO_ROOT / "docs" / "internal" / "continuous_kernel_substrate_v1.json"
NOTE_PATH = REPO_ROOT / "docs" / "internal" / "continuous_kernel_substrate_v1.md"
REPORT_PATH = REPO_ROOT / "results" / "continuous_kernel_pilot" / "report.json"
TRAJECTORY_PATH = REPO_ROOT / "results" / "continuous_kernel_pilot" / "trajectory.csv"
KNOCKOUT_PATH = REPO_ROOT / "results" / "continuous_kernel_pilot" / "knockout_report.json"

ALLOWED_DECISIONS = {
    "continuous_full_loop_working",
    "continuous_substrate_but_partial_loop",
    "continuous_reset_blocked",
}


def test_continuous_kernel_artifacts_exist() -> None:
    assert NOTE_PATH.exists()
    assert SPEC_PATH.exists()
    assert REPORT_PATH.exists()
    assert TRAJECTORY_PATH.exists()
    assert KNOCKOUT_PATH.exists()


def test_continuous_kernel_spec_and_report() -> None:
    spec = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    knockout = json.loads(KNOCKOUT_PATH.read_text(encoding="utf-8"))

    assert spec["pilot_decision"] in ALLOWED_DECISIONS
    assert report["decision"] in ALLOWED_DECISIONS
    assert report["steps"] >= 1000
    assert len(spec["primitive_roles"]) == 6
    assert len(spec["lens_algorithms"]) >= 3
    assert len(spec["packaging_algorithms"]) >= 3
    assert len(report.get("knockout_results", [])) == 6
    assert len(knockout.get("knockout_results", [])) == 6
    assert report["kernel_dimension"] >= 16

