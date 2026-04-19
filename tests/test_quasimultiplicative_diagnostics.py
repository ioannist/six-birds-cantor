from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


def test_quasimultiplicative_report_is_consistent() -> None:
    subprocess.run([sys.executable, "scripts/run_quasimultiplicative_diagnostics.py"], check=True)

    report_path = Path("results/quasimultiplicative_diagnostics/report.json")
    assert report_path.exists()
    payload = json.loads(report_path.read_text(encoding="utf-8"))

    assert payload["decision"] in {"advance_to_bridge_lemmas", "stop_qm_branch"}
    families = {entry["family_id"]: entry for entry in payload["families"]}
    required = {
        "classical.middle_thirds",
        "classical.restricted_digits_base5_024",
        "contextual_local.prefix_memory_no_22_base3",
        "contextual_local.prefix_memory_last_digit_rule",
        "contextual_local.domain_gated_two_map_local_ifs",
        "toy.local_ifs.nested_three_map_local_ifs",
    }
    assert required.issubset(families)

    required_fields = {
        "config_path",
        "depths_checked",
        "root_proxies_used",
        "qm_defect_summary",
        "bridge_defect_summary",
        "domain_truncation_summary",
        "depth_stability_summary",
        "qm_status",
        "classification_note",
        "artifact_paths",
    }
    for family_id in required:
        entry = families[family_id]
        assert required_fields.issubset(entry)
        assert entry["qm_status"] in {"promising", "inconclusive", "blocked"}
        assert entry["classification_note"]

    assert families["contextual_local.domain_gated_two_map_local_ifs"]["qm_status"] in {"promising", "inconclusive", "blocked"}
    assert families["classical.middle_thirds"]["qm_status"] == "promising" or families["contextual_local.prefix_memory_no_22_base3"]["qm_status"] == "promising"
