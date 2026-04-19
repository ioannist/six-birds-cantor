from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


def _load(path: str) -> dict:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def test_distinction_note_and_dependency_load() -> None:
    note_path = REPO_ROOT / "docs/internal/stratumwise_thermodynamic_distinction_v1.md"
    assert note_path.exists()

    dependency = _load("docs/internal/proof_dependency_stratumwise_distinction_v1.json")
    routes = {
        "root_window_separation_route",
        "profile_gap_route",
        "weighted_conditional_distinction_route",
    }
    assert dependency["selected_working_route"] in routes
    assert dependency["selected_reserve_route"] in routes
    assert dependency["selected_working_route"] != dependency["selected_reserve_route"]

    required = {
        "SD-LEM-1",
        "SD-LEM-2",
        "SD-LEM-3",
        "SD-LEM-4",
        "SD-LEM-5",
        "SD-COR-6",
        "SD-THM-7",
    }
    assert required <= {item["lemma_id"] for item in dependency["lemmas"]}


def test_report_witnesses_and_assumptions() -> None:
    assumptions = _load("docs/internal/continuous_theorem_assumptions_v1.json")
    dependency = _load("docs/internal/proof_dependency_stratumwise_distinction_v1.json")
    report = _load("results/stratumwise_distinction/report.json")

    assumption_ids = {
        item["assumption_id"] for item in assumptions["assumption_catalog"]
    }
    referenced = set(dependency["assumptions_used"])
    for lemma in dependency["lemmas"]:
        referenced.update(lemma["assumptions_used"])
        assert lemma["status"] in {"closed_in_note", "standard_external", "localized_gap"}
    assert referenced <= assumption_ids

    assert report["decision"] in {
        "stratumwise_distinction_sharpened",
        "stratumwise_distinction_signal_but_still_ambiguous",
        "stratumwise_route_not_viable",
    }
    assert report["selected_working_route"] == dependency["selected_working_route"]
    assert report["selected_reserve_route"] == dependency["selected_reserve_route"]
    assert set(report["configs"]) == {
        "generated.continuous_full_loop_kernel",
        "generated.continuous_full_loop_kernel_shell",
    }
    assert dependency["witness_families"] == [
        "generated.continuous_full_loop_kernel",
        "generated.continuous_full_loop_kernel_shell",
    ]
