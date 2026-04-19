#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import math
import statistics
from dataclasses import asdict
from pathlib import Path
from typing import Any


PRIMITIVES = ("P1", "P2", "P3", "P4", "P5", "P6")


def _load_kernel_module(repo_root: Path):
    import sys

    src_path = repo_root / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    from contextual_cantor.continuous_kernel_substrate import PRIMITIVES as MODULE_PRIMITIVES
    from contextual_cantor.continuous_kernel_substrate import simulate_substrate

    assert tuple(MODULE_PRIMITIVES) == PRIMITIVES
    return simulate_substrate


def _metrics_from_state(state: Any) -> dict[str, Any]:
    variation_history = list(state.kernel_variation_history)
    budget_history = list(state.budget_history)
    tau_history = list(state.tau_history)
    lens_history = list(state.lens_history)
    packaging_history = list(state.packaging_history)
    unique_lenses = len(set(lens_history))
    unique_packagings = len(set(packaging_history))
    mean_variation = statistics.fmean(variation_history) if variation_history else 0.0
    stdev_variation = statistics.pstdev(variation_history) if len(variation_history) > 1 else 0.0
    tail = variation_history[-100:] if len(variation_history) >= 100 else variation_history
    head = variation_history[:100] if len(variation_history) >= 100 else variation_history
    trend_ratio = (statistics.fmean(tail) + 1e-12) / (statistics.fmean(head) + 1e-12) if head else 1.0
    stabilization = "stabilize"
    if mean_variation > 0.09 or unique_lenses > 4 or unique_packagings > 4:
        stabilization = "keep_exploring"
    elif mean_variation > 0.03 or trend_ratio > 0.8:
        stabilization = "metastabilize"
    return {
        "mean_variation": mean_variation,
        "stdev_variation": stdev_variation,
        "min_variation": min(variation_history) if variation_history else 0.0,
        "max_variation": max(variation_history) if variation_history else 0.0,
        "variation_trend_ratio": trend_ratio,
        "lens_switch_count": state.lens_switch_count,
        "packaging_switch_count": state.packaging_switch_count,
        "tau_switch_count": state.tau_switch_count,
        "tau_min": min(tau_history) if tau_history else state.tau,
        "tau_max": max(tau_history) if tau_history else state.tau,
        "budget_min": min(budget_history) if budget_history else state.budget,
        "budget_max": max(budget_history) if budget_history else state.budget,
        "budget_mean": statistics.fmean(budget_history) if budget_history else state.budget,
        "unique_lenses": unique_lenses,
        "unique_packagings": unique_packagings,
        "cache_hits": state.cache_hits,
        "cache_misses": state.cache_misses,
        "cache_invalidation_counts": dict(state.invalidation_counts),
        "stabilization_regime": stabilization,
        "finite_state_like": bool(mean_variation < 0.01 and unique_lenses <= 2 and unique_packagings <= 2),
        "primitive_activity": dict(state.primitive_activity),
    }


def _trajectory_rows(trajectory: list[dict[str, Any]], state: Any) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in trajectory:
        rows.append(
            {
                "step": item["step"],
                "variation": item["variation"],
                "tau": item["p3"]["tau"],
                "budget": item["p6"]["budget"],
                "income": item["p6"]["income"],
                "lens": item["lens"]["name"],
                "packaging": item["packaging"]["name"],
                "phase": item["p3"]["phase"],
                "protocol_state": item["p3"]["protocol_state"],
                "action_weight_P1": item["action_weights"]["P1"],
                "action_weight_P2": item["action_weights"]["P2"],
                "action_weight_P3": item["action_weights"]["P3"],
                "action_weight_P4": item["action_weights"]["P4"],
                "action_weight_P5": item["action_weights"]["P5"],
                "action_weight_P6": item["action_weights"]["P6"],
            }
        )
    return rows


def _summarize_knockout(full_metrics: dict[str, Any], knock_metrics: dict[str, Any], removed: str) -> dict[str, Any]:
    material = False
    reasons: list[str] = []
    if full_metrics["stabilization_regime"] != knock_metrics["stabilization_regime"]:
        material = True
        reasons.append("stabilization regime changed")
    if full_metrics["lens_switch_count"] > 0 and knock_metrics["lens_switch_count"] <= max(1, int(0.5 * full_metrics["lens_switch_count"])):
        material = True
        reasons.append("lens switching collapsed")
    if full_metrics["packaging_switch_count"] > 0 and knock_metrics["packaging_switch_count"] <= max(1, int(0.5 * full_metrics["packaging_switch_count"])):
        material = True
        reasons.append("packaging switching collapsed")
    if full_metrics["tau_switch_count"] > 0 and knock_metrics["tau_switch_count"] <= max(1, int(0.5 * full_metrics["tau_switch_count"])):
        material = True
        reasons.append("tau switching collapsed")
    if full_metrics["mean_variation"] > 0 and knock_metrics["mean_variation"] <= 0.7 * full_metrics["mean_variation"]:
        material = True
        reasons.append("variation damped")
    if full_metrics["budget_max"] - full_metrics["budget_min"] > 0 and (knock_metrics["budget_max"] - knock_metrics["budget_min"]) <= 0.7 * (full_metrics["budget_max"] - full_metrics["budget_min"]):
        material = True
        reasons.append("budget range collapsed")
    return {
        "removed": removed,
        "stable_family_emerged": bool(knock_metrics["mean_variation"] < 0.06 and knock_metrics["unique_lenses"] <= 3 and knock_metrics["unique_packagings"] <= 3),
        "closure_idempotence_defect_proxy": knock_metrics["mean_variation"],
        "induced_structure_type": "continuous_richer" if knock_metrics["mean_variation"] > 0.02 else "finite_state_like",
        "theorem_amenable": bool(knock_metrics["mean_variation"] < 0.12 and knock_metrics["unique_packagings"] >= 1),
        "material_degradation": material,
        "material_reasons": reasons,
        "summary": {
            "lens_switch_count": knock_metrics["lens_switch_count"],
            "packaging_switch_count": knock_metrics["packaging_switch_count"],
            "tau_switch_count": knock_metrics["tau_switch_count"],
            "budget_min": knock_metrics["budget_min"],
            "budget_max": knock_metrics["budget_max"],
            "stabilization_regime": knock_metrics["stabilization_regime"],
        },
    }


