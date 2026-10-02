#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Any


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _ensure_report(repo_root: Path, path: Path, script: str) -> None:
    if path.exists():
        return
    subprocess.run(["python", script], cwd=repo_root, check=True)


def _round_signature(signature: list[float]) -> tuple[float, ...]:
    return tuple(round(float(x), 6) for x in signature)


def _reconstructibility_label(mismatch_rate: float, unexplained: int) -> str:
    if unexplained == 0:
        return "yes"
    if mismatch_rate < 0.5:
        return "partial"
    return "no"


def _definability_verdict(label: str) -> str:
    if label == "yes":
        return "reconstructible_from_T0"
    if label == "partial":
        return "partial_nondefinability_signal"
    return "not_reconstructible_from_T0"


def _macro_verdict(admissible: int, inadmissible: int) -> str:
    if inadmissible > 0 and admissible == 0:
        return "T0_too_coarse_for_closed_macro_dynamics"
    if inadmissible > admissible:
        return "T0_under_pressure_from_macro_obstruction"
    return "no_extension_pressure_from_macro_admissibility"


def _new_strata_after_forcing(runs: list[dict[str, Any]]) -> tuple[bool, int]:
    source_signatures: dict[tuple[float, str], set[tuple[float, ...]]] = defaultdict(set)
    target_signatures: dict[tuple[float, str], set[tuple[float, ...]]] = defaultdict(set)
    material_events = 0

    for run in runs:
        summary = run["completion_summary"]
        feedback = run["feedback"]
        signature = _round_signature(summary["final_signature"])
        tau = float(run["tau"])
        source_signatures[(tau, run["lens_state"])].add(signature)
        post = run.get("post_feedback_completion_summary")
        if (feedback.get("numerical_object_change", False)
                and post is not None and post.get("numerically_converged", False)):
            material_events += 1
            # Compare the ACTUAL post-feedback output to its pre-feedback
            # panel, rather than relabelling the old signature as a new one.
            target_signatures[(tau, run["lens_state"])].add(_round_signature(post["final_signature"]))

    new_strata = 0
    for key, signatures in target_signatures.items():
        inherited = source_signatures.get(key, set())
        new_strata += len(signatures - inherited)
    return new_strata > 0, new_strata


def _summarize_config(
    config_id: str,
    pressure: dict[str, Any],
    completion: dict[str, Any],
) -> dict[str, Any]:
    pressure_cfg = next(item for item in pressure["runs"] if item["family_id"] == config_id)
    completion_cfg = next(item for item in completion["summaries"] if item["config_id"] == config_id)
    runs = completion_cfg["runs"]

    t0_descriptor_map: dict[tuple[Any, ...], set[tuple[float, ...]]] = defaultdict(set)
    descriptor_counts: dict[tuple[Any, ...], int] = defaultdict(int)

    for run in runs:
        descriptor = (
            config_id,
            round(float(run["tau"]), 3),
            run["lens_state"],
            round(float(pressure_cfg["pressure_profiles"]["1.0"]["pressure_proxy"]), 9),
            round(float(pressure_cfg["growth_bound_proxy"]), 9),
        )
        descriptor_counts[descriptor] += 1
        t0_descriptor_map[descriptor].add(
            _round_signature(run["completion_summary"]["final_signature"])
        )

    mismatched_descriptors = {
        key: value for key, value in t0_descriptor_map.items() if len(value) > 1
    }
    runs_on_mismatched_descriptors = sum(
        descriptor_counts[key] for key in mismatched_descriptors
    )
    mismatch_rate = runs_on_mismatched_descriptors / max(1, len(runs))
    unexplained_strata = sum(len(value) - 1 for value in mismatched_descriptors.values())
    reconstructible = _reconstructibility_label(mismatch_rate, unexplained_strata)
    definability_verdict = _definability_verdict(reconstructible)

    admissible_count = int(completion_cfg["macro_admissibility_summary"]["admissible_count"])
    run_count = int(completion_cfg["macro_admissibility_summary"]["run_count"])
    inadmissible_count = run_count - admissible_count
    macro_verdict = _macro_verdict(admissible_count, inadmissible_count)

    saturation = bool(completion_cfg["saturation_summary"]["saturated"])
    material_feedback_events = int(
        completion_cfg["p4_from_p5_feedback_summary"]["material_feedback_events"]
    )
    forcing_active = material_feedback_events > 0
    forcing_creates_new_strata, new_strata_count = _new_strata_after_forcing(runs)

    fixed_point_total = int(
        completion_cfg["fixed_point_count_summary"]["distinct_fixed_point_total"]
    )

    return {
        "config_id": config_id,
        "cocycle_pressure_mean": pressure_cfg["pressure_profiles"]["1.0"]["pressure_proxy"],
        "cocycle_growth_slope": pressure_cfg["growth_bound_proxy"],
        "tau_values_checked": completion_cfg["tau_values_checked"],
        "lens_values_checked": completion_cfg["lens_values_checked"],
        "initial_conditions_checked": completion_cfg["initial_conditions_checked"],
        "saturation_summary": completion_cfg["saturation_summary"],
        "forcing_summary": {
            "material_p4_from_p5_events": material_feedback_events,
            "new_packaged_strata_after_forcing": forcing_creates_new_strata,
            "new_packaged_strata_count": new_strata_count,
            "new_strata_certified": False,
            "scope": "numerical_pre_post_completion_comparison_only",
        },
        "definability_test": {
            "reconstructible_from_T0": "unknown",
            "sampled_descriptor_label": reconstructible,
            "exact_factorization_decided": False,
            "definability_mismatch_rate": mismatch_rate,
            "strata_not_explained_by_T0": unexplained_strata,
            "descriptor_count": len(t0_descriptor_map),
            "fixed_point_count": fixed_point_total,
            "note": "These are rounded sampled descriptors. Their sampled label does not decide factorization through the exact original T0 object.",
        },
        "macro_admissibility_obstruction": {
            "admissible_count": admissible_count,
            "inadmissible_count": inadmissible_count,
            "macro_admissibility_verdict": macro_verdict,
        },
        "object_identity_verdict": (
            "completion_strata_finer_than_T0_objects"
            if unexplained_strata > 0
            else "completion_strata_reconstructible_from_T0"
        ),
        "saturation_verdict": "saturated" if saturation else "not_saturated",
        "p4_from_p5_forcing_verdict": (
            "active_and_strata_generating"
            if forcing_active and forcing_creates_new_strata
            else "active_but_not_strata_generating"
            if forcing_active
            else "inactive"
        ),
        "definability_verdict": definability_verdict,
        "macro_admissibility_verdict": macro_verdict,
    }


