from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_PATH = REPO_ROOT / "docs" / "internal" / "delayed_return_theorem_package_v1.json"
AUDIT_PATH = REPO_ROOT / "docs" / "internal" / "non_sft_witness_evidence_v2.json"
REPORT_PATH = REPO_ROOT / "results" / "non_sft_witness_v2" / "report.json"


def test_delayed_return_package_freeze_and_audit_load() -> None:
    assert PACKAGE_PATH.exists()
    assert AUDIT_PATH.exists()
    assert REPORT_PATH.exists()

    package = json.loads(PACKAGE_PATH.read_text(encoding="utf-8"))
    audit = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))

    assert package["closed_class_id"] == "bounded_return_full_core_delayed_gate_subclass"
    assert package["proof_status"] == "closed_in_note"
    assert audit["target_class_id"] == package["closed_class_id"]
    assert audit["decision"] in {
        "non_sft_witness_found",
        "finite_state_renewal_like_only",
        "impact_blocker_remains",
    }
    assert report["target_class_id"] == package["closed_class_id"]
    assert report["decision"] == audit["decision"]

    required_candidates = {
        "frontier.fw_delayed_return_gate_a3",
        "frontier.fw_delayed_return_gate_a1",
        "frontier.fw_delayed_return_gate_a2",
        "contextual_local.prefix_memory_last_digit_rule",
        "contextual_local.prefix_memory_no_22_base3",
        "contextual_local.domain_gated_two_map_local_ifs",
    }
    assert required_candidates <= set(audit["candidate_families"])

    if audit["decision"] == "non_sft_witness_found":
        assert audit["selected_family"] is not None
        assert audit["in_class_status"] == "yes"
        assert audit["non_sft_status"] == "yes"
    else:
        assert audit["selected_family"] in required_candidates
        assert audit["finite_state_renewal_like_status"] in {"yes", "unknown"}
        assert audit["notes"]

