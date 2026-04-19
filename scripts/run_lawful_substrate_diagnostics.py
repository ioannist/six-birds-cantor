#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
GENERATED_DIR = REPO_ROOT / "configs" / "experiments" / "generated"
REPORT_DIR = REPO_ROOT / "results" / "lawful_substrate_diagnostics"
REPORT_PATH = REPORT_DIR / "report.json"
CSV_PATH = REPORT_DIR / "report.csv"
TARGET_JSON = REPO_ROOT / "docs" / "internal" / "primitive_generated_theorem_targets_v1.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def classify_family(config: dict) -> dict:
    params = config["parameters"]
    frozen = params["frozen_generation"]
    coverage = set(params.get("primitive_coverage", []))
    closure = float(frozen["closure_idempotence_defect"])
    multi = int(frozen["multi_primitive_interaction_score"])
    status = frozen.get("status", "inconclusive")
    induced = frozen.get("induced_core_type", "unknown")
    if closure <= 0.05:
        closure_status = "stable"
    elif closure <= 0.5:
        closure_status = "metastable"
    else:
        closure_status = "unstable"

    if "P1" in coverage and "P6" in coverage and multi >= 4:
        primitive = "genuinely_multi_primitive"
    elif coverage <= {"P3", "P4", "P5"}:
        primitive = "mostly_structural"
    else:
        primitive = "unclear"

    if status == "promising" and induced == "finite_state_renewal_like":
        theorem = "working_candidate" if closure_status == "stable" else "stretch_candidate"
    elif status == "blocked" or induced in {"finite_state", "trivial"}:
        theorem = "blocked"
    else:
        theorem = "stretch_candidate" if closure_status != "unstable" else "blocked"

    if theorem == "blocked":
        frontier = "blocked"
    elif primitive == "genuinely_multi_primitive" and "P1" in coverage and "P6" in coverage:
        frontier = "promising"
    else:
        frontier = "promising" if closure_status == "stable" else "inconclusive"

    return {
        "family_id": config["family_id"],
        "bundle_origin": params["bundle_origin"],
        "closure_status": closure_status,
        "primitive_dependence_status": primitive,
        "induced_structure_type": induced,
        "theorem_amenability_status": theorem,
        "frontier_status": frontier,
        "note": frozen.get("classification_note", ""),
        "closure_idempotence_defect": closure,
        "multi_primitive_interaction_score": multi,
        "constraint_only_share": frozen.get("constraint_only_share"),
        "status": status,
        "return_time_regime": frozen.get("return_time_regime", "unknown"),
        "effective_alphabet_regime": frozen.get("effective_alphabet_regime", "unknown"),
        "stable_rule_family": frozen.get("stable_rule_family", False),
    }


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    fieldnames = [
        "family_id",
        "bundle_origin",
        "closure_status",
        "primitive_dependence_status",
        "induced_structure_type",
        "theorem_amenability_status",
        "frontier_status",
        "closure_idempotence_defect",
        "multi_primitive_interaction_score",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key) for key in fieldnames})


def main() -> None:
    protocol = load_json(GENERATED_DIR / "pg_protocol_lens.json")
    rewrite = load_json(GENERATED_DIR / "pg_rewrite_bundle.json")
    rows = [classify_family(protocol), classify_family(rewrite)]
    decision = "working_target_extracted"
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report = {
        "schema_version": "1.0",
        "report_id": "lawful-substrate-diagnostics-v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "frozen_generated_families": rows,
        "lawfulness_metrics": {
            "stable_rule_family_count": sum(1 for row in rows if row["stable_rule_family"]),
            "promising_family_count": sum(1 for row in rows if row["frontier_status"] == "promising"),
            "multi_primitive_max": max(row["multi_primitive_interaction_score"] for row in rows),
            "closure_idempotence_min": min(row["closure_idempotence_defect"] for row in rows),
            "closure_idempotence_max": max(row["closure_idempotence_defect"] for row in rows),
            "frontier_signal": "rewrite_bundle is the stronger frontier signal; protocol_lens is the safer theorem anchor.",
        },
        "candidate_theorem_targets": load_json(TARGET_JSON)["candidate_theorem_targets"],
        "working_target": "primitive_generated_structural_class",
        "stretch_target": "primitive_generated_rewrite_protocol_class",
        "decision": decision,
        "notes": [
            "protocol_lens gives the clean working anchor.",
            "rewrite_bundle gives the stronger stretch signal.",
            "The delayed-return class is reserved for later comparison only.",
        ],
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_csv(CSV_PATH, rows)


if __name__ == "__main__":
    main()

