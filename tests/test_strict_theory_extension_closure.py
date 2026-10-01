from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


def _load(path: str) -> dict:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def test_closure_dependency_json_is_consistent() -> None:
    closure = _load("docs/internal/proof_dependency_strict_theory_extension_closure_v1.json")
    dependency = _load("docs/internal/proof_dependency_strict_theory_extension_v1.json")
    assumptions = _load("docs/internal/continuous_theorem_assumptions_v1.json")

    assumption_ids = {item["assumption_id"] for item in assumptions["assumption_catalog"]}
    allowed_statuses = {"closed_in_note", "standard_external", "localized_gap"}

    assert closure["selected_extension_route"] == "forcing_lemma_nondefinability_route"
    assert closure["witness_families"] == [
        "generated.continuous_full_loop_kernel",
        "generated.continuous_full_loop_kernel_shell",
    ]

    required_lemmas = {
        "SE-LEM-1",
        "SE-LEM-2",
        "SE-LEM-3",
        "SE-LEM-4",
        "SE-COR-5",
        "SE-THM-6",
    }
    assert required_lemmas <= {item["lemma_id"] for item in closure["lemmas"]}

    for assumption_id in closure["assumptions_used"]:
        assert assumption_id in assumption_ids

    for lemma in closure["lemmas"]:
        assert lemma["status"] in allowed_statuses
        for assumption_id in lemma["assumptions_used"]:
            assert assumption_id in assumption_ids

    lemma_status = {item["lemma_id"]: item["status"] for item in dependency["lemmas"]}
    assert lemma_status["ST-LEM-5"] in {"closed_in_note", "standard_external"}
    assert lemma_status["ST-THM-7"] == "closed_in_note"


def test_closure_support_report_exists_and_loads() -> None:
    report = _load("results/strict_theory_extension_closure/report.json")

    assert report["decision"] == "diagnostic_only_not_certified"
    assert report["mathematical_certification"]["main_theorem_certified"] is False
    assert report["definability_verdict"] == "exact_factorization_not_decided"
    assert report["selected_extension_route"] == "forcing_lemma_nondefinability_route"
    assert set(report["configs"]) == {
        "generated.continuous_full_loop_kernel",
        "generated.continuous_full_loop_kernel_shell",
    }
    assert "definability_verdict" in report
    assert "p4_from_p5_forcing_verdict" in report
    assert "macro_admissibility_verdict" in report
