import json
from pathlib import Path


def test_claim_consistency_report_exists_and_loads() -> None:
    path = Path("results/paper_claim_consistency/report.json")
    assert path.exists()
    data = json.loads(path.read_text())

    assert data["decision"] in {
        "consistent",
        "consistent_with_minor_manual_checks",
        "inconsistent",
    }


def test_only_four_core_theoremlets_are_used_as_closed_theoremlets() -> None:
    data = json.loads(Path("results/paper_claim_consistency/report.json").read_text())
    found = data["closed_theoremlets_found"]

    assert set(found) == {
        "continuous_full_loop_lawfulness_theoremlet",
        "cocycle_pressure_closure_theoremlet",
        "strict_theory_extension_theoremlet",
        "conditional_pressure_disintegration_theoremlet",
    }
    assert all(found.values())
    assert not data["extra_theorem_labels"]


def test_forbidden_claims_do_not_appear_as_positive_claims_and_support_only_stays_support_only() -> None:
    data = json.loads(Path("results/paper_claim_consistency/report.json").read_text())

    assert not data["forbidden_claim_hit_list"]
    support_hits = data["support_only_reference_only_hit_list"]
    assert any(item["status"] == "support-only" for item in support_hits)
