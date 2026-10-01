#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _ensure_report(repo_root: Path, path: Path, script: str) -> None:
    if path.exists():
        return
    subprocess.run(["python", script], cwd=repo_root, check=True)


def _signature(values: list[float]) -> tuple[float, ...]:
    return tuple(round(float(x), 6) for x in values)


def _descriptor_tuple(
    config_id: str,
    run: dict[str, Any],
    pressure_cfg: dict[str, Any],
) -> tuple[Any, ...]:
    return (
        config_id,
        round(float(run["tau"]), 3),
        run["lens_state"],
        round(float(pressure_cfg["pressure_profiles"]["1.0"]["pressure_proxy"]), 9),
        round(float(pressure_cfg["growth_bound_proxy"]), 9),
    )


def _summarize_config(
    config_id: str,
    pressure: dict[str, Any],
    completion: dict[str, Any],
) -> dict[str, Any]:
    pressure_cfg = next(item for item in pressure["runs"] if item["family_id"] == config_id)
    completion_cfg = next(item for item in completion["summaries"] if item["config_id"] == config_id)
    runs = completion_cfg["runs"]

    descriptor_to_strata: dict[tuple[Any, ...], set[tuple[float, ...]]] = defaultdict(set)
    descriptor_to_runs: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    forced_strata_counter: Counter[tuple[float, ...]] = Counter()

    for run in runs:
        if not run["completion_summary"].get("numerically_converged", False):
            continue
        descriptor = _descriptor_tuple(config_id, run, pressure_cfg)
        sig = _signature(run["completion_summary"]["final_signature"])
        descriptor_to_strata[descriptor].add(sig)
        descriptor_to_runs[descriptor].append(run)
        feedback = run["feedback"]
        if feedback["applied"] and feedback["to_lens"] != feedback["from_lens"]:
            forced_strata_counter[sig] += 1

    mismatch_matrix = []
    multiple_strata_descriptor_count = 0
    for descriptor, strata in sorted(descriptor_to_strata.items()):
        row = {
            "descriptor": {
                "config_id": descriptor[0],
                "tau": descriptor[1],
                "lens_state": descriptor[2],
                "cocycle_pressure_mean": descriptor[3],
                "cocycle_growth_slope": descriptor[4],
            },
            "run_count": len(descriptor_to_runs[descriptor]),
            "strata_count": len(strata),
            "strata_signatures": [list(sig) for sig in sorted(strata)],
        }
        if len(strata) > 1:
            multiple_strata_descriptor_count += 1
        mismatch_matrix.append(row)

    forcing_summary = completion_cfg["p4_from_p5_feedback_summary"]
    material_events = int(forcing_summary["material_feedback_events"])
    persistent_forced_strata = sum(1 for count in forced_strata_counter.values() if count > 1)
    # Only the pre-change signature was recorded; no new-operator result was computed.
    new_strata_after_forcing = False
    persistence_after_forcing = False

    macro_summary = completion_cfg["macro_admissibility_summary"]
    admissible_count = int(macro_summary["admissible_count"])
    inadmissible_count = int(macro_summary["run_count"]) - admissible_count

    return {
        "config_id": config_id,
        "descriptor_count": len(descriptor_to_strata),
        "mismatch_matrix": mismatch_matrix,
        "multiple_strata_descriptor_count": multiple_strata_descriptor_count,
        "same_T0_descriptor_maps_to_multiple_T1_strata": multiple_strata_descriptor_count > 0,
        "forcing_to_new_strata_summary": {
            "material_p4_from_p5_events": material_events,
            "new_strata_after_forcing": new_strata_after_forcing,
            "persistent_forced_strata_count": 0,
            "repeated_pre_feedback_signature_count": persistent_forced_strata,
            "persistence_after_forcing": persistence_after_forcing,
        },
        "admissibility_obstruction_summary": {
            "admissible_count": admissible_count,
            "inadmissible_count": inadmissible_count,
        },
        "definability_verdict": (
            "rounded_descriptor_collision_only"
            if multiple_strata_descriptor_count > 0
            else "no_collision_in_finite_sample"
        ),
        "forcing_verdict": (
            "forcing_generates_persistent_new_strata"
            if new_strata_after_forcing and persistence_after_forcing
            else "forcing_not_persistent"
            if new_strata_after_forcing
            else "forcing_not_shown"
        ),
        "macro_admissibility_verdict": (
            "numerical_lumpability_obstruction_only"
            if admissible_count == 0 and inadmissible_count > 0
            else "no_global_macro_obstruction"
        ),
    }


