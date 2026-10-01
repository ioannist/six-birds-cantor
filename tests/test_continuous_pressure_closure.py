from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ASSUMPTIONS_PATH = REPO_ROOT / "docs" / "internal" / "continuous_theorem_assumptions_v1.json"
DEPENDENCY_PATH = REPO_ROOT / "docs" / "internal" / "proof_dependency_continuous_pressure_v1.json"
CLOSURE_PATH = REPO_ROOT / "docs" / "internal" / "proof_dependency_continuous_pressure_closure_v1.json"
REPORT_PATH = REPO_ROOT / "results" / "continuous_pressure_closure" / "report.json"
NOTE_PATH = REPO_ROOT / "docs" / "internal" / "continuous_pressure_closure_v1.md"

ALLOWED_DECISIONS = {"closed_on_working_class", "working_class_narrowed_and_closed"}
ALLOWED_STATUSES = {"closed_in_note", "standard_external", "localized_gap"}


def test_continuous_pressure_closure_artifacts_exist() -> None:
    assert ASSUMPTIONS_PATH.exists()
    assert DEPENDENCY_PATH.exists()
    assert CLOSURE_PATH.exists()
    assert REPORT_PATH.exists()
    assert NOTE_PATH.exists()


def test_continuous_pressure_closure_structure() -> None:
    assumptions = json.loads(ASSUMPTIONS_PATH.read_text(encoding="utf-8"))
    dependency = json.loads(DEPENDENCY_PATH.read_text(encoding="utf-8"))
    closure = json.loads(CLOSURE_PATH.read_text(encoding="utf-8"))
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))

    assert closure["decision"] in ALLOWED_DECISIONS
    assert dependency["selected_pressure_route"] == "fekete_sup_cocycle_route"
    assert dependency["selected_observable_family"] == "selector_weighted_operator_growth_observable"
    assert all(lemma["status"] in ALLOWED_STATUSES for lemma in closure["lemmas"])

    available = {entry["assumption_id"] for entry in assumptions["assumption_catalog"]}
    referenced = set(closure["assumptions_used"]) | {aid for lemma in closure["lemmas"] for aid in lemma["assumptions_used"]}
    assert referenced <= available

    assert {entry["family_id"] for entry in closure["witness_families"]} == {
        "generated.continuous_full_loop_kernel",
        "generated.continuous_full_loop_kernel_shell",
    }
    assert closure["closed_class_id"] == "continuous_full_loop_lawful_kernel_class_shell_stable"
    assert closure["decision"] == "closed_on_working_class"
    assert report["support_summary"]["all_six_primitives_active"] is True
    assert report["support_summary"]["monotonicity_support_fraction"] == 1.0
    assert report["decision"] == "diagnostic_only_not_certified"
    assert report["mathematical_certification"]["main_theorem_certified"] is False
    assert report["support_summary"]["shell_exit_count"] == sum(run["shell_exit_count"] for run in report["runs"])
    assert dependency["mathematical_certification"]["main_theorems_certified"] is False
    assert dependency["lemmas"][1]["status"] == "closed_in_note"
    assert dependency["lemmas"][2]["status"] == "closed_in_note"
    assert dependency["lemmas"][-1]["status"] == "closed_in_note"

