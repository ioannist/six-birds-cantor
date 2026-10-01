#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path
from typing import Any


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _ensure_report(repo_root: Path, path: Path, script: str) -> None:
    if path.exists():
        return
    subprocess.run(["python", script], cwd=repo_root, check=True)


def _summarize_config(
    config_id: str,
    pressure: dict[str, Any],
    closure: dict[str, Any],
    completion: dict[str, Any],
) -> dict[str, Any]:
    pressure_cfg = next(item for item in pressure["runs"] if item["family_id"] == config_id)
    closure_cfg = next(item for item in closure["per_config"] if item["config_id"] == config_id)
    completion_cfg = next(item for item in completion["summaries"] if item["config_id"] == config_id)

    base_object_map = {
        "object_type": "T0 audited descriptor classes",
        "descriptor_count": closure_cfg["descriptor_count"],
        "descriptor_fields": [
            "config_id",
            "tau",
            "lens_state",
            "cocycle_pressure_mean",
            "cocycle_growth_slope",
        ],
    }
    extended_object_map = {
        "object_type": "T1 numerical completion candidates",
        "strata_count": completion_cfg["fixed_point_count_summary"]["distinct_fixed_point_total"],
        "strata_source": "rounded signatures of numerically converged completion candidates",
    }

    mismatch_rows = closure_cfg["mismatch_matrix"]
    multi_strata_rows = [row for row in mismatch_rows if row["strata_count"] > 1]
    non_factorization_rate = len(multi_strata_rows) / max(1, len(mismatch_rows))
    factor_through_t0 = len(multi_strata_rows) == 0

    forcing_summary = closure_cfg["forcing_to_new_strata_summary"]
    macro_summary = closure_cfg["admissibility_obstruction_summary"]

    return {
        "config_id": config_id,
        "base_object_map": base_object_map,
        "extended_object_map": extended_object_map,
        "pressure_summary": {
            "pressure_proxy": pressure_cfg["pressure_profiles"]["1.0"]["pressure_proxy"],
            "growth_slope": pressure_cfg["growth_bound_proxy"],
        },
        "factorization_test": {
            "factor_through_T0": None,
            "rounded_descriptor_has_no_sampled_split": factor_through_t0,
            "non_factorization_rate": non_factorization_rate,
            "multiple_T1_strata_per_T0_class": len(multi_strata_rows),
            "note": "A split of rounded readouts is a sampled descriptor collision only; exact base-object factorization is not decided.",
        },
        "saturation_summary": completion_cfg["saturation_summary"],
        "forcing_summary": forcing_summary,
        "macro_admissibility_summary": macro_summary,
    }


