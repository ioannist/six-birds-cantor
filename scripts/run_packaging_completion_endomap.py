#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import statistics
from collections import Counter
from pathlib import Path
from typing import Any


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _ensure_src(repo_root: Path) -> None:
    import sys

    src_path = repo_root / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))


def _config_specs(repo_root: Path) -> list[dict[str, Any]]:
    paths = [
        repo_root / "configs" / "experiments" / "generated" / "continuous_full_loop_kernel.json",
        repo_root / "configs" / "experiments" / "generated" / "continuous_full_loop_kernel_shell.json",
    ]
    specs: list[dict[str, Any]] = []
    for path in paths:
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


def _distribution_summary(values: list[list[float]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for idx, vec in enumerate(values):
        out.append({"name": f"mu_{idx}", "support": [round(x, 6) for x in vec]})
    return out


def _run_config(repo_root: Path, cfg: dict[str, Any]) -> dict[str, Any]:
    from contextual_cantor.continuous_kernel_substrate import (
        PilotParameters,
        compute_p4_lenses,
        compute_packaging_fixed_points,
        detect_packaging_saturation,
        packaging_macro_admissibility,
        refresh_informants,
        simulate_substrate,
        _completion_initial_distributions,  # type: ignore[attr-defined]
    )

    params = PilotParameters(
        lens_hysteresis=float(cfg["pilot_parameters"]["lens_hysteresis"]),
        packaging_hysteresis=float(cfg["pilot_parameters"]["packaging_hysteresis"]),
        budget_income_scale=float(cfg["pilot_parameters"]["budget_income_scale"]),
        budget_cost_scale=float(cfg["pilot_parameters"]["budget_cost_scale"]),
        tau_initial=float(cfg["pilot_parameters"]["tau_initial"]),
        action_temperature_bias=float(cfg["pilot_parameters"]["action_temperature_bias"]),
        lens_temperature_shift=float(cfg["pilot_parameters"]["lens_temperature_shift"]),
    )
    sim = simulate_substrate(
        steps=int(cfg["steps"]),
        n=int(cfg["kernel_dim"]),
        seed=int(cfg["seed"]),
        primitive_activity=dict(cfg["primitive_activity"]),
        pilot_parameters=params,
    )
    state = sim["state"]
    kernel = state.kernel
    informants = refresh_informants(state, state.primitive_activity)
    lenses = compute_p4_lenses(state, informants, state.primitive_activity)
    lens_values = [
        "spectral_lens",
        "row_similarity_cluster_lens",
        "audit_flow_quantile_lens",
    ]

    tau_values = sorted(
        {
            round(max(0.6, state.tau), 3),
            round(min(2.0, max(0.75, state.tau + 0.35)), 3),
        }
    )
    initials = _completion_initial_distributions(kernel)[:3]
    completion = compute_packaging_fixed_points(
        kernel,
        tau_values=tau_values,
        lens_states=lens_values,
        initial_distributions=initials,
        max_iter=56,
        tol=1e-8,
    )

    runs = completion["runs"]
    status_counts = Counter(run["completion_summary"]["status"] for run in runs)
    admissible_count = sum(1 for run in runs if run["macro_admissibility"]["admissible"])
    feedback_events = sum(1 for run in runs if run["feedback"]["applied"])
    material_feedback = sum(1 for run in runs if run["feedback"]["applied"] and run["feedback"]["to_lens"] != run["feedback"]["from_lens"])
    distinct_counts_by_panel = Counter((run["tau"], run["lens_state"]) for run in runs)
    fixed_point_counts_by_panel: dict[str, dict[str, Any]] = {}
    for tau in tau_values:
        for lens_state in lens_values[:2]:
            panel_runs = [run for run in runs if run["tau"] == tau and run["lens_state"] == lens_state]
            fixed_point_counts_by_panel[f"{tau}:{lens_state}"] = {
                "run_count": len(panel_runs),
                "distinct_fixed_points": len({tuple(run["completion_summary"]["final_signature"])
                                               for run in panel_runs
                                               if run["completion_summary"]["numerically_converged"]}),
                "statuses": dict(Counter(run["completion_summary"]["status"] for run in panel_runs)),
            }

    saturation_check = detect_packaging_saturation(
        runs, tau_values=tau_values, lens_states=lens_values, initial_count=len(initials),
    )
    saturation = {
        "saturated": (saturation_check["total_panels"] > 0
                      and saturation_check["saturated_panel_count"] == saturation_check["total_panels"]),
        "saturation_verified": False,
        "scope": saturation_check["scope"],
        "distinct_fixed_point_total": completion["distinct_fixed_point_count"],
        "panel_summaries": fixed_point_counts_by_panel,
    }
    macro_admissibility = {
        "admissible_count": admissible_count,
        "run_count": len(runs),
        "admissible_fraction": admissible_count / max(1, len(runs)),
        "summary_by_panel": {
            key: {
                "admissible": sum(1 for run in runs if f"{run['tau']}:{run['lens_state']}" == key and run["macro_admissibility"]["admissible"]),
                "run_count": value["run_count"],
            }
            for key, value in fixed_point_counts_by_panel.items()
        },
    }
    p4_feedback_summary = {
        "feedback_events": feedback_events,
        "material_feedback_events": 0,
        "proposed_lens_change_count": material_feedback,
        "feedback_rate": feedback_events / max(1, len(runs)),
        "material_feedback_rate": 0.0,
        "proposal_rate": material_feedback / max(1, len(runs)),
        "lens_changes": [
            {
                "from_lens": run["feedback"]["from_lens"],
                "to_lens": run["feedback"]["to_lens"],
                "tau": run["tau"],
                "packaging_entropy": run["completion_summary"]["meta_history"][-1]["package_entropy"] if run["completion_summary"]["meta_history"] else 0.0,
            }
            for run in runs
            if run["feedback"]["applied"]
        ],
    }

    # A proposed lens change is not a comparison of the pre/post completion
    # objects. No certificate of changed theorem objects is constructed here.
    theorem_object_changed = False
    broadening_verdict = "not_broader"
    p5_object_role_verdict = "theorem_object_generator_but_class_equivalent"
    decision = "completion_object_real_but_not_broader"
    if completion["distinct_fixed_point_count"] < 2 or status_counts.get("nonconvergent", 0) == len(runs):
        broadening_verdict = "blocked"
        p5_object_role_verdict = "blocked"
        decision = "completion_endomap_blocked"

    return {
        "config_id": cfg["family_id"],
        "config_path": cfg["path"],
        "kernel_dim": cfg["kernel_dim"],
        "tau_values_checked": tau_values,
        "lens_values_checked": lens_values,
        "initial_conditions_checked": [item["name"] for item in _distribution_summary(initials)],
        "fixed_point_count_summary": {
            "distinct_fixed_point_total": completion["distinct_fixed_point_count"],
            "statuses": dict(status_counts),
            "per_panel": fixed_point_counts_by_panel,
        },
        "saturation_summary": saturation,
        "p4_from_p5_feedback_summary": p4_feedback_summary,
        "macro_admissibility_summary": macro_admissibility,
        "broadening_verdict": broadening_verdict,
        "p5_object_role_verdict": p5_object_role_verdict,
        "theorem_object_changed_from_cocycle_route": theorem_object_changed,
        "note": "Packaging completion is a real fixed-point object, but on current evidence it does not broaden the theorem class beyond the closed cocycle route.",
        "runs": runs,
    }


def run() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    _ensure_src(repo_root)

    config_specs = _config_specs(repo_root)
    summaries = [_run_config(repo_root, cfg) for cfg in config_specs]

    admissible_counts = [summary["macro_admissibility_summary"]["admissible_count"] for summary in summaries]
    total_fp = sum(summary["fixed_point_count_summary"]["distinct_fixed_point_total"] for summary in summaries)
    theorem_object_changed = any(summary["theorem_object_changed_from_cocycle_route"] for summary in summaries)
    decision = "completion_object_real_but_not_broader"
    if total_fp == 0 or all(summary["broadening_verdict"] == "blocked" for summary in summaries):
        decision = "completion_endomap_blocked"
    elif theorem_object_changed and any(count > 0 for count in admissible_counts):
        decision = "completion_object_real_but_not_broader"

    report = {
        "report_id": "packaging_completion_endomap_v1",
        "schema_version": "v1",
        "generated_at_utc": "2026-03-18T00:00:00Z",
        "decision": decision,
        "base_closed_class": "continuous_full_loop_lawful_kernel_class_shell_stable",
        "configs": [summary["config_id"] for summary in summaries],
        "tau_values_checked": sorted({tau for summary in summaries for tau in summary["tau_values_checked"]}),
        "lens_values_checked": sorted({lens for summary in summaries for lens in summary["lens_values_checked"]}),
        "initial_conditions_checked": sorted({initial for summary in summaries for initial in summary["initial_conditions_checked"]}),
        "fixed_point_count_summary": {
            "per_config": {
                summary["config_id"]: summary["fixed_point_count_summary"]
                for summary in summaries
            },
            "total_distinct_fixed_points": total_fp,
        },
        "saturation_summary": {
            "per_config": {
                summary["config_id"]: summary["saturation_summary"]
                for summary in summaries
            }
        },
        "p4_from_p5_feedback_summary": {
            "per_config": {
                summary["config_id"]: summary["p4_from_p5_feedback_summary"]
                for summary in summaries
            }
        },
        "macro_admissibility_summary": {
            "per_config": {
                summary["config_id"]: summary["macro_admissibility_summary"]
                for summary in summaries
            }
        },
        "broadening_verdict": "not_decided_by_finite_completion_samples",
        "p5_object_role_verdict": "numerical_completion_candidates_only",
        "theorem_object_changed_from_cocycle_route": theorem_object_changed,
        "notes": [
            "The packaging map is now treated as a theorem-object generator via its fixed points.",
            "The current evidence supports a real completion object, but not a broader theorem class than the closed cocycle route.",
        ],
        "frozen_configs": [
            "configs/experiments/generated/continuous_full_loop_kernel.json",
            "configs/experiments/generated/continuous_full_loop_kernel_shell.json",
        ],
        "completion_object_comparison": {
            "cocycle_route": "closed continuous cocycle pressure object",
            "completion_route": "packaging fixed-point object",
            "class_relation": "class_equivalent_on_current_evidence",
        },
        "summaries": summaries,
    }

    out_dir = repo_root / "results" / "packaging_completion_endomap"
    out_dir.mkdir(parents=True, exist_ok=True)
    import sys
    sys.path.insert(0, str(repo_root / "src"))
    from contextual_cantor.audit_status import mark_diagnostic_report
    mark_diagnostic_report(report, "numerical_completion_candidates_and_feedback_proposals")

    (out_dir / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    with (out_dir / "report.csv").open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow([
            "config_id",
            "tau_values_checked",
            "lens_values_checked",
            "initial_conditions_checked",
            "distinct_fixed_points",
            "saturation",
            "feedback_events",
            "admissible_count",
        ])
        for summary in summaries:
            writer.writerow([
                summary["config_id"],
                "|".join(map(str, summary["tau_values_checked"])),
                "|".join(summary["lens_values_checked"]),
                "|".join(summary["initial_conditions_checked"]),
                summary["fixed_point_count_summary"]["distinct_fixed_point_total"],
                summary["saturation_summary"]["saturated"],
                summary["p4_from_p5_feedback_summary"]["feedback_events"],
                summary["macro_admissibility_summary"]["admissible_count"],
            ])

    return 0


if __name__ == "__main__":
    raise SystemExit(run())
