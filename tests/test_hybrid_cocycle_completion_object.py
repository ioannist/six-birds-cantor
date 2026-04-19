from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = REPO_ROOT / "docs" / "internal" / "hybrid_cocycle_completion_object_v1.json"
REPORT_PATH = REPO_ROOT / "results" / "hybrid_object_diagnostics" / "report.json"

ALLOWED_DECISIONS = {
    "advance_hybrid_theorem",
    "hybrid_real_but_not_yet_broader",
    "freeze_on_cocycle_route",
}


def test_hybrid_artifacts_exist() -> None:
    assert JSON_PATH.exists()
    assert REPORT_PATH.exists()


def test_hybrid_structure() -> None:
    target = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))

    assert target["decision"] in ALLOWED_DECISIONS
    assert report["decision"] in ALLOWED_DECISIONS
    assert set(report["frozen_configs"]) == {
        "configs/experiments/generated/continuous_full_loop_kernel.json",
        "configs/experiments/generated/continuous_full_loop_kernel_shell.json",
    }
    for key in [
        "object_identity_verdict",
        "saturation_verdict",
        "p4_from_p5_forcing_verdict",
        "class_broadening_verdict",
    ]:
        assert key in report
        assert key in target
    assert len(report["broadening_tests"]) == 4
    assert target["candidate_hybrid_story"]["route_id"] == "hybrid_same_class_stronger_object"