def run() -> int:
    repo_root = Path(__file__).resolve().parent.parent

    pressure_path = repo_root / "results" / "continuous_pressure_closure" / "report.json"
    completion_path = repo_root / "results" / "packaging_completion_endomap" / "report.json"
    closure_path = repo_root / "results" / "strict_theory_extension_closure" / "report.json"

    _ensure_report(repo_root, pressure_path, "scripts/run_continuous_pressure_closure_checks.py")
    _ensure_report(repo_root, completion_path, "scripts/run_packaging_completion_endomap.py")
    _ensure_report(repo_root, closure_path, "scripts/run_strict_theory_extension_closure_checks.py")

    pressure = _load_json(pressure_path)
    completion = _load_json(completion_path)
    closure = _load_json(closure_path)

    configs = completion["configs"]
    per_config = [
        _summarize_config(config_id, pressure, closure, completion) for config_id in configs
    ]

    intrinsic_extension = all(
        not item["factorization_test"]["rounded_descriptor_has_no_sampled_split"] for item in per_config
    )
    saturation_active = all(
        bool(item["saturation_summary"]["saturated"]) for item in per_config
    )
    forcing_active = all(
        item["forcing_summary"]["new_strata_after_forcing"]
        and item["forcing_summary"]["persistence_after_forcing"]
        for item in per_config
    )
    macro_obstruction = all(
        item["macro_admissibility_summary"]["admissible_count"] == 0
        and item["macro_admissibility_summary"]["inadmissible_count"] > 0
        for item in per_config
    )

    decision = "canonical_object_and_intrinsic_extension_closed"
    if not intrinsic_extension:
        decision = "canonical_object_extracted_but_extension_not_intrinsic"
    elif not (saturation_active and forcing_active and macro_obstruction):
        decision = "canonical_object_not_yet_stable"

    report = {
        "report_id": "canonical_hybrid_extension_v1",
        "schema_version": "v1",
        "generated_at_utc": "2026-03-18T00:00:00Z",
        "decision": decision,
        "base_theory_id": "T0_cocycle_pressure_theory",
        "extended_theory_id": "T1_hybrid_cocycle_plus_completion_theory",
        "configs": configs,
        "frozen_configs": [
            "configs/experiments/generated/continuous_full_loop_kernel.json",
            "configs/experiments/generated/continuous_full_loop_kernel_shell.json",
        ],
        "base_object_map": {
            "map_id": "t0_cocycle_object_map",
            "description": "Audited cocycle descriptor quotient on the shell-stable class.",
        },
        "extended_object_map": {
            "map_id": "t1_packaged_object_map",
            "description": "Packaged fixed-point strata map induced by the completion endomap and forcing structure.",
        },
        "factorization_test": {
            "factor_through_T0": None,
            "non_factorization_rate": sum(
                item["factorization_test"]["non_factorization_rate"] for item in per_config
            )
            / max(1, len(per_config)),
            "multiple_T1_strata_per_T0_class": sum(
                item["factorization_test"]["multiple_T1_strata_per_T0_class"]
                for item in per_config
            ),
            "per_config": {
                item["config_id"]: item["factorization_test"] for item in per_config
            },
        },
        "object_identity_verdict": "exact_object_identity_not_decided",
        "factorization_verdict": "exact_factorization_not_decided",
        "saturation_verdict": (
            "finite_start_duplicate_signal_only"
            if saturation_active
            else "saturation_not_stable"
        ),
        "forcing_verdict": (
            "feedback_proposals_without_post_change_certificate"
            if forcing_active
            else "forcing_not_stably_object_generating"
        ),
        "macro_admissibility_verdict": (
            "numerical_lumpability_obstruction_only"
            if macro_obstruction
            else "macro_obstruction_not_global"
        ),
        "per_config": per_config,
        "notes": [
            "The canonical object is the pair of T0 cocycle object map and T1 packaged-object map on the same audited shell.",
            "Intrinsic extension is tested by non-factorization, not by class broadening.",
            "This support report is evidence only; theorem closure lives in the note.",
        ],
    }

    out_dir = repo_root / "results" / "canonical_hybrid_extension"
    out_dir.mkdir(parents=True, exist_ok=True)
    import sys
    sys.path.insert(0, str(repo_root / "src"))
    from contextual_cantor.audit_status import mark_diagnostic_report
    mark_diagnostic_report(report, "rounded_descriptor_collision_diagnostic")

    (out_dir / "report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    with (out_dir / "report.csv").open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(
            [
                "config_id",
                "t0_descriptor_count",
                "t1_strata_count",
                "factor_through_T0",
                "non_factorization_rate",
                "multiple_T1_strata_per_T0_class",
                "persistent_new_strata",
                "inadmissible_count",
            ]
        )
        for item in per_config:
            writer.writerow(
                [
                    item["config_id"],
                    item["base_object_map"]["descriptor_count"],
                    item["extended_object_map"]["strata_count"],
                    item["factorization_test"]["factor_through_T0"],
                    item["factorization_test"]["non_factorization_rate"],
                    item["factorization_test"]["multiple_T1_strata_per_T0_class"],
                    item["forcing_summary"]["persistent_forced_strata_count"],
                    item["macro_admissibility_summary"]["inadmissible_count"],
                ]
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(run())
