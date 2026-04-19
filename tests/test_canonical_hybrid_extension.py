from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


def _load(path: str) -> dict:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def test_canonical_object_and_dependency_load() -> None:
    canonical = _load("docs/internal/canonical_hybrid_theorem_object_v1.json")
    dependency = _load("docs/internal/proof_dependency_canonical_hybrid_extension_v1.json")

    assert canonical["decision"] in {
        "canonical_object_and_intrinsic_extension_closed",
        "canonical_object_extracted_but_extension_not_intrinsic",
        "canonical_object_not_yet_stable",
    }
    assert canonical["next_consequence_target"] in {
        "hybrid_pressure_root_consequence",
        "package_strata_measure_consequence",
        "regularity_or_stability_consequence",
    }
    assert "factorization_verdict" in canonical

    required = {
        "CH-LEM-1",
        "CH-LEM-2",
        "CH-LEM-3",
        "CH-LEM-4",
        "CH-LEM-5",
        "CH-COR-6",
        "CH-THM-7",
    }
    assert required <= {item["lemma_id"] for item in dependency["lemmas"]}


def test_support_report_and_witnesses() -> None:
    report = _load("results/canonical_hybrid_extension/report.json")
    dependency = _load("docs/internal/proof_dependency_canonical_hybrid_extension_v1.json")

    assert set(report["configs"]) == {
        "generated.continuous_full_loop_kernel",
        "generated.continuous_full_loop_kernel_shell",
    }
    assert dependency["witness_families"] == [
        "generated.continuous_full_loop_kernel",
        "generated.continuous_full_loop_kernel_shell",
    ]
    assert "factorization_verdict" in report
