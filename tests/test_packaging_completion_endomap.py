from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
NOTE_PATH = REPO_ROOT / "docs" / "internal" / "packaging_completion_endomap_v1.md"
JSON_PATH = REPO_ROOT / "docs" / "internal" / "packaging_completion_endomap_v1.json"
REPORT_PATH = REPO_ROOT / "results" / "packaging_completion_endomap" / "report.json"

ALLOWED_DECISIONS = {
    "advance_completion_object_theorem",
    "completion_object_real_but_not_broader",
    "completion_endomap_blocked",
}


def test_packaging_completion_artifacts_exist() -> None:
    assert NOTE_PATH.exists()
    assert JSON_PATH.exists()
    assert REPORT_PATH.exists()


def test_packaging_completion_structure() -> None:
    spec = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))

    assert spec["decision"] in ALLOWED_DECISIONS
    assert report["decision"] in ALLOWED_DECISIONS
    assert set(report["frozen_configs"]) == {
        "configs/experiments/generated/continuous_full_loop_kernel.json",
        "configs/experiments/generated/continuous_full_loop_kernel_shell.json",
    }
    assert len(report["tau_values_checked"]) >= 2
    assert len(report["initial_conditions_checked"]) >= 3
    assert "fixed_point_count_summary" in report
    assert "p4_from_p5_feedback_summary" in report
    assert "macro_admissibility_summary" in report
    assert "completion_map_definition" in spec
    assert "fixed_point_protocol" in spec
    assert "saturation_definition" in spec
    assert "p4_from_p5_feedback_rule" in spec
    assert "macro_admissibility_rule" in spec

