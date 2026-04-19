from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = REPO_ROOT / "docs" / "internal" / "frontier_target_class_v1.json"
NOTE_PATH = REPO_ROOT / "docs" / "internal" / "frontier_target_class_v1.md"
CONFIG_PATHS = [
    REPO_ROOT / "configs" / "experiments" / "frontier" / "fw_delayed_return_gate_a3.json",
    REPO_ROOT / "configs" / "experiments" / "frontier" / "fw_delayed_return_gate_a1.json",
    REPO_ROOT / "configs" / "experiments" / "frontier" / "fw_delayed_return_gate_a2.json",
]
ALLOWED_DECISIONS = {
    "advance_bounded_return_delayed_gate",
    "advance_finite_state_renewal_local_domain",
    "advance_countable_state_delayed_return",
    "not_ready_for_theorem_branch",
}
ALLOWED_SELECTIONS = {"working", "stretch", "reserve"}
ALLOWED_MEMBERSHIP = {"in", "out", "unknown"}


def test_frontier_target_files_exist() -> None:
    assert NOTE_PATH.exists()
    assert JSON_PATH.exists()
    for path in CONFIG_PATHS:
        assert path.exists()


def test_frontier_target_json_is_consistent() -> None:
    payload = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    assert payload["decision"] in ALLOWED_DECISIONS

    classes = payload["candidate_classes"]
    assert sum(1 for entry in classes if entry["selection_status"] == "working") == 1
    assert sum(1 for entry in classes if entry["selection_status"] == "stretch") == 1
    for entry in classes:
        assert entry["selection_status"] in ALLOWED_SELECTIONS

    witness_ids = {entry["family_id"] for entry in payload["witness_families"]}
    membership_ids = {entry["family_id"] for entry in payload["family_membership"]}
    assert witness_ids == membership_ids
    expected = {
        "frontier.fw_delayed_return_gate_a3",
        "frontier.fw_delayed_return_gate_a1",
        "frontier.fw_delayed_return_gate_a2",
    }
    assert expected <= witness_ids
    for entry in payload["family_membership"]:
        assert entry["working_class_membership"] in ALLOWED_MEMBERSHIP
        assert entry["stretch_class_membership"] in ALLOWED_MEMBERSHIP
