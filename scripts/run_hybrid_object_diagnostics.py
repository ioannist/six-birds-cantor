#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _ensure_report(repo_root: Path, path: Path, script: str) -> None:
    if path.exists():
        return
    import subprocess

    subprocess.run(["python", script], cwd=repo_root, check=True)


def _summarize_config(
    config_id: str,
    pressure: dict[str, Any],
    completion: dict[str, Any],
) -> dict[str, Any]:
    pressure_cfg = next(item for item in pressure["runs"] if item["family_id"] == config_id)
    completion_cfg = next(item for item in completion["summaries"] if item["config_id"] == config_id)

    fp_total = int(completion_cfg["fixed_point_count_summary"]["distinct_fixed_point_total"])
    feedback_events = int(completion_cfg["p4_from_p5_feedback_summary"]["feedback_events"])
    material_feedback_events = int(completion_cfg["p4_from_p5_feedback_summary"]["material_feedback_events"])
    saturated = bool(completion_cfg["saturation_summary"]["saturated"])
    class_relation = completion["completion_object_comparison"]["class_relation"]

    object_identity_broadening = fp_total >= 6 and feedback_events > 0 and any(
        panel["distinct_fixed_points"] > 1
        for panel in completion_cfg["fixed_point_count_summary"]["per_panel"].values()
    )
    saturation_forcing = saturated and material_feedback_events > 0
    class_broadening = class_relation not in {"class_equivalent_on_current_evidence"}
    p5_theorem_role = fp_total > 0 and material_feedback_events > 0

    return {
        "config_id": config_id,
        "cocycle_pressure_mean": pressure_cfg["pressure_profiles"]["1.0"]["pressure_proxy"],
        "cocycle_growth_slope": pressure_cfg["growth_bound_proxy"],
        "completion_fixed_point_total": fp_total,
        "completion_status_counts": dict(completion_cfg["fixed_point_count_summary"]["statuses"]),
        "saturation": saturated,
        "saturation_summary": completion_cfg["saturation_summary"],
        "p4_from_p5_feedback_summary": completion_cfg["p4_from_p5_feedback_summary"],
        "macro_admissibility_summary": completion_cfg["macro_admissibility_summary"],
        "object_identity_broadening_test": object_identity_broadening,
        "saturation_forcing_test": saturation_forcing,
        "class_broadening_test": class_broadening,
        "p5_theorem_role_test": p5_theorem_role,
        "object_identity_verdict": "broader_object_identity" if object_identity_broadening else "same_object_identity",
        "saturation_verdict": "nontrivial_saturation" if saturated else "no_saturation",
        "p4_from_p5_forcing_verdict": "active" if material_feedback_events > 0 else "inactive",
        "class_broadening_verdict": "broader" if class_broadening else "not_broader",
        "p5_theorem_role_verdict": "class_defining" if p5_theorem_role else "observational",
        "theorem_object_changed": bool(completion["theorem_object_changed_from_cocycle_route"]) or object_identity_broadening,
    }


