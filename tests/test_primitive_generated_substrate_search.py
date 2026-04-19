from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
NOTE_PATH = REPO_ROOT / "docs" / "internal" / "primitive_generated_cantor_matrix_v1.md"
MATRIX_PATH = REPO_ROOT / "docs" / "internal" / "primitive_generated_cantor_matrix_v1.json"
REPORT_PATH = REPO_ROOT / "results" / "primitive_generated_substrate_search" / "report.json"

ALLOWED_DECISIONS = {
    "primitive_generation_working",
    "primitive_generation_too_weak",
    "primitive_generation_needs_richer_bundle_space",
}


def test_primitive_generated_matrix_and_report_load() -> None:
    assert NOTE_PATH.exists()
    assert MATRIX_PATH.exists()
    assert REPORT_PATH.exists()

    matrix = json.loads(MATRIX_PATH.read_text(encoding="utf-8"))
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))

    bundles = matrix.get("candidate_bundles", [])
    assert len(bundles) >= 6

    coverage_by_bundle = {
        entry["bundle_id"]: set(entry.get("primitive_coverage", []))
        for entry in bundles
    }
    assert any({"P1", "P3", "P6"}.issubset(coverage) for coverage in coverage_by_bundle.values())
    assert any("P1" in coverage for coverage in coverage_by_bundle.values())
    assert any("P3" in coverage for coverage in coverage_by_bundle.values())
    assert any("P6" in coverage for coverage in coverage_by_bundle.values())

    assert report["decision"] in ALLOWED_DECISIONS
    assert len(report.get("candidate_bundles", [])) >= 6
    assert len(report.get("generated_substrates", [])) >= 1


def test_primitive_generated_report_has_promising_bundle() -> None:
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    statuses = {entry["bundle_id"]: entry["status"] for entry in report.get("generated_substrates", [])}
    assert any(status == "promising" for status in statuses.values())
    assert report.get("top_bundles")
