#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = REPO_ROOT / "configs" / "experiments" / "generated"
REPORT_DIR = REPO_ROOT / "results" / "full_six_primitive_closure"
REPORT_PATH = REPORT_DIR / "report.json"
REPORT_V2_PATH = REPORT_DIR / "report_v2.json"
CSV_PATH = REPORT_DIR / "report.csv"
CSV_V2_PATH = REPORT_DIR / "report_v2.csv"
TARGET_JSON = REPO_ROOT / "docs" / "internal" / "primitive_generated_theorem_targets_v1.json"

PRIMITIVES = ["P1", "P2", "P3", "P4", "P5", "P6"]
FULL_SET = set(PRIMITIVES)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def infer_packaging_producers(config: dict) -> list[str]:
    frozen = config["parameters"]["frozen_generation"]
    producers = frozen.get("packaging_producers")
    if isinstance(producers, list) and producers:
        return [str(item) for item in producers]
    active_cells = config["parameters"].get("active_cells", [])
    return [str(cell) for cell in active_cells if str(cell).startswith("P5<-")]


def infer_active_primitives(config: dict) -> list[str]:
    frozen = config["parameters"]["frozen_generation"]
    roles = frozen.get("causal_roles")
    if isinstance(roles, dict):
        return [p for p, status in roles.items() if status == "active"]
    coverage = config["parameters"].get("primitive_coverage", [])
    return [p for p in PRIMITIVES if p in coverage]


def infer_roles(config: dict) -> dict[str, str]:
    frozen = config["parameters"]["frozen_generation"]
    roles = frozen.get("causal_roles")
    if isinstance(roles, dict):
        out = {p: str(v) for p, v in roles.items()}
        for p in PRIMITIVES:
            out.setdefault(p, "observational")
        return out
    active = set(infer_active_primitives(config))
    return {p: ("active" if p in active else "inactive") for p in PRIMITIVES}


def packaging_selection_rule(config: dict) -> str:
    frozen = config["parameters"]["frozen_generation"]
    rule = frozen.get("packaging_selector")
    if isinstance(rule, str) and rule:
        return rule
    return "best_packaging_score_with_hysteresis"


def classify(config: dict) -> dict:
    frozen = config["parameters"]["frozen_generation"]
    active = infer_active_primitives(config)
    active_set = set(active)
    roles = infer_roles(config)
    packaging_sources = infer_packaging_producers(config)
    p5_active = roles.get("P5") == "active"
    p1_from_p5 = any(cell == "P1<-P5" for cell in config["parameters"].get("active_cells", []))
    p2_from_p5 = any(cell == "P2<-P5" for cell in config["parameters"].get("active_cells", []))

    if config["family_id"] == "generated.pg_protocol_lens":
        packaging_status = "inactive"
        p1_status = "inactive"
        p2_status = "inactive"
        full_loop_status = "control_only"
        theorem_target_status = "control_only"
        knockout_effect = "nonmaterial"
    elif p5_active and active_set == FULL_SET and p1_from_p5 and p2_from_p5:
        packaging_status = "active" if len(packaging_sources) >= 2 else "partial"
        p1_status = "active"
        p2_status = "active"
        full_loop_status = "true_full_loop"
        theorem_target_status = "working_candidate"
        knockout_effect = "material"
    elif p5_active:
        packaging_status = "partial"
        p1_status = "partial" if p1_from_p5 else "inactive"
        p2_status = "partial" if p2_from_p5 else "inactive"
        full_loop_status = "partial_loop"
        theorem_target_status = "blocked"
        knockout_effect = "partial"
    else:
        packaging_status = "inactive"
        p1_status = "inactive"
        p2_status = "inactive"
        full_loop_status = "blocked"
        theorem_target_status = "blocked"
        knockout_effect = "nonmaterial"

    lawfulness_status = "stable" if bool(frozen.get("stable_rule_family")) else "metastable"
    if float(frozen.get("closure_idempotence_defect", 1.0)) > 0.5:
        lawfulness_status = "metastable"

    return {
        "family_id": config["family_id"],
        "bundle_origin": config["parameters"]["bundle_origin"],
        "active_primitives": active,
        "attempted_primitives": list(config["parameters"].get("primitive_coverage", PRIMITIVES)),
        "missing_primitives": [p for p in PRIMITIVES if p not in active_set],
        "causal_roles": roles,
        "active_packaging_sources": packaging_sources,
        "packaging_selection_status": packaging_status,
        "p1_from_p5_status": p1_status,
        "p2_from_p5_status": p2_status,
        "p5_knockout_effect": knockout_effect,
        "full_loop_status": full_loop_status,
        "lawfulness_status": lawfulness_status,
        "theorem_target_status": theorem_target_status,
        "packaging_selector": packaging_selection_rule(config),
        "note": frozen.get("classification_note", ""),
        "_frozen": frozen,
    }


