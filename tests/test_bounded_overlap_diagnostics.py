from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


def test_bounded_overlap_report_is_consistent() -> None:
    subprocess.run([sys.executable, "scripts/run_bounded_overlap_diagnostics.py"], check=True)

    report_path = Path("results/bounded_overlap_diagnostics/report.json")
    assert report_path.exists()
    payload = json.loads(report_path.read_text(encoding="utf-8"))

    assert payload["decision"] in {"advance_to_overlap_lemmas", "stop_bounded_overlap_branch"}
    families = {entry["family_id"]: entry for entry in payload["families"]}
    required = {
        "contextual_local.prefix_memory_last_digit_rule",
        "contextual_local.prefix_memory_no_22_base3",
        "contextual_local.domain_gated_two_map_local_ifs",
        "toy.local_ifs.nested_three_map_local_ifs",
    }
    assert required.issubset(families)

    required_fields = {
        "config_path",
        "depths_checked",
        "root_proxy_used",
        "max_overlap_multiplicity_by_depth",
        "max_overlap_multiplicity_overall",
        "ratio_proxy_by_depth",
        "memory_growth_proxy",
        "depth_sensitivity",
        "bounded_overlap_status",
        "classification_note",
        "artifact_paths",
    }
    for family_id in required:
        entry = families[family_id]
        assert required_fields.issubset(entry)
        assert entry["bounded_overlap_status"] in {"promising", "inconclusive", "blocked"}
        assert entry["classification_note"]
