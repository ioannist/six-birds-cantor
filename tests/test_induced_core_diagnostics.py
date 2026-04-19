from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


def test_induced_core_report_is_consistent() -> None:
    subprocess.run([sys.executable, "scripts/run_induced_core_diagnostics.py"], check=True)

    report_path = Path("results/induced_core_diagnostics/report.json")
    assert report_path.exists()
    payload = json.loads(report_path.read_text(encoding="utf-8"))

    assert payload["decision"] in {"advance_to_induced_pressure", "abandon_domain_gated_family_as_frontier_target"}
    families = {entry["family_id"]: entry for entry in payload["families"]}
    required = {
        "contextual_local.domain_gated_two_map_local_ifs",
        "toy.local_ifs.nested_three_map_local_ifs",
        "contextual_local.prefix_memory_no_22_base3",
        "classical.middle_thirds",
    }
    assert required.issubset(families)

    required_fields = {
        "core_definition",
        "depths_checked",
        "return_length_cap",
        "root_proxy_used",
        "original_qm_defect_summary",
        "induced_qm_defect_summary",
        "original_bridge_defect_summary",
        "induced_bridge_defect_summary",
        "induced_truncation_defect_summary",
        "return_time_summary",
        "induced_alphabet_growth_summary",
        "induced_status",
        "classification_note",
        "artifact_paths",
    }
    for family_id in required:
        entry = families[family_id]
        assert required_fields.issubset(entry)
        assert entry["induced_status"] in {"promising", "inconclusive", "blocked"}
        assert entry["classification_note"]

    assert families["contextual_local.domain_gated_two_map_local_ifs"]["induced_status"] in {"promising", "inconclusive", "blocked"}
    assert families["classical.middle_thirds"]["induced_status"] != "blocked" or families["contextual_local.prefix_memory_no_22_base3"]["induced_status"] != "blocked"
