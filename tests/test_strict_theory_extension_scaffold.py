from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


def _load(path: str) -> dict:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def test_dependency_json_loads_and_route_is_allowed() -> None:
    dependency = _load("docs/internal/proof_dependency_strict_theory_extension_v1.json")

    assert dependency["selected_extension_route"] in {
        "forcing_lemma_nondefinability_route",
        "fixed_point_stratification_route",
        "macro_admissibility_obstruction_route",
    }


def test_assumptions_and_lemma_blocks_are_consistent() -> None:
    dependency = _load("docs/internal/proof_dependency_strict_theory_extension_v1.json")
    assumptions = _load("docs/internal/continuous_theorem_assumptions_v1.json")
    allowed_statuses = {"closed_in_note", "standard_external", "localized_gap"}
    assumption_ids = {item["assumption_id"] for item in assumptions["assumption_catalog"]}
    lemma_ids = {item["lemma_id"] for item in dependency["lemmas"]}

    assert dependency["witness_families"] == [
        "generated.continuous_full_loop_kernel",
        "generated.continuous_full_loop_kernel_shell",
    ]

    for assumption_id in dependency["assumptions_used"]:
        assert assumption_id in assumption_ids

    required_lemmas = {
        "ST-LEM-1",
        "ST-LEM-2",
        "ST-LEM-3",
        "ST-LEM-4",
        "ST-LEM-5",
        "ST-COR-6",
        "ST-THM-7",
    }
    assert required_lemmas <= lemma_ids

    for lemma in dependency["lemmas"]:
        assert lemma["status"] in allowed_statuses
        for assumption_id in lemma["assumptions_used"]:
            assert assumption_id in assumption_ids
