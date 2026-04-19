from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


def test_post_overlap_impact_report_is_consistent() -> None:
    subprocess.run([sys.executable, "scripts/run_theorem_diagnostics.py"], check=True)

    report_path = Path("results/theorem_diagnostics/classification_report_v2.json")
    assert report_path.exists()
    report = json.loads(report_path.read_text(encoding="utf-8"))

    assert report["based_on_bowen_class"] == "docs/internal/bowen_class_v2.json"
    assert report["impact_decision"] in {"stronger_sft_like_theorem", "bridge_toward_frontier"}
    assert report["summary"]["non_sft_blocker_status"] in {"remains", "partially_relaxed", "resolved"}

    families = {entry["family_id"]: entry for entry in report["families"]}
    assert "contextual_local.prefix_memory_last_digit_rule" in families
    assert families["contextual_local.prefix_memory_last_digit_rule"]["bowen_v2_status"] == "included"
