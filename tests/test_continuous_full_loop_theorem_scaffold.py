from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEPENDENCY_PATH = REPO_ROOT / "docs" / "internal" / "proof_dependency_continuous_full_loop_v1.json"
NOTE_PATH = REPO_ROOT / "docs" / "internal" / "continuous_full_loop_theorem_scaffold_v1.md"
ASSUMPTIONS_PATH = REPO_ROOT / "docs" / "internal" / "continuous_theorem_assumptions_v1.json"

ALLOWED_ROUTES = {
    "hysteretic_switched_operator_cocycle",
    "compact_random_dynamical_system",
    "deterministic_skew_product_with_budget_feedback",
}
ALLOWED_STATUSES = {"closed_in_note", "standard_external", "localized_gap"}

REQUIRED_BLOCKS = [
    "CK-LEM-1",
    "CK-LEM-2",
    "CK-LEM-3",
    "CK-LEM-4",
    "CK-LEM-5",
    "CK-LEM-6",
    "CK-THM-7",
]


def test_continuous_full_loop_scaffold_artifacts_exist() -> None:
    assert NOTE_PATH.exists()
    assert DEPENDENCY_PATH.exists()


def test_continuous_full_loop_dependency_structure() -> None:
    dependency = json.loads(DEPENDENCY_PATH.read_text(encoding="utf-8"))
    assumptions = json.loads(ASSUMPTIONS_PATH.read_text(encoding="utf-8"))
    assumption_ids = {entry["assumption_id"] for entry in assumptions["assumption_catalog"]}

    assert dependency["working_class_id"] == "continuous_full_loop_lawful_kernel_class"
    assert dependency["stretch_class_id"] == "continuous_full_loop_lawful_kernel_class_with_wider_parameter_shell"
    assert dependency["selected_route"] in ALLOWED_ROUTES
    assert dependency["selected_route"] == "deterministic_skew_product_with_budget_feedback"
    assert len(dependency["lemmas"]) == 7
    assert {lemma["lemma_id"] for lemma in dependency["lemmas"]} == set(REQUIRED_BLOCKS)
    for lemma in dependency["lemmas"]:
        assert lemma["status"] in ALLOWED_STATUSES
        assert set(lemma["assumptions_used"]).issubset(assumption_ids)
    assert any(entry["family_id"] == "generated.continuous_full_loop_kernel" for entry in dependency["witness_families"])
    assert any(entry["family_id"] == "generated.continuous_full_loop_kernel_shell" for entry in dependency["witness_families"])
    assert "P1<-P5" in dependency["theorem_statement_short"] or "P1<-P5" in NOTE_PATH.read_text(encoding="utf-8")
    assert "P2<-P5" in dependency["theorem_statement_short"] or "P2<-P5" in NOTE_PATH.read_text(encoding="utf-8")
