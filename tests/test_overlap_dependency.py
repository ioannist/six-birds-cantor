from __future__ import annotations

import json
from pathlib import Path


def test_overlap_dependency_json_is_consistent() -> None:
    dep_path = Path("docs/internal/proof_dependency_overlap_v1.json")
    assumptions_path = Path("docs/internal/theorem_assumptions_v1.json")

    dep = json.loads(dep_path.read_text(encoding="utf-8"))
    assumptions = json.loads(assumptions_path.read_text(encoding="utf-8"))
    assumption_ids = set(assumptions["assumption_catalog"].keys())

    assert dep["target_subclass_id"]
    assert set(dep["assumptions_used"]).issubset(assumption_ids)

    lemmas = {entry["lemma_id"]: entry for entry in dep["lemmas"]}
    assert {"LEM-OVL-1", "LEM-OVL-2", "COR-OVL-3"}.issubset(lemmas)
    assert "contextual_local.prefix_memory_last_digit_rule" in dep["witness_families"]

    for lemma in dep["lemmas"]:
        assert set(lemma["assumptions_used"]).issubset(assumption_ids)
        assert lemma["status"] in {"closed_in_note", "standard_external", "localized_gap"}
