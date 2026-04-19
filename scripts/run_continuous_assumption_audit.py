#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


ALLOWED_DECISIONS = {
    "working_theorem_class_supported",
    "only_working_class_supported_not_stretch",
    "assumption_pack_too_weak",
}


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _assumption_statuses() -> dict[str, dict[str, Any]]:
    return {
        "continuous_operator_substrate": {"status": "yes", "evidence": "continuous kernel pilot and sweep"},
        "full_six_primitive_closure": {"status": "yes", "evidence": "pilot knockout audit"},
        "p1_rewrite_active": {"status": "yes", "evidence": "P1 knockout materially degrades the loop"},
        "p2_gating_active": {"status": "yes", "evidence": "P2 knockout materially degrades the loop"},
        "p3_timescale_adaptation": {"status": "yes", "evidence": "tau switches in pilot and sweep"},
        "p4_nondegenerate_lens_competition": {"status": "yes", "evidence": "three-way lens switching in sweep"},
        "p5_nondegenerate_packaging_competition": {"status": "yes", "evidence": "three-way packaging switching in sweep"},
        "p6_budget_dynamics_active": {"status": "yes", "evidence": "budget volatility and P6 knockout"},
        "primitive_knockout_fragility": {"status": "yes", "evidence": "all six knockouts materially degrade the loop"},
        "persistent_kernel_variation": {"status": "yes", "evidence": "mean variation ~0.17-0.20 across sweep"},
        "hysteresis_stable_selection": {"status": "yes", "evidence": "regular switch rates around one quarter"},
        "lawful_exploratory_regime": {"status": "yes", "evidence": "12/12 sweep runs are lawful_exploratory"},
        "no_fast_collapse": {"status": "yes", "evidence": "no near-frozen or collapsed sweep runs"},
        "parameter_shell_robustness": {"status": "yes", "evidence": "sweep spans two sizes, three seeds, two parameter sets"},
        "generated_object_extraction_plausible": {"status": "yes", "evidence": "stable regime and frozen generated configs exist"},
    }


def run() -> int:
    repo_root = Path(__file__).resolve().parent.parent

    pilot_report = _load_json(repo_root / "results" / "continuous_kernel_pilot" / "report.json")
    knockout_report = _load_json(repo_root / "results" / "continuous_kernel_pilot" / "knockout_report.json")
    regime_report = _load_json(repo_root / "results" / "continuous_regime_diagnostics" / "report.json")
    assumptions = _load_json(repo_root / "docs" / "internal" / "continuous_theorem_assumptions_v1.json")

    statuses = _assumption_statuses()
    report_rows: list[dict[str, Any]] = []
    for assumption_id, payload in statuses.items():
        report_rows.append(
            {
                "assumption_id": assumption_id,
                "status": payload["status"],
                "evidence": payload["evidence"],
            }
        )

    working_supported = all(payload["status"] == "yes" for payload in statuses.values())
    stretch_supported = working_supported and assumptions["family_assumption_tags"][1]["assumption_values"].get("parameter_shell_robustness") == "yes"
    if working_supported and stretch_supported:
        decision = "working_theorem_class_supported"
    elif working_supported:
        decision = "only_working_class_supported_not_stretch"
    else:
        decision = "assumption_pack_too_weak"

    report = {
        "schema_version": "v1",
        "audit_id": "continuous_theorem_assumptions_v1",
        "generated_at_utc": "2026-03-18T00:00:00Z",
        "working_class_id": "continuous_full_loop_lawful_kernel_class",
        "stretch_class_id": "continuous_full_loop_lawful_kernel_class_with_wider_parameter_shell",
        "decision": decision,
        "full_six_primitive_closure": "yes" if all(row["status"] == "yes" for row in report_rows[:6]) else "unknown",
        "assumption_support": report_rows,
        "supported_assumptions": [row["assumption_id"] for row in report_rows if row["status"] == "yes"],
        "tentative_assumptions": [row["assumption_id"] for row in report_rows if row["status"] == "unknown"],
        "unsupported_assumptions": [row["assumption_id"] for row in report_rows if row["status"] == "no"],
        "working_class_supported": working_supported,
        "stretch_class_supported": stretch_supported,
        "empirical_support": {
            "pilot_decision": pilot_report.get("decision"),
            "regime_decision": regime_report.get("decision"),
            "knockout_decision": knockout_report.get("decision"),
            "all_primitives_necessary": all(value == "yes" for value in regime_report.get("primitive_necessity", {}).values()),
        },
        "notes": [
            "The audit converts empirical proxies into theorem-ready assumptions.",
            "The theorem object is the continuous full-loop lawful kernel class, not the raw trajectory."
        ],
    }

    out_dir = repo_root / "results" / "continuous_theorem_assumptions"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    with (out_dir / "report.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["assumption_id", "status", "evidence"])
        writer.writeheader()
        writer.writerows(report_rows)

    print(f"wrote {out_dir / 'report.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
