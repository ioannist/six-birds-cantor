from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = REPO_ROOT / "results" / "full_six_primitive_closure" / "report.json"
NOTE_PATH = REPO_ROOT / "docs" / "internal" / "full_six_primitive_closure_v1.md"
JSON_PATH = REPO_ROOT / "docs" / "internal" / "full_six_primitive_closure_v1.json"
TARGET_PATH = REPO_ROOT / "docs" / "internal" / "primitive_generated_theorem_targets_v1.json"
REWRITE_CONFIG = REPO_ROOT / "configs" / "experiments" / "generated" / "pg_rewrite_bundle.json"
FULL_LOOP_CONFIG = REPO_ROOT / "configs" / "experiments" / "generated" / "pg_full_loop_bundle.json"

ALLOWED_DECISIONS = {
    "full_six_primitive_target_found",
    "p5_not_yet_causally_closed",
    "no_full_six_primitive_target_yet",
    "p5_causally_closed",
}


def test_full_six_closure_artifacts_exist() -> None:
    assert NOTE_PATH.exists()
    assert JSON_PATH.exists()
    assert REPORT_PATH.exists()
    assert TARGET_PATH.exists()
    assert REWRITE_CONFIG.exists()


def test_full_six_closure_audit_structure() -> None:
    payload = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    assert payload["working_target_decision"] in ALLOWED_DECISIONS
    candidates = payload["candidate_substrates"]
    assert candidates
    by_family = {entry["family_id"]: entry for entry in candidates}
    assert "generated.pg_protocol_lens" in by_family
    assert "generated.pg_rewrite_bundle" in by_family
    if FULL_LOOP_CONFIG.exists():
        assert "generated.pg_full_loop_bundle" in by_family
    assert by_family["generated.pg_protocol_lens"]["theorem_target_status"] == "control_only"
    rewrite = by_family["generated.pg_rewrite_bundle"]
    assert rewrite["theorem_target_status"] == "working_candidate"
    assert sorted(rewrite["active_primitives"]) == ["P1", "P2", "P3", "P4", "P5", "P6"]
    assert rewrite["full_loop_status"] == "true_full_loop"
    assert rewrite["packaging_selection_status"] == "active"
    assert rewrite["p1_from_p5_status"] == "active"
    assert rewrite["p2_from_p5_status"] == "active"
    if payload["working_target_decision"] in {"full_six_primitive_target_found", "p5_causally_closed"}:
        assert any(
            sorted(entry["active_primitives"]) == ["P1", "P2", "P3", "P4", "P5", "P6"]
            for entry in candidates
        )
        assert next(
            row for row in next(item for item in payload["knockout_results"] if item["family_id"] == "generated.pg_rewrite_bundle")["knockouts"]
            if row["removed"] == "P5"
        )["lawful_loop_changes_materially"] is True
    else:
        assert by_family["generated.pg_protocol_lens"]["theorem_target_status"] != "working_candidate"
    for entry in payload["knockout_results"]:
        assert len(entry["knockouts"]) == 6


def test_full_six_target_file_is_demoted() -> None:
    target = json.loads(TARGET_PATH.read_text(encoding="utf-8"))
    assert target["working_target"] == "primitive_generated_rewrite_protocol_class"
    assert target["decision"] == "working_target_extracted"
    classes = {entry["class_id"]: entry for entry in target["candidate_theorem_targets"]}
    assert classes["primitive_generated_structural_class"]["selection_status"] == "reserve"
    assert classes["primitive_generated_rewrite_protocol_class"]["selection_status"] == "working"
    assert classes["primitive_generated_delayed_return_class"]["selection_status"] == "stretch"
