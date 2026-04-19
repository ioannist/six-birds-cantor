from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


def _load(path: str) -> dict:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def test_consequence_note_and_dependency_load() -> None:
    note_path = REPO_ROOT / "docs/internal/hybrid_pressure_root_consequence_v1.md"
    assert note_path.exists()

    dependency = _load("docs/internal/proof_dependency_hybrid_pressure_root_v1.json")
    assert dependency["selected_working_route"] in {
        "stratumwise_pressure_existence_route",
        "root_separation_within_T0_route",
        "conditional_pressure_disintegration_route",
    }
    stretch = dependency.get("selected_stretch_route")
    if stretch is not None:
        assert stretch in {
            "stratumwise_pressure_existence_route",
            "root_separation_within_T0_route",
            "conditional_pressure_disintegration_route",
        }
        assert dependency["selected_working_route"] != stretch
    if dependency["selected_working_route"] == "conditional_pressure_disintegration_route":
        rejected = {item["route_id"] for item in dependency.get("rejected_routes", [])}
        assert {
            "stratumwise_pressure_existence_route",
            "root_separation_within_T0_route",
        } <= rejected

    required = {
        "HR-LEM-1",
        "HR-LEM-2",
        "HR-LEM-3",
        "HR-LEM-4",
        "HR-LEM-5",
        "HR-COR-6",
        "HR-THM-7",
    }
    assert required <= {item["lemma_id"] for item in dependency["lemmas"]}


def test_assumptions_report_and_witnesses() -> None:
    assumptions = _load("docs/internal/continuous_theorem_assumptions_v1.json")
    dependency = _load("docs/internal/proof_dependency_hybrid_pressure_root_v1.json")
    report = _load("results/hybrid_pressure_root/report.json")

    assumption_ids = {
        item["assumption_id"] for item in assumptions["assumption_catalog"]
    }
    referenced = set(dependency["assumptions_used"])
    for lemma in dependency["lemmas"]:
        referenced.update(lemma["assumptions_used"])
        assert lemma["status"] in {"closed_in_note", "standard_external", "localized_gap"}
    assert referenced <= assumption_ids

    assert report["decision"] in {
        "consequence_route_plausible",
        "consequence_route_signal_but_not_sharp",
        "consequence_route_not_ready",
    }
    assert report["selected_working_route"] == dependency["selected_working_route"]
    assert report.get("selected_stretch_route") == dependency.get("selected_stretch_route")
    assert set(report["configs"]) == {
        "generated.continuous_full_loop_kernel",
        "generated.continuous_full_loop_kernel_shell",
    }
    assert dependency["witness_families"] == [
        "generated.continuous_full_loop_kernel",
        "generated.continuous_full_loop_kernel_shell",
    ]
