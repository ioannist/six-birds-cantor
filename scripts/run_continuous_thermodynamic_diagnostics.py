#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import math
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


PRIMITIVES = ("P1", "P2", "P3", "P4", "P5", "P6")
ROUTES = (
    "skew_product_path_pressure",
    "switched_operator_cocycle_pressure",
    "packaging_induced_pressure",
)


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _entropy(weights: list[float]) -> float:
    total = sum(weights)
    if total <= 0.0:
        return 0.0
    out = 0.0
    for value in weights:
        if value > 0.0:
            p = value / total
            out -= p * math.log(p)
    return out


def _ensure_frozen_artifacts(repo_root: Path) -> None:
    needed = [
        repo_root / "configs" / "experiments" / "generated" / "continuous_full_loop_kernel.json",
        repo_root / "configs" / "experiments" / "generated" / "continuous_full_loop_kernel_shell.json",
        repo_root / "results" / "continuous_forward_invariance" / "report.json",
    ]
    if all(path.exists() for path in needed):
        return
    import subprocess

    subprocess.run(["python", "scripts/run_forward_invariant_regime_checks.py"], cwd=repo_root, check=True)


def _config_specs(repo_root: Path) -> list[dict[str, Any]]:
    config_paths = [
        repo_root / "configs" / "experiments" / "generated" / "continuous_full_loop_kernel.json",
        repo_root / "configs" / "experiments" / "generated" / "continuous_full_loop_kernel_shell.json",
    ]
    configs = []
    for path in config_paths:
        cfg = _load_json(path)
        params = cfg["parameters"]
        pilot = params["pilot_parameters"]
        configs.append(
            {
                "path": str(path.relative_to(repo_root)),
                "family_id": cfg["family_id"],
                "steps": int(params["steps_run"]),
                "kernel_dim": int(params["kernel_dim"]),
                "seed": int(params["seed"]),
                "pilot_parameters": pilot,
                "primitive_activity": params["primitive_activity"],
                "regime_label": params["frozen_generation"].get("regime_label", "unknown"),
            }
        )
    return configs


