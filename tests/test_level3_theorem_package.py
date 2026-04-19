from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


def _load(path: str) -> dict:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def test_package_and_ledger_load() -> None:
    package = _load("docs/internal/level3_theorem_package_v1.json")
    ledger = _load("docs/internal/final_paper_core_claim_ledger_v1.json")

    assert package["paper_core_positioning"] in {
        "level3_core_on_audited_shell",
        "level2_with_level3_signal_only",
        "freeze_as_level2_only",
    }
    required = {
        "continuous_full_loop_lawfulness_theoremlet",
        "cocycle_pressure_closure_theoremlet",
        "strict_theory_extension_theoremlet",
        "conditional_pressure_disintegration_theoremlet",
    }
    assert required <= {item["theoremlet_id"] for item in package["included_theoremlets"]}

    nonclaims = set(package["nonclaims"])
    assert {
        "no broader-class theorem beyond the audited shell",
        "no external/non-SFT breadth claim beyond what is actually closed",
        "no direct stratumwise root-separation theorem",
        "no packaging-induced broader theorem class claim",
        "no shell-general theorem beyond the audited shell-stable class",
    } <= nonclaims

    assert package["reserve_routes"]
    assert ledger["claim_counts"]["closed_theoremlet"] >= 4


def test_report_and_core_status() -> None:
    package = _load("docs/internal/level3_theorem_package_v1.json")
    report = _load("results/level3_theorem_package/report.json")

    assert report["final_positioning_decision"] == package["paper_core_positioning"]
    theoremlets = {item["theoremlet_id"]: item for item in package["included_theoremlets"]}
    for key in [
        "continuous_full_loop_lawfulness_theoremlet",
        "cocycle_pressure_closure_theoremlet",
        "strict_theory_extension_theoremlet",
        "conditional_pressure_disintegration_theoremlet",
    ]:
        assert theoremlets[key]["status"] == "closed_in_note"
