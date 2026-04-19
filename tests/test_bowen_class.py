import json
from pathlib import Path


def test_bowen_class_json_is_consistent():
    bowen_path = Path("docs/internal/bowen_class_v1.json")
    assumptions_path = Path("docs/internal/theorem_assumptions_v1.json")

    bowen = json.loads(bowen_path.read_text())
    assumptions = json.loads(assumptions_path.read_text())

    assert bowen["decision"] in {"proved_primary", "narrowed_and_proved"}
    assert bowen["selected_hypothesis"] in {
        "quasi_multiplicativity",
        "tempered_memory",
        "almost_additivity",
        "narrow_hybrid",
    }
    assert bowen["proof_status"] == "proved_in_note"

    included = set(bowen["included_families"])
    assert "contextual_local.prefix_memory_no_22_base3" in included
    assert any(family.startswith("contextual_local.") for family in included)

    assumption_ids = set(assumptions["assumption_catalog"].keys())
    assert set(bowen["assumptions_used"]).issubset(assumption_ids)

    primary_class_id = assumptions["primary_class_id"]
    if bowen["decision"] == "proved_primary":
        assert bowen["proved_class_id"] == primary_class_id
    else:
        assert bowen["proved_class_id"] != primary_class_id

    accounted = (
        set(bowen["included_families"])
        | set(bowen["excluded_families"])
        | set(bowen.get("not_claimed_families", []))
    )
    config_family_ids = set()
    for path in Path("configs/experiments").glob("**/*.json"):
        config_family_ids.add(json.loads(path.read_text())["family_id"])
    assert accounted == config_family_ids