def run() -> int:
    repo_root = Path(__file__).resolve().parent.parent

    pressure_path = repo_root / "results" / "continuous_pressure_closure" / "report.json"
    completion_path = repo_root / "results" / "packaging_completion_endomap" / "report.json"
    hybrid_path = repo_root / "results" / "hybrid_object_diagnostics" / "report.json"

    _ensure_report(
        repo_root, pressure_path, "scripts/run_continuous_pressure_closure_checks.py"
    )
    _ensure_report(
        repo_root, completion_path, "scripts/run_packaging_completion_endomap.py"
    )
    _ensure_report(repo_root, hybrid_path, "scripts/run_hybrid_object_diagnostics.py")

    pressure = _load_json(pressure_path)
    completion = _load_json(completion_path)
    hybrid = _load_json(hybrid_path)

    configs = completion["configs"]
    per_config = [_summarize_config(config_id, pressure, completion) for config_id in configs]

    saturation_real = all(
        item["saturation_verdict"] == "saturated" for item in per_config
    )
    forcing_real = all(
        item["p4_from_p5_forcing_verdict"] == "active_and_strata_generating"
        for item in per_config
    )
    nondefinable = all(
        item["definability_test"]["sampled_descriptor_label"] == "no"
        for item in per_config
    )
    macro_obstruction = all(
        item["macro_admissibility_verdict"]
        == "T0_too_coarse_for_closed_macro_dynamics"
        for item in per_config
    )
    partial_definability = any(
        item["definability_test"]["sampled_descriptor_label"] == "partial"
        for item in per_config
    )

    decision = "strict_extension_signal_but_not_certified"
    if saturation_real and forcing_real and nondefinable and macro_obstruction:
        decision = "strict_extension_certified"
    elif not (saturation_real and forcing_real):
        decision = "no_strict_extension_beyond_cocycle"
    elif partial_definability or not macro_obstruction:
        decision = "strict_extension_signal_but_not_certified"

    definability_verdict = (
        "nondefinable_from_T0"
        if nondefinable
        else "partial_nondefinability_signal"
        if partial_definability
        else "reconstructible_from_T0"
    )
    macro_admissibility_verdict = (
        "T0_too_coarse_for_closed_macro_dynamics"
        if macro_obstruction
        else "no_strict_extension_pressure_from_macro_admissibility"
    )

    report = {
        "report_id": "strict_theory_extension_audit_v1",
        "schema_version": "v1",
        "generated_at_utc": "2026-03-18T00:00:00Z",
        "base_theory_id": "T0_cocycle_pressure_theory",
        "extended_theory_id": "T1_hybrid_cocycle_plus_completion_theory",
        "base_closed_class": "continuous_full_loop_lawful_kernel_class_shell_stable",
        "configs": configs,
        "frozen_configs": [
            "configs/experiments/generated/continuous_full_loop_kernel.json",
            "configs/experiments/generated/continuous_full_loop_kernel_shell.json",
        ],
        "saturation_evidence": {
            "saturation_real": saturation_real,
            "per_config": {
                item["config_id"]: item["saturation_summary"] for item in per_config
            },
        },
        "forcing_evidence": {
            "forcing_real": forcing_real,
            "per_config": {
                item["config_id"]: item["forcing_summary"] for item in per_config
            },
        },
        "definability_test": {
            "reconstructible_from_T0": "unknown",
            "sampled_descriptor_label": "no" if nondefinable else "partial" if partial_definability else "yes",
            "exact_factorization_decided": False,
            "definability_mismatch_rate": sum(
                item["definability_test"]["definability_mismatch_rate"] for item in per_config
            )
            / max(1, len(per_config)),
            "strata_not_explained_by_T0": sum(
                item["definability_test"]["strata_not_explained_by_T0"] for item in per_config
            ),
            "per_config": {
                item["config_id"]: item["definability_test"] for item in per_config
            },
            "note": "Rounded candidate comparisons are diagnostics. Neither a sampled collision nor its absence decides factorization through the exact original T0 map.",
        },
        "macro_admissibility_obstruction": {
            "admissible_count": sum(
                item["macro_admissibility_obstruction"]["admissible_count"]
                for item in per_config
            ),
            "inadmissible_count": sum(
                item["macro_admissibility_obstruction"]["inadmissible_count"]
                for item in per_config
            ),
            "macro_admissibility_verdict": macro_admissibility_verdict,
            "per_config": {
                item["config_id"]: item["macro_admissibility_obstruction"]
                for item in per_config
            },
        },
        "object_identity_verdict": (
            "hybrid_objects_strictly_finer_than_T0_objects"
            if nondefinable
            else "hybrid_objects_not_shown_finer_than_T0"
        ),
        "saturation_verdict": "saturation_certified" if saturation_real else "saturation_not_shown",
        "p4_from_p5_forcing_verdict": (
            "forcing_active_with_new_strata"
            if forcing_real
            else "forcing_not_shown_to_generate_new_strata"
        ),
        "definability_verdict": definability_verdict,
        "macro_admissibility_verdict": macro_admissibility_verdict,
        "decision": decision,
        "notes": [
            "This audit replaces the v1 broadening question with the paper-native question of strict theory extension.",
            "The sampled configurations are held fixed; membership in an invariant original shell is not certified.",
            "Lumpability diagnostics are distinct from an exact non-factorization witness.",
            f"Hybrid v1 decision for comparison: {hybrid['decision']}.",
        ],
        "per_config": per_config,
    }

    out_dir = repo_root / "results" / "strict_theory_extension"
    out_dir.mkdir(parents=True, exist_ok=True)
    report["historical_workflow_verdicts"] = {
        key: report[key] for key in ("object_identity_verdict", "saturation_verdict",
                                    "p4_from_p5_forcing_verdict", "definability_verdict",
                                    "macro_admissibility_verdict")
    }
    report.update({
        "object_identity_verdict": "exact_object_identity_not_decided",
        "saturation_verdict": "numerical_convergence_signal_only",
        "p4_from_p5_forcing_verdict": "numerical_post_feedback_candidates_only",
        "definability_verdict": "exact_factorization_not_decided",
        "macro_admissibility_verdict": "numerical_lumpability_diagnostic_only",
    })
    import sys
    sys.path.insert(0, str(repo_root / "src"))
    from contextual_cantor.audit_status import mark_diagnostic_report
    mark_diagnostic_report(report, "numerical_completion_refinement_and_rounded_descriptors")
    (out_dir / "report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    with (out_dir / "report.csv").open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(
            [
                "config_id",
                "reconstructible_from_T0",
                "definability_mismatch_rate",
                "strata_not_explained_by_T0",
                "material_p4_from_p5_events",
                "new_packaged_strata_after_forcing",
                "admissible_count",
                "inadmissible_count",
            ]
        )
        for item in per_config:
            writer.writerow(
                [
                    item["config_id"],
                    item["definability_test"]["reconstructible_from_T0"],
                    item["definability_test"]["definability_mismatch_rate"],
                    item["definability_test"]["strata_not_explained_by_T0"],
                    item["forcing_summary"]["material_p4_from_p5_events"],
                    item["forcing_summary"]["new_packaged_strata_after_forcing"],
                    item["macro_admissibility_obstruction"]["admissible_count"],
                    item["macro_admissibility_obstruction"]["inadmissible_count"],
                ]
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(run())
