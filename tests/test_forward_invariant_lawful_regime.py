from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEPENDENCY_PATH = REPO_ROOT / "docs" / "internal" / "proof_dependency_forward_invariant_regime_v1.json"
NOTE_PATH = REPO_ROOT / "docs" / "internal" / "forward_invariant_lawful_regime_v1.md"
ASSUMPTIONS_PATH = REPO_ROOT / "docs" / "internal" / "continuous_theorem_assumptions_v1.json"
CONTINUOUS_DEP_PATH = REPO_ROOT / "docs" / "internal" / "proof_dependency_continuous_full_loop_v1.json"

ALLOWED_DECISIONS = {"closed_on_working_class", "working_class_narrowed_and_closed"}
ALLOWED_STATUSES = {"closed_in_note", "standard_external", "localized_gap"}
REQUIRED_BLOCKS = ["FR-LEM-1", "FR-LEM-2", "FR-LEM-3", "FR-LEM-4", "FR-LEM-5", "FR-THM-6", "FR-COR-7"]


def test_forward_invariant_artifacts_exist() -> None:
    assert NOTE_PATH.exists()
    assert DEPENDENCY_PATH.exists()


def test_forward_invariant_dependency_structure() -> None:
    dependency = json.loads(DEPENDENCY_PATH.read_text(encoding="utf-8"))
    assumptions = json.loads(ASSUMPTIONS_PATH.read_text(encoding="utf-8"))
    assumption_ids = {entry["assumption_id"] for entry in assumptions["assumption_catalog"]}
    continuous_dep = json.loads(CONTINUOUS_DEP_PATH.read_text(encoding="utf-8"))

    assert dependency["decision"] in ALLOWED_DECISIONS
    assert dependency["closed_class_id"] == "continuous_full_loop_lawful_kernel_class_shell_stable"
    assert dependency["selected_route"] == "deterministic_skew_product_with_budget_feedback"
    assert len(dependency["lemmas"]) == 7
    assert {lemma["lemma_id"] for lemma in dependency["lemmas"]} == set(REQUIRED_BLOCKS)
    for lemma in dependency["lemmas"]:
        assert lemma["status"] in ALLOWED_STATUSES
        assert set(lemma["assumptions_used"]).issubset(assumption_ids)
    witness_ids = {entry["family_id"] for entry in dependency["witness_families"]}
    assert "generated.continuous_full_loop_kernel" in witness_ids
    assert "generated.continuous_full_loop_kernel_shell" in witness_ids
    by_lemma = {entry["lemma_id"]: entry for entry in continuous_dep["lemmas"]}
    assert by_lemma["CK-LEM-5"]["status"] == "closed_in_note"
    assert by_lemma["CK-THM-7"]["status"] == "closed_in_note"
