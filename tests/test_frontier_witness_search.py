from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = REPO_ROOT / "results" / "frontier_witness_search" / "report.json"
SHORTLIST_PATH = REPO_ROOT / "docs" / "internal" / "frontier_witness_shortlist_v1.json"
NOTE_PATH = REPO_ROOT / "docs" / "internal" / "frontier_witness_search_v1.md"
ALLOWED_DECISIONS = {
    "promising_frontier_witness_found",
    "only_finite_state_renewal_candidates_found",
    "current_design_space_blocked",
}
ALLOWED_STATUSES = {"promising", "inconclusive", "blocked"}


def test_frontier_witness_artifacts_exist_and_load() -> None:
    assert NOTE_PATH.exists()
    assert REPORT_PATH.exists()
    assert SHORTLIST_PATH.exists()

    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    shortlist = json.loads(SHORTLIST_PATH.read_text(encoding="utf-8"))

    assert report["decision"] in ALLOWED_DECISIONS
    assert shortlist["decision"] in ALLOWED_DECISIONS


def test_frontier_witness_report_has_enough_candidates_and_templates() -> None:
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    candidates = report["candidate_families"]
    assert len(candidates) >= 8
    assert len({entry["template_type"] for entry in candidates}) >= 3

    for entry in candidates:
        assert "family_id" in entry
        assert "template_type" in entry
        assert "parameter_summary" in entry
        assert "original_diagnostics" in entry
        assert "induced_diagnostics" in entry
        assert "induced_core_type" in entry
        assert "return_time_regime" in entry
        assert "effective_alphabet_regime" in entry
        assert entry["frontier_status"] in ALLOWED_STATUSES
        assert isinstance(entry["classification_note"], str) and entry["classification_note"].strip()
        assert isinstance(entry["artifact_paths"], list)


def test_frontier_witness_shortlist_has_top_candidate_or_blocker() -> None:
    shortlist = json.loads(SHORTLIST_PATH.read_text(encoding="utf-8"))
    if shortlist["decision"] == "current_design_space_blocked":
        assert isinstance(shortlist["next_branch"], str) and shortlist["next_branch"].strip()
    else:
        top_candidates = shortlist["top_candidates"]
        assert top_candidates
        for entry in top_candidates:
            assert entry["frontier_status"] in ALLOWED_STATUSES
            assert isinstance(entry["why_selected"], str) and entry["why_selected"].strip()
