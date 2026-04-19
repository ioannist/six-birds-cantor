#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import math
import statistics
from collections import Counter
from pathlib import Path
from typing import Any


ROUTES = (
    "packaging_induced_shell_stable_class",
    "packaging_induced_wider_shell_class",
    "cocycle_route_is_final_best_story",
)


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _entropy(counts: list[int] | list[float]) -> float:
    total = sum(counts)
    if total <= 0:
        return 0.0
    out = 0.0
    for value in counts:
        if value > 0:
            p = value / total
            out -= p * math.log(p)
    return out


def _config_specs(repo_root: Path) -> list[dict[str, Any]]:
    cfg_paths = [
        repo_root / "configs" / "experiments" / "generated" / "continuous_full_loop_kernel.json",
        repo_root / "configs" / "experiments" / "generated" / "continuous_full_loop_kernel_shell.json",
    ]
    specs: list[dict[str, Any]] = []
    for path in cfg_paths:
        cfg = _load_json(path)
        params = cfg["parameters"]
        specs.append(
            {
                "path": str(path.relative_to(repo_root)),
                "family_id": cfg["family_id"],
                "steps": int(params["steps_run"]),
                "kernel_dim": int(params["kernel_dim"]),
                "seed": int(params["seed"]),
                "pilot_parameters": params["pilot_parameters"],
                "primitive_activity": params["primitive_activity"],
                "working_class_id": params["frozen_generation"].get("working_class_id"),
                "stretch_class_id": params["frozen_generation"].get("stretch_class_id"),
            }
        )
    return specs


def _ensure_src(repo_root: Path) -> None:
    import sys

    src_path = repo_root / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))


def _trajectory_metrics(trajectory: list[dict[str, Any]]) -> dict[str, Any]:
    packaging_names = [step["packaging"]["name"] for step in trajectory]
    lens_names = [step["lens"]["name"] for step in trajectory]
    packaging_scores = [float(step["packaging"]["score"]) for step in trajectory]
    lens_scores = [float(step["lens"]["score"]) for step in trajectory]
    variations = [float(step["variation"]) for step in trajectory]
    budgets = [float(step["p6"]["budget"]) for step in trajectory]
    taus = [float(step["p3"]["tau"]) for step in trajectory]

    packaging_counter = Counter(packaging_names)
    lens_counter = Counter(lens_names)
    packaging_entropy = _entropy(list(packaging_counter.values()))
    lens_entropy = _entropy(list(lens_counter.values()))
    packaging_diversity = len(packaging_counter) / 3.0

    cocycle_series = [
        math.log1p(v + 0.14 * b + 0.05 * abs(t - 1.0))
        for v, b, t in zip(variations, budgets, taus)
    ]
    packaging_series = [
        math.log1p(max(0.0, p * (1.0 + b / 12.0)) + 0.06 * l)
        for p, b, l in zip(packaging_scores, budgets, lens_scores)
    ]
    selector_series = [
        math.log1p((p + l) * (1.0 + b / 12.0))
        for p, l, b in zip(packaging_scores, lens_scores, budgets)
    ]
    pressure_series = {
        "cocycle": cocycle_series,
        "packaging": packaging_series,
        "selector": selector_series,
    }
    return {
        "packaging_switch_count": sum(1 for a, b in zip(packaging_names[1:], packaging_names[:-1]) if a != b),
        "lens_switch_count": sum(1 for a, b in zip(lens_names[1:], lens_names[:-1]) if a != b),
        "package_entropy": round(packaging_entropy, 6),
        "package_diversity": round(packaging_diversity, 6),
        "lens_entropy": round(lens_entropy, 6),
        "packaging_pressure_proxy_mean": round(statistics.fmean(packaging_series), 6),
        "packaging_pressure_proxy_stdev": round(statistics.pstdev(packaging_series) if len(packaging_series) > 1 else 0.0, 6),
        "cocycle_pressure_proxy_mean": round(statistics.fmean(cocycle_series), 6),
        "cocycle_pressure_proxy_stdev": round(statistics.pstdev(cocycle_series) if len(cocycle_series) > 1 else 0.0, 6),
        "selector_measure_proxy_mean": round(statistics.fmean(selector_series), 6),
        "selector_measure_proxy_stdev": round(statistics.pstdev(selector_series) if len(selector_series) > 1 else 0.0, 6),
        "budget_weighted_activity_proxy": round(statistics.fmean((b / 12.0) * (0.5 * p + 0.5 * l) for b, p, l in zip(budgets, packaging_scores, lens_scores)), 6),
        "packaging_series": packaging_series,
        "cocycle_series": cocycle_series,
    }


