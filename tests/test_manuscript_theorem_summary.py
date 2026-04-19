from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


def _load(path: str) -> dict:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def test_theorem_summary_and_manifest_exist() -> None:
    summary_path = REPO_ROOT / "docs/internal/manuscript_theorem_summary_v1.md"
    assert summary_path.exists()
    summary_text = summary_path.read_text(encoding="utf-8")
    for label in [
        "Continuous Full-Loop Lawfulness",
        "Cocycle Pressure Closure",
        "Strict Theory Extension",
        "Conditional Pressure Disintegration",
    ]:
        assert label in summary_text

    manifest = _load("docs/internal/figure_manifest_v1.json")
    assert manifest["paper_core_positioning"] == "level3_core_on_audited_shell"
    assert len(manifest["figures"]) + len(manifest["tables"]) >= 5


def test_figure_bindings_respect_claim_ledger() -> None:
    manifest = _load("docs/internal/figure_manifest_v1.json")
    ledger = _load("docs/internal/final_paper_core_claim_ledger_v1.json")

    claims = {item["claim_id"]: item for item in ledger["claims"]}
    for entry in manifest["figures"] + manifest["tables"]:
        assert "allowed_claim_ids" in entry
        for claim_id in entry["allowed_claim_ids"]:
            assert claim_id in claims
            assert claims[claim_id]["claim_status"] != "nonclaim"

    nonclaims = {item["claim_id"] for item in ledger["claims"] if item["claim_status"] == "nonclaim"}
    for binding in manifest["allowed_claim_bindings"]:
        assert binding["claim_id"] not in nonclaims
