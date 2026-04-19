from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ASSUMPTIONS_PATH = REPO_ROOT / "docs" / "internal" / "delayed_return_theorem_assumptions_v1.json"
NOTE_PATH = REPO_ROOT / "docs" / "internal" / "delayed_return_theorem_assumptions_v1.md"
REPORT_PATH = REPO_ROOT / "results" / "delayed_return_diagnostics" / "report.json"


def test_delayed_return_assumption_pack_loads() -> None:
    assert NOTE_PATH.exists()
    assert ASSUMPTIONS_PATH.exists()
    payload = json.loads(ASSUMPTIONS_PATH.read_text(encoding="utf-8"))
    profiles = {entry["class_id"] for entry in payload["class_profiles"]}
    assert "bounded_return_delayed_gate_subclass" in profiles
    assert "countable_state_delayed_return_local_domain_class" in profiles

    tagged = {entry["family_id"] for entry in payload["family_assumption_tags"]}
    assert "frontier.fw_delayed_return_gate_a3" in tagged
    assert "frontier.fw_delayed_return_gate_a1" in tagged
    assert "frontier.fw_delayed_return_gate_a2" in tagged


def test_delayed_return_report_is_consistent() -> None:
    assert REPORT_PATH.exists()
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    assert report["decision"] in {
        "working_class_supported",
        "working_class_too_weak",
        "stretch_class_plausible",
    }
    families = report["families"]
    assert families
    assert any(entry["family_id"].startswith("frontier.fw_delayed_return_gate_") for entry in families)
    assert any(entry["status"] != "blocked" for entry in families if entry["family_id"].startswith("frontier.fw_delayed_return_gate_"))
