from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_PATH = REPO_ROOT / "docs" / "internal" / "continuous_full_loop_theorem_package_v1.json"
TARGET_PATH = REPO_ROOT / "docs" / "internal" / "continuous_thermodynamic_target_v1.json"
REPORT_PATH = REPO_ROOT / "results" / "continuous_thermodynamic_diagnostics" / "report.json"
WORKING_CONFIG = REPO_ROOT / "configs" / "experiments" / "generated" / "continuous_full_loop_kernel.json"
SHELL_CONFIG = REPO_ROOT / "configs" / "experiments" / "generated" / "continuous_full_loop_kernel_shell.json"

ALLOWED_DECISIONS = {
    "thermodynamic_working_target_extracted",
    "thermodynamic_target_plausible_but_not_sharp",
    "thermodynamic_target_not_ready",
}


def test_continuous_thermodynamic_artifacts_exist() -> None:
    assert PACKAGE_PATH.exists()
    assert TARGET_PATH.exists()
    assert REPORT_PATH.exists()
    assert WORKING_CONFIG.exists()
    assert SHELL_CONFIG.exists()


def test_continuous_thermodynamic_structure() -> None:
    package = json.loads(PACKAGE_PATH.read_text(encoding="utf-8"))
    target = json.loads(TARGET_PATH.read_text(encoding="utf-8"))
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))

    assert package["proof_status"] == "closed_in_note"
    assert target["decision"] in ALLOWED_DECISIONS
    assert sum(1 for route in target["candidate_routes"] if route["selection_status"] == "working") == 1
    assert sum(1 for route in target["candidate_routes"] if route["selection_status"] == "stretch") == 1
    assert target["working_target"] == "switched_operator_cocycle_pressure"
    assert target["stretch_target"] == "packaging_induced_pressure"
    assert report["decision"] in ALLOWED_DECISIONS
    assert report["working_target"]["route_id"] == "switched_operator_cocycle_pressure"
    assert report["stretch_target"]["route_id"] == "packaging_induced_pressure"
    assert {cfg["family_id"] for cfg in package["witness_configs"]} == {
        "generated.continuous_full_loop_kernel",
        "generated.continuous_full_loop_kernel_shell",
    }
    assert set(report["frozen_configs"]) == {
        "configs/experiments/generated/continuous_full_loop_kernel.json",
        "configs/experiments/generated/continuous_full_loop_kernel_shell.json",
    }

