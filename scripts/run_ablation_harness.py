#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import random
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any


def canonical_json_sha256(data: Any) -> str:
    canonical = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _depths_for_cutoff(depth_cutoff: int) -> list[int]:
    a = max(2, depth_cutoff - 4)
    b = max(2, depth_cutoff - 2)
    return sorted({a, b, depth_cutoff})


def _reorder_list(values: list[Any], ordering: str, seed: int) -> list[Any]:
    out = list(values)
    if ordering == "lex":
        try:
            out = sorted(out)
        except Exception:
            pass
    elif ordering == "reverse":
        try:
            out = sorted(out, reverse=True)
        except Exception:
            out = list(reversed(out))
    elif ordering == "shuffled":
        rng = random.Random(seed)
        rng.shuffle(out)
    return out


def _apply_branch_ordering(config: dict[str, Any], ordering: str, seed: int) -> tuple[dict[str, Any], str]:
    cfg = deepcopy(config)
    params = cfg.get("parameters", {})
    if not isinstance(params, dict):
        return cfg, "not_applicable:parameters_not_object"

    touched = False
    engine = str(cfg.get("engine", ""))
    family_id = str(cfg.get("family_id", ""))

    if engine == "classical_similarity" and isinstance(params.get("allowed_digits"), list):
        params["allowed_digits"] = _reorder_list(params["allowed_digits"], ordering, seed)
        touched = True

    if engine == "finite_state_symbolic":
        if isinstance(params.get("edges"), list):
            params["edges"] = _reorder_list(params["edges"], ordering, seed)
            touched = True
        if isinstance(params.get("start_digits"), list):
            params["start_digits"] = _reorder_list(params["start_digits"], ordering, seed)
            touched = True
        if isinstance(params.get("transition_digits"), dict):
            td = params["transition_digits"]
            for k, v in td.items():
                if isinstance(v, list):
                    td[k] = _reorder_list(v, ordering, seed)
                    touched = True

    if engine == "contextual_feedback" or family_id.startswith("contextual_local.feedback"):
        if isinstance(params.get("protocol_digits"), dict):
            pd = params["protocol_digits"]
            for k, v in pd.items():
                if isinstance(v, list):
                    pd[k] = _reorder_list(v, ordering, seed)
                    touched = True
        if isinstance(params.get("gating_digits_by_state"), dict):
            gd = params["gating_digits_by_state"]
            for k, v in gd.items():
                if isinstance(v, list):
                    gd[k] = _reorder_list(v, ordering, seed)
                    touched = True

    cfg["parameters"] = params
    if not touched:
        return cfg, "not_applicable:no_orderable_sequences"
    return cfg, "applied"


def _reference_root_for_family(family_id: str) -> float | None:
    import math

    if family_id == "classical.middle_thirds":
        return math.log(2.0) / math.log(3.0)
    if family_id == "classical.restricted_digits_base5_024":
        return math.log(3.0) / math.log(5.0)
    if family_id == "finite_state.adjacency_no_consecutive_2_base3":
        phi = (1.0 + math.sqrt(5.0)) / 2.0
        return math.log(phi) / math.log(3.0)
    return None


