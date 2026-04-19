from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ASSUMPTIONS_PATH = REPO_ROOT / "docs" / "internal" / "continuous_theorem_assumptions_v1.json"
DEPENDENCY_PATH = REPO_ROOT / "docs" / "internal" / "proof_dependency_continuous_pressure_v1.json"
REPORT_PATH = REPO_ROOT / "results" / "continuous_pressure_existence" / "report.json"
NOTE_PATH = REPO_ROOT / "docs" / "internal" / "continuous_pressure_existence_v1.md"
SCRIPT_PATH = REPO_ROOT / "scripts" / "run_continuous_pressure_checks.py"

ALLOWED_ROUTES = {
    "fekete_sup_cocycle_route",
    "kingman_measure_route",
    "almost_subadditive_external_route",
}

ALLOWED_STATUSES = {"closed_in_note", "standard_external", "localized_gap"}


def test_continuous_pressure_artifacts_exist() -> None:
    assert ASSUMPTIONS_PATH.exists()
    assert DEPENDENCY_PATH.exists()
    assert REPORT_PATH.exists()
    assert NOTE_PATH.exists()
    assert SCRIPT_PATH.exists()


def test_continuous_pressure_structure() -> None:
    assumptions = json.loads(ASSUMPTIONS_PATH.read_text(encoding="utf-8"))
    dependency = json.loads(DEPENDENCY_PATH.read_text(encoding="utf-8"))
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))

    assert dependency["working_class_id"] == "continuous_full_loop_lawful_kernel_class_shell_stable"
    assert dependency["selected_pressure_route"] in ALLOWED_ROUTES
    assert dependency["selected_observable_family"]
    referenced = set(dependency["assumptions_used"])
    available = {entry["assumption_id"] for entry in assumptions["assumption_catalog"]}
    assert referenced <= available
    assert sum(1 for lemma in dependency["lemmas"] if lemma["status"] in ALLOWED_STATUSES) == len(dependency["lemmas"])
    assert {entry["family_id"] for entry in dependency["witness_families"]} == {
        "generated.continuous_full_loop_kernel",
        "generated.continuous_full_loop_kernel_shell",
    }
    assert report["selected_pressure_route"] == "switched_operator_cocycle_pressure"
    assert report["selected_observable_family"] == "selector_weighted_operator_growth_observable"
    assert report["support_summary"]["all_six_primitives_active"] is True

