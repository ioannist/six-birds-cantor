#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import statistics
import subprocess
from collections import Counter, defaultdict
from dataclasses import asdict
from pathlib import Path
from typing import Any


PRIMITIVES = ("P1", "P2", "P3", "P4", "P5", "P6")


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _ensure_pilot_artifacts(repo_root: Path) -> None:
    report = repo_root / "results" / "continuous_kernel_pilot" / "report.json"
    knockout = repo_root / "results" / "continuous_kernel_pilot" / "knockout_report.json"
    if report.exists() and knockout.exists():
        return
    subprocess.run(["python", "scripts/run_continuous_kernel_pilot.py"], cwd=repo_root, check=True)


def _regime_label(metrics: dict[str, Any]) -> str:
    mean_variation = metrics["mean_variation"]
    lens_switches = metrics["lens_switch_count"]
    packaging_switches = metrics["packaging_switch_count"]
    tau_switches = metrics["tau_switch_count"]
    finite_state_like = metrics["finite_state_like"]
    budget_volatility = metrics["budget_volatility"]
    if finite_state_like or (mean_variation < 0.01 and lens_switches <= 2 and packaging_switches <= 2):
        return "near_frozen"
    if budget_volatility < 0.03 and mean_variation < 0.03:
        return "collapsed"
    if mean_variation > 0.22 and (lens_switches == 0 or packaging_switches == 0):
        return "pathological"
    if mean_variation >= 0.06 and lens_switches >= 20 and packaging_switches >= 20 and tau_switches >= 2:
        return "lawful_exploratory"
    if mean_variation >= 0.02 and (lens_switches >= 5 or packaging_switches >= 5):
        return "lawful_metastable"
    return "collapsed"


def _dominant_primitive_counts(trajectory: list[dict[str, Any]]) -> dict[str, int]:
    counts = Counter()
    for step in trajectory:
        weights = step["action_weights"]
        dominant = max(PRIMITIVES, key=lambda p: weights[p])
        counts[dominant] += 1
    return {primitive: counts.get(primitive, 0) for primitive in PRIMITIVES}


def _mean_action_weights(trajectory: list[dict[str, Any]]) -> dict[str, float]:
    totals = defaultdict(float)
    for step in trajectory:
        weights = step["action_weights"]
        for primitive in PRIMITIVES:
            totals[primitive] += float(weights[primitive])
    steps = max(1, len(trajectory))
    return {primitive: totals[primitive] / steps for primitive in PRIMITIVES}


