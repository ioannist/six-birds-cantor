from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
TARGET_PATH = REPO_ROOT / "docs" / "internal" / "packaging_induced_stretch_v1.json"
NOTE_PATH = REPO_ROOT / "docs" / "internal" / "packaging_induced_stretch_v1.md"
REPORT_PATH = REPO_ROOT / "results" / "packaging_induced_stretch" / "report.json"
WORKING_CONFIG = REPO_ROOT / "configs" / "experiments" / "generated" / "continuous_full_loop_kernel.json"
SHELL_CONFIG = REPO_ROOT / "configs" / "experiments" / "generated" / "continuous_full_loop_kernel_shell.json"

ALLOWED_DECISIONS = {
    "advance_packaging_induced_theorem",
    "packaging_route_plausible_but_not_broader",
    "freeze_on_cocycle_route",
}


def test_packaging_stretch_artifacts_exist() -> None:
    assert NOTE_PATH.exists()
    assert TARGET_PATH.exists()
    assert REPORT_PATH.exists()
    assert WORKING_CONFIG.exists()
    assert SHELL_CONFIG.exists()


def test_packaging_stretch_structure() -> None:
    target = json.loads(TARGET_PATH.read_text(encoding="utf-8"))
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))

    assert target["decision"] in ALLOWED_DECISIONS
    assert sum(1 for route in target["candidate_routes"] if route["selection_status"] == "selected") == 1
    assert sum(1 for route in target["candidate_routes"] if route["selection_status"] == "reserve") == 1
    assert sum(1 for route in target["candidate_routes"] if route["selection_status"] == "rejected") == 1
    assert any(route["route_id"] == "packaging_induced_shell_stable_class" for route in target["candidate_routes"])
    assert report["decision"] in ALLOWED_DECISIONS
    assert set(report["frozen_configs"]) == {
        "configs/experiments/generated/continuous_full_loop_kernel.json",
        "configs/experiments/generated/continuous_full_loop_kernel_shell.json",
    }
    assert report["route_comparison"]["working_route"] == "packaging_induced_shell_stable_class"
    assert report["route_comparison"]["reserve_route"] == "packaging_induced_wider_shell_class"
    assert report["route_comparison"]["rejected_route"] == "cocycle_route_is_final_best_story"
    test_ids = {item["test_id"] for item in report["broadening_tests"]}
    assert test_ids == {
        "class_broadening_test",
        "primitive_value_test",
        "nondegeneracy_test",
        "robustness_test",
    }