def _evaluate_run(
    *,
    repo_root: Path,
    config: dict[str, Any],
    config_path: str,
    run_id: str,
    depth_cutoff: int,
    tol: float,
    s_max: float,
    output_dir: Path,
    notes: str,
) -> dict[str, Any]:
    src_path = repo_root / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

    from contextual_cantor.local_pressure import analyze_config  # type: ignore

    depths = _depths_for_cutoff(depth_cutoff)
    analysis = analyze_config(config=config, depths=depths, s_min=0.0, s_max=s_max, tol=tol)
    rows = analysis["rows"]
    final = rows[-1]
    drift = 0.0
    if len(rows) >= 2 and rows[-2]["upper_root"] is not None and rows[-1]["upper_root"] is not None:
        drift = abs(rows[-1]["upper_root"] - rows[-2]["upper_root"])

    family_id = str(config["family_id"])
    ref = _reference_root_for_family(family_id)
    abs_error = None
    if ref is not None and final["upper_root"] is not None:
        abs_error = abs(float(final["upper_root"]) - float(ref))

    run_dir = output_dir / family_id.replace(".", "_") / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = run_dir / "result_manifest.json"
    manifest = {
        "schema_version": "1.0",
        "run_id": run_id,
        "timestamp_utc": dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z"),
        "status": "success",
        "code_version": "UNSET",
        "config_path": config_path,
        "config_hash_method": "sha256-json-canonical-v1",
        "config_hash_sha256": canonical_json_sha256(config),
        "family_id": family_id,
        "engine": config["engine"],
        "parameters": config["parameters"],
        "artifacts": [],
        "summary_metrics": {
            "final_depth": final["depth"],
            "final_upper_root": final["upper_root"],
            "final_lower_root": final["lower_root"],
            "interval_root_width": final["interval_root_width"],
            "last_step_upper_root_drift": drift,
            "reference_root": ref,
            "abs_error": abs_error,
            "tol": tol,
            "s_max": s_max,
            "depth_cutoff": depth_cutoff,
        },
        "command": "python scripts/run_ablation_harness.py",
        "exit_status": 0,
        "warnings": [],
        "notes": notes,
        "environment": {"python": sys.version.split()[0]},
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")

    return {
        "run_id": run_id,
        "manifest_path": manifest_path.relative_to(repo_root).as_posix(),
        "final_depth": final["depth"],
        "final_upper_root": final["upper_root"],
        "final_lower_root": final["lower_root"],
        "interval_root_width": final["interval_root_width"],
        "last_step_drift": drift,
        "reference_root": ref,
        "abs_error": abs_error,
    }


def _tol_for_precision(kind: str, default_tol: float) -> float:
    if kind == "loose":
        return 1e-6
    if kind == "tight":
        return 1e-12
    return default_tol


def _smax_for_discretization(kind: str, default_smax: float) -> float:
    if kind == "coarse":
        return 1.0
    return default_smax


def run(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run OFAT robustness ablation harness for local-pressure.")
    parser.add_argument("--plan", required=True, type=Path)
    args = parser.parse_args(argv)

    repo_root = Path(__file__).resolve().parent.parent
    plan_path = args.plan if args.plan.is_absolute() else (Path.cwd() / args.plan)
    plan_path = plan_path.resolve()
    plan = _load_json(plan_path)
    if not isinstance(plan, dict):
        raise ValueError("plan must be object")

    thresholds_path = repo_root / "configs" / "regressions" / "local_pressure_regression_thresholds_v1.json"
    thresholds = _load_json(thresholds_path)
    if not isinstance(thresholds, dict):
        raise ValueError("thresholds file must be object")

    ablation_id = str(plan["ablation_id"])
    output_dir = repo_root / "results" / "robustness" / ablation_id
    output_dir.mkdir(parents=True, exist_ok=True)

    defaults = plan["default_settings"]
    factors = plan["factors"]
    families = plan["families"]

    rows: list[dict[str, Any]] = []

    for fam in families:
        family_id = str(fam["family_id"])
        config_path = str(fam["config_path"])
        config = _load_json(repo_root / config_path)
        if not isinstance(config, dict):
            raise ValueError(f"config must be object: {config_path}")

        default_result = _evaluate_run(
            repo_root=repo_root,
            config=deepcopy(config),
            config_path=config_path,
            run_id=f"{ablation_id}-{family_id.replace('.', '-')}-default",
            depth_cutoff=int(defaults["depth_cutoff"]),
            tol=float(defaults.get("tol", 1e-10)),
            s_max=float(defaults.get("s_max", 2.0)),
            output_dir=output_dir,
            notes="default_setting",
        )
        default_upper = default_result["final_upper_root"]

        rows.append(
            {
                "family_id": family_id,
                "ablation_factor": "default",
                "setting_value": "default",
                "parameter_value": json.dumps(defaults, sort_keys=True),
                **default_result,
                "spread_vs_default": 0.0,
                "is_unstable": False,
                "notes": "default",
            }
        )

        factor_order = [
            "depth_cutoff",
            "numerical_precision",
            "discretization_choice",
            "branch_ordering",
            "random_seed",
        ]

        for factor in factor_order:
            values = factors.get(factor, [])
            for value in values:
                if factor == "depth_cutoff" and int(value) == int(defaults["depth_cutoff"]):
                    continue
                if factor == "numerical_precision" and str(value) == str(defaults["numerical_precision"]):
                    continue
                if factor == "discretization_choice" and str(value) == str(defaults["discretization_choice"]):
                    continue
                if factor == "branch_ordering" and str(value) == str(defaults["branch_ordering"]):
                    continue
                if factor == "random_seed" and int(value) == int(defaults["random_seed"]):
                    continue

                cfg = deepcopy(config)
                depth_cutoff = int(defaults["depth_cutoff"])
                tol = float(defaults.get("tol", 1e-10))
                s_max = float(defaults.get("s_max", 2.0))
                notes = "applied"
                seed = int(defaults.get("random_seed", 0))

                if factor == "depth_cutoff":
                    depth_cutoff = int(value)
                elif factor == "numerical_precision":
                    tol = _tol_for_precision(str(value), float(defaults.get("tol", 1e-10)))
                elif factor == "discretization_choice":
                    s_max = _smax_for_discretization(str(value), float(defaults.get("s_max", 2.0)))
                elif factor == "branch_ordering":
                    cfg, notes = _apply_branch_ordering(cfg, str(value), seed)
                elif factor == "random_seed":
                    # Seed perturbation is meaningful only under shuffled branch ordering.
                    cfg, notes = _apply_branch_ordering(cfg, "shuffled", int(value))
                    if notes.startswith("not_applicable"):
                        notes = "not_applicable:seed_only_with_shuffled_ordering"

                run_id = f"{ablation_id}-{family_id.replace('.', '-')}-{factor}-{value}"
                result = _evaluate_run(
                    repo_root=repo_root,
                    config=cfg,
                    config_path=config_path,
                    run_id=run_id,
                    depth_cutoff=depth_cutoff,
                    tol=tol,
                    s_max=s_max,
                    output_dir=output_dir,
                    notes=f"factor={factor}; value={value}; {notes}",
                )

                spread = None
                if default_upper is not None and result["final_upper_root"] is not None:
                    spread = abs(float(result["final_upper_root"]) - float(default_upper))

                instability_rules = thresholds.get("instability_rules", {})
                spread_limit = instability_rules.get("spread_vs_default_max", 1e-2)
                drift_limit = instability_rules.get("last_step_drift_max", 2e-2)
                unstable = False
                if spread is not None and spread > float(spread_limit):
                    unstable = True
                if result["last_step_drift"] is not None and float(result["last_step_drift"]) > float(drift_limit):
                    unstable = True

                rows.append(
                    {
                        "family_id": family_id,
                        "ablation_factor": factor,
                        "setting_value": str(value),
                        "parameter_value": json.dumps({factor: value}, sort_keys=True),
                        **result,
                        "spread_vs_default": spread,
                        "is_unstable": unstable,
                        "notes": notes,
                    }
                )

    table_path = output_dir / "stability_table.csv"
    fieldnames = [
        "family_id",
        "ablation_factor",
        "setting_value",
        "run_id",
        "manifest_path",
        "final_depth",
        "final_upper_root",
        "final_lower_root",
        "interval_root_width",
        "last_step_drift",
        "reference_root",
        "abs_error",
        "spread_vs_default",
        "is_unstable",
        "notes",
    ]
    with table_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k) for k in fieldnames})

    summary_by_family: dict[str, dict[str, Any]] = {}
    for row in rows:
        fid = row["family_id"]
        summary = summary_by_family.setdefault(
            fid,
            {
                "default_upper_root": None,
                "max_spread": 0.0,
                "max_drift": 0.0,
                "unstable_count": 0,
            },
        )
        if row["ablation_factor"] == "default":
            summary["default_upper_root"] = row["final_upper_root"]
        if row.get("spread_vs_default") is not None:
            summary["max_spread"] = max(summary["max_spread"], float(row["spread_vs_default"]))
        if row.get("last_step_drift") is not None:
            summary["max_drift"] = max(summary["max_drift"], float(row["last_step_drift"]))
        if row.get("is_unstable"):
            summary["unstable_count"] += 1

    unstable_rows = [r for r in rows if r.get("is_unstable")]
    summary_json_path = output_dir / "stability_summary.json"
    summary_json_path.write_text(
        json.dumps(
            {
                "ablation_id": ablation_id,
                "plan_path": plan_path.relative_to(repo_root).as_posix(),
                "run_count": len(rows),
                "family_count": len(summary_by_family),
                "summary_by_family": summary_by_family,
                "unstable_cases": [
                    {
                        "family_id": r["family_id"],
                        "ablation_factor": r["ablation_factor"],
                        "setting_value": r["setting_value"],
                        "run_id": r["run_id"],
                        "spread_vs_default": r["spread_vs_default"],
                        "last_step_drift": r["last_step_drift"],
                        "notes": r["notes"],
                    }
                    for r in unstable_rows
                ],
                "recommended_defaults": {
                    "depth_cutoff": defaults["depth_cutoff"],
                    "numerical_precision": defaults["numerical_precision"],
                    "discretization_choice": defaults["discretization_choice"],
                    "branch_ordering": defaults["branch_ordering"],
                    "random_seed": defaults["random_seed"],
                },
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )

    report_path = output_dir / "stability_report.md"
    lines = [
        f"# Stability Report: {ablation_id}",
        "",
        f"Total runs: {len(rows)}",
        f"Families covered: {len(summary_by_family)}",
        "",
        "## Recommended default settings",
        f"- depth_cutoff: {defaults['depth_cutoff']}",
        f"- numerical_precision: {defaults['numerical_precision']} (tol={defaults['tol']})",
        f"- discretization_choice: {defaults['discretization_choice']} (s_max={defaults['s_max']})",
        f"- branch_ordering: {defaults['branch_ordering']}",
        f"- random_seed: {defaults['random_seed']}",
        "",
        "## Family stability summary",
    ]
    for fid, s in sorted(summary_by_family.items()):
        lines.append(
            f"- {fid}: default_upper_root={s['default_upper_root']}, max_spread={s['max_spread']:.6g}, "
            f"max_drift={s['max_drift']:.6g}, unstable_cases={s['unstable_count']}"
        )

    lines.append("")
    lines.append("## Unstable cases")
    if not unstable_rows:
        lines.append("- None flagged by current thresholds.")
    else:
        for r in unstable_rows:
            lines.append(
                f"- {r['family_id']} | factor={r['ablation_factor']} | value={r['setting_value']} | "
                f"spread={r['spread_vs_default']} | drift={r['last_step_drift']} | notes={r['notes']}"
            )

    lines.append("")
    lines.append("## Notes")
    lines.append("- random_seed is only semantically meaningful when branch ordering is shuffled.")
    lines.append("- factors not affecting a family are marked via notes as not_applicable.")
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(
        f"ablation_id={ablation_id} run_count={len(rows)} "
        f"stability_table={table_path.relative_to(repo_root).as_posix()} "
        f"summary={summary_json_path.relative_to(repo_root).as_posix()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