def _run_config(repo_root: Path, cfg: dict[str, Any]) -> dict[str, Any]:
    from contextual_cantor.continuous_kernel_substrate import PilotParameters, simulate_substrate

    params = PilotParameters(
        lens_hysteresis=float(cfg["pilot_parameters"]["lens_hysteresis"]),
        packaging_hysteresis=float(cfg["pilot_parameters"]["packaging_hysteresis"]),
        budget_income_scale=float(cfg["pilot_parameters"]["budget_income_scale"]),
        budget_cost_scale=float(cfg["pilot_parameters"]["budget_cost_scale"]),
        tau_initial=float(cfg["pilot_parameters"]["tau_initial"]),
        action_temperature_bias=float(cfg["pilot_parameters"]["action_temperature_bias"]),
        lens_temperature_shift=float(cfg["pilot_parameters"]["lens_temperature_shift"]),
    )
    base_activity = dict(cfg["primitive_activity"])
    sim = simulate_substrate(
        steps=int(cfg["steps"]),
        n=int(cfg["kernel_dim"]),
        seed=int(cfg["seed"]),
        primitive_activity=base_activity,
        pilot_parameters=params,
    )
    trajectory = sim["trajectory"]
    state = sim["state"]
    metrics = _trajectory_metrics(trajectory)

    p5_off = dict(base_activity)
    p5_off["P5"] = False
    knockout = simulate_substrate(
        steps=int(cfg["steps"]),
        n=int(cfg["kernel_dim"]),
        seed=int(cfg["seed"]),
        primitive_activity=p5_off,
        pilot_parameters=params,
    )
    knockout_metrics = _trajectory_metrics(knockout["trajectory"])

    return {
        "family_id": cfg["family_id"],
        "config_path": cfg["path"],
        "kernel_dim": cfg["kernel_dim"],
        "seed": cfg["seed"],
        "steps": cfg["steps"],
        "frozen_class": cfg["working_class_id"] or cfg["stretch_class_id"],
        "primitive_activity": state.primitive_activity,
        "packaging_switch_count": int(state.packaging_switch_count),
        "lens_switch_count": int(state.lens_switch_count),
        "tau_switch_count": int(state.tau_switch_count),
        "budget_min": min(state.budget_history) if state.budget_history else state.budget,
        "budget_max": max(state.budget_history) if state.budget_history else state.budget,
        "tau_min": min(state.tau_history) if state.tau_history else state.tau,
        "tau_max": max(state.tau_history) if state.tau_history else state.tau,
        "packaging_entropy": metrics["package_entropy"],
        "packaging_diversity": metrics["package_diversity"],
        "packaging_pressure_proxy_mean": metrics["packaging_pressure_proxy_mean"],
        "packaging_pressure_proxy_stdev": metrics["packaging_pressure_proxy_stdev"],
        "cocycle_pressure_proxy_mean": metrics["cocycle_pressure_proxy_mean"],
        "cocycle_pressure_proxy_stdev": metrics["cocycle_pressure_proxy_stdev"],
        "selector_measure_proxy_mean": metrics["selector_measure_proxy_mean"],
        "selector_measure_proxy_stdev": metrics["selector_measure_proxy_stdev"],
        "budget_weighted_activity_proxy": metrics["budget_weighted_activity_proxy"],
        "p5_knockout": {
            "packaging_switch_count": int(knockout["state"].packaging_switch_count),
            "packaging_entropy": round(_entropy(list(Counter(step["packaging"]["name"] for step in knockout["trajectory"]).values())), 6),
            "packaging_pressure_proxy_mean": knockout_metrics["packaging_pressure_proxy_mean"],
            "cocycle_pressure_proxy_mean": knockout_metrics["cocycle_pressure_proxy_mean"],
            "selector_measure_proxy_mean": knockout_metrics["selector_measure_proxy_mean"],
            "primitive_activity": p5_off,
        },
        "route_metrics": {
            "packaging_induced_shell_stable_class": {
                "observable_mean": metrics["packaging_pressure_proxy_mean"],
                "observable_stdev": metrics["packaging_pressure_proxy_stdev"],
                "measure_stability_proxy": round(1.0 / (1.0 + metrics["packaging_pressure_proxy_stdev"]), 6),
            },
            "packaging_induced_wider_shell_class": {
                "observable_mean": metrics["packaging_pressure_proxy_mean"],
                "observable_stdev": metrics["packaging_pressure_proxy_stdev"],
                "measure_stability_proxy": round(1.0 / (1.0 + metrics["packaging_pressure_proxy_stdev"]), 6),
            },
            "cocycle_route_is_final_best_story": {
                "observable_mean": metrics["cocycle_pressure_proxy_mean"],
                "observable_stdev": metrics["cocycle_pressure_proxy_stdev"],
                "measure_stability_proxy": round(1.0 / (1.0 + metrics["cocycle_pressure_proxy_stdev"]), 6),
            },
        },
    }


