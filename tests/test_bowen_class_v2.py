from __future__ import annotations

import json
from pathlib import Path


def test_bowen_class_v2_json_is_consistent() -> None:
    bowen_path = Path("docs/internal/bowen_class_v2.json")
    assumptions_path = Path("docs/internal/theorem_assumptions_v1.json")

    bowen = json.loads(bowen_path.read_text(encoding="utf-8"))
    assumptions = json.loads(assumptions_path.read_text(encoding="utf-8"))
    assumption_ids = set(assumptions["assumption_catalog"].keys())

    assert bowen["decision"] in {"proved_primary", "narrowed_and_proved"}
    assert bowen["selected_hypothesis"] in {
        "quasi_multiplicativity",
        "tempered_memory",
        "almost_additivity",
        "narrow_hybrid",
    }
    assert bowen["proof_status"] == "proved_in_note"

    included = set(bowen["included_families"])
    assert "contextual_local.prefix_memory_last_digit_rule" in included
    assert "contextual_local.prefix_memory_no_22_base3" in included
    assert any(fam.startswith("classical.") for fam in included)

    assert set(bowen["assumptions_used"]).issubset(assumption_ids)

    primary_class_id = assumptions["primary_class_id"]
    if bowen["decision"] == "proved_primary":
        assert bowen["proved_class_id"] == primary_class_id
    else:
        assert bowen["proved_class_id"] != primary_class_id

    config_family_ids = set()
    for path in Path("configs/experiments").glob("**/*.json"):
        config_family_ids.add(json.loads(path.read_text(encoding="utf-8"))["family_id"])
    accounted = set(bowen["included_families"]) | set(bowen["excluded_families"]) | set(bowen["not_claimed_families"])
    assert accounted == config_family_ids
