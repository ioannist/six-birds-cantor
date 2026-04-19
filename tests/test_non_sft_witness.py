from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


def test_non_sft_witness_evidence_is_consistent() -> None:
    subprocess.run([sys.executable, "scripts/run_non_sft_witness_diagnostics.py"], check=True)

    evidence_path = Path("docs/internal/non_sft_witness_evidence_v1.json")
    assert evidence_path.exists()
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))

    assert evidence["decision"] in {"non_sft_witness_found", "impact_blocker_confirmed"}
    required_candidates = {
        "contextual_local.domain_gated_two_map_local_ifs",
        "toy.local_ifs.nested_three_map_local_ifs",
        "contextual_local.prefix_memory_no_22_base3",
        "contextual_local.prefix_memory_last_digit_rule",
    }
    assert required_candidates.issubset(set(evidence["candidate_families"]))

    if evidence["decision"] == "non_sft_witness_found":
        assert evidence["selected_family"] is not None
        assert evidence["in_class_status"] == "yes"
        assert evidence["non_sft_status"] == "yes"
    else:
        assert evidence["notes"]
        assert any("blocker" in note.lower() for note in evidence["notes"])