def _metrics_from_run(run: dict[str, Any], primitive_necessity: dict[str, str]) -> dict[str, Any]:
    state = run["state"]
    trajectory = run["trajectory"]
    variation_history = [float(item["variation"]) for item in trajectory]
    budget_history = [float(item["p6"]["budget"]) for item in trajectory]
    tau_history = [float(item["p3"]["tau"]) for item in trajectory]
    mean_variation = statistics.fmean(variation_history) if variation_history else 0.0
    stdev_variation = statistics.pstdev(variation_history) if len(variation_history) > 1 else 0.0
    budget_volatility = (max(budget_history) - min(budget_history)) if budget_history else 0.0
    lens_switch_count = int(state.lens_switch_count)
    packaging_switch_count = int(state.packaging_switch_count)
    tau_switch_count = int(state.tau_switch_count)
    finite_state_like = bool(mean_variation < 0.01 and lens_switch_count <= 2 and packaging_switch_count <= 2)
    stability = "stabilize"
    if mean_variation > 0.09 or lens_switch_count > 60 or packaging_switch_count > 60:
        stability = "keep_exploring"
    elif mean_variation > 0.03 or tau_switch_count > 1:
        stability = "metastabilize"
    active_primitive_summary = {
        "primitive_activity": dict(state.primitive_activity),
        "dominant_primitive_counts": _dominant_primitive_counts(trajectory),
        "mean_action_weights": _mean_action_weights(trajectory),
        "primitive_necessity": primitive_necessity,
    }
    return {
        "steps": len(trajectory),
        "kernel_dim": len(state.kernel),
        "seed": run["seed"],
        "lens_switch_count": lens_switch_count,
        "packaging_switch_count": packaging_switch_count,
        "tau_switch_count": tau_switch_count,
        "budget_min": min(budget_history) if budget_history else state.budget,
        "budget_max": max(budget_history) if budget_history else state.budget,
        "budget_volatility": budget_volatility,
        "state_variation_summary": {
            "mean_variation": mean_variation,
            "stdev_variation": stdev_variation,
            "min_variation": min(variation_history) if variation_history else 0.0,
            "max_variation": max(variation_history) if variation_history else 0.0,
            "trend_ratio": ((statistics.fmean(variation_history[-100:]) + 1e-12) / (statistics.fmean(variation_history[:100]) + 1e-12)) if len(variation_history) >= 100 else 1.0,
            "finite_state_like": finite_state_like,
        },
        "closure_defect_proxy": mean_variation,
        "active_primitive_summary": active_primitive_summary,
        "hysteresis_persistence": {
            "lens_switch_rate": lens_switch_count / max(1, len(trajectory)),
            "packaging_switch_rate": packaging_switch_count / max(1, len(trajectory)),
            "tau_switch_rate": tau_switch_count / max(1, len(trajectory)),
        },
        "persistent_nontrivial_variation": bool(mean_variation >= 0.03 and not finite_state_like),
        "switching_richness": bool(lens_switch_count >= 20 and packaging_switch_count >= 20),
        "finite_state_looking_vs_richer_dynamic_signature": "richer" if not finite_state_like and (lens_switch_count >= 20 or packaging_switch_count >= 20) else "finite_state_looking",
        "regime_label": _regime_label(
            {
                "mean_variation": mean_variation,
                "lens_switch_count": lens_switch_count,
                "packaging_switch_count": packaging_switch_count,
                "tau_switch_count": tau_switch_count,
                "finite_state_like": finite_state_like,
                "budget_volatility": budget_volatility,
            }
        ),
    }


