from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


def _load(path: str) -> dict:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def test_strict_theory_extension_artifacts_exist_and_load() -> None:
    target = _load("docs/internal/hybrid_cocycle_completion_object_v2.json")
    report = _load("results/strict_theory_extension/report.json")

    assert target["decision"] in {
        "strict_extension_certified",
        "strict_extension_signal_but_not_certified",
        "no_strict_extension_beyond_cocycle",
    }
    assert report["decision"] in {
        "strict_extension_certified",
        "strict_extension_signal_but_not_certified",
        "no_strict_extension_beyond_cocycle",
    }
    assert target["decision"] == report["decision"]


def test_strict_theory_extension_report_shape() -> None:
    report = _load("results/strict_theory_extension/report.json")

    assert set(report["configs"]) == {
        "generated.continuous_full_loop_kernel",
        "generated.continuous_full_loop_kernel_shell",
    }
    assert set(report["frozen_configs"]) == {
        "configs/experiments/generated/continuous_full_loop_kernel.json",
        "configs/experiments/generated/continuous_full_loop_kernel_shell.json",
    }
    for field in (
        "definability_verdict",
        "macro_admissibility_verdict",
        "saturation_verdict",
        "p4_from_p5_forcing_verdict",
    ):
        assert field in report

    assert report["definability_test"]["reconstructible_from_T0"] in {"yes", "no", "partial"}
    assert report["macro_admissibility_obstruction"]["inadmissible_count"] >= 0