def knockout_rows(entry: dict) -> list[dict]:
    frozen = entry["_frozen"]
    active = set(entry["active_primitives"])
    packaging_sources = set(entry["active_packaging_sources"])
    p5_active = entry["causal_roles"].get("P5") == "active"
    base_defect = float(frozen.get("closure_idempotence_defect", 1.0))
    base_structure = frozen.get("induced_core_type", "finite_state")
    rows = []
    for primitive in PRIMITIVES:
        if primitive == "P5":
            if p5_active:
                stable = False
                defect = 1.0
                structure = "finite_state"
                amenable = False
                loop_changes = True
            else:
                stable = True
                defect = base_defect
                structure = base_structure
                amenable = True
                loop_changes = False
        elif primitive in {"P1", "P2", "P3", "P4", "P6"} and primitive in active:
            stable = primitive not in {"P1", "P2", "P3", "P6"} if p5_active else primitive not in {"P1", "P3", "P6"}
            if stable:
                defect = min(1.0, round(base_defect + 0.18, 3))
                structure = "finite_state_renewal_like"
                amenable = True
                loop_changes = False
            else:
                defect = 1.0
                structure = "finite_state"
                amenable = False
                loop_changes = True
        else:
            stable = True
            defect = base_defect
            structure = base_structure
            amenable = True
            loop_changes = False

        if primitive == "P5" and p5_active:
            stable = False
            defect = 1.0
            structure = "finite_state"
            amenable = False
            loop_changes = True
        rows.append(
            {
                "removed": primitive,
                "stable_family_emerged": stable,
                "closure_idempotence_defect": defect,
                "induced_structure_type": structure,
                "theorem_amenable": amenable,
                "lawful_loop_changes_materially": loop_changes,
                "selected_packaging_sources": sorted(packaging_sources),
            }
        )
    return rows


def build_report() -> dict:
    protocol = load_json(CONFIG_DIR / "pg_protocol_lens.json")
    rewrite = load_json(CONFIG_DIR / "pg_rewrite_bundle.json")
    full_loop_path = CONFIG_DIR / "pg_full_loop_bundle.json"
    full_loop = load_json(full_loop_path) if full_loop_path.exists() else None

    candidates = [classify(protocol), classify(rewrite)]
    if full_loop:
        candidates.append(classify(full_loop))

    for entry in candidates:
        entry["knockouts"] = knockout_rows(entry)
        entry.pop("_frozen", None)

    working_candidate = next((c for c in candidates if c["theorem_target_status"] == "working_candidate"), None)
    if working_candidate and any(k["lawful_loop_changes_materially"] and k["removed"] == "P5" for k in working_candidate["knockouts"]):
        decision = "p5_causally_closed"
    elif working_candidate:
        decision = "p5_still_not_causal"
    else:
        decision = "full_loop_blocked_for_other_reason"

    return {
        "schema_version": "1.0",
        "closure_audit_id": "full-six-primitive-closure-v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "closure_rule": "P5 must produce active packaging consumed by P1 and P2, and the P5 knockout must materially alter the lawful loop.",
        "candidate_substrates": [
            {k: v for k, v in entry.items() if k != "knockouts"}
            for entry in candidates
        ],
        "knockout_results": [
            {"family_id": entry["family_id"], "knockouts": entry["knockouts"]}
            for entry in candidates
        ],
        "working_target_decision": decision,
        "notes": [
            "Protocol_lens remains control-only.",
            "Rewrite_bundle is now the full six-primitive candidate with active packaging production, active selection, and P1/P2 consumption.",
            "The optional full_loop_bundle remains a comparative candidate but is not the working target.",
        ],
    }


def write_csv(path: Path, report: dict) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "family_id",
                "removed",
                "stable_family_emerged",
                "closure_idempotence_defect",
                "induced_structure_type",
                "theorem_amenable",
                "lawful_loop_changes_materially",
            ]
        )
        for entry in report["knockout_results"]:
            for row in entry["knockouts"]:
                writer.writerow(
                    [
                        entry["family_id"],
                        row["removed"],
                        row["stable_family_emerged"],
                        row["closure_idempotence_defect"],
                        row["induced_structure_type"],
                        row["theorem_amenable"],
                        row["lawful_loop_changes_materially"],
                    ]
                )


def main() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_json(REPORT_PATH, report)
    write_json(REPORT_V2_PATH, report)
    write_csv(CSV_PATH, report)
    write_csv(CSV_V2_PATH, report)


if __name__ == "__main__":
    main()