def run() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    src_path = repo_root / "src"
    import sys

    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

    from contextual_cantor.continuous_kernel_substrate import PilotParameters, simulate_substrate

    _ensure_pilot_artifacts(repo_root)

    pilot_report = _load_json(repo_root / "results" / "continuous_kernel_pilot" / "report.json")
    knockout_report = _load_json(repo_root / "results" / "continuous_kernel_pilot" / "knockout_report.json")

    primitive_necessity: dict[str, str] = {}
    for entry in knockout_report.get("knockout_results", []):
        removed = entry["removed"]
        primitive_necessity[removed] = "yes" if entry.get("material_degradation") else "no"
    for primitive in PRIMITIVES:
        primitive_necessity.setdefault(primitive, "unknown")

    seeds = [5, 17, 29]
    kernel_sizes = [16, 20]
    parameter_sets = [
        {
            "tag": "baseline",
            "lens_hysteresis": 0.025,
            "packaging_hysteresis": 0.018,
            "budget_income_scale": 1.0,
            "budget_cost_scale": 1.0,
            "tau_initial": 1.0,
            "action_temperature_bias": 0.0,
            "lens_temperature_shift": 0.0,
        },
        {
            "tag": "exploratory",
            "lens_hysteresis": 0.017,
            "packaging_hysteresis": 0.012,
            "budget_income_scale": 1.08,
            "budget_cost_scale": 0.96,
            "tau_initial": 0.88,
            "action_temperature_bias": 0.045,
            "lens_temperature_shift": 0.02,
        },
    ]

    runs: list[dict[str, Any]] = []
    csv_rows: list[dict[str, Any]] = []
    for seed in seeds:
        for kernel_dim in kernel_sizes:
            for param_set in parameter_sets:
                pilot_params = PilotParameters(
                    lens_hysteresis=param_set["lens_hysteresis"],
                    packaging_hysteresis=param_set["packaging_hysteresis"],
                    budget_income_scale=param_set["budget_income_scale"],
                    budget_cost_scale=param_set["budget_cost_scale"],
                    tau_initial=param_set["tau_initial"],
                    action_temperature_bias=param_set["action_temperature_bias"],
                    lens_temperature_shift=param_set["lens_temperature_shift"],
                )
                sim = simulate_substrate(steps=600, n=kernel_dim, seed=seed, pilot_parameters=pilot_params)
                metrics = _metrics_from_run(
                    {"seed": seed, "state": sim["state"], "trajectory": sim["trajectory"]},
                    primitive_necessity,
                )
                metrics.update(
                    {
                        "seed": seed,
                        "kernel_dim": kernel_dim,
                        "parameter_tag": param_set["tag"],
                        "parameter_values": param_set,
                    }
                )
                runs.append(metrics)
                csv_rows.append(
                    {
                        "seed": seed,
                        "kernel_dim": kernel_dim,
                        "parameter_tag": param_set["tag"],
                        "regime_label": metrics["regime_label"],
                        "mean_variation": metrics["state_variation_summary"]["mean_variation"],
                        "lens_switch_count": metrics["lens_switch_count"],
                        "packaging_switch_count": metrics["packaging_switch_count"],
                        "tau_switch_count": metrics["tau_switch_count"],
                        "budget_min": metrics["budget_min"],
                        "budget_max": metrics["budget_max"],
                        "budget_volatility": metrics["budget_volatility"],
                    }
                )

    label_counts = Counter(run["regime_label"] for run in runs)
    working_regime_class = "lawful_metastable_full_loop_class"
    stretch_regime_class = "lawful_exploratory_full_loop_class"

    decision = "lawful_regime_extracted"
    if label_counts.get("pathological", 0) > 0 and label_counts.get("lawful_exploratory", 0) == 0:
        decision = "continuous_regime_needs_richer_search"
    elif label_counts.get("lawful_exploratory", 0) == 0:
        decision = "continuous_regime_too_brittle"

    report = {
        "schema_version": "v1",
        "regime_id": "continuous_lawful_regime_v1",
        "generated_at_utc": "2026-03-18T00:00:00Z",
        "sweep_parameters": {
            "seeds": seeds,
            "kernel_sizes": kernel_sizes,
            "parameter_sets": parameter_sets,
            "steps_per_run": 600,
        },
        "pilot_reference": {
            "decision": pilot_report.get("decision"),
            "knockout_decision": knockout_report.get("decision"),
        },
        "runs": runs,
        "regime_summary": {
            "label_counts": dict(label_counts),
            "stable_regime_fraction": sum(1 for run in runs if run["regime_label"] in {"lawful_metastable", "lawful_exploratory"}) / max(1, len(runs)),
            "persistent_nontrivial_fraction": sum(1 for run in runs if run["persistent_nontrivial_variation"]) / max(1, len(runs)),
            "switching_rich_fraction": sum(1 for run in runs if run["switching_richness"]) / max(1, len(runs)),
        },
        "primitive_necessity": primitive_necessity,
        "working_regime_class": working_regime_class,
        "stretch_regime_class": stretch_regime_class,
        "decision": decision,
    }

    out_dir = repo_root / "results" / "continuous_regime_diagnostics"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    with (out_dir / "report.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "seed",
                "kernel_dim",
                "parameter_tag",
                "regime_label",
                "mean_variation",
                "lens_switch_count",
                "packaging_switch_count",
                "tau_switch_count",
                "budget_min",
                "budget_max",
                "budget_volatility",
            ],
        )
        writer.writeheader()
        writer.writerows(csv_rows)

    regime_summary_rows = [
        {
            "regime_label": label,
            "count": count,
        }
        for label, count in sorted(label_counts.items())
    ]
    with (out_dir / "regime_summary.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["regime_label", "count"])
        writer.writeheader()
        writer.writerows(regime_summary_rows)

    print(f"wrote {out_dir / 'report.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())

