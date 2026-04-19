from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = REPO_ROOT / "results" / "external_witness_import" / "report.json"
SHORTLIST_PATH = REPO_ROOT / "docs" / "internal" / "external_witness_shortlist_v1.json"
NOTE_PATH = REPO_ROOT / "docs" / "internal" / "external_witness_import_v1.md"
CONFIG_DIR = REPO_ROOT / "configs" / "experiments" / "external"

ALLOWED_DECISIONS = {
    "external_witness_imported",
    "external_candidates_only_partially_usable",
    "no_viable_external_witness_selected",
}


def test_external_witness_import_artifacts_exist_and_load() -> None:
    assert NOTE_PATH.exists()
    assert REPORT_PATH.exists()
    assert SHORTLIST_PATH.exists()

    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    shortlist = json.loads(SHORTLIST_PATH.read_text(encoding="utf-8"))

    assert report["decision"] in ALLOWED_DECISIONS
    assert shortlist["decision"] in ALLOWED_DECISIONS

    assert len(report["source_families_examined"]) >= 4
    assert len(report["candidate_families"]) >= 1

    if report["decision"] == "external_witness_imported":
        assert report["top_candidates"]

    if shortlist["decision"] == "external_witness_imported":
        assert shortlist["top_candidates"]


def test_external_import_configs_exist() -> None:
    expected = {
        CONFIG_DIR / "external-countable-gdms-countable-alphabet.json",
        CONFIG_DIR / "external-pseudo-markov-countable-alphabet.json",
        CONFIG_DIR / "external-local-ifs-non-sft-bridge.json",
    }
    assert all(path.exists() for path in expected)