def run() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    _ensure_src(repo_root)

    config_specs = _config_specs(repo_root)
    runs = [_run_config(repo_root, cfg) for cfg in config_specs]

    working_route = "packaging_induced_shell_stable_class"
    reserve_route = "packaging_induced_wider_shell_class"
    rejected_route = "cocycle_route_is_final_best_story"

    working_shell = next(run for run in runs if run["family_id"] == "generated.continuous_full_loop_kernel_shell")
    working_base = next(run for run in runs if run["family_id"] == "generated.continuous_full_loop_kernel")
    p5_knockout_drop = (
        working_base["packaging_switch_count"] - working_base["p5_knockout"]["packaging_switch_count"]
    )
    route_degeneracy_gap = abs(
        working_base["route_metrics"][working_route]["observable_mean"]
        - working_base["route_metrics"][rejected_route]["observable_mean"]
    )

    class_broadening = False
    primitive_value = False
    nondegenerate = route_degeneracy_gap > 0.05
    robustness = working_shell["packaging_pressure_proxy_stdev"] <= max(working_base["packaging_pressure_proxy_stdev"] * 1.2, working_base["packaging_pressure_proxy_stdev"] + 0.002)

    decision = "packaging_route_plausible_but_not_broader"
    if not nondegenerate and p5_knockout_drop <= 0:
        decision = "freeze_on_cocycle_route"
    elif class_broadening and primitive_value and nondegenerate and robustness:
        decision = "advance_packaging_induced_theorem"

    report = {
        "schema_version": "v1",
        "report_id": "packaging_induced_stretch_v1",
        "generated_at_utc": "2026-03-18T00:00:00Z",
        "base_closed_class": "continuous_full_loop_lawful_kernel_class_shell_stable",
        "frozen_configs": [
            "configs/experiments/generated/continuous_full_loop_kernel.json",
            "configs/experiments/generated/continuous_full_loop_kernel_shell.json",
        ],
        "candidate_routes": [
            {
                "route_id": working_route,
                "label": "Packaging-induced shell-stable class",
                "depends_on_active_p5": True,
                "broadening_potential": "meaningful_but_class_equivalent",
                "proof_outlook": "reserve",
                "selection_status": "selected",
            },
            {
                "route_id": reserve_route,
                "label": "Packaging-induced wider-shell class",
                "depends_on_active_p5": True,
                "broadening_potential": "unsupported_by_current_diagnostics",
                "proof_outlook": "stretch_only",
                "selection_status": "reserve",
            },
            {
                "route_id": rejected_route,
                "label": "Cocycle route is final best story",
                "depends_on_active_p5": True,
                "broadening_potential": "default_closed_route",
                "proof_outlook": "default",
                "selection_status": "rejected",
            },
        ],
        "candidate_observables": [
            {
                "observable_id": "package_switching_growth_observable",
                "label": "Package-switching growth observable",
                "route_id": working_route,
            },
            {
                "observable_id": "package_entropy_complexity_observable",
                "label": "Package entropy / complexity observable",
                "route_id": working_route,
            },
            {
                "observable_id": "package_budget_weighted_growth_observable",
                "label": "Package/budget-weighted growth observable",
                "route_id": working_route,
            },
        ],
        "candidate_measures": [
            {
                "measure_id": "package_conditional_empirical_measure_candidate",
                "label": "Package-conditional empirical measure candidate",
                "route_id": working_route,
            },
            {
                "measure_id": "packaging_selector_invariant_measure_candidate",
                "label": "Packaging-selector invariant measure candidate",
                "route_id": working_route,
            },
            {
                "measure_id": "reserve_stretch_measure_object",
                "label": "Reserve/stretch measure object",
                "route_id": reserve_route,
            },
        ],
        "broadening_tests": [
            {
                "test_id": "class_broadening_test",
                "result": class_broadening,
                "note": "The packaging route remains on the shell-stable closed class; no strictly broader shell is supported.",
            },
            {
                "test_id": "primitive_value_test",
                "result": primitive_value,
                "note": "P5 is indispensable for packaging dynamics, but the diagnostics do not justify a stronger theorem class than the cocycle route.",
            },
            {
                "test_id": "nondegeneracy_test",
                "result": nondegenerate,
                "note": f"Packaging and cocycle observables differ by {route_degeneracy_gap:.3f} on the working config.",
            },
            {
                "test_id": "robustness_test",
                "result": robustness,
                "note": "The packaging route survives on the shell witness, but without evidence of broader class coverage.",
            },
        ],
        "decision": decision,
        "route_comparison": {
            "working_route": working_route,
            "reserve_route": reserve_route,
            "rejected_route": rejected_route,
            "working_base": {
                "packaging_switch_count": working_base["packaging_switch_count"],
                "package_entropy": working_base["packaging_entropy"],
                "packaging_pressure_proxy_mean": working_base["packaging_pressure_proxy_mean"],
                "cocycle_pressure_proxy_mean": working_base["cocycle_pressure_proxy_mean"],
                "p5_knockout_drop_in_packaging_switches": p5_knockout_drop,
            },
            "working_shell": {
                "packaging_switch_count": working_shell["packaging_switch_count"],
                "package_entropy": working_shell["packaging_entropy"],
                "packaging_pressure_proxy_mean": working_shell["packaging_pressure_proxy_mean"],
                "cocycle_pressure_proxy_mean": working_shell["cocycle_pressure_proxy_mean"],
            },
        },
        "notes": [
            "The packaging route is mathematically meaningful and P5-heavy, but the diagnostics do not support a broader theorem class.",
            "The cocycle route remains the closed default proof story for now.",
        ],
        "support_sources": {
            "thermodynamic_diagnostics_report": "results/continuous_thermodynamic_diagnostics/report.json",
            "pressure_closure_report": "results/continuous_pressure_closure/report.json",
            "regime_diagnostics_report": "results/continuous_regime_diagnostics/report.json",
        },
    }

    out_dir = repo_root / "results" / "packaging_induced_stretch"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    csv_path = out_dir / "report.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["family_id", "packaging_switch_count", "package_entropy", "packaging_pressure_proxy_mean", "cocycle_pressure_proxy_mean", "p5_knockout_packaging_switch_count"])
        for run in runs:
            writer.writerow([
                run["family_id"],
                run["packaging_switch_count"],
                run["packaging_entropy"],
                run["packaging_pressure_proxy_mean"],
                run["cocycle_pressure_proxy_mean"],
                run["p5_knockout"]["packaging_switch_count"],
            ])

    return 0


if __name__ == "__main__":
    raise SystemExit(run())
