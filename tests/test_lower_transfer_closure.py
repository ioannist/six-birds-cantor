from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
LOWER_DEP_PATH = REPO_ROOT / "docs" / "internal" / "proof_dependency_lower_transfer_v1.json"
DELAYED_DEP_PATH = REPO_ROOT / "docs" / "internal" / "proof_dependency_delayed_return_v1.json"
ASSUMPTIONS_PATH = REPO_ROOT / "docs" / "internal" / "delayed_return_theorem_assumptions_v1.json"
NOTE_PATH = REPO_ROOT / "docs" / "internal" / "lower_transfer_truncation_control_v1.md"
ALLOWED_DECISIONS = {"closed_on_working_class", "working_class_narrowed_and_closed"}
ALLOWED_STATUS = {"closed_in_note", "standard_external", "localized_gap"}
REQUIRED_BLOCKS = {"LT-LEM-1", "LT-LEM-2", "LT-LEM-3", "LT-LEM-4", "LT-THM-5", "LT-COR-6"}


def test_lower_transfer_dependency_is_consistent() -> None:
    assert NOTE_PATH.exists()
    assert LOWER_DEP_PATH.exists()
    assert DELAYED_DEP_PATH.exists()
    assert ASSUMPTIONS_PATH.exists()

    lower = json.loads(LOWER_DEP_PATH.read_text(encoding="utf-8"))
    delayed = json.loads(DELAYED_DEP_PATH.read_text(encoding="utf-8"))
    assumptions = json.loads(ASSUMPTIONS_PATH.read_text(encoding="utf-8"))
    assumption_ids = set(assumptions["assumption_catalog"].keys())

    assert lower["decision"] in ALLOWED_DECISIONS
    assert lower["selected_lower_route"] == "induced_cylinder_premeasure"
    assert "frontier.fw_delayed_return_gate_a3" in lower["witness_families"]
    assert set(lower["assumptions_used"]).issubset(assumption_ids)

    lemma_ids = set()
    for lemma in lower["lemmas"]:
        lemma_ids.add(lemma["lemma_id"])
        assert set(lemma["assumptions_used"]).issubset(assumption_ids)
        assert lemma["status"] in ALLOWED_STATUS
    assert REQUIRED_BLOCKS.issubset(lemma_ids)

    dr6 = next(lemma for lemma in delayed["lemmas"] if lemma["lemma_id"] == "DR-LEM-6")
    dr7 = next(lemma for lemma in delayed["lemmas"] if lemma["lemma_id"] == "DR-THM-7")
    assert dr6["status"] in {"closed_in_note", "standard_external"}
    assert dr7["status"] == "closed_in_note"
