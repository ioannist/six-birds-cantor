from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = REPO_ROOT / "results" / "lawful_substrate_diagnostics" / "report.json"
TARGET_PATH = REPO_ROOT / "docs" / "internal" / "primitive_generated_theorem_targets_v1.json"
NOTE_PATH = REPO_ROOT / "docs" / "internal" / "lawful_substrate_diagnostics_v1.md"
CONFIG_PROTOCOL = REPO_ROOT / "configs" / "experiments" / "generated" / "pg_protocol_lens.json"
CONFIG_REWRITE = REPO_ROOT / "configs" / "experiments" / "generated" / "pg_rewrite_bundle.json"

ALLOWED_DECISIONS = {
    "working_target_extracted",
    "generated_substrates_interesting_but_not_theorem_ready",
    "generated_substrates_need_richer_bundle_search",
}
ALLOWED_CLOSURE_DECISIONS = {
    "working_target_extracted",
    "generated_substrates_interesting_but_not_theorem_ready",
    "generated_substrates_need_richer_bundle_search",
}


def test_lawful_substrate_artifacts_exist() -> None:
    assert NOTE_PATH.exists()
    assert TARGET_PATH.exists()
    assert REPORT_PATH.exists()
    assert CONFIG_PROTOCOL.exists()
    assert CONFIG_REWRITE.exists()


def test_lawful_substrate_target_selection() -> None:
    payload = json.loads(TARGET_PATH.read_text(encoding="utf-8"))
    assert payload["decision"] in ALLOWED_CLOSURE_DECISIONS
    classes = payload["candidate_theorem_targets"]
    assert sum(1 for entry in classes if entry["selection_status"] == "working") == 1
    assert sum(1 for entry in classes if entry["selection_status"] == "stretch") == 1
    assert {entry["family_id"] for entry in payload["frozen_generated_families"]} == {
        "generated.pg_protocol_lens",
        "generated.pg_rewrite_bundle",
    }
    assert payload["working_target"] == "primitive_generated_rewrite_protocol_class"
    assert payload["stretch_target"] == "primitive_generated_delayed_return_class"


def test_lawful_substrate_report_loads() -> None:
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    assert report["decision"] in ALLOWED_DECISIONS
    frozen = {entry["family_id"]: entry for entry in report.get("frozen_generated_families", [])}
    assert "generated.pg_protocol_lens" in frozen
    assert "generated.pg_rewrite_bundle" in frozen
    assert frozen["generated.pg_protocol_lens"]["closure_status"] == "stable"
    assert frozen["generated.pg_rewrite_bundle"]["primitive_dependence_status"] == "genuinely_multi_primitive"
    assert len(report.get("candidate_theorem_targets", [])) == 3
