from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


def _load(path: str) -> dict:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def test_consequence_note_and_dependency_load() -> None:
    note_path = REPO_ROOT / "docs/internal/conditional_pressure_disintegration_v1.md"
    assert note_path.exists()

    dependency = _load("docs/internal/proof_dependency_conditional_disintegration_v1.json")
    assert dependency["selected_consequence_object"]

    required = {
        "CDI-LEM-1",
        "CDI-LEM-2",
        "CDI-LEM-3",
        "CDI-LEM-4",
        "CDI-LEM-5",
        "CDI-COR-6",
        "CDI-THM-7",
    }
    assert required <= {item["lemma_id"] for item in dependency["lemmas"]}


def test_assumptions_report_and_witnesses() -> None:
    assumptions = _load("docs/internal/continuous_theorem_assumptions_v1.json")
    dependency = _load("docs/internal/proof_dependency_conditional_disintegration_v1.json")
    report = _load("results/conditional_disintegration/report.json")

    assumption_ids = {
        item["assumption_id"] for item in assumptions["assumption_catalog"]
    }
    referenced = set(dependency["assumptions_used"])
    for lemma in dependency["lemmas"]:
        referenced.update(lemma["assumptions_used"])
        assert lemma["status"] in {"closed_in_note", "standard_external", "localized_gap"}
    assert referenced <= assumption_ids

    assert dependency["witness_families"] == [
        "generated.continuous_full_loop_kernel",
        "generated.continuous_full_loop_kernel_shell",
    ]
    assert set(report["configs"]) == {
        "generated.continuous_full_loop_kernel",
        "generated.continuous_full_loop_kernel_shell",
    }
    assert report["decision"] == "diagnostic_only_not_certified"
    assert report["mathematical_certification"]["pressure_disintegration_certified"] is False
