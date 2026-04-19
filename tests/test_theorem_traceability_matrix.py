from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


def _load(path: str) -> dict:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def test_traceability_matrix_loads_and_covers_core_theoremlets() -> None:
    matrix = _load("docs/internal/theorem_traceability_matrix_v1.json")
    theoremlets = {item["theoremlet_id"]: item for item in matrix["theoremlets"]}

    assert matrix["paper_core_positioning"] == "level3_core_on_audited_shell"
    required = {
        "continuous_full_loop_lawfulness_theoremlet",
        "cocycle_pressure_closure_theoremlet",
        "strict_theory_extension_theoremlet",
        "conditional_pressure_disintegration_theoremlet",
    }
    assert required <= theoremlets.keys()
    for theoremlet_id in required:
        entry = theoremlets[theoremlet_id]
        assert entry["status"] == "closed_in_note"
        assert entry["assumptions_used"]
        assert entry["dependency_paths"]
        assert entry["evidence_paths"]


def test_scope_firewall_and_claim_safety() -> None:
    matrix = _load("docs/internal/theorem_traceability_matrix_v1.json")
    ledger = _load("docs/internal/final_paper_core_claim_ledger_v1.json")

    firewall = matrix["scope_firewall"]
    assert {
        "core_closed_claims",
        "support_only_claims",
        "reserve_routes",
        "explicit_nonclaims",
    } <= firewall.keys()
    assert matrix["decision"] in {
        "traceability_complete",
        "traceability_complete_with_minor_gaps",
        "traceability_not_yet_safe",
    }

    nonclaims = {
        item["claim_id"] for item in ledger["claims"] if item["claim_status"] == "nonclaim"
    }
    for entry in matrix["theoremlets"]:
        assert not any(claim_id in nonclaims for claim_id in entry["allowed_claim_ids"])
