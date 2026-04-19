import json
from pathlib import Path


def test_final_manuscript_handoff_artifacts_exist() -> None:
    assert Path("docs/internal/final_manuscript_readiness_v1.md").exists()
    handoff_path = Path("docs/internal/final_manuscript_handoff_v1.json")
    assert handoff_path.exists()
    assert Path("paper/build/main.pdf").exists()

    data = json.loads(handoff_path.read_text())
    assert data["paper_core_positioning"] == "level3_core_on_audited_shell"
    assert data["final_readiness_decision"] in {
        "ready_for_manuscript_handoff",
        "ready_with_minor_typographic_warnings",
        "not_ready",
    }


def test_final_manuscript_handoff_contains_core_theoremlets_and_nonclaims() -> None:
    data = json.loads(Path("docs/internal/final_manuscript_handoff_v1.json").read_text())
    theoremlet_ids = {item["theoremlet_id"] for item in data["closed_theoremlets"]}
    assert theoremlet_ids == {
        "continuous_full_loop_lawfulness_theoremlet",
        "cocycle_pressure_closure_theoremlet",
        "strict_theory_extension_theoremlet",
        "conditional_pressure_disintegration_theoremlet",
    }

    assert set(data["nonclaim_ids"]) >= {
        "no_broader-class_theorem_beyond_the_audited_shell",
        "no_external/non-SFT_breadth_claim_beyond_what_is_actually_closed",
        "no_direct_stratumwise_root-separation_theorem",
        "no_packaging-induced_broader_theorem_class_claim",
        "no_shell-general_theorem_beyond_the_audited_shell-stable_class",
    }