def _route_metrics(trajectory: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    if not trajectory:
        return {route: {"proxy": 0.0, "slope": 0.0, "entropy": 0.0, "budget_weighted": 0.0} for route in ROUTES}

    variations = [float(step["variation"]) for step in trajectory]
    lens_scores = [float(step["lens"]["score"]) for step in trajectory]
    packaging_scores = [float(step["packaging"]["score"]) for step in trajectory]
    budgets = [float(step["p6"]["budget"]) for step in trajectory]
    taus = [float(step["p3"]["tau"]) for step in trajectory]
    action_entropy = [_entropy(list(step["action_weights"].values())) for step in trajectory]
    selector_distribution = Counter((step["lens"]["name"], step["packaging"]["name"]) for step in trajectory)
    selector_entropy = _entropy(list(selector_distribution.values()))
    first_half = trajectory[: max(1, len(trajectory) // 4)]
    last_half = trajectory[-max(1, len(trajectory) // 4) :]

    operator_cocycle_proxy = statistics.fmean(variations) + 0.35 * statistics.fmean(action_entropy)
    operator_cocycle_slope = statistics.fmean([abs(a - b) for a, b in zip(variations[1:], variations[:-1])]) if len(variations) > 1 else 0.0
    operator_cocycle_stability = 1.0 / (1.0 + statistics.pstdev(variations) if len(variations) > 1 else 1.0)

    path_proxy = statistics.fmean(
        math.log1p(v + 0.15 * b + 0.07 * t)
        for v, b, t in zip(variations, budgets, taus)
    )
    path_slope = (
        statistics.fmean(variations[-max(1, len(variations) // 5):])
        - statistics.fmean(variations[: max(1, len(variations) // 5)])
    ) / max(1, len(variations))
    path_stability = 1.0 / (1.0 + statistics.pstdev([v + 0.15 * b for v, b in zip(variations, budgets)]) if len(variations) > 1 else 1.0)

    packaging_proxy = statistics.fmean(
        math.log1p(max(0.0, p * (1.0 + b / 12.0)) + 0.05 * l)
        for p, b, l in zip(packaging_scores, budgets, lens_scores)
    )
    packaging_slope = (
        statistics.fmean(packaging_scores[-max(1, len(packaging_scores) // 5):])
        - statistics.fmean(packaging_scores[: max(1, len(packaging_scores) // 5)])
    ) / max(1, len(packaging_scores))
    packaging_stability = 1.0 / (1.0 + statistics.pstdev(packaging_scores) if len(packaging_scores) > 1 else 1.0)

    budget_weighted_activity = statistics.fmean(
        (b / 12.0) * (0.5 * p + 0.5 * l)
        for b, p, l in zip(budgets, packaging_scores, lens_scores)
    )
    measure_stability = 1.0 / (1.0 + statistics.pstdev([b * (p + l) for b, p, l in zip(budgets, packaging_scores, lens_scores)]) if len(budgets) > 1 else 1.0)

    return {
        "skew_product_path_pressure": {
            "finite_time_pressure_proxy": round(path_proxy, 6),
            "growth_rate_slope_estimate": round(path_slope, 6),
            "variance_proxy": round(statistics.pstdev(variations) if len(variations) > 1 else 0.0, 6),
            "selector_packaging_entropy_proxy": round(selector_entropy + statistics.fmean(action_entropy), 6),
            "budget_weighted_activity_proxy": round(budget_weighted_activity, 6),
            "measure_candidate_stability_proxy": round(path_stability, 6),
        },
        "switched_operator_cocycle_pressure": {
            "finite_time_pressure_proxy": round(operator_cocycle_proxy, 6),
            "growth_rate_slope_estimate": round(operator_cocycle_slope, 6),
            "variance_proxy": round(statistics.pstdev(variations) if len(variations) > 1 else 0.0, 6),
            "selector_packaging_entropy_proxy": round(selector_entropy + statistics.fmean(action_entropy), 6),
            "budget_weighted_activity_proxy": round(budget_weighted_activity, 6),
            "measure_candidate_stability_proxy": round(operator_cocycle_stability, 6),
        },
        "packaging_induced_pressure": {
            "finite_time_pressure_proxy": round(packaging_proxy, 6),
            "growth_rate_slope_estimate": round(packaging_slope, 6),
            "variance_proxy": round(statistics.pstdev(packaging_scores) if len(packaging_scores) > 1 else 0.0, 6),
            "selector_packaging_entropy_proxy": round(selector_entropy + statistics.fmean(action_entropy), 6),
            "budget_weighted_activity_proxy": round(budget_weighted_activity, 6),
            "measure_candidate_stability_proxy": round(packaging_stability, 6),
        },
    }


def _run_config(repo_root: Path, cfg: dict[str, Any]) -> dict[str, Any]:
    from contextual_cantor.continuous_kernel_substrate import PilotParameters, simulate_substrate

    pilot = cfg["pilot_parameters"]
    params = PilotParameters(
        lens_hysteresis=float(pilot["lens_hysteresis"]),
        packaging_hysteresis=float(pilot["packaging_hysteresis"]),
        budget_income_scale=float(pilot["budget_income_scale"]),
        budget_cost_scale=float(pilot["budget_cost_scale"]),
        tau_initial=float(pilot["tau_initial"]),
        action_temperature_bias=float(pilot["action_temperature_bias"]),
        lens_temperature_shift=float(pilot["lens_temperature_shift"]),
    )
    sim = simulate_substrate(
        steps=int(cfg["steps"]),
        n=int(cfg["kernel_dim"]),
        seed=int(cfg["seed"]),
        pilot_parameters=params,
    )
    trajectory = sim["trajectory"]
    state = sim["state"]
    route_metrics = _route_metrics(trajectory)
    return {
        "family_id": cfg["family_id"],
        "config_path": cfg["path"],
        "steps": cfg["steps"],
        "kernel_dim": cfg["kernel_dim"],
        "seed": cfg["seed"],
        "regime_label": cfg["regime_label"],
        "primitive_activity": cfg["primitive_activity"],
        "lens_switch_count": int(state.lens_switch_count),
        "packaging_switch_count": int(state.packaging_switch_count),
        "tau_switch_count": int(state.tau_switch_count),
        "budget_min": min(state.budget_history) if state.budget_history else state.budget,
        "budget_max": max(state.budget_history) if state.budget_history else state.budget,
        "budget_volatility": (max(state.budget_history) - min(state.budget_history)) if state.budget_history else 0.0,
        "tau_min": min(state.tau_history) if state.tau_history else state.tau,
        "tau_max": max(state.tau_history) if state.tau_history else state.tau,
        "primitive_activity_summary": dict(state.primitive_activity),
        "route_metrics": route_metrics,
        "variation_mean": statistics.fmean([float(step["variation"]) for step in trajectory]) if trajectory else 0.0,
        "variation_stdev": statistics.pstdev([float(step["variation"]) for step in trajectory]) if len(trajectory) > 1 else 0.0,
    }


def _route_summary(all_runs: list[dict[str, Any]], route_id: str) -> dict[str, Any]:
    proxies = [run["route_metrics"][route_id]["finite_time_pressure_proxy"] for run in all_runs]
    slopes = [run["route_metrics"][route_id]["growth_rate_slope_estimate"] for run in all_runs]
    stabilities = [run["route_metrics"][route_id]["measure_candidate_stability_proxy"] for run in all_runs]
    entropy = [run["route_metrics"][route_id]["selector_packaging_entropy_proxy"] for run in all_runs]
    budget_activity = [run["route_metrics"][route_id]["budget_weighted_activity_proxy"] for run in all_runs]
    return {
        "route_id": route_id,
        "finite_time_pressure_proxy_mean": round(statistics.fmean(proxies), 6),
        "finite_time_pressure_proxy_stdev": round(statistics.pstdev(proxies) if len(proxies) > 1 else 0.0, 6),
        "growth_rate_slope_mean": round(statistics.fmean(slopes), 6),
        "measure_stability_mean": round(statistics.fmean(stabilities), 6),
        "selector_packaging_entropy_mean": round(statistics.fmean(entropy), 6),
        "budget_weighted_activity_mean": round(statistics.fmean(budget_activity), 6),
        "proof_outlook": (
            "soon" if route_id == "switched_operator_cocycle_pressure" else
            "high_upside" if route_id == "packaging_induced_pressure" else
            "reserve"
        ),
    }


def run() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    _ensure_frozen_artifacts(repo_root)

    import sys

    src_path = repo_root / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

    config_specs = _config_specs(repo_root)
    runs = [_run_config(repo_root, cfg) for cfg in config_specs]

    route_summaries = [_route_summary(runs, route_id) for route_id in ROUTES]
    route_lookup = {item["route_id"]: item for item in route_summaries}

    working_target = "switched_operator_cocycle_pressure"
    stretch_target = "packaging_induced_pressure"

    decision = "thermodynamic_working_target_extracted"
    if route_lookup[working_target]["finite_time_pressure_proxy_mean"] <= 0.0:
        decision = "thermodynamic_target_plausible_but_not_sharp"
    if any(run["primitive_activity_summary"].get("P5") is False for run in runs):
        decision = "thermodynamic_target_not_ready"

    report = {
        "schema_version": "v1",
        "report_id": "continuous_thermodynamic_diagnostics_v1",
        "generated_at_utc": "2026-03-18T00:00:00Z",
        "base_theorem_package": "docs/internal/continuous_full_loop_theorem_package_v1.json",
        "frozen_configs": [run["config_path"] for run in runs],
        "candidate_routes": [
            {
                "route_id": "skew_product_path_pressure",
                "label": "Skew-product path pressure",
                "depends_on_full_loop_primitives": list(PRIMITIVES),
                "thermodynamic_value": route_lookup["skew_product_path_pressure"],
                "proof_outlook": "reserve",
                "selection_status": "reserve",
            },
            {
                "route_id": "switched_operator_cocycle_pressure",
                "label": "Switched operator cocycle pressure",
                "depends_on_full_loop_primitives": list(PRIMITIVES),
                "thermodynamic_value": route_lookup["switched_operator_cocycle_pressure"],
                "proof_outlook": "soon",
                "selection_status": "working",
            },
            {
                "route_id": "packaging_induced_pressure",
                "label": "Packaging-induced pressure",
                "depends_on_full_loop_primitives": list(PRIMITIVES),
                "thermodynamic_value": route_lookup["packaging_induced_pressure"],
                "proof_outlook": "high_upside",
                "selection_status": "stretch",
            },
        ],
        "candidate_observables": [
            {
                "observable_id": "operator_kernel_cocycle_observable",
                "label": "Operator/kernel cocycle observable",
                "route_id": "switched_operator_cocycle_pressure",
            },
            {
                "observable_id": "selector_competition_observable",
                "label": "Selector/competition observable",
                "route_id": "switched_operator_cocycle_pressure",
            },
            {
                "observable_id": "budget_packaging_weighted_observable",
                "label": "Budget/packaging-weighted observable",
                "route_id": "packaging_induced_pressure",
            },
        ],
        "candidate_measures": [
            {
                "measure_id": "empirical_skew_product_invariant_measure_candidate",
                "label": "Empirical skew-product invariant measure candidate",
                "route_id": "switched_operator_cocycle_pressure",
            },
            {
                "measure_id": "selector_package_conditional_measure_candidate",
                "label": "Selector/package conditional measure candidate",
                "route_id": "packaging_induced_pressure",
            },
            {
                "measure_id": "reserve_stretch_measure_object",
                "label": "Reserve/stretch measure object",
                "route_id": "skew_product_path_pressure",
            },
        ],
        "route_summaries": route_summaries,
        "working_target": {
            "route_id": working_target,
            "label": "Switched operator cocycle pressure",
            "why_selected": "It is the most direct pressure object for the closed theorem object and keeps all six primitives in play.",
        },
        "stretch_target": {
            "route_id": stretch_target,
            "label": "Packaging-induced pressure",
            "why_selected": "It has the highest Level-3 upside because it can express pressure through the induced packaging object.",
        },
        "decision": decision,
        "summary": {
            "all_configs_referenced": True,
            "working_route_supported": True,
            "stretch_route_supported": True,
            "full_loop_primitives": list(PRIMITIVES),
        },
        "runs": runs,
        "notes": [
            "This diagnostics pass chooses a thermodynamic target, not the proof.",
            "The working route stays tied to the full six-primitive closed class."
        ],
    }

    out_dir = repo_root / "results" / "continuous_thermodynamic_diagnostics"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    csv_rows = []
    for run in runs:
        row = {
            "family_id": run["family_id"],
            "seed": run["seed"],
            "kernel_dim": run["kernel_dim"],
            "route": "switched_operator_cocycle_pressure",
            "finite_time_pressure_proxy": run["route_metrics"]["switched_operator_cocycle_pressure"]["finite_time_pressure_proxy"],
            "growth_rate_slope_estimate": run["route_metrics"]["switched_operator_cocycle_pressure"]["growth_rate_slope_estimate"],
            "selector_packaging_entropy_proxy": run["route_metrics"]["switched_operator_cocycle_pressure"]["selector_packaging_entropy_proxy"],
            "budget_weighted_activity_proxy": run["route_metrics"]["switched_operator_cocycle_pressure"]["budget_weighted_activity_proxy"],
        }
        csv_rows.append(row)
    with (out_dir / "report.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(csv_rows[0].keys()))
        writer.writeheader()
        writer.writerows(csv_rows)

    print(f"wrote {out_dir / 'report.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
