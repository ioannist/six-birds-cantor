from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
NOTE_PATH = REPO_ROOT / "docs" / "internal" / "p5_causal_closure_v1.md"
JSON_PATH = REPO_ROOT / "docs" / "internal" / "p5_causal_closure_v1.json"
REPORT_PATH = REPO_ROOT / "results" / "full_six_primitive_closure" / "report_v2.json"
FULL_LOOP_CONFIG = REPO_ROOT / "configs" / "experiments" / "generated" / "pg_full_loop_bundle.json"
REWRITE_CONFIG = REPO_ROOT / "configs" / "experiments" / "generated" / "pg_rewrite_bundle.json"

ALLOWED_DECISIONS = {
    "p5_causally_closed",
    "p5_still_not_causal",
    "full_loop_blocked_for_other_reason",
}


def test_p5_causal_closure_artifacts_exist() -> None:
    assert NOTE_PATH.exists()
    assert JSON_PATH.exists()
    assert REPORT_PATH.exists()
    assert REWRITE_CONFIG.exists()


def test_p5_causal_closure_structure() -> None:
    payload = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    assert payload["decision"] in ALLOWED_DECISIONS
    candidates = {entry["family_id"]: entry for entry in payload["candidate_substrates"]}
    assert "generated.pg_protocol_lens" in candidates
    assert "generated.pg_rewrite_bundle" in candidates
    assert candidates["generated.pg_rewrite_bundle"]["packaging_selection_status"] == "active"
    assert len(candidates["generated.pg_rewrite_bundle"]["active_packaging_sources"]) >= 2
    assert candidates["generated.pg_rewrite_bundle"]["p1_from_p5_status"] != "inactive"
    assert candidates["generated.pg_rewrite_bundle"]["p2_from_p5_status"] != "inactive"
    if payload["decision"] == "p5_causally_closed":
        assert candidates["generated.pg_rewrite_bundle"]["p5_knockout_effect"] == "material"
        assert candidates["generated.pg_rewrite_bundle"]["full_loop_status"] == "true_full_loop"


def test_p5_report_has_knockout_runs() -> None:
    payload = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    by_family = {entry["family_id"]: entry for entry in payload["knockout_results"]}
    rewrite = by_family["generated.pg_rewrite_bundle"]
    assert len(rewrite["knockouts"]) == 6
    p5_row = next(row for row in rewrite["knockouts"] if row["removed"] == "P5")
    assert p5_row["lawful_loop_changes_materially"] is True
    assert p5_row["stable_family_emerged"] is False
    assert payload["working_target_decision"] in ALLOWED_DECISIONS
