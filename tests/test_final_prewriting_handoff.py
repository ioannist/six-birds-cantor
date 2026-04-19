import json
from pathlib import Path


HANDOFF_NOTE = Path("docs/internal/final_prewriting_handoff_v1.md")
HANDOFF_JSON = Path("docs/internal/final_prewriting_handoff_v1.json")
CHECKLIST_JSON = Path("docs/internal/final_submission_checklist_v1.json")


def load_json(path: Path):
    return json.loads(path.read_text())


def test_handoff_files_exist_and_core_theoremlets_present():
    assert HANDOFF_NOTE.exists()
    assert HANDOFF_JSON.exists()
    assert CHECKLIST_JSON.exists()

    handoff = load_json(HANDOFF_JSON)
    checklist = load_json(CHECKLIST_JSON)

    assert handoff["paper_core_positioning"] == "level3_core_on_audited_shell"
    assert handoff["decision"] in {
        "handoff_ready_for_writing",
        "handoff_ready_with_minor_manual_checks",
        "handoff_not_safe",
    }
    assert handoff["canonical_theorem_object"]["canonical_object"] == "T1_hybrid_cocycle_plus_completion_theory"

    theoremlet_ids = {item["theoremlet_id"] for item in handoff["closed_theoremlets"]}
    required = {
        "continuous_full_loop_lawfulness_theoremlet",
        "cocycle_pressure_closure_theoremlet",
        "strict_theory_extension_theoremlet",
        "conditional_pressure_disintegration_theoremlet",
    }
    assert theoremlet_ids == required
    assert all(item["status"] == "closed_in_note" for item in handoff["closed_theoremlets"])

    categories = {item["category"] for item in checklist["items"]}
    assert {
        "theorem_object",
        "theoremlet",
        "assumption_scope",
        "claim_scope",
        "figure_binding",
        "risk_posture",
        "writing_guardrail",
    }.issubset(categories)


def test_handoff_claim_sets_and_nonclaims_are_explicit():
    handoff = load_json(HANDOFF_JSON)

    required_nonclaims = {
        "no_broader-class_theorem_beyond_the_audited_shell",
        "no_external/non-SFT_breadth_claim_beyond_what_is_actually_closed",
        "no_direct_stratumwise_root-separation_theorem",
        "no_packaging-induced_broader_theorem_class_claim",
        "no_shell-general_theorem_beyond_the_audited_shell-stable_class",
    }
    assert required_nonclaims.issubset(set(handoff["nonclaim_ids"]))
    assert handoff["reserve_ids"]
    assert "closure_deficit_proxy_support" in handoff["support_only_ids"]
