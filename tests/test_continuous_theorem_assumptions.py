from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ASSUMPTIONS_PATH = REPO_ROOT / "docs" / "internal" / "continuous_theorem_assumptions_v1.json"
NOTE_PATH = REPO_ROOT / "docs" / "internal" / "continuous_theorem_assumptions_v1.md"
REPORT_PATH = REPO_ROOT / "results" / "continuous_theorem_assumptions" / "report.json"
WORKING_CONFIG = REPO_ROOT / "configs" / "experiments" / "generated" / "continuous_full_loop_kernel.json"
SHELL_CONFIG = REPO_ROOT / "configs" / "experiments" / "generated" / "continuous_full_loop_kernel_shell.json"

ALLOWED_DECISIONS = {
    "working_theorem_class_supported",
    "only_working_class_supported_not_stretch",
    "assumption_pack_too_weak",
}


def test_continuous_theorem_assumption_artifacts_exist() -> None:
    assert ASSUMPTIONS_PATH.exists()
    assert NOTE_PATH.exists()
    assert REPORT_PATH.exists()
    assert WORKING_CONFIG.exists()
    assert SHELL_CONFIG.exists()


def test_continuous_theorem_assumption_structure() -> None:
    assumptions = json.loads(ASSUMPTIONS_PATH.read_text(encoding="utf-8"))
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))

    assert assumptions["working_class_id"] == "continuous_full_loop_lawful_kernel_class"
    assert assumptions["stretch_class_id"] == "continuous_full_loop_lawful_kernel_class_with_wider_parameter_shell"
    assert report["decision"] in ALLOWED_DECISIONS
    assert sum(1 for entry in assumptions["class_profiles"] if entry["selection_status"] == "working") == 1
    assert sum(1 for entry in assumptions["class_profiles"] if entry["selection_status"] == "stretch") == 1
    assert assumptions["class_profiles"][0]["class_id"]
    assert assumptions["class_profiles"][1]["class_id"]
    assert assumptions["family_assumption_tags"]
    assert report["working_class_supported"] is True
    assert report["full_six_primitive_closure"] == "yes"
    assert report["empirical_support"]["all_primitives_necessary"] is True
    for family in ("generated.continuous_full_loop_kernel", "generated.continuous_full_loop_kernel_shell"):
        assert any(entry["family_id"] == family for entry in assumptions["family_assumption_tags"])
