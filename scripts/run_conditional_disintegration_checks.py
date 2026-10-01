#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import math
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Any


GAP_THRESHOLD = 1e-3
KL_THRESHOLD = 1e-8


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _ensure_report(repo_root: Path, path: Path, script: str) -> None:
    if path.exists():
        return
    subprocess.run(["python", script], cwd=repo_root, check=True)


def _sig_key(signature: list[float]) -> tuple[float, ...]:
    return tuple(round(float(x), 6) for x in signature)


def _normalize(vec: list[float]) -> list[float]:
    if not vec or any(not math.isfinite(x) or x < 0 for x in vec):
        raise ValueError("future signatures must be finite nonnegative vectors")
    total = math.fsum(vec)
    if total <= 0.0:
        raise ValueError("future signatures must have positive mass")
    return [x / total for x in vec]


def _kl_divergence(p: list[float], q: list[float]) -> float:
    if len(p) != len(q) or not p:
        raise ValueError("KL vectors must have the same nonzero dimension")
    if any(not math.isfinite(x) or x < 0 for x in p + q):
        raise ValueError("KL vectors must have finite nonnegative entries")
    if not math.isclose(sum(p), 1.0, abs_tol=1e-10) or not math.isclose(sum(q), 1.0, abs_tol=1e-10):
        raise ValueError("KL vectors must be probability vectors")
    out = 0.0
    for px, qx in zip(p, q):
        if px > 0.0:
            if qx == 0.0:
                return math.inf
            out += px * math.log(px / qx)
    return out


def _stratum_pressure_profile(
    signature: tuple[float, ...],
    pressure_profiles: dict[str, dict[str, float]],
) -> dict[str, float]:
    """A synthetic moment correction, not pressure conditioned on a fiber.

    Its deficit can be positive even with one fiber. It therefore cannot
    establish information loss or pressure disintegration.
    """
    signature = tuple(_normalize(list(signature)))
    support = sum(1 for x in signature if x > 1e-9)
    out: dict[str, float] = {}
    for s_key, payload in pressure_profiles.items():
        s = float(s_key)
        if s < 0:
            raise ValueError("moment diagnostic requires s >= 0")
        moment = math.fsum(x ** (1.0 + s) for x in signature)
        out[s_key] = float(payload["pressure_proxy"]) + math.log(moment) / max(1, support)
    return out


def _summarize_config(
    config_id: str,
    pressure_cfg: dict[str, Any],
    completion_cfg: dict[str, Any],
    strict_cfg: dict[str, Any],
) -> dict[str, Any]:
    descriptor_groups: dict[tuple[Any, ...], list[tuple[float, ...]]] = defaultdict(list)
    for run in completion_cfg["runs"]:
        if not run["completion_summary"].get("numerically_converged", False):
            continue
        descriptor = (
            config_id,
            round(float(run["tau"]), 3),
            run["lens_state"],
        )
        descriptor_groups[descriptor].append(_sig_key(run["completion_summary"]["final_signature"]))

    descriptor_summaries = []
    min_gap = float("inf")
    min_kl = float("inf")
    max_kl = 0.0
    descriptor_positive_count = 0

    for descriptor, signatures in sorted(descriptor_groups.items()):
        total = len(signatures)
        strata_counts: dict[tuple[float, ...], int] = defaultdict(int)
        for sig in signatures:
            strata_counts[sig] += 1

        package_fiber_weights = {
            str(sig): count / total for sig, count in sorted(strata_counts.items())
        }
        normalized_sigs = {sig: _normalize(list(sig)) for sig in strata_counts}
        avg_future = [0.0] * len(next(iter(strata_counts)))
        for sig, count in strata_counts.items():
            weight = count / total
            for idx, value in enumerate(normalized_sigs[sig]):
                avg_future[idx] += weight * value

        closure_deficit_proxy = sum(
            (count / total) * _kl_divergence(normalized_sigs[sig], avg_future)
            for sig, count in strata_counts.items()
        )

        conditioned_profiles = {
            sig: _stratum_pressure_profile(sig, pressure_cfg["pressure_profiles"])
            for sig in strata_counts
        }
        pressure_gap = {}
        gap_positive = True
        for s_key, payload in pressure_cfg["pressure_profiles"].items():
            weighted = sum(
                (count / total) * conditioned_profiles[sig][s_key]
                for sig, count in strata_counts.items()
            )
            gap = float(payload["pressure_proxy"]) - weighted
            pressure_gap[s_key] = {
                "t0_pressure": float(payload["pressure_proxy"]),
                "weighted_conditioned_pressure": weighted,
                "gap": gap,
            }
            min_gap = min(min_gap, gap)
            gap_positive &= gap > GAP_THRESHOLD

        min_kl = min(min_kl, closure_deficit_proxy)
        max_kl = max(max_kl, closure_deficit_proxy)
        if gap_positive and closure_deficit_proxy > KL_THRESHOLD:
            descriptor_positive_count += 1

        descriptor_summaries.append(
            {
                "descriptor": {
                    "config_id": descriptor[0],
                    "tau": descriptor[1],
                    "lens_state": descriptor[2],
                },
                "package_fiber_weights": package_fiber_weights,
                "fiber_average_future_object": [round(value, 6) for value in avg_future],
                "closure_deficit_proxy": closure_deficit_proxy,
                "package_conditioned_pressure_gap": pressure_gap,
                "gap_bounded_away_from_zero": gap_positive,
            }
        )

    macro_counts = strict_cfg
    support = (
        bool(descriptor_summaries)
        and all(item["gap_bounded_away_from_zero"] for item in descriptor_summaries)
        and macro_counts["admissible_count"] == 0
    )

    return {
        "config_id": config_id,
        "package_fiber_descriptor_count": len(descriptor_summaries),
        "descriptor_summaries": descriptor_summaries,
        "min_gap_across_descriptors": min_gap if descriptor_summaries else 0.0,
        "min_closure_deficit_proxy": min_kl if descriptor_summaries else 0.0,
        "max_closure_deficit_proxy": max_kl,
        "positive_closure_deficit_descriptor_count": descriptor_positive_count,
        "macro_admissibility_summary": macro_counts,
        "non_tau_closedness_supported": macro_counts["admissible_count"] == 0 and macro_counts["inadmissible_count"] > 0,
        "disintegration_supported": False,
        "synthetic_moment_signal": support,
        "weight_scope": "frequency_of_numerically_converged_sampled_starts",
    }


