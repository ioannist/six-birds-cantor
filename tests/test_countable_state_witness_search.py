from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = REPO_ROOT / "results" / "countable_state_witness_search" / "report.json"
SHORTLIST_PATH = REPO_ROOT / "docs" / "internal" / "countable_state_redesign_shortlist_v1.json"
NOTE_PATH = REPO_ROOT / "docs" / "internal" / "countable_state_redesign_search_v1.md"


def test_countable_state_witness_search_report() -> None:
    if not REPORT_PATH.exists() or not SHORTLIST_PATH.exists() or not NOTE_PATH.exists():
        subprocess.run([sys.executable, "scripts/run_countable_state_witness_search.py"], check=True)

    assert REPORT_PATH.exists()
    assert SHORTLIST_PATH.exists()
    assert NOTE_PATH.exists()

    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    shortlist = json.loads(SHORTLIST_PATH.read_text(encoding="utf-8"))

    assert report["decision"] in {
        "promising_countable_state_candidate_found",
        "only_finite_state_like_candidates_found",
        "design_space_blocked",
    }
    assert shortlist["decision"] == report["decision"]

    candidates = report["candidate_families"]
    assert len(candidates) >= 10
    assert len({entry["template_type"] for entry in candidates}) >= 4

    for entry in candidates:
        assert "original_diagnostics" in entry
        assert "induced_diagnostics" in entry
        assert "compression_diagnostics" in entry
        assert "induced_core_type" in entry
        assert "frontier_status" in entry
        assert "classification_note" in entry
        assert "artifact_paths" in entry

    assert shortlist["top_candidates"] or "blocked" in shortlist["next_branch"].lower()

    if report["decision"] == "promising_countable_state_candidate_found":
        assert any(entry["induced_core_type"] == "countable_state_candidate" for entry in candidates)

