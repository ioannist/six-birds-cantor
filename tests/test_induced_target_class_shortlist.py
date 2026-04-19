from __future__ import annotations

import json
from pathlib import Path


def test_induced_target_class_shortlist_is_consistent() -> None:
    shortlist = json.loads(Path("docs/internal/induced_target_class_shortlist_v1.json").read_text(encoding="utf-8"))
    assert shortlist["decision"] in {
        "advance_finite_state_induced_only",
        "advance_finite_state_renewal",
        "advance_countable_state_renewal",
        "no_credible_frontier_target_yet",
    }

    selected = [c for c in shortlist["candidate_classes"] if c["selection_status"] == "selected"]
    assert len(selected) == 1

    families = {entry["family_id"]: entry for entry in shortlist["family_evaluation"]}
    assert "contextual_local.domain_gated_two_map_local_ifs" in families
    target = families["contextual_local.domain_gated_two_map_local_ifs"]
    assert target["induced_core_type"]
    assert target["return_time_regime"]
    assert target["effective_alphabet_regime"]