def run() -> int:
    repo_root = Path(__file__).resolve().parent.parent

    pressure_path = repo_root / "results" / "continuous_pressure_closure" / "report.json"
    completion_path = repo_root / "results" / "packaging_completion_endomap" / "report.json"
    strict_path = repo_root / "results" / "strict_theory_extension" / "report.json"

    _ensure_report(repo_root, pressure_path, "scripts/run_continuous_pressure_closure_checks.py")
    _ensure_report(repo_root, completion_path, "scripts/run_packaging_completion_endomap.py")
    _ensure_report(repo_root, strict_path, "scripts/run_strict_theory_extension_audit.py")

    pressure = _load_json(pressure_path)
    completion = _load_json(completion_path)
    strict = _load_json(strict_path)

    configs = completion["configs"]
    per_config = [_summarize_config(config_id, pressure, completion) for config_id in configs]

    decision = "closed_on_audited_shell_class"
    if not all(item["same_T0_descriptor_maps_to_multiple_T1_strata"] for item in per_config):
        decision = "narrowed_and_closed"
    elif not all(
        item["forcing_to_new_strata_summary"]["persistence_after_forcing"] for item in per_config
    ):
        decision = "narrowed_and_closed"

    report = {
        "report_id": "strict_theory_extension_closure_v1",
        "schema_version": "v1",
        "generated_at_utc": "2026-03-18T00:00:00Z",
        "decision": decision,
        "closed_class_id": "continuous_full_loop_lawful_kernel_class_shell_stable",
        "selected_extension_route": "forcing_lemma_nondefinability_route",
        "configs": configs,
        "frozen_configs": [
            "configs/experiments/generated/continuous_full_loop_kernel.json",
            "configs/experiments/generated/continuous_full_loop_kernel_shell.json"
        ],
        "definability_mismatch_matrix": {
            item["config_id"]: item["mismatch_matrix"] for item in per_config
        },
        "forcing_to_new_strata_summary": {
            item["config_id"]: item["forcing_to_new_strata_summary"] for item in per_config
        },
        "admissibility_obstruction_counts": {
            item["config_id"]: item["admissibility_obstruction_summary"] for item in per_config
        },
        "same_T0_descriptor_maps_to_multiple_T1_strata": {
            item["config_id"]: item["same_T0_descriptor_maps_to_multiple_T1_strata"]
            for item in per_config
        },
        "definability_verdict": "exact_factorization_not_decided",
        "p4_from_p5_forcing_verdict": (
            "forcing_generates_persistent_new_strata"
            if all(
                item["forcing_verdict"] == "forcing_generates_persistent_new_strata"
                for item in per_config
            )
            else "forcing_requires_narrowing"
        ),
        "macro_admissibility_verdict": (
            "numerical_lumpability_obstruction_only"
            if all(
                item["macro_admissibility_verdict"] == "numerical_lumpability_obstruction_only"
                for item in per_config
            )
            else "macro_obstruction_requires_narrowing"
        ),
        "strict_extension_report_reference": strict["decision"],
        "per_config": per_config,
        "notes": [
            "The closure note uses audited-shell definability: T0-definable means constant on the audited T0 descriptor classes.",
            "The closure does not appeal to class broadening.",
            "This support report is evidence only; theorem closure lives in the note."
        ]
    }

    out_dir = repo_root / "results" / "strict_theory_extension_closure"
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
        writer.writerow([
            "config_id",
            "multiple_strata_descriptor_count",
            "material_p4_from_p5_events",
            "persistent_forced_strata_count",
            "admissible_count",
            "inadmissible_count",
        ])
        for item in per_config:
            writer.writerow([
                item["config_id"],
                item["multiple_strata_descriptor_count"],
                item["forcing_to_new_strata_summary"]["material_p4_from_p5_events"],
                item["forcing_to_new_strata_summary"]["persistent_forced_strata_count"],
                item["admissibility_obstruction_summary"]["admissible_count"],
                item["admissibility_obstruction_summary"]["inadmissible_count"],
            ])

    return 0


if __name__ == "__main__":
    raise SystemExit(run())
