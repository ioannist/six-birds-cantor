from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEP_PATH = REPO_ROOT / "docs" / "internal" / "proof_dependency_delayed_return_v1.json"
ASSUMPTIONS_PATH = REPO_ROOT / "docs" / "internal" / "delayed_return_theorem_assumptions_v1.json"
NOTE_PATH = REPO_ROOT / "docs" / "internal" / "delayed_return_proof_scaffold_v1.md"

ALLOWED_ROUTES = {
    "induced_cylinder_premeasure",
    "induced_markov_renewal_measure",
    "induced_gibbs_like_measure",
}
ALLOWED_STATUS = {"closed_in_note", "standard_external", "localized_gap"}
REQUIRED_BLOCKS = {
    "DR-LEM-1",
    "DR-LEM-2",
    "DR-LEM-3",
    "DR-LEM-4",
    "DR-LEM-5",
    "DR-LEM-6",
    "DR-THM-7",
}


def test_delayed_return_dependency_json_is_consistent() -> None:
    assert NOTE_PATH.exists()
    assert DEP_PATH.exists()
    assert ASSUMPTIONS_PATH.exists()

    dep = json.loads(DEP_PATH.read_text(encoding="utf-8"))
    assumptions = json.loads(ASSUMPTIONS_PATH.read_text(encoding="utf-8"))
    assumption_ids = set(assumptions["assumption_catalog"].keys())

    assert dep["working_class_id"] == "bounded_return_delayed_gate_subclass"
    assert dep["selected_lower_route"] in ALLOWED_ROUTES
    assert "frontier.fw_delayed_return_gate_a3" in dep["witness_families"]

    assert set(dep["assumptions_used"]).issubset(assumption_ids)
    lemma_ids = set()
    for lemma in dep["lemmas"]:
        lemma_ids.add(lemma["lemma_id"])
        assert set(lemma["assumptions_used"]).issubset(assumption_ids)
        assert lemma["status"] in ALLOWED_STATUS
    assert REQUIRED_BLOCKS.issubset(lemma_ids)
