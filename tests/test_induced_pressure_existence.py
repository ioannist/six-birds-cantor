from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PRESSURE_DEP_PATH = REPO_ROOT / "docs" / "internal" / "proof_dependency_induced_pressure_v1.json"
DELAYED_DEP_PATH = REPO_ROOT / "docs" / "internal" / "proof_dependency_delayed_return_v1.json"
ASSUMPTIONS_PATH = REPO_ROOT / "docs" / "internal" / "delayed_return_theorem_assumptions_v1.json"
NOTE_PATH = REPO_ROOT / "docs" / "internal" / "induced_pressure_existence_v1.md"
ALLOWED_DECISIONS = {"pressure_closed_for_working_class", "working_class_narrowed_and_pressure_closed"}
ALLOWED_STATUS = {"closed_in_note", "standard_external", "localized_gap"}
REQUIRED_BLOCKS = {"IP-LEM-1", "IP-LEM-2", "IP-LEM-3", "IP-LEM-4", "IP-COR-5"}


def test_induced_pressure_dependency_is_consistent() -> None:
    assert NOTE_PATH.exists()
    assert PRESSURE_DEP_PATH.exists()
    assert DELAYED_DEP_PATH.exists()
    assert ASSUMPTIONS_PATH.exists()

    pressure = json.loads(PRESSURE_DEP_PATH.read_text(encoding="utf-8"))
    delayed = json.loads(DELAYED_DEP_PATH.read_text(encoding="utf-8"))
    assumptions = json.loads(ASSUMPTIONS_PATH.read_text(encoding="utf-8"))
    assumption_ids = set(assumptions["assumption_catalog"].keys())

    assert pressure["decision"] in ALLOWED_DECISIONS
    assert pressure["proved_pressure_class_id"]
    assert "frontier.fw_delayed_return_gate_a3" in pressure["witness_families"]
    assert set(pressure["assumptions_used"]).issubset(assumption_ids)

    lemma_ids = set()
    for lemma in pressure["lemmas"]:
        lemma_ids.add(lemma["lemma_id"])
        assert set(lemma["assumptions_used"]).issubset(assumption_ids)
        assert lemma["status"] in ALLOWED_STATUS
    assert REQUIRED_BLOCKS.issubset(lemma_ids)

    dr3 = next(lemma for lemma in delayed["lemmas"] if lemma["lemma_id"] == "DR-LEM-3")
    assert dr3["status"] in {"closed_in_note", "standard_external"}