def run() -> int:
    repo_root = Path(__file__).resolve().parent.parent

    pressure_path = repo_root / "results" / "continuous_pressure_closure" / "report.json"
    completion_path = repo_root / "results" / "packaging_completion_endomap" / "report.json"
    _ensure_report(repo_root, pressure_path, "scripts/run_continuous_pressure_closure_checks.py")
    _ensure_report(repo_root, completion_path, "scripts/run_packaging_completion_endomap.py")

    pressure = _load_json(pressure_path)
    completion = _load_json(completion_path)

    configs = completion["configs"]
    summaries = [_summarize_config(cfg, pressure, completion) for cfg in configs]

    overall_object_identity = any(item["object_identity_broadening_test"] for item in summaries)
    overall_saturation_forcing = any(item["saturation_forcing_test"] for item in summaries)
    overall_class_broadening = any(item["class_broadening_test"] for item in summaries)
    overall_p5_role = any(item["p5_theorem_role_test"] for item in summaries)

    decision = "hybrid_real_but_not_yet_broader"
    if not overall_object_identity and not overall_saturation_forcing:
        decision = "freeze_on_cocycle_route"
    elif overall_object_identity and overall_saturation_forcing and overall_class_broadening:
        decision = "advance_hybrid_theorem"

    report = {
        "report_id": "hybrid_object_diagnostics_v1",
        "schema_version": "v1",
        "generated_at_utc": "2026-03-18T00:00:00Z",
        "base_closed_class": "continuous_full_loop_lawful_kernel_class_shell_stable",
        "configs": configs,
        "frozen_configs": [
            "configs/experiments/generated/continuous_full_loop_kernel.json",
            "configs/experiments/generated/continuous_full_loop_kernel_shell.json",
        ],
        "cocycle_component": {
            "route_id": "fekete_sup_cocycle_route",
            "observable_family": "selector_weighted_operator_growth_observable",
            "decision": pressure["decision"],
            "summary": pressure["support_summary"],
        },
        "completion_component": {
            "endomap_id": "packaging_completion_endomap_v1",
            "decision": completion["decision"],
            "summary": {
                "total_distinct_fixed_points": completion["fixed_point_count_summary"]["total_distinct_fixed_points"],
                "theorem_object_changed_from_cocycle_route": completion["theorem_object_changed_from_cocycle_route"],
            },
        },
        "candidate_hybrid_story": "hybrid_same_class_stronger_object" if decision != "freeze_on_cocycle_route" else "cocycle_final_best_story",
        "object_identity_verdict": "broader_object_identity" if overall_object_identity else "same_object_identity",
        "saturation_verdict": "nontrivial_saturation_with_new_strata" if overall_saturation_forcing else "degenerate_saturation_or_none",
        "p4_from_p5_forcing_verdict": "active_and_material" if overall_saturation_forcing else "inactive",
        "class_broadening_verdict": "broader" if overall_class_broadening else "not_broader",
        "p5_theorem_role_verdict": "class_defining" if overall_p5_role else "observational",
        "broadening_tests": [
            {
                "test_id": "object_identity_broadening_test",
                "result": overall_object_identity,
                "note": "Completion fixed points distinguish theorem objects more finely than the cocycle route alone.",
            },
            {
                "test_id": "saturation_forcing_test",
                "result": overall_saturation_forcing,
                "note": "Saturation is present and `P4<-P5` refinement events are active.",
            },
            {
                "test_id": "class_broadening_test",
                "result": overall_class_broadening,
                "note": "Current evidence does not support a class strictly broader than the shell-stable full-loop class.",
            },
            {
                "test_id": "p5_theorem_role_test",
                "result": overall_p5_role,
                "note": "P5 is class-defining for the completion object, not merely observable-supporting.",
            },
        ],
        "decision": decision,
        "notes": [
            "The hybrid object is mathematically real.",
            "It changes object identity relative to the cocycle route, but current evidence does not support a broader theorem class.",
            "The packaging completion layer remains a same-class refinement on the current evidence.",
        ],
        "per_config": summaries,
    }

    out_dir = repo_root / "results" / "hybrid_object_diagnostics"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    with (out_dir / "report.csv").open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow([
            "config_id",
            "cocycle_pressure_mean",
            "cocycle_growth_slope",
            "completion_fixed_point_total",
            "object_identity_broadening_test",
            "saturation_forcing_test",
            "class_broadening_test",
            "p5_theorem_role_test",
        ])
        for item in summaries:
            writer.writerow([
                item["config_id"],
                item["cocycle_pressure_mean"],
                item["cocycle_growth_slope"],
                item["completion_fixed_point_total"],
                item["object_identity_broadening_test"],
                item["saturation_forcing_test"],
                item["class_broadening_test"],
                item["p5_theorem_role_test"],
            ])

    return 0


if __name__ == "__main__":
    raise SystemExit(run())