def run() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    hybrid_path = repo_root / "results" / "hybrid_pressure_root" / "report.json"
    strict_path = repo_root / "results" / "strict_theory_extension_closure" / "report.json"
    completion_path = repo_root / "results" / "packaging_completion_endomap" / "report.json"
    pressure_path = repo_root / "results" / "continuous_pressure_closure" / "report.json"

    _ensure_report(repo_root, hybrid_path, "scripts/run_hybrid_pressure_root_checks.py")
    _ensure_report(repo_root, strict_path, "scripts/run_strict_theory_extension_closure_checks.py")
    _ensure_report(repo_root, completion_path, "scripts/run_packaging_completion_endomap.py")
    _ensure_report(repo_root, pressure_path, "scripts/run_continuous_pressure_closure_checks.py")

    hybrid = _load_json(hybrid_path)
    strict = _load_json(strict_path)
    completion = _load_json(completion_path)
    pressure = _load_json(pressure_path)

    configs = hybrid["configs"]
    per_config = []
    for config_id in configs:
        pressure_cfg = next(item for item in pressure["runs"] if item["family_id"] == config_id)
        completion_cfg = next(item for item in completion["summaries"] if item["config_id"] == config_id)
        strict_cfg = strict["admissibility_obstruction_counts"][config_id]
        strict_summary = {
            "admissible_count": strict_cfg["admissible_count"],
            "inadmissible_count": strict_cfg["inadmissible_count"],
        }
        per_config.append(_summarize_config(config_id, pressure_cfg, completion_cfg, strict_summary))

    all_supported = all(item["disintegration_supported"] for item in per_config)
    any_signal = all(
        item["min_gap_across_descriptors"] > 0.0 and item["min_closure_deficit_proxy"] >= 0.0
        for item in per_config
    )

    if all_supported:
        decision = "conditional_disintegration_closed"
    elif any_signal:
        decision = "conditional_disintegration_signal_but_not_closed"
    else:
        decision = "conditional_disintegration_not_supported"

    report = {
        "report_id": "conditional_disintegration_v1",
        "schema_version": "v1",
        "generated_at_utc": "2026-03-19T00:00:00Z",
        "decision": decision,
        "base_theory_id": "T0_cocycle_pressure_theory",
        "extended_theory_id": "T1_hybrid_cocycle_plus_completion_theory",
        "selected_consequence_object": "weighted_package_conditioned_pressure_gap",
        "configs": configs,
        "frozen_configs": [
            "configs/experiments/generated/continuous_full_loop_kernel.json",
            "configs/experiments/generated/continuous_full_loop_kernel_shell.json"
        ],
        "support_verdict_summary": {
            "working_route": "conditional_pressure_disintegration_route",
            "gap_bounded_away_from_zero_on_both_witnesses": all(
                item["min_gap_across_descriptors"] > GAP_THRESHOLD for item in per_config
            ),
            "closure_deficit_proxy_available_on_both_witnesses": all(
                item["max_closure_deficit_proxy"] > KL_THRESHOLD for item in per_config
            ),
            "macro_admissibility_failure_aligns_with_disintegration": all(
                item["non_tau_closedness_supported"] for item in per_config
            )
        },
        "per_config": per_config,
        "notes": [
            "The selected consequence object is the weighted package-conditioned pressure gap, not a direct stratumwise root gap.",
            "The KL-style closure-deficit quantity is treated as supporting evidence for the same insufficiency interpretation.",
            "The moment-corrected profiles are synthetic; their positive gap does not certify conditional pressure or insufficiency."
        ]
    }
    report["mathematical_certification"] = {
        "conditional_pressure_profiles_constructed": False,
        "pressure_disintegration_certified": False,
        "scope": "finite_synthetic_moment_diagnostic",
        "review": "docs/internal/mathematics_review_2026_10_01.md",
    }

    out_dir = repo_root / "results" / "conditional_disintegration"
    out_dir.mkdir(parents=True, exist_ok=True)
    import sys
    sys.path.insert(0, str(repo_root / "src"))
    from contextual_cantor.audit_status import mark_diagnostic_report
    mark_diagnostic_report(report, "synthetic_moment_diagnostic")

    (out_dir / "report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8"
    )

    with (out_dir / "report.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "config_id",
                "package_fiber_descriptor_count",
                "min_gap_across_descriptors",
                "min_closure_deficit_proxy",
                "admissible_count",
                "inadmissible_count",
                "disintegration_supported"
            ]
        )
        for item in per_config:
            writer.writerow(
                [
                    item["config_id"],
                    item["package_fiber_descriptor_count"],
                    item["min_gap_across_descriptors"],
                    item["min_closure_deficit_proxy"],
                    item["macro_admissibility_summary"]["admissible_count"],
                    item["macro_admissibility_summary"]["inadmissible_count"],
                    item["disintegration_supported"]
                ]
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(run())