def _decision(full_metrics: dict[str, Any], knockout_summaries: list[dict[str, Any]]) -> str:
    all_causal = all(summary["material_degradation"] for summary in knockout_summaries)
    if all_causal and not full_metrics["finite_state_like"] and full_metrics["lens_switch_count"] > 0 and full_metrics["packaging_switch_count"] > 0 and full_metrics["tau_switch_count"] > 0:
        return "continuous_full_loop_working"
    if full_metrics["finite_state_like"]:
        return "continuous_reset_blocked"
    return "continuous_substrate_but_partial_loop"


def run() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    simulate_substrate = _load_kernel_module(repo_root)

    out_dir = repo_root / "results" / "continuous_kernel_pilot"
    out_dir.mkdir(parents=True, exist_ok=True)

    full = simulate_substrate(steps=1000, n=16, seed=17)
    full_state = full["state"]
    full_metrics = _metrics_from_state(full_state)
    trajectory = full["trajectory"]

    knockout_results: list[dict[str, Any]] = []
    for removed in PRIMITIVES:
        primitive_activity = {p: True for p in PRIMITIVES}
        primitive_activity[removed] = False
        run_out = simulate_substrate(steps=1000, n=16, seed=17, primitive_activity=primitive_activity)
        run_metrics = _metrics_from_state(run_out["state"])
        knockout_results.append(_summarize_knockout(full_metrics, run_metrics, removed))

    decision = _decision(full_metrics, knockout_results)
    report = {
        "schema_version": "v1",
        "substrate_id": "continuous_kernel_substrate_v1",
        "generated_at_utc": "2026-03-18T00:00:00Z",
        "steps": len(trajectory),
        "kernel_dimension": len(full_state.kernel),
        "decision": decision,
        "pilot_decision": decision,
        "continuous_state_variation_summary": {
            "mean_variation": full_metrics["mean_variation"],
            "stdev_variation": full_metrics["stdev_variation"],
            "min_variation": full_metrics["min_variation"],
            "max_variation": full_metrics["max_variation"],
            "variation_trend_ratio": full_metrics["variation_trend_ratio"],
            "stabilization_regime": full_metrics["stabilization_regime"],
            "finite_state_like": full_metrics["finite_state_like"],
        },
        "lens_summary": {
            "switch_count": full_metrics["lens_switch_count"],
            "unique_lenses": full_metrics["unique_lenses"],
        },
        "packaging_summary": {
            "switch_count": full_metrics["packaging_switch_count"],
            "unique_packagings": full_metrics["unique_packagings"],
        },
        "timescale_summary": {
            "switch_count": full_metrics["tau_switch_count"],
            "tau_min": full_metrics["tau_min"],
            "tau_max": full_metrics["tau_max"],
        },
        "budget_summary": {
            "budget_min": full_metrics["budget_min"],
            "budget_max": full_metrics["budget_max"],
            "budget_mean": full_metrics["budget_mean"],
        },
        "primitive_activity_summary": full_metrics["primitive_activity"],
        "cache_summary": {
            "hits": full_metrics["cache_hits"],
            "misses": full_metrics["cache_misses"],
            "invalidation_counts": full_metrics["cache_invalidation_counts"],
        },
        "knockout_results": knockout_results,
    }

    report_path = out_dir / "report.json"
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    trajectory_path = out_dir / "trajectory.csv"
    with trajectory_path.open("w", encoding="utf-8", newline="") as f:
        rows = _trajectory_rows(trajectory, full_state)
        if rows:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

    knockout_path = out_dir / "knockout_report.json"
    knockout_path.write_text(
        json.dumps({"decision": decision, "knockout_results": knockout_results}, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    csv_report_path = out_dir / "report.csv"
    with csv_report_path.open("w", encoding="utf-8", newline="") as f:
        fieldnames = [
            "decision",
            "steps",
            "kernel_dimension",
            "mean_variation",
            "lens_switch_count",
            "packaging_switch_count",
            "tau_switch_count",
            "budget_min",
            "budget_max",
            "stabilization_regime",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(
            {
                "decision": decision,
                "steps": len(trajectory),
                "kernel_dimension": len(full_state.kernel),
                "mean_variation": full_metrics["mean_variation"],
                "lens_switch_count": full_metrics["lens_switch_count"],
                "packaging_switch_count": full_metrics["packaging_switch_count"],
                "tau_switch_count": full_metrics["tau_switch_count"],
                "budget_min": full_metrics["budget_min"],
                "budget_max": full_metrics["budget_max"],
                "stabilization_regime": full_metrics["stabilization_regime"],
            }
        )

    print(f"wrote {report_path.relative_to(repo_root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())

